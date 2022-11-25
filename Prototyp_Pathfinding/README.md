# Dokumentation för Pathfinder

I filen Pathfinder.py finns det två klasser: Node och Graph. Pathfinderna är baserad på en bruteforce av DFS där vi räknar ut alla vägar som når till målet och tar den bästa av vägarna (den vägen som går igenom mitten är bäst om det finns två oliak vägar som har lika många noder). Anledningen till detta är för att jag ville ha en rekursiv funktion så att jag enkelt skulle kunna få med den tidigare noden, den nuvarande noden och den nästkommande noden. 

För att köra programmet så behöver man först skapa alla noder, i dehär fallet kör vi med två uppsättnigar av av alla noder på kartan. Dessa två noder representerar olika körriktningar t.ex "RA" == right direction A eller "LA" == Left direction A