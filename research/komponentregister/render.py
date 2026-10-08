#!/usr/bin/env python3
"""Render the component register from its canonical CSV files (stdlib only)."""
import argparse
import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SECTIONS = {
    'core': 'Aktuell Core och bänkhårdvara',
    'bom': 'Puck rev A BOM',
    'decoders': 'Alternativa videodekodrar',
    'video_out': 'FPGA minne och bildutgång',
    'measurement': 'RF och mätning',
    'power_control': 'Kraftförsörjning styrning och SBC spår',
    'vtx': 'VTX kandidater från samtalet',
    'vtx_external': 'Övriga namn i OpenVTX research',
    'osd': 'Sändarsidans OSD hårdvara',
    'reference_hardware': 'Jämförelseprodukter och övriga hårdvarureferenser',
    'projects': 'Projekt och verktyg',
    'interfaces': 'Gränssnitt och signaler',
}
STATUS = {
    'core_target': 'Core mål', 'bom': 'BOM rev A', 'bom_dnp': 'BOM DNP',
    'in_use': 'Används i utvecklingen', 'planned': 'Planerat',
    'research': 'Research', 'reference': 'Referens', 'not_selected': 'Ej valt',
}
OWNERSHIP = {'owned': 'Hemma', 'ordered': 'Beställt',
             'not_reported': 'Ej uppgivet', 'not_applicable': 'Ej tillämpligt'}
LIFECYCLE = {
    'unknown': 'Ej kontrollerad', 'not_applicable': 'Ej tillämpligt',
    'active': 'Active', 'active_reported': 'Active enligt tidigare källnotering',
    'production': 'Production', 'recommended_for_new_designs': 'Recommended for New Designs',
    'discontinued': 'Discontinued', 'nrnd_reported': 'NRND enligt tidigare källnotering',
}


def read_csv(name):
    with (ROOT / name).open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        records = list(reader)
    if not records or any(None in row or any(v is None for v in row.values()) for row in records):
        raise ValueError(f'Empty or malformed CSV: {name}')
    return records


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def render():
    parts = read_csv('components.csv')
    sources = read_csv('sources.csv')
    source_by_id = {s['id']: s for s in sources}
    ids = [p['id'] for p in parts]
    if len(ids) != len(set(ids)) or len(source_by_id) != len(sources):
        raise ValueError('Duplicate record or source ID')
    if len({p['name'].casefold() for p in parts}) != len(parts):
        raise ValueError('Duplicate canonical name; keep aliases on the existing record')
    bom_refs = []
    for part in parts:
        if not re.fullmatch(r'[CBPI][0-9]{3}', part['id']):
            raise ValueError(f'Invalid register ID: {part["id"]}')
        if part['section'] not in SECTIONS or part['status'] not in STATUS:
            raise ValueError(f'Unknown section or status: {part["id"]}')
        if part['ownership'] not in OWNERSHIP or part['lifecycle'] not in LIFECYCLE:
            raise ValueError(f'Unknown ownership or lifecycle: {part["id"]}')
        if not part['name'] or not part['class'] or not part['kind'] or not part['source_ids']:
            raise ValueError(f'Missing identity or classification: {part["id"]}')
        for sid in part['source_ids'].split(';'):
            if sid not in source_by_id:
                raise ValueError(f'Missing source {sid}: {part["id"]}')
        if part['section'] == 'bom':
            refs = part['refs'].split()
            if len(refs) != int(part['design_qty']):
                raise ValueError(f'BOM count mismatch: {part["id"]}')
            bom_refs.extend(refs)
    if len(bom_refs) != len(set(bom_refs)):
        raise ValueError('A BOM placement is mapped more than once')
    counts = Counter(p['section'] for p in parts)
    header = f'''# OpenVRX komponenter och research

Register över {len(parts)} komponent-, projekt- och gränssnittsposter, grundat på
projektsamtalet, befintliga research-anteckningar och den exporterade rev A BOM:en.
Uppdaterat 2026-10-08. Alla {len(bom_refs)} schemapositioner i BOM-exporten är mappade,
även generiska delar, testpunkter, monteringshål och DNP-positioner.

[components.csv](components.csv) är registret som ändras. Det innehåller även
MPN, alias/varianter, tillverkare, omfattning, ägarstatus, antal, referensbeteckningar,
footprint, livscykel och datum för livscykelkontroll, primärlänk och nästa kontroll.
[sources.csv](sources.csv) håller källornas filvägar, läsdatum, versionslås och
SHA-256 för lokala underlag. Den här läsvyn genereras med [render.py](render.py).

## Så läses läget

**Core mål** betyder att gatewaren utvecklas mot delen. **BOM rev A** betyder
att den finns i den nuvarande schemaexporten. **Används i utvecklingen** gäller
projekt, verktyg och implementerade gränssnitt. Inget av detta betyder att
OpenVRX har körts på hårdvara. **Research**, **Referens** och **Planerat** är
separata från ett valt eller verifierat komponentval.

Hemma: Eachine Moneagle i förpackning och ett kamera/VTX-set som ägaren uppger
ankom 2026-10-08. Kartongetiketten är `S2-OSD`; lösbladet är märkt
`5.8G 40CH AIO FPV CAMERA`. Exakt modell och kretskort är inte identifierade.
Beställt: Tang Nano 20K; ägaren väntar leverans 2026-10-09 (ej mottaget per
2026-10-08). Lösbladets uppgifter har inte verifierats mot hårdvaran; inget
har provats på hårdvara. Övrigt innehav är **ej uppgivet**; antalet i
`design_qty` gäller konstruktionen, inte lagret.
Kontrollerad livscykel innebär inte kontrollerad tillgång.

`C` identifierar fysisk komponent, modul, produkt eller kortfamilj; `B` en
generisk BOM-grupp; `P` ett projekt eller verktyg; `I` ett gränssnitt/signal.
ID:n är interna och får inte återanvändas. Schemat har sina egna beteckningar,
till exempel U4/U5, och tillverkarens orderkod ligger i `part_number`.
`aliases` innehåller också familjenamn och närliggande varianter; fältet är
inte ett påstående om elektrisk eller mekanisk utbytbarhet.

Läsdatum i källtabellen är när underlaget lästes. En äldre livscykelnotering
behåller sitt ursprungliga datum i CSV:n. Poster från extern OpenVTX-research
är namnkandidater; klassificering och specifikationer därifrån behöver egen
kontroll innan komponentval. Butiker, priser och inköpslänkar ingår inte.

## Samband att behålla

- Mottagarkedjan: RX5808/RTC6715 → TVP5150AM1 → Core på GW2AR-18 → DVI/HDMI.
- Rev A är ett separat dekoderkort. FPGA, mottagarmoduler och OLED ligger utanför dess BOM.
- OpenOSD-X och OpenPixelOSD skapar analog OSD före mottagaren. Core behöver
  verifiera den färdiga OSD-bilden genom avkodning, mixning och skalning.
  MSP DisplayPort är FC:ns ritkommandon till OSD:n; egen telemetrirendering
  i Core kräver en separat dataväg. Se SRC23 och SRC24.
- LMX/HMC/MAX/RF-förstärkarna hör till ett möjligt framtida analogt VTX-spår.
  De är inte tillägg till rev A BOM eller ett valt RF-schema.

## Underhåll

1. Sök på namn, MPN och alias innan en post läggs till. Lägg ny evidens på
   befintligt ID; ge en annan ordervariant en egen post när skillnaden spelar roll.
2. Spara ursprung, roll, projektläge och nästa kontroll. Ange saknad identitet
   som okänd; gör inte ett familjenamn till en verifierad orderkod.
3. Ändra innehav efter ägaruppgift, BOM-status efter schemaexport och
   hårdvarustatus efter mätning. Behåll äldre källor när ny evidens tillkommer.
4. Vid ny BOM-export: mappa varje referensbeteckning en gång, kontrollera
   mängder och footprint, och omkontrollera livscykeln före kortbeställning.
5. Kör `python3 research/komponentregister/render.py` från OpenVRX-navet.
   Kör samma kommando med `--check` för att kontrollera CSV och läsvy utan att skriva.

## Index

| Grupp | Poster |
|---|---:|
'''
    lines = [header.rstrip()]
    for section, title in SECTIONS.items():
        lines.append(f'| {title} | {counts[section]} |')
    for section, title in SECTIONS.items():
        lines += ['', f'## {title}', '', '| ID | Namn och varianter | Klass / typ | Projektläge | Roll och underlag |', '|---|---|---|---|---|']
        for part in (p for p in parts if p['section'] == section):
            name = part['name'] + (f' ({part["aliases"]})' if part['aliases'] else '')
            status = STATUS[part['status']]
            if part['ownership'] in ('owned', 'ordered'):
                status += '; ' + OWNERSHIP[part['ownership']]
            if part['lifecycle'] not in ('unknown', 'not_applicable'):
                status += '; ' + LIFECYCLE[part['lifecycle']] + ' ' + part['lifecycle_checked_on']
            notes = part['notes']
            if part['refs']:
                notes = f'{part["design_qty"]} st: {part["refs"]}. ' + notes
            links = []
            for sid in part['source_ids'].split(';'):
                source = source_by_id[sid]
                links.append(f'[{sid}]({source["url"]})' if source['url'] else sid)
            if part['primary_url']:
                links.append(f'[Primärkälla]({part["primary_url"]})')
            lines.append('| ' + ' | '.join(cell(v) for v in [part['id'], name, f'{part["class"]} / {part["kind"]}', status, notes + ' ' + ', '.join(links)]) + ' |')
    lines += ['', '## Källor', '', '| ID | Underlag | Källversion och datum | Läsdatum |', '|---|---|---|---|']
    for source in sources:
        title = f'[{source["title"]}]({source["url"]})' if source['url'] else source['title']
        version = source['revision'][:12] or 'Ingen versionslåsning'
        if source['source_date']:
            version += '; ' + source['source_date']
        if source['notes']:
            title += '. ' + source['notes']
        lines.append('| ' + ' | '.join(cell(v) for v in [source['id'], title, version, source['read_on']]) + ' |')
    return '\n'.join(lines) + '\n', len(parts), len(bom_refs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check without writing')
    args = parser.parse_args()
    markdown, count, placements = render()
    target = ROOT / 'README.md'
    if args.check:
        if not target.exists() or target.read_text(encoding='utf-8') != markdown:
            parser.exit(1, 'README.md differs from the canonical CSV files; run render.py\n')
    else:
        target.write_text(markdown, encoding='utf-8')
    print(f'{count} records; {placements} distinct BOM placements; view matches CSV')
