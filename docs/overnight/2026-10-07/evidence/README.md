# Evidence för nattpasset

Allt är simulering, källgranskning eller syntes/routning. Ingen hårdvara
är verifierad. Stora råloggar, bitströmmar och källarkiv ligger kvar på
utvecklingsvärden under `private/notes/overnight_2026-10-07/` eller Cores
ignorerade `gateware/sim/build/fuzz/`. Filerna här är publicerbara utdrag.

| Filer | Bevisvärde |
|---|---|
| `baseline.json`, `baseline-core-7cc4eda.log` | Fryst baslinje, 395 passed/1 xfailed, returstatus och tid. |
| `m4_dual_mix.build.json`, `m6_puck_proto.build.json`, `tmds-fuses.log` | Färska byggmanifest och HDMI-IOB-jämförelse; byggindata matchar 7cc4eda. |
| `campaign-contract-tests.log`, `integrated-light-gate.log` | 28 runnerkontroller; senaste integrerade modell/snabbgrind 249 passed. Ingen RTL i dessa små kontroller. |
| `density-default-parity.json`, `integrated-density-parity.json` | Sex frön med density 1; den senare jämför alla ursprungliga Scenario-fält och skiljer ut nya ahead-metadata. |
| `targeted-mixer-display.log`, `issue18.json` | Mixer och negativ displaykontroll, 29 passed/1 xfailed; exakt #18-vittne efter RTL/modell-agreement. |
| `r03-seed48.json`, `r03-seed126.json` | Bevarade experiment med 3ad2c2b, deras källkontrakt och senare granskningsbeslut. Seed 126:s gamla known-resultat är inte accepterat som grönt med strikt kontroll. |
| `campaign-and-visibility-tests.log` | Historiska små tester av den experimentella visningskopplingen; denna orakeländring avvisades senare. |
| `transition-probe-126.json`, `low-buf-review.json` | Observation-only-bänk, byte-identiska stimuli, 72 RGB-prov; 45 i BUF med video före publicering. OVN-F1. |
| `upstream-oracle-negative-controls.json` | Tre konkreta fall som upstream 0e0bf49 missade och de nya kontrollerna fångar. |
| `integrated-retained-log-review.json` | Sparade R03-loggar analyserade med integrerat orakel; inga nya RTL-körningar. Seed 48 grönt, seed 126 store/read. |
| `r06-pal-low-full.json`, `r06-pal.log`, `r06-pal-resume.log` | Riktig en-worker-kampanj/resume: fyra fulla PAL/LOW-bilder, 2880 rader, bara #17; resume körde noll nya frön. |
| `final-suite.json`, `final-suite.log` | Slutgrind från fryst aece6eb: 432 passed, 2 xfailed, returstatus 0; alla 171 källhashar oförändrade. |
| `final-integration.json`, `final-build-verification.log` | Pushad Core fb6896a, bara tre Markdown-ändringar från testad kod; M4/M6-manifest mot slutkoden. |
| `final-puck.json`, `final-puck.log` | Puck 8917d27 med core fb6896a; 1 kontraktstest med negativa kontroller passerar. |
| `final-checkpoint.json` | Navets rapportcommit, pushade Core/Puck-revisioner, R08 komplett och verifierad PAUSED-status före stopptid. |

R06:s äldre vsync-noteringar uttrycker perioder i nominella 1650-klockors-
rader; de är inte det faktiska radantalet för en PAL-bild med varierande
radlängd. Bildlängdsinvarianten använder bänkens räknade radstarter.

`WORKPLAN.md`, `tasks.json`, `STATUS.md` och `LOW_BUF_FINDING.md` anger
acceptance och återstående arbete. Resultat från Opus äldre kampanjrundor
kommer från deras egna orakelversioner; de är inte automatiskt verifiering
med Codex strikta kontroller.
