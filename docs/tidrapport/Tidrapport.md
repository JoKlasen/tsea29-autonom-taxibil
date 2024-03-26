Denna fil är skriven med [MarkDown](https://www.markdownguide.org/basic-syntax/)

Uppdatera tidrapporten **senast** kl 16 varje måndag, enligt [Leveranser](http://www.isy.liu.se/edu/kurs/TSEA29/leveranser/)  
Glöm inte att även uppdatera tidplanen.

# Tidrapport Grupp 13
Svara på följande frågor i tidrapporten varje vecka:
1. Vilka framsteg har gjorts sedan förra tidrapporten?
2. Finns det några problem?
3. Vad ska göras kommande vecka?

## Tidrapport t o m Vecka 43 (Oscar Sandell) (rapporteras måndag v44)
1. Fram till och med vecka 43 har alla dokument fixats till v 1.0, detta inkluderar, kravspecifikationen, systemskiss, designspecifikationen, projektplan och tidplan.

2. Just nu finns det inga problem i och med att det praktiska arbetet påbörjas under v44.

3. Den kommande vecka ska materialet hämtas ut samt att arbetet ska påbörjas enligt tidplanen. Det jobb som ska göras denna vecka är följande; Koppla ihop virkort, 
programmera rutin för att skicka pulser till fartreglage, programmera rutin för att skicka pulser till styrservo, programmera ultraljudssensorn så att
man kan avgöra avstånd till eventuella hinder, samla data från kameran så att det finns en bild att bildbehandla, påbörja bildhantering av datan från kameran, designa layout av för den externa applikationen, programmera layout för den externa applikationen och programmera manuella knappar för manuell styrning på den externa enheten.

## Tidrapport för v44 (Hannes Nörager) (rapporteras måndag v45)
1. Under vecka 44 installerades OpenCV på Rapberry Pi och den tillhörande kameran kalibrerades. Webapplikationen samt kommunikation därifrån till Raspberry Pi utvecklades och är i stort sett färdig. Styrmodul och sensormodul har virats, hallsensorer har simulerats m.h.a knappar med gott resultat

2. Några problem har varit att installera OpenCV, vilket visade sig vara svårt för vår Raspberry Pi att kompilera. En del felsökning av fick göras i början då pinouten för JTAGen inte överensstämde med det om stod beskrivet på kontakten utan fanns på separat plats på Vanheden.

3. Den kommande veckan kommer en mindre bana byggas för att testa kameran samt börja tolka bilder. Interface för att prata med AVR-processorerna från Raspberry Pi kommer påbörjas. Vi kommer även implementera ultraljudssensorn, samt utveckla/testa manuella styrkommandon från styrmodulen.

## Tidrapport för v45 (Linus Thorsell) (rapporteras måndag v46)
1. Hallsensor/Ultraljud fungerar, Parser av kommandon fungerar, påbörjat grafritning och traversering, testat lite. Sensormodulen typ färdig, styrmodulen parsern färdig, kan skicka o skriva uart med kommunikationsmodulen. Edgedetection/bildhantering har haft stora framsteg, Grundläggande edgedetection färdig, mycket kalibrering kvar. Kommunikation med controlmodulen, och manuell styrning integrerad och fungerar.

2. Watchdog, med klockor var knasigt. Vår AVR var ur funktion(resettade fel), så vi bytte AVR. Fel stringcmp funktion i parsern gjorde så det inte fungerade. Bilen körde iväg med fullspeed när de brusade, fixades med ny AVR. Bråkade med trigger funktionen till ultraljudfunktionen.

3. Försöka göra klart pathfinding. Skriva watchdog för bilen så den inte springer iväg vid radioförlust. Utöka parsingen, och dess följdfunktioner, utveckla styrmodulen lite. Fortsätta med openCV försöka få vinkelfelet. Skicka vidare information mellan control och sensor moduler.

## Tidrapport för v46 (Oscar Sandell) (rapporteras måndag v47)
1. Vi jobbade vidare på parsern (utökade kommandona) för komunikationsmodulen så att vi kan ta emot data och översätta det till kommandon.

2. Pathfindingen är klar, den ger en lista med noder som den ska till för att komma i mål, den ger även en färdbeskrivning. Den säger vilken riktning relativt till bilen som den ska köra (FORWARD,LEFT,RIGHT)

3. Vi va i arenan under fredagen och tog samplebilder så att opencvboysen kan få ut vettig data så att vi kan börja testa enkel autonom körning v 47

4. Vi har också börjat skissa på en ny virning så att vi kan gå ner till ett virkort istället för att vi ska ha två olika virkort (det blir ju lite bökigt)

5. Vi jobbade på att utöka edgedetection i opencv.

Vecka 47 ska vi göra systemtester och börja testa autonom körning, även fila lite på kontrol och sensormodulen. Även kanske vira om komponenterna på ett enda virkort

## Tidrapport för v47 (Johan Klasén)

1. Virkorten har virats om så att båda avr-modulerna sitter på ett gemensamt kort. Vi har även kommit så pass långt med bilen att den kan köra i autonomt läge för att följa kantlinjer på banan. Bildhantering är dock så pass långsamt så att det inte hinner skicka nya fel i tillräcklig takt för att undvika att bilen kör av banan. Kollisionsdektektionen har även påbörjats och har fungerande basfunktion.

2. I princip hela gruppen har under veckan varit sjuka i olika omgångar och det har tyvärr fallit bort ganska mycket tid på grund av det. Det har även varit lite problem med planneringen av arbetsuppgifter. Projektet har kännts väntande på den autonoma körningen men den borde kanske ha delats upp i mindre delar vid ett tidigare stadie för att kunna fördela arbetsbelastningen bättre. Vi har även insett att projektplanen och dess aktiviteter inte är tillräcklig detaljerade. 

3. Under den kommade veckan ska hela gruppen tillsammans gå igenom bildhanteringen för att alla gruppmedlemmar ska bli insatta i dess uppbyggnad och arbetet ska kunna delas upp. Plannering ska uppdateras med tydligare aktiviteter så att alla gruppmedlemmar vet vad dom ska göra framöver. Mindre städning av kod.


## Tidrapport för v48 (Hannes Nörager)
1. Delar av gruppen har fortsatt varit sjuk. Trots detta har kameraoptimering påbörjats med undersökning av multiprocessing och nedskalning av beräkningarna för linjeigenkänning, samt uppdatering av hastighets- och ultraljudsinformation ifrån sensormodulen. Skrivande av användarhandledning och teknisk dokumentation har inletts.

2. Sjukdom och uppdelandet av uppgifter har varit komplicerat att hantera, men löst på ett bra sätt.

3. Den kommande veckan kommer bestå av mycket testning, optimering och felsökning samt skrivande av dokumentation.

### Statusrapport:
1. Vilken funktionalitet har roboten idag?

Manuell körning, videofeed, pathfinding logik, sensor telemetri, långsam autonom körning

2. Vilken funktionalitet återstår?

Avancerad autonom körning, finjusteringar och optimeringar

3. Hur mycket tid har ni kvar av budgeterade timmar?

404/960 timmar kvarvarande.

4. Hur många timmar har respektive projektmedlem kvar att leverera (för att nå målet på 160 timmar) och hur ska dessa timmar fördelas över de kvarvarande veckorna? Redovisa i en tabell i statusrapporten hur många timmar detta blir per person och vecka. Redovisa också vilka aktiviteter som respektive person ska arbeta med.

Linus: 51,5 (20, 20, 11.5) Dokumentation, Rutt-input i appen, PID-Tuning, optimera server & app för snabbare kommunikation.

Oscar: 63 (25,20,18) Dokumentation, optimeringsarbete, integrering av pathfinding + testningen av det, optimering av AVR för snabbare kommunikation

Hannes: 74 (32,32,10) Dokumentation, kameraoptimering

Johan: 78 (30, 30, 18) Dokumentation, allmänt optimeringsarbete

Zackarias: 74 (26, 32, 16) Dokumentation, optimering av datorseende

Thomas: 63(23,23,17) Dokumentation, optimering av opencv, integerering och testning av kör logik opencv.

5. Är arbetsbelastningen jämn i gruppen? Om ej, ange orsak och vilken åtgärd ni vidtar.

Arbetsbelastningen är förskjuten då bildbehandlingen varit svår att utveckla och arbetet har varit ganska pipelinat. Vi åtgärdar detta genom att fördela kvarvarande uppgifter därefter.

6. Beskriv eventuella tekniska problem.

Kameran tar bilder för långsamt och därför kan ej PID-loopen få sitt felvärde tillräckligt ofta för att korrigera körriktningen.

7. Beskriv eventuella samarbetsproblem.

Svårt att arbeta effektivt när allt är beroende av roboten och dess system samt ev. skillnader i schema mellan olika delar av gruppen.


## Tidrapport för v49 (Oscar Sandell)

Vilka framsteg har gjorts sedan förra tidrapporten?

1. Förra veckan gjorde vi en massa framsteg, vi testade bilen i Arenan där vi kom fram till att pathfindingen och openCV koden verkade funkade helt okej. Vi tunade parametrarna när bilen ska svänga och vi ändrade även kamerastativ (tog en som va längre). Vi bytte även så att vi fick bilderna ifrån en ström istället för att vi tog en ny bild varje gång vilket ökar fpsen i bildtagningen + bildbehandlingen.

Finns det några problem?

2. Vi har fortfarande lite problem med att bilderna som vi använder är lite utdaterade och skulle behöva se till att vi får bilder som är up-to-date. Vi har även haft en hel del problem med att när vi väl ska testa bilen i Arenan så har vår kod inte varit i den senaste versionen så vi har behövt sitta och merga in all kod till den senaste versionen i onsdags och fredags innan vi kunde börja testa.

Vad ska göras kommande vecka?

3. Den kommande veckan ska vi se till att bilen får bilder som är fräscha och up-to-date, vi ska se till att vi har en pidloop för hastigheten och sen ska vi även bocka av så att vi uppfyller de krav som finns i kravspecifikationen

## Tidrapport för v50 och v51

Vilka framsteg har gjorts sedan förra tidrapporten?
Den tekniska dokumentationen och användarhandledning har färdigställts och levererats. Under veckan har produkten finjusterats och slutliga modifikationer gjorts. Produkten har presenterats för kund i enhetlighet med krav och beslut för BP5 och levererats till kunden. 
Presentation av projektarbetet har förberetts och genomförts för annan grupp och kund. En efterstudie av projektet har lämnats in.

Finns det några problem?
Nej, alla leveranser är klara och det inväntas bara ett slutgitltigt godkännande.

Vad ska göras kommande vecka?
-