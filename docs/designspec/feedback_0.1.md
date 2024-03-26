# Feedback designspec 0.1

## 3.3
- [X] Datorseende -  Vilken data kommer komma ut? Format?
    
    Vinkelfel/sidfel - Tomas och Zackarias utökar texten s.4

- [X] Gärna en schematisk bild vad man ser och vad som plockas ut.

## 4 Styr
- [X] Beskriv gärna PD-regleringen och loopen. Vad tar den för indata? 
- [X] Ytterligare reglerloop för hastighet.

- [x] Koppla fartreglare och styrservo till timerpins, lämpligtvis PD4/5 och PB3 (OC-pinnar).

## 5 Sensor
- [X] Ändra beskrivning så att halleffekt är via IRS istället för pollning.

- [X] **Rekomendation** Gör en Arduino-liknande milli()-funktion för att använda till real-tids omvandligar för hastighet/avstånd och liknande.

- [x] Rita om pins på kopplingsschemat så halleffektsensorerna går till PD2/3 och att ultraljudssensorns *Echo Output* går till PB2. 

## 6 Extern app
- [X] Förtydliga i text att webservern ligger på den externa datorn och ansluter via socket till RPI.

## 7 Kommunikation

- [X] Förtydliga att json-formatet är i strängformat i form av ASCII eller dylikt.

- [ ] **Rekomendation**: gör ett excelark och stapla upp all data och format som skickas.

## 8 Komponentlista

- [x] Ändra exo-3 från 20MHz till 16MHz
