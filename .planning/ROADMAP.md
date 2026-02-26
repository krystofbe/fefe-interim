# Roadmap: fefe's blog — interim

## Overview

Ein Python-Scraper zieht Posts aus r/fefe_blog_interim, filtert die besten per Wilson Score, und ein Jinja2-Generator baut daraus statisches HTML im fefe-Stil. GitHub Actions deployt das Ergebnis automatisch auf GitHub Pages. Der Build-Stack wird von Grund auf aufgebaut: erst Scraper, dann Generator, dann Deployment-Automatisierung.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Project Foundation** - Projektstruktur, uv-Setup und lokaler Build-Einstiegspunkt (completed 2026-02-26)
- [x] **Phase 2: Reddit Scraper** - Daten holen, filtern und als JSON persistieren (completed 2026-02-26)
- [x] **Phase 3: Site Generator** - Statisches HTML + RSS aus Scraped-Daten generieren (completed 2026-02-26)
- [ ] **Phase 4: Deployment & Automation** - GitHub Pages Hosting und GitHub Actions Cron-Job

## Phase Details

### Phase 1: Project Foundation
**Goal**: Der Projektrahmen steht — Dependencies sind definiert, die Verzeichnisstruktur existiert, und `python build.py` kann aufgerufen werden (auch wenn es noch nichts tut).
**Depends on**: Nothing (first phase)
**Requirements**: DEPL-03, DEPL-04
**Success Criteria** (what must be TRUE):
  1. `uv sync` installiert alle Dependencies ohne Fehler
  2. `python build.py` läuft durch ohne Exception (auch wenn Output leer ist)
  3. Die Projektstruktur (scraper/, generator/, templates/, output/) ist vorhanden
**Plans:** 1/1 plans complete

Plans:
- [ ] 01-01-PLAN.md — Projektstruktur, pyproject.toml mit uv, build.py Skeleton

### Phase 2: Reddit Scraper
**Goal**: Der Scraper holt Posts von r/fefe_blog_interim, filtert statistisch signifikante Posts per Wilson Score und speichert die Ergebnisse als JSON-Datei.
**Depends on**: Phase 1
**Requirements**: SCRP-01, SCRP-02, SCRP-03, SCRP-04
**Success Criteria** (what must be TRUE):
  1. `python build.py` (oder `python scraper.py`) erzeugt eine `posts.json` mit mindestens einem Post
  2. Jeder Post in posts.json enthält: Titel, Body/Selftext, Score, Kommentaranzahl, Erstelldatum, externe Links
  3. Nur Posts mit statistisch signifikantem Wilson Score sind in der Ausgabe (nicht alle Posts roh)
  4. Der Scraper braucht keinen API-Key oder OAuth — läuft anonym
**Plans:** 2/2 plans complete

Plans:
- [x] 02-01-PLAN.md — Reddit JSON API Fetch und rohe Post-Extraktion
- [x] 02-02-PLAN.md — Wilson Score Filterung und JSON-Persistierung

### Phase 3: Site Generator
**Goal**: Aus posts.json generiert der Generator eine vollständige statische Website: Startseite, Monats-Archivseiten und RSS-Feed — alle im fefe-Stil mit Custom CSS.
**Depends on**: Phase 2
**Requirements**: SITE-01, SITE-02, SITE-03, SITE-04, SITE-05, SITE-06, RSS-01
**Success Criteria** (what must be TRUE):
  1. `python build.py` generiert `output/index.html` mit Posts (Datum, Tag, Body, Reddit-Link, Kommentaranzahl sichtbar)
  2. `output/index.html` zeigt Sidebar (Status, Über-Sektion, Archiv-Links, Tag-Übersicht) und ist responsive (Sidebar versteckt auf Mobile)
  3. Monats-Archivseiten existieren unter `output/YYYY/MM/index.html` mit allen Posts des jeweiligen Monats
  4. `output/feed.xml` ist ein valider RSS/Atom-Feed mit Titel, Beschreibung, Datum und Link pro Eintrag
  5. Das Custom CSS (IBM Plex Mono + Newsreader, Amber-Theme) ist eingebunden und visuell korrekt
**Plans:** 3/3 plans complete

Plans:
- [x] 03-01-PLAN.md — Jinja2 Templates + CSS + Index Page Generator (Wave 1)
- [x] 03-02-PLAN.md — Sidebar, Archive Pages + Responsive Layout (Wave 2)
- [x] 03-03-PLAN.md — RSS/Atom Feed Generator (Wave 2)

### Phase 4: Deployment & Automation
**Goal**: Die generierte Site ist öffentlich auf GitHub Pages erreichbar und wird automatisch täglich aktualisiert durch einen GitHub Actions Cron-Job.
**Depends on**: Phase 3
**Requirements**: DEPL-01, DEPL-02, TEST-01
**Success Criteria** (what must be TRUE):
  1. Die Site ist unter einer GitHub Pages URL öffentlich aufrufbar
  2. Ein GitHub Actions Workflow läuft automatisch (Cron-Schedule), scrapt Posts und pusht neue HTML-Dateien
  3. Playwright MCP Browser-Test bestätigt: Seite lädt, Posts sind sichtbar, Sidebar ist sichtbar, RSS-Link funktioniert
**Plans**: TBD

Plans:
- [ ] 04-01: GitHub Pages Konfiguration und initialer Deploy
- [ ] 04-02: GitHub Actions Workflow mit Cron-Job
- [ ] 04-03: Playwright MCP Verifikation der Live-Seite

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Foundation | 1/1 | Complete   | 2026-02-26 |
| 2. Reddit Scraper | 2/2 | Complete   | 2026-02-26 |
| 3. Site Generator | 3/3 | Complete   | 2026-02-26 |
| 4. Deployment & Automation | 0/3 | Not started | - |
