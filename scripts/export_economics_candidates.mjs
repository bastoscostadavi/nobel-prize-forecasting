import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook } from '@oai/artifact-tool';

const directory = path.resolve(process.cwd(), 'agent-data/economics/candidates');
const source = path.join(directory, 'candidates.json');
const data = JSON.parse(await fs.readFile(source, 'utf8'));
const workbook = Workbook.create();
if (process.argv.includes('--help-csv')) {
  console.log(workbook.help('workbook.toCSV', { include: 'index,examples,notes', maxChars: 3500 }).ndjson);
  process.exit(0);
}
const sheet = workbook.worksheets.add('Candidates');
const rows = [['candidate_id', 'contribution', 'credited_names', 'subfield', 'overlap_review', 'conflict_flags', 'credit_note', 'sources'],
  ...data.candidates.map(c => [c.candidate_id, c.discovery, c.credited_names.join('; '), c.subfield,
    c.overlap_review ?? '', c.conflict_flags.join('; '), c.credit_note, c.sources.join('; ')])];
if (rows.length !== 51 || new Set(rows.slice(1).map(row => row[0])).size !== 50) throw new Error('Expected 50 unique entries');
sheet.getRange('A1:H51').values = rows;
sheet.getRange('A1:H51').format.font = {name: 'Arial', size: 11};
sheet.getRange('A1:H1').format = {fill: '#1F4E78', font: {name: 'Arial', size: 11, bold: true, color: '#FFFFFF'}};
sheet.getRange('A1:A51').format.columnWidth = 12;
sheet.getRange('B1:B51').format.columnWidth = 64;
sheet.getRange('C1:C51').format.columnWidth = 62;
sheet.getRange('A1:C51').format.wrapText = true;
sheet.getRange('A1:C51').format.autofitRows();
workbook.recalculate();
console.log((await workbook.inspect({kind: 'table', range: 'Candidates!A1:C4', include: 'values', tableMaxRows: 4, tableMaxCols: 3, maxChars: 2000})).ndjson);
const preview = await workbook.render({sheetName: 'Candidates', range: 'A1:C8', scale: 1.5, format: 'png'});
await fs.writeFile('/private/tmp/economics-candidates-preview.png', new Uint8Array(await preview.arrayBuffer()));
// CSV serialization reads the authored, verified Artifact Tool cell matrix.
const values = sheet.getRange('A1:H51').values;
if (JSON.stringify(values) !== JSON.stringify(rows)) throw new Error('Cell contents differ from canonical input');
const quote = value => '"' + String(value ?? '').replaceAll('"', '""') + '"';
await fs.writeFile(path.join(directory, 'candidates.csv'),
  values.map(row => row.map(quote).join(',')).join('\n') + '\n');
console.log('Saved CSV with 50 contributions from the verified Artifact Tool matrix.');
