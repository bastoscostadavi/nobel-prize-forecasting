# OpenAI committee-model sensitivity comparison

The nomination lists, personas, substantive protocol, evidence boundary, and five-simulation allocation are fixed. The model arms use independent deterministic candidate-order shuffles, so this is a model-arm sensitivity comparison rather than an exact prompt-token pair.
Obvious saved-name variants are normalized for this comparison; the raw arm summaries retain the exact saved strings.

| Committee model | Katori–Ye wins | Share | Wilson 95% CI | Distinct winners | Entropy (bits) |
|---|---:|---:|---:|---:|---:|
| gpt-5.6-terra (`high`) | 59/60 | 98.3% | 91.1%–99.7% | 2 | 0.122 |
| gpt-6-luna (`high`) | 34/60 | 56.7% | 44.1%–68.4% | 21 | 2.799 |

Katori–Ye changes by -41.7% (Luna minus Terra).
The full winner distributions have total-variation distance 0.417.
Simulation-level Fisher exact: p = 1.61224e-08.
Paired 12-nomination-run sign-flip test: p = 0.00195312.

**Conclusion:** The committee-model substitution materially changes the simulated winner distribution.

## Winner configurations

| Laureates | Terra | Luna |
|---|---:|---:|
| Hidetoshi Katori + Jun Ye | 59 | 34 |
| Charles L. Kane + Eugene J. Mele + Laurens W. Molenkamp | 0 | 3 |
| Michael Berry + Yakir Aharonov | 0 | 3 |
| Alexei Kitaev + Andrew M. Steane + Peter W. Shor | 0 | 2 |
| Harald Rose + Maximilian Haider + Ondrej L. Krivanek | 1 | 1 |
| Michel Della Negra + Peter Jenni + Tejinder Virdee | 0 | 2 |
| Alessandra Buonanno + Frans Pretorius + Thibault Damour | 0 | 1 |
| Alexander A. Belavin + Alexander B. Zamolodchikov + Alexander M. Polyakov | 0 | 1 |
| Alexandre Blais + Andreas Wallraff + Robert J. Schoelkopf | 0 | 1 |
| Alfred Y. Cho + Federico Capasso + Jérôme Faist | 0 | 1 |
| Artur K. Ekert + Charles H. Bennett + Gilles Brassard | 0 | 1 |
| Bart J. van Wees + David A. Wharam | 0 | 1 |
| Chang C. Tsuei + Dale J. Van Harlingen + John R. Kirtley | 0 | 1 |
| Charles L. Bennett + David N. Spergel + Lyman A. Page Jr. | 0 | 1 |
| Christophe Salomon + John E. Thomas + Rudolf Grimm | 0 | 1 |
| Eli Yablonovitch + John D. Joannopoulos + Sajeev John | 0 | 1 |
| Frans Pretorius + John G. Baker + Manuela Campanelli | 0 | 1 |
| Harald Rose + Knut Urban + Maximilian Haider | 0 | 1 |
| Jocelyn Bell Burnell | 0 | 1 |
| Juan Ignacio Cirac + Peter Zoller + Rainer Blatt | 0 | 1 |
| Peter F. Moulton + Ursula Keller + Wilson Sibbett | 0 | 1 |

See the JSON companion for per-nomination-run counts and exact test metadata.
