# Arbetsfördelning för natten 7–8 oktober

Uppdaterad 2026-10-08. Stopptid 08:00 Europe/Stockholm (06:00 UTC).
Användaren har bett Codex att ta över, kontrollera och checka in arbete på
`main`. Användarens Mistral Vibe CLI arbetar i en egen terminal.
**Codex ska inte starta, styra eller konfigurera Vibe.**

## Start och gränser

| Repo | `main` vid start | Anmärkning |
|---|---|---|
| OpenVRX | `4d43600` | Båda nattinstruktionerna lästa. |
| OpenVRX-Core | `7cc4eda` | Senaste pair-join-fixen ingår. |
| OpenVRX-Puck | `9d2fb57` | `core/` pekar på `82c4134`. |

Arbetskopiorna var rena före fast-forward. Verktygen finns på Linuxvärden;
WSL-kommandon i äldre instruktioner gäller en annan värd. Inget är
verifierat på hårdvara. Ingen reset, stash, clean eller force-push.

## Filägare

| Ägare | Filer och ansvar |
|---|---|
| Luna/max, avslutad med kreditfel | Sparade `WORKPLAN.md` och `tasks.json`; root har tagit över granskning och uppdatering. |
| Användarens Vibe, överlämnat utkast | Navets `REVIEW.md`, `AGENTS.md`, `VIBE_REPORT.md`. Rapporten beskriver avslutat dokumentationsarbete; root får granska och checka in. |
| Codex/root, R02 | Core `gateware/sim/fuzz_campaign.py`, nytt `test_fuzz_campaign.py`. Inga RTL-ändringar. |
| Codex/root, R03/R06 | `sim/test_fuzz_chain.py`, `sim/tb_chain.v`, `sim/FUZZ_2026-10-07.md` och granskade delar av `model/fuzz_stream.py`. Strikt checksum och täckning behålls; bänken räknar riktiga rader. Fjärrens `main` `0e0bf49` är integrerad lokalt till `aece6eb`; fullsviten körs fryst före push. |
| Codex/root, R04 | Core `gateware/sim/test_mixer.py` för B-spegeltest. Modellen får en observationslista över fältstarter från ec06c56 för #18-diagnostik; utdataregler och RTL är oförändrade. M4/M6-verifiering och byggstatus. |
| Codex/root, samordning | Denna fil, plan, tasklistan, status/evidence, slutgranskning av navdokument, Git/commit/push och eventuell verifierad Puck-gitlänk. |

Vibes historiska rapport bevaras. Root rättar faktapåståenden i de
överlämnade dokumenten och antecknar rättelserna i körjournalen. Ingen
annan agent äger Core-filerna i den här arbetskopian. Fuzzkampanjen på en
annan värd hör till Opus; starta inte samma rundor igen.

Opus har nu pushat kampanjens tester/logg till fjärrens main. Inga RTL-
eller byggindata har ändrats jämfört med 7cc4eda. Root behåller historiken
och granskar egna kontrolländringar ovanpå den nya basen. Fynd OVN-F1 och
rättelsen av antagandet om blank LOW→BUF-bild finns i `LOW_BUF_FINDING.md`.

Ett tungt test- eller byggjobb åt gången mellan repona, under
`flock /home/lenny/openvrx-review/build.lock <kommando>`. Ändra inga
bildlägen, stift, IOB-register, SDC, licens- eller BOM-beslut.

## Återupptagning

Läs `WORKPLAN.md`, `tasks.json`, `STATUS.md` och denna fil. Kontrollera
Git-status, levande arbetare och test-/byggprocesser innan nästa paket.
Ett agentbesked eller en avslutad process räcker inte som acceptance;
root granskar resultatet innan exakt ägda filer checkas in. Ingen ny Luna
startas automatiskt efter kreditfelet. Spara checkpoint och stoppa
fortsättningen vid 08:00, eller tidigare om verifierbara paket är klara.

## Checkpoint 06:03

PAL-processen och dess riktiga resume är klara. Fullsviten kör nu ensam
under låset från `private/notes/overnight_2026-10-07/final-core-aece6eb`.
Levande status/resultat finns i `evidence/final-suite.json`; låt processen
slutföras och starta ingen kopia. Core main har lokalt två granskade
commits, men har ännu inte pushats. Pucks core/ är rent på 82c4134 och
ska bara flyttas efter accepterad Core-grind och push. R08 anger nästa steg.

## Fjärrkontroll 07:00

Navet har fast-forwardats till `76a1121`, bara ändringar i Opus
`docs/ARBETSPLAN_2026-10-05.md`. Core-fjärren står på `059aadd`;
diffen från `0e0bf49` rör bara `sim/FUZZ_2026-10-07.md`. Den uppdaterar
kampanjtotalsiffror och bekräftar OVN-F1 samt den felaktiga kontrollen
3ad2c2b. Bevara dessa fyra fjärrcommits och rootens strikta kontroller
vid integration efter slutgrinden. Den frysta koden är fortfarande
`aece6eb`; ingen ny testkörning eller RTL-ändring har startats.

## Slutacceptance, 2026-10-08 07:43

Fullsviten är klar: 432 passed, 2 xfailed, returstatus 0, oförändrade
171 källhashar. Core `fb6896a` integrerar Opus slutlogg med bevarad historik
och är pushad. Puck `8917d27` är pushad med samma rena Core-gitlänk;
1 kontraktstest passerar. Ingen tung process eller bygglåshållare finns
kvar. Root äger slutrapporten och dess evidence; den pushas i avslutet.
Stoppa sedan automationen; starta inget nytt paket. #17/#18 och OVN-F1
ligger kvar för ägarbeslut enligt slutrapporten.
