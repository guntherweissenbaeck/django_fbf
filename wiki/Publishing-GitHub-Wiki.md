# Publishing GitHub Wiki

## Wie GitHub Wikis funktionieren
Ein GitHub Wiki ist ein separates Git Repository: `<REPO_NAME>.wiki.git`. Es liegt nicht als Ordner im Hauptrepository. Inhalte werden serverseitig gerendert. Dieses Projekt verwendet ein lokales `wiki/` Verzeichnis als Staging.

## Repository klonen
```bash
git clone https://github.com/<OWNER>/<REPO_NAME>.wiki.git wiki-publish
cd wiki-publish
```

## Inhalte übernehmen
Vom Projektwurzelverzeichnis aus:
```bash
# Annahme: im Projekt existiert Ordner wiki/
rsync -av --delete ../django_fbf/wiki/ ./
# Oder falls innerhalb schon
# rsync -av --delete ../wiki/ ./
```

Alternativ (ohne rsync):
```bash
cp -R ../django_fbf/wiki/* .
```

## Startseite setzen
Die Datei `Home.md` wird automatisch als Startseite genutzt. Interne Verlinkungen im Format `[[Seitentitel]]` sollten Seitennamen exakt matchen.

## Änderungen committen & pushen
```bash
git add .
git commit -m "Publish aktualisierte Wiki-Inhalte"
git push origin main  # oder 'master' je nach Default
```

## Aktualisierungshäufigkeit
Empfohlen: Bei funktionalen Änderungen an Architektur, Datenmodell oder Deployment unmittelbar Wiki anpassen (Definition-of-Done Kriterium).

## Typische Stolpersteine
- Falscher Branch: Wiki Repos haben meist einen Default Branch (main/master). Andere Branches werden ignoriert.
- Dateinamen Groß/Kleinschreibung: GitHub behandelt Links case-sensitive.
- Sonderzeichen / Umlaute: Möglich, aber Leerzeichen durch `-` oder weglassen (Lesbarkeit / Linksicherheit).

## Optional: Automatisierung
- GitHub Action: Bei Merge in `main` -> Sync `wiki/` in Wiki Repo (mittels PAT mit Repo Wikirechten)
- Pre-Commit Check: Prüft geänderte Dateien im `wiki/` Ordner auf Broken Links

## Linkprüfung lokal (einfach)
```bash
grep -R "[[" wiki/
```
Manuell sicherstellen, dass alle referenzierten Dateien existieren.

Weiter: [[Home]]
