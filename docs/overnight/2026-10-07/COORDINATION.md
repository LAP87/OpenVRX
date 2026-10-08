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
| Codex/root, R03 | Granskade delar av `model/fuzz_stream.py`, `sim/test_fuzz_chain.py`, `sim/FUZZ_2026-10-07.md`; de två valda grencommitsen är ännu oincheckade. |
| Codex/root, R04 | Core `gateware/sim/test_mixer.py` för B-spegeltest. Modellen får en observationslista över fältstarter från ec06c56 för #18-diagnostik; utdataregler och RTL är oförändrade. M4/M6-verifiering och byggstatus. |
| Codex/root, samordning | Denna fil, plan, tasklistan, status/evidence, slutgranskning av navdokument, Git/commit/push och eventuell verifierad Puck-gitlänk. |

Vibes historiska rapport bevaras. Root rättar faktapåståenden i de
överlämnade dokumenten och antecknar rättelserna i körjournalen. Ingen
annan agent äger Core-filerna i den här arbetskopian. Fuzzkampanjen på en
annan värd hör till Opus; starta inte samma rundor igen.

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
