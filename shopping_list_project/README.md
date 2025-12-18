# Shopping List Project
Dieses Projekt ist eine grafische Desktop-Anwendung zur Verwaltung von Einkaufslisten. Die Anwendung wurde in Python mit der Standardbibliothek tkinter für das GUI umgesetzt und folgt einer modularen Struktur.

---

## Voraussetzungen

* Python **3.9** oder neuer
* Keine externen Abhängigkeiten (nur Python-Standardbibliothek)

---

## Programmstart

Das Projekt ist als Python-Paket aufgebaut.

### Start über das Modul

Im Hauptverzeichnis des Projekts kann das Programm wie folgt gestartet werden:

```bash
python -m shopping_list.main
```

Alternativ kann (bei entsprechender Projektstruktur) auch direkt die Datei `main.py` ausgeführt werden:

```bash
python main.py
```

Nach dem Start öffnet sich ein grafisches Fenster mit einer leeren Einkaufsliste.

---

## Grundlegende Funktionsweise

Die Anwendung arbeitet mit **Tabs**, wobei jeder Tab eine eigenständige Einkaufsliste darstellt. Innerhalb eines Tabs können Artikel hinzugefügt, entfernt sowie importiert oder exportiert werden.

Ein Artikel besteht aus:

* einem Namen
* einer Menge (Stück oder Gewicht)
* einem Preis pro Einheit

Es wird zwischen zwei Artikeltypen unterschieden:

* **Stückartikel** (z. B. 2 Brote)
* **Gewichtsartikel** (z. B. 1,5 kg Äpfel)

Die Berechnung des Gesamtpreises erfolgt automatisch auf Basis der eingegebenen Daten.

---

## Funktionsumfang

### Verwaltung von Einkaufslisten

* Erstellen mehrerer Einkaufslisten über Tabs
* Umbenennen von Tabs
* Schließen einzelner Tabs

### Artikelverwaltung

* Hinzufügen neuer Artikel über ein Eingabefenster
* Unterstützung von Stück- und Gewichtsartikeln
* Validierung der Eingaben (z. B. numerische Werte, Menge > 0)
* Entfernen ausgewählter Artikel

### Import und Export

* Export einer Einkaufsliste in eine Textdatei (`.txt`)
* Import einer bestehenden Einkaufsliste aus einer Textdatei (`.txt`)
* Automatisches Zusammenführen identischer Artikel beim Import
* Auflösung von Namenskonflikten durch automatische Umbenennung

### Anzeige

* Übersichtliche tabellarische Darstellung der Artikel
* Ständige Anzeige des aktuellen Gesamtpreises pro Liste

---

## Dateiformat beim Export

Einkaufslisten werden in einem textbasierten, spaltenorientierten Format gespeichert:

```
Typ | Name                     |     Menge | Einzelpreis
C   | Brot                     |         2 |        1.49
W   | Äpfel                    |     1.500 |        2.99
# Gesamtpreis|8.97
```

* `C` steht für Stückartikel
* `W` steht für Gewichtsartikel
* Die letzte Zeile enthält den Gesamtpreis der Liste

---

## Interne Struktur

* **GUI (gui.py)**: Grafische Oberfläche und Benutzerinteraktion
* **Modelle (models.py)**: Datenklassen für Einkaufsartikel
* **Factory (factories.py)**: Zentrale Erzeugung von Artikelobjekten
* **Persistenz (persistence.py)**: Speichern und Laden von Einkaufslisten
* **main.py**: Einstiegspunkt der Anwendung

- `shopping_list/` enthält den Source Code (Paket)
- `tests/` enthält (optionale) Unit-Tests
