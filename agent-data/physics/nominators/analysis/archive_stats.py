#!/usr/bin/env python3
"""Nominator statistics for the Nobel Prize in Physics, 1961-1975, from the public
nomination archive (nobelprize.org/nomination/archive).

Usage:
    python3 archive_stats.py [--cache DIR] [--out archive_stats.md]

Fetches (with an on-disk cache) the yearly list pages, every nomination detail page
(show.php?id=...), and the laureate lists from api.nobelprize.org, then writes a
Markdown report.

Units:
  * "record"   = one row in the archive (one show.php page). A record may carry
                 several nominees (joint nomination) and several co-signing nominators.
  * "signature" = (record, nominator) pair. Shares by nominator type/country are
                 computed over signatures, so a letter co-signed by 3 people counts 3.
                 Unknown nominators ("N.N.", no name) are kept as their own category.
"""
import argparse
import collections
import html
import json
import os
import re
import subprocess
import time

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124 Safari/537.36")
BASE = "https://www.nobelprize.org/nomination/archive/"
YEARS = range(1961, 1976)
NORDIC = {"SE", "DK", "NO", "FI", "IS"}

REGION = {
    # Nordic
    **{c: "Nordic" for c in NORDIC},
    # Western Europe (non-Nordic)
    **{c: "Europe (other West)" for c in
       "GB IE FR DE CH AT NL BE LU IT ES PT GR MC".split()},
    # Eastern Europe incl. USSR
    **{c: "Eastern Europe / USSR" for c in
       "SU RU PL CS CZ SK HU RO BG YU RS HR SI DD UA BY".split()},
    "US": "North America", "CA": "North America",
    **{c: "Asia" for c in "JP CN TW HK IN PK KR SG IL IR TH PH ID LK BD MY".split()},
    **{c: "Latin America" for c in "MX BR AR CL PE CO VE UY CU".split()},
    **{c: "Oceania" for c in "AU NZ".split()},
    **{c: "Africa / Middle East" for c in "ZA EG NG KE LB TR SA IQ".split()},
}


METHOD = """
## Method

* Source: every physics (prize=1) row of the nobelprize.org nomination archive for
  1961-1975, one detail page (`show.php?id=`) per row. Each detail page lists the
  nominee(s) and nominator(s) with name, gender, birth/death year, profession (not
  always), city and country, and - for laureates - "Awarded the Nobel Prize in X YYYY".
  Some blocks add state, university or department (see "Fields" above).
* Unit: shares in sections 2-3 and 5 are over *signatures* (record x nominator), so a
  letter co-signed by three professors counts three times. Distinct nominators are
  identified by the archive's person id (`show_people.php?id=`).
* Prior laureate = the nominator's archive block (or, as fallback, a surname + birth-year
  match to api.nobelprize.org physics/chemistry laureates) shows a Physics or Chemistry
  prize awarded strictly before the nomination year (nominations for year Y close on
  31 January of Y, before that year's award).
* Country = the country printed on the nominator's detail block (location at the time of
  nomination as recorded by the archive), mapped to broad regions by ISO code.
* KVA (Royal Swedish Academy of Sciences) membership is not recorded in the archive, so
  category (c) is not determinable here. The Swedish-based share is the closest proxy
  (KVA physics-class members and Nobel committee members are mostly Sweden-based), but
  it also includes invited Swedish professors who were not members.

## Caveats

* Old data: 1961-1975 is the most recent public window (50-year secrecy rule; later
  years return 0 rows). The nominator pool then was ~100-180 letters/year; today the
  committee sends roughly 3,000 invitations and a few hundred candidates are nominated,
  so absolute volumes are not comparable; use the shares, not the counts.
* Geography has shifted: in 1961-75 China (PRC) is essentially absent and the USSR,
  West Germany and the UK loom large. Today China, Japan, South Korea, India and
  Europe-wide institutions would carry much more weight; US share has probably grown.
* The invited-nominator list rotates by university each year (Nordic chairs always
  invited; others by rotation), which inflates year-to-year country swings.
* "N.N." rows are nominations whose signatory is unknown/illegible; they are kept in the
  denominators of section 2 but have no country.
* Laureate status relies on name/birth-year matching and on-page award labels; a few
  misses are possible (e.g. name spelling differences).
* No subfield/speciality is recorded for nominators; any subfield weighting must be
  inferred externally (e.g. from the nominee they back).
"""


def fetch(url, path, sleep=0.3):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return open(path, encoding="utf-8", errors="replace").read()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["curl", "-s", "-A", UA, url, "-o", path], check=True)
    time.sleep(sleep)
    return open(path, encoding="utf-8", errors="replace").read()


def clean(s):
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def parse_show(h):
    """Return dict(year, nominees=[...], nominators=[...]) from a show.php page."""
    body = h[h.find('<div id="main">'):]
    body = body[:body.find("Share this")]
    year = int(re.search(r'rubr">Year:</span></td><td[^>]*>\s*(\d{4})', body).group(1))
    parts = re.split(r"<b>(Nominee|Nominator)[^<]*:</b>", body)
    out = {"year": year, "nominees": [], "nominators": []}
    for role, chunk in zip(parts[1::2], parts[2::2]):
        p = {}
        m = re.search(r"show_people\.php\?id=(\d+)", chunk)
        p["id"] = m.group(1) if m else None
        for k, v in re.findall(r'rubr">([^<]+):</span></td><td[^>]*>(.*?)</td>', chunk, re.S):
            p[k.strip()] = clean(v)
        cc = re.search(r"\(([A-Z]{2})\)", p.get("Country", ""))
        p["cc"] = cc.group(1) if cc else None
        p["country"] = re.sub(r"\s*\([A-Z]{2}\)\s*", "", p.get("Country", "")).strip() or None
        p["awards"] = [(a, int(y)) for a, y in
                       re.findall(r"Nobel Prize in ([A-Za-z ]+?) (\d{4})", chunk)]
        (out["nominees"] if role == "Nominee" else out["nominators"]).append(p)
    return out


def norm_name(s):
    s = html.unescape(s or "").lower()
    s = re.sub(r"[^a-z ]", "", __import__("unicodedata").normalize("NFKD", s)
               .encode("ascii", "ignore").decode())
    return s.split()


def load_laureates(cache):
    """(surname, birth_year) -> list of (category, award_year) for phy+che laureates."""
    idx = collections.defaultdict(list)
    for cat in ("phy", "che"):
        url = f"https://api.nobelprize.org/2.1/laureates?nobelPrizeCategory={cat}&limit=400"
        data = json.loads(fetch(url, os.path.join(cache, f"laureates_{cat}.json")))
        for l in data["laureates"]:
            name = (l.get("familyName") or l.get("orgName") or {}).get("en", "")
            by = (l.get("birth") or {}).get("date", "")[:4]
            for pz in l.get("nobelPrizes", []):
                c = pz["category"]["en"]
                if c in ("Physics", "Chemistry"):
                    nm = norm_name(name)
                    if nm:
                        idx[(nm[-1], by)].append((c, int(pz["awardYear"])))
    return idx


def pct(n, d):
    return f"{100 * n / d:.1f}%" if d else "-"


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join("---" if i == 0 else "---:" for i in range(len(headers))) + "|"]
    lines += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(lines)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="/private/tmp/claude-501/-Users-davicosta-Desktop-projects-"
                    "nobel-prize-forecasting/221175dc-bcf6-445f-abd0-d9974d942539/scratchpad/archive")
    ap.add_argument("--out", default=os.path.join(here, "archive_stats.md"))
    a = ap.parse_args()

    records = []
    available = []
    for y in YEARS:
        lh = fetch(f"{BASE}list.php?prize=1&year={y}", os.path.join(a.cache, f"list_{y}.html"))
        ids = re.findall(r"show\.php\?id=(\d+)", lh)
        if ids:
            available.append(y)
        for i in ids:
            r = parse_show(fetch(f"{BASE}show.php?id={i}", os.path.join(a.cache, "show", f"{i}.html")))
            r["id"] = i
            records.append(r)
    lidx = load_laureates(a.cache)

    def is_prior_laureate(p, year):
        # 1) award info printed on the archive page itself
        aw = [(c, y) for c, y in p["awards"] if c in ("Physics", "Chemistry")]
        # 2) fallback: surname + birth year match against the API
        if not aw and p.get("Name"):
            nm = norm_name(p["Name"])
            if nm:
                aw = lidx.get((nm[-1], p.get("Year, Birth", "")), [])
        return any(y < year for _, y in aw), aw

    sigs = []  # (record, nominator)
    for r in records:
        for p in r["nominators"]:
            known = bool(p.get("id")) and p.get("Name", "").strip() not in ("", "N.N.")
            prior, aw = is_prior_laureate(p, r["year"]) if known else (False, [])
            p["known"], p["prior"], p["aw"] = known, prior, aw
            sigs.append((r, p))

    L = []
    w = L.append
    w("# Physics Nobel nominators, 1961-1975 (public nomination archive)\n")
    w(f"Generated by `archive_stats.py` from nobelprize.org/nomination/archive (prize=1). "
      f"Years with data: {available[0]}-{available[-1]} ({len(available)} years). "
      f"Records: {len(records)}; nominator signatures: {len(sigs)}.\n")

    # ---- 1. per year
    w("## 1. Volume per year\n")
    rows = []
    for y in available:
        rs = [r for r in records if r["year"] == y]
        noms = {p["id"] for r in rs for p in r["nominators"] if p["known"]}
        nees = {p["id"] for r in rs for p in r["nominees"] if p.get("id")}
        nsig = sum(len(r["nominators"]) for r in rs)
        rows.append((y, len(rs), nsig, len(noms), len(nees)))
    tot = (sum(x[1] for x in rows), sum(x[2] for x in rows))
    allnoms = {p["id"] for _, p in sigs if p["known"]}
    allnees = {p["id"] for r in records for p in r["nominees"] if p.get("id")}
    rows.append(("**All**", tot[0], tot[1], len(allnoms), len(allnees)))
    w(table(["Year", "Records", "Nominator signatures", "Distinct nominators",
             "Distinct nominees"], rows))
    w("\nDistinct counts in the *All* row are over the whole window (not the sum of years). "
      "Distinct nominators exclude unknown (N.N.) signatories; a nominator who sent separate "
      "letters for several candidates in one year counts once.\n")

    # ---- 2. nominator type
    w("## 2. Nominator type (share of signatures)\n")
    n = len(sigs)
    unk = [s for s in sigs if not s[1]["known"]]
    lau = [s for s in sigs if s[1]["known"] and s[1]["prior"]]
    nord = [s for s in sigs if s[1]["known"] and not s[1]["prior"] and s[1]["cc"] in NORDIC]
    rest = [s for s in sigs if s[1]["known"] and not s[1]["prior"] and s[1]["cc"] not in NORDIC]
    lau_nordic = sum(1 for s in lau if s[1]["cc"] in NORDIC)
    all_nordic = sum(1 for s in sigs if s[1]["known"] and s[1]["cc"] in NORDIC)
    w(table(["Type (mutually exclusive, in this order)", "Signatures", "Share"], [
        ("(a) Prior physics/chemistry laureate", len(lau), pct(len(lau), n)),
        ("(b) Nordic-based, not a laureate", len(nord), pct(len(nord), n)),
        ("(c) Royal Swedish Academy of Sciences member", "n/a", "not determinable"),
        ("(d) Everyone else (known)", len(rest), pct(len(rest), n)),
        ("Unknown nominator (N.N.)", len(unk), pct(len(unk), n)),
        ("Total", n, "100%"),
    ]))
    w(f"\nOverlaps: {lau_nordic} of the laureate signatures are Nordic-based. "
      f"All Nordic-based signatures (incl. laureates): {all_nordic} ({pct(all_nordic, n)}). "
      f"Swedish-based only: {sum(1 for s in sigs if s[1]['cc'] == 'SE')} "
      f"({pct(sum(1 for s in sigs if s[1]['cc'] == 'SE'), n)}).\n")
    lau_people = {s[1]["id"] for s in lau}
    lau_by_year = collections.Counter(s[0]["year"] for s in lau)
    phy_l = sum(1 for s in lau if any(c == "Physics" and y < s[0]["year"] for c, y in s[1]["aw"]))
    w(f"Of the laureate signatures, {phy_l} come from physics laureates and "
      f"{len(lau) - phy_l} from chemistry-only laureates. "
      f"Distinct prior laureates who nominated: {len(lau_people)}. "
      "Laureate share by year: " + ", ".join(
          f"{y}: {pct(lau_by_year[y], sum(1 for s in sigs if s[0]['year'] == y))}"
          for y in available) + ".\n")

    # ---- 3. country / region
    w("## 3. Nominator country and region (share of signatures with a known country)\n")
    ks = [s for s in sigs if s[1]["country"]]
    nk = len(ks)
    cc = collections.Counter(s[1]["country"] for s in ks)
    rows = [(c, k, pct(k, nk)) for c, k in cc.most_common(15)]
    other = nk - sum(k for _, k in cc.most_common(15))
    rows += [("Other", other, pct(other, nk)), ("Total with country", nk, "100%")]
    w(table(["Country", "Signatures", "Share"], rows))
    w(f"\n{n - nk} signatures ({pct(n - nk, n)}) have no country (mostly N.N.).\n")
    rc = collections.Counter(REGION.get(s[1]["cc"], "Other/unmapped") for s in ks)
    w(table(["Region", "Signatures", "Share"],
            [(r, k, pct(k, nk)) for r, k in rc.most_common()]))
    unm = collections.Counter(s[1]["country"] for s in ks if s[1]["cc"] not in REGION)
    if unm:
        w("\nUnmapped countries: " + ", ".join(f"{c} ({k})" for c, k in unm.most_common()) + "\n")
    w("")

    # ---- 4. nominations per nominator
    w("## 4. Nominations per nominator (known nominators, whole window)\n")
    per = collections.Counter(s[1]["id"] for s in sigs if s[1]["known"])
    yrs = collections.defaultdict(set)
    for r, p in sigs:
        if p["known"]:
            yrs[p["id"]].add(r["year"])
    dist = collections.Counter(min(v, 6) for v in per.values())
    np_ = len(per)
    rows = [(("6+" if k == 6 else k), dist[k], pct(dist[k], np_),
             sum(v for v in per.values() if min(v, 6) == k),
             pct(sum(v for v in per.values() if min(v, 6) == k), sum(per.values())))
            for k in sorted(dist)]
    w(table(["Signatures per nominator", "Nominators", "Share of nominators",
             "Signatures", "Share of signatures"], rows))
    ydist = collections.Counter(min(len(v), 5) for v in yrs.values())
    w("\nDistinct nomination *years* per nominator: " + ", ".join(
        f"{'5+' if k == 5 else k} yr: {ydist[k]} ({pct(ydist[k], np_)})" for k in sorted(ydist)) + ".\n")
    top = per.most_common(10)
    name = {p["id"]: p.get("Name") for _, p in sigs}
    w("Most active nominators: " + "; ".join(f"{name[i]} ({k})" for i, k in top) + ".\n")
    multi_nee = sum(1 for r in records if len(r["nominees"]) > 1)
    multi_nor = sum(1 for r in records if len(r["nominators"]) > 1)
    w(f"Records naming more than one nominee (joint nominations): {multi_nee} of "
      f"{len(records)} ({pct(multi_nee, len(records))}). "
      f"Records co-signed by more than one nominator: {multi_nor} ({pct(multi_nor, len(records))}).\n")
    # nominators who, in a given year, backed >1 distinct candidate across records
    yr_nees = collections.defaultdict(set)
    for r, p in sigs:
        if p["known"]:
            for q in r["nominees"]:
                yr_nees[(p["id"], r["year"])].add(q.get("id"))
    spread = sum(1 for v in yr_nees.values() if len(v) > 1)
    w(f"Nominator-years in which the nominator supported >1 distinct nominee: "
      f"{spread} of {len(yr_nees)} ({pct(spread, len(yr_nees))}).\n")

    # ---- 5. home bias
    w("## 5. Home bias (nominator and nominee in same country)\n")
    pairs = [(r, p, q) for r, p in sigs for q in r["nominees"] if p["cc"] and q.get("cc")]
    same = sum(1 for _, p, q in pairs if p["cc"] == q["cc"])
    w(f"Over nominator-nominee pairs with both countries known: {same} of {len(pairs)} "
      f"({pct(same, len(pairs))}) are same-country.\n")
    rows = []
    for c, _ in collections.Counter(p["country"] for _, p, _ in pairs).most_common(10):
        ps = [(p, q) for _, p, q in pairs if p["country"] == c]
        s = sum(1 for p, q in ps if p["cc"] == q["cc"])
        rows.append((c, len(ps), pct(s, len(ps))))
    w(table(["Nominator country", "Pairs", "Same-country share"], rows))
    # base rate: share if nominees were drawn from the overall nominee-country mix
    nee_cc = collections.Counter(q["cc"] for _, _, q in pairs)
    tot_p = len(pairs)
    exp = sum(collections.Counter(p["cc"] for _, p, _ in pairs)[c] * nee_cc[c] / tot_p
              for c in nee_cc) / tot_p
    w(f"\nBaseline (same-country share expected if nominees were matched at random to "
      f"nominators, holding both country mixes fixed): {100 * exp:.1f}%.\n")

    # ---- fields
    w("## Fields shown in the archive\n")
    fields = collections.Counter(k for _, p in sigs for k in p
                                 if k not in ("id", "cc", "country", "awards", "known", "prior", "aw"))
    w("Nominator fields present (count of signatures): " +
      ", ".join(f"{k} ({v})" for k, v in fields.most_common()) + ". "
      "No subfield/speciality field; 'Profession' is a coarse free-text title "
      "(e.g. Physicist); it is blank for most signatures.\n")
    prof = collections.Counter(p.get("Profession", "") for _, p in sigs if p["known"])
    w("Top nominator 'Profession' values: " +
      ", ".join(f"{k or '(blank)'} ({v})" for k, v in prof.most_common(10)) + ".\n")

    w(METHOD)
    open(a.out, "w").write("\n".join(L))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
