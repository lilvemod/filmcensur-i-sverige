# filmcensur-i-sverige

## Beskrivning:
Programmet filmcensur.py låter användaren ta reda på information om en film som visades på bio i Sverige mellan 1911 och 2010 blev censurerad eller inte av Statens Biografbyrå.

Programmet använder sig av öppna data som tillgängliggjorts av Riksarkivet, här: https://sok.riksarkivet.se/data-api/nedladdningsbara-datamangder/svensk-filmcensur
Datan tillgängliggörs genom en CC0 licens och inkluderas i detta program. Filen klipp.csv har modifierats för detta program genom att den getts en kolumn med rubriker från postbeskrivningen.

Hur programmet funkar:
Programmet kan köras som det är, dvs. genom `python project.py` och användaren promptas då att skriva en titel i terminalen.

Programmet kan också köras genom att lägga till kommandoradsargumentet "-t" fäljt av filmens titel, som i exemplet `python project.py -t "askungen"` för att få information om filmen Askungen.

Programmet kan även köras genom kommandoradsargumentet "-" följt av ett heltal, som i `python project.py -r 1`. Genom att köra programmet på detta sätt så får du information om en film som väljs fram slumpmässigt från registret.

Om inga klipp gjordes för filmen du valt så skrivs en kort sammanfattning ut till terminalen och programmet avslutas.
Om det gjordes några klipp så får du välja om du vill spara ned sammanfattningen till en fil eller om det bara ska skrivas ut till terminalen.

## Externa bibliotek:
Programmet använder sig av några externa bibliotek som kan installeras med pip, dessa är:

#### pandas
För att installera, kör
`pip install pandas`

#### prettytable
För att installera, kör
`pip install prettytable`

#### pytest
För att installera, kör
`pip install pytest`
Obs! Behövs endast för att köra tester i test_filcensur.py

## Tester:
En testfil finns med som testar de olika funktionerna som finns i filmcensur.py. De flesta av testerna simulerar de DataFrame objekt som funktionerna ska returnera.

## Om programmet
Det här programmet skrevs ursprungligen som mitt slutprojekt för kursen CS50p, Introduction to Programming with Python under 2026.





