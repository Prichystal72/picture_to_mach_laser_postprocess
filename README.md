## Generátor kódu pro laser z obrázku

Tento program umožňuje převést bitmapový obrázek na G-code pro laser (Mach3), včetně pokročilých úprav a náhledu výsledku.

### Hlavní funkce

- **Načtení obrázku** (PNG, JPG, BMP)
- **Úprava jasu a kontrastu**
- **Filtry:**
	- Převod na odstíny šedi
	- Převod na černobílý (prahování)
	- Novinový efekt (dithering)
	- ASCII art
	- Invertování barev
- **Nastavení fontu a velikosti písma pro ASCII art**
- **Nastavení parametrů laseru:**
	- Velikost bodu laseru (mm)
	- Výsledná šířka obrázku (mm)
	- Počátek X, Y (mm)
	- Maximální výkon (S)
- **Nastavení rychlosti pohybu:**
	- Rychlost G1 (mm/min) – laserování
	- Rychlost G0 (mm/min) – rychlé přesuny
- **Přehledné oddělení sekcí v UI**
- **Náhled výsledného obrázku po všech úpravách a převzorkování**
- **Export do G-code pro Mach3:**
	- Hlavička s jednotkami, absolutním režimem, vypnutím laseru, návratem na počátek
	- Komentáře s autorem, datem a časem
	- Rychlost (F) nastavena pouze u prvního G1 a G0
	- Přehledný a čitelný kód

### Postup použití

1. Načtěte obrázek tlačítkem "Načíst obrázek".
2. Upravte jas, kontrast a použijte požadované filtry.
3. Nastavte parametry laseru a rozměry.
4. Nastavte rychlosti pohybu (G1 pro pálení, G0 pro přesuny).
5. Klikněte na "Export do Mach3" a uložte G-code.
6. Výsledek uvidíte v náhledu vpravo.

### Autor

Jaroslav Přichystal