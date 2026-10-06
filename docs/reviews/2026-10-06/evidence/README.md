# Verifieringsunderlag 2026-10-06

Loggar och JSON från granskningen. Maskinnamn och absoluta arbetsytssökvägar är ersatta med `<workspace>`; commit-id, verktygsversioner, testutfall och SHA-256 är bevarade. Avslutande blanksteg i loggrader är borttagna; råloggarna finns kvar i den privata arbetsmappen.

- `snapshot.json`: versioner vid granskningsstart; senare main-commits anges i rapporten.
- `core_full.log`: 280 gröna och fyra långa-sökvägsfel i Fables bas. `path_fix_tests.log`: fem riktade tester efter rättningen.
- `build_artifact_tests.log`: 24 nya kontroller plus befintlig pull-kontroll. `main_collect.log`: 308 insamlade.
- `main_build_results.json` och två `.build.json`: två riktiga byggen från ren Core `6a61a17`. Manifestens artefakter hör till Core `gateware/build/`; enbart manifestkopian räcker inte för att verifiera bitströmmen.
- `noise_targeted.log`, `i2c_targeted.log`, `formal_targeted.log`: de separata nattgrenarnas riktade tester.
- `puck_main_result.json` och `puck_main_tests.log`: nytt Core-gitlänk-kontrakt och isolerad 114-delars export. `puck_tests.log` är den tidigare körningen mot Fables Puck-snapshot.
- `repro_results.json`: körning av den portabla runnern mot `e5585ba`, inklusive morgonversionens radkontroll och standardlägets saknade första rad. Exit 0 betyder reproducerade observationer, inklusive fel.
- `missing_first_line_summary.json`: den tidigare oberoende FB-körningens okända bildord; inga hårdvarumätningar.

Nya körningar sparas under ignorerad `repro/build/`. Rapporten skiljer full svit, riktad kontroll, byggen och fortfarande öppna RTL-fel.
