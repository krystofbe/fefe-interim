# Requirements: fefe's blog — interim

**Defined:** 2026-02-26
**Core Value:** Die hochgevoteten Posts aus r/fefe_blog_interim als lesbaren, fefe-ähnlichen Blog darstellen — automatisch, kostenlos, zuverlässig.

## v1 Requirements

### Scraping

- [x] **SCRP-01**: Scraper holt Posts von r/fefe_blog_interim via Reddit JSON API (kein Auth)
- [x] **SCRP-02**: Wilson Score Interval filtert statistisch signifikant hochgevotete Posts
- [x] **SCRP-03**: Post-Daten werden extrahiert: Titel, Selftext/Body, Score, Kommentaranzahl, Erstelldatum, externe Links
- [x] **SCRP-04**: Scraper speichert Posts als JSON-Datei (Datenbasis für Generator)

### Site-Generierung

- [x] **SITE-01**: Jinja2-Template generiert Startseite mit gefilterten Posts (chronologisch)
- [x] **SITE-02**: Posts zeigen Datum, Tag (Security/Politik/Wirtschaft/Netz/Gesellschaft), Body-Text, Reddit-Link, Kommentaranzahl
- [x] **SITE-03**: Sidebar mit Status, Über-Sektion, Archiv-Links, Tag-Übersicht
- [x] **SITE-04**: Responsive Layout (Sidebar hidden auf Mobile)
- [x] **SITE-05**: Archiv-Seiten pro Monat mit allen Posts des Monats
- [x] **SITE-06**: Custom CSS aus Template (IBM Plex Mono + Newsreader, Amber-Theme)

### RSS

- [x] **RSS-01**: RSS/Atom Feed mit allen Blog-Posts (Titel, Beschreibung, Datum, Link)

### Deployment

- [ ] **DEPL-01**: Site wird auf GitHub Pages gehostet (statisch, kostenlos)
- [ ] **DEPL-02**: GitHub Actions Workflow mit Cron-Job scrapt + baut automatisch
- [x] **DEPL-03**: Lokaler `python build.py` Build zum Testen
- [x] **DEPL-04**: uv als Python Package Manager für alle Dependencies

### Testing

- [ ] **TEST-01**: Playwright MCP Browser-Tests verifizieren generierte Seite (manuell via Claude)

## v2 Requirements

### Erweiterte Features

- **FEAT-01**: Tag-basierte Filterung auf der Website (nur Posts mit bestimmtem Tag anzeigen)
- **FEAT-02**: Volltextsuche über Posts
- **FEAT-03**: Dark Mode Toggle
- **FEAT-04**: "Ältere Einträge laden" Pagination auf Startseite

## Out of Scope

| Feature | Reason |
|---------|--------|
| Tailwind CSS | Template hat bereits fertiges Custom CSS |
| Eigene Inhalte | Nur Reddit-Kuratierung, kein CMS |
| Kommentarsystem | Reddit ist die Diskussionsplattform |
| User-Accounts | Öffentliche, read-only Seite |
| OAuth/API-Keys | Reddit public JSON API reicht |
| Dynamischer Server | Rein statisch, keine Hosting-Kosten |
| Playwright Test-Files | Tests laufen manuell via Playwright MCP |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCRP-01 | Phase 2 | Complete |
| SCRP-02 | Phase 2 | Complete |
| SCRP-03 | Phase 2 | Complete |
| SCRP-04 | Phase 2 | Complete |
| SITE-01 | Phase 3 | Complete |
| SITE-02 | Phase 3 | Complete |
| SITE-03 | Phase 3 | Complete |
| SITE-04 | Phase 3 | Complete |
| SITE-05 | Phase 3 | Complete |
| SITE-06 | Phase 3 | Complete |
| RSS-01 | Phase 3 | Complete |
| DEPL-01 | Phase 4 | Pending |
| DEPL-02 | Phase 4 | Pending |
| DEPL-03 | Phase 1 | Complete |
| DEPL-04 | Phase 1 | Complete |
| TEST-01 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0

---
*Requirements defined: 2026-02-26*
*Last updated: 2026-02-26 after 03-03 completion (RSS-01 complete)*
