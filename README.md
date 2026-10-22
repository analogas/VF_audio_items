# Audio sandėlys — testinis prototipas

1. Išpakuok ZIP kompiuteryje.
2. GitHub projekte pagrindiniame aplanke įkelk main.py, requirements.txt, Dockerfile, render.yaml ir README.md. Nekelk ZIP ar išorinio aplanko.
3. Patvirtink įkėlimą (Commit changes) main šakoje.
4. Render: New > Blueprint > pasirink projektą. Blueprint Path: render.yaml.
5. Prieš patvirtindamas patikrink, kad abiejų paslaugų planas Free ir nerodoma mokėtina suma. Jei Free duomenų bazės neleidžia rinktis, sustok.
6. Kai paprašys APP_PASSWORD, įrašyk ilgą bendrą slaptažodį, ne savo GitHub slaptažodį.
7. Atidaryk sukurtos web paslaugos HTTPS nuorodą ir prisijunk.

Duomenys laikomi Postgres, ne konteineryje. Nemokama Render DB yra laikina; nekelk vienintelės realaus inventoriaus kopijos. Prieš termino pabaigą duomenis reikia eksportuoti arba perkelti.

Funkcijos: kategorijos, kiekiniai daiktai, dėžių turinys, šou išvykos, automobilio priskyrimas, bendra apžvalga. Kiekių pakeitimai apsaugoti DB transakcija ir eilutės užraktu. Grįžus dėžės priskyrimą rankiniu būdu pakeisk į Sandėlyje. Tai ne grąžinimo patikra.

Apribojimai: bendras slaptažodis; nėra asmeninių vartotojų, istorijos, QR, redagavimo/trynimo, automatinių backupų ar fizinio pakrovimo patvirtinimo. Duomenys kituose telefonuose atsinaujina perkrovus puslapį. Ši versija neturi offline režimo. HTTPS būtinas prisijungimo slapukui.

Patikra: atlikta Python sintaksės ir archyvo turinio patikra; visas serveris su Postgres ir Render šiame pokalbyje nepaleistas. Pirmiausia bandyk su bandomaisiais duomenimis.
