# Sparade IQ-koder genom faktisk RTL: modellen stämmer, bilden är inte godkänd

Uppgift84 körde tre första, separata Icarus-fall på fryst Core `031bba053943ee04ce303ae75b5e701746169c97`, träd `83734acc12ba3c4708a002fef3fd85abd9279fc5`. Samma seed2/CN12/7bit-koder och modellfacit som uppgift81–83 återanvändes. Ingen IQ/demodulator/modell kördes om och inga produktionsvärden ändrades.

| Fall | Faktiskt kompilerad AVG/COMB/WHITE_X8/SW | Entries | Slutna rader | Driver, s |
|---|---|---:|---:|---:|
| gated_avg8 | 8/1/20/10 | 0 | 0 | 32.276 |
| gated_avg16 | 16/1/20/11 | 261363 | 723 | 35.455 |
| no_v_avg16 | 16/1/20/11 | 0 | 0 | 32.090 |

Alla råord och markörer är byteidentiska med respektive sparat modellresultat. Sex faktiska nativeanrop, tre kompileringar och tre VVP-körningar, avslutades med rc0. Varje körning fullföljde2669333sampel; inga signaler, timeout eller omkörningar. Icarus/VVP12.0stable, 40MHz-bänk, reset4/drain8, COMB1 och WHITE_X8=20. Den oförändrade bänkens readmemh-varning om att filen är kortare än minnesarrayen bevaras; explicit sampelantal och slutmarkören avgör fullföljandet.

## Vad detta fastställer

AVG8 ger inga bildord från just dessa PLL-koder. AVG16 ger723slutna strukturellt giltiga rader och360ord i en sista oavslutad rad. Oberoende avkodning av faktisk RTL-text och tidsstämplar ger samma källradstillhörighet som modellen:377av723slutna rader har fel etikett, med fördelningen −4:20, −3:70, −2:108, −1:179, 0:346.

Nativeordens tidsstämplar ligger4eller5bänksampel efter motsvarande modellord:129760respektive130880ord. Skillnaden är redovisad, inte bortanpassad. Källtidsmappningen använder originalets H-gränser utan skattad kompensation.

Pixelmåttet återanvänds från uppgift83 först efter exakt råbyteidentitet: **0av723giltiga rader klarar ursprunglig RMSE<16**. Ingen ny pixelgräns, offset-/gainpassning eller grön bildacceptans införs. [Startupfråga Core#34](https://github.com/LAP87/OpenVRX-Core/issues/34) och det stoppade designrådet kvarstår.

Det tredje fallet använder den redan skapade, hashbundna V-maskade indatan från83. Faktisk AVG16-RTL ger då0ord. Detta är en verklig semantisk indatakontroll. Den bevisar inte en viss intern V-arm-/countdownorsak i RTL: inga nya sådana interna signaler loggades.

## Granskning och gränser

En oberoende stdlib-läsare avkodade53-bitarsorden, markörer, compiledparams och källtider. Sex ägda rå-/parameter-/nod-/falsk bild-/bred native-/hårdvaruskador avvisades. Slutgranskningen läste samma kopior. Alla264Gitblob-/arkiv-/källbytes samt bundna runtime-, verktygs-, hjälpar-, indata- och facitbytes var oförändrade. Råinventeringen omfattar57filer/42091471byte; hash och storlek finns i [evidensen](IQ_NATIVE_FIDELITY_2026-11-07.json).

En inline-förberedelse skrev JSON-boolean som Pythonliteral och stannade före kontrakt/kvittoskrivning. Det efterföljande driveranropet hittade därför inget kontrakt och startade inget jobb. Diagnosen är bevarad; en separat korrigerad inline-förberedelse slutförde endast det ännu ej startade tredje fallet. Ingen kompilering eller simulering upprepades.

Endast dessa tre parameterfall är native-/modelljämförda. Detta accepterar ingen användbar brusbild, full mottagarkedja, aktuell main, helsvit, FPGA-route, fysisk HDMI/SDRAM eller hårdvara. Ingen Core-commit gjordes. [Exakta hjälpare och bänk](../research/experiments/iq_native_2026-11-07/).
