# fefe's blog — interim

## What This Is

Ein statischer Interim-Blog, der Community-Posts aus r/fefe_blog_interim kuratiert und als hübsche, fefe-inspirierte Website auf GitHub Pages bereitstellt. Solange fefe nicht selbst bloggt, sammelt ein Python-Scraper die besten Reddit-Posts und generiert daraus statisches HTML im Look des originalen fefe-Blogs.

## Core Value

Die hochgevoteten Posts aus r/fefe_blog_interim als lesbaren, fefe-ähnlichen Blog darstellen — automatisch, kostenlos, zuverlässig.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Reddit-Scraper holt Posts von r/fefe_blog_interim via JSON API (kein Auth nötig)
- [ ] Statistische Methode filtert "heiße" Posts (z.B. Wilson Score Interval relativ zum Subreddit-Durchschnitt)
- [ ] Statische HTML-Generierung via Jinja2 im Stil des vorhandenen Templates
- [ ] Custom CSS aus dem Template (IBM Plex Mono + Newsreader, Amber-Theme, Sidebar, Tags, responsive)
- [ ] RSS-Feed für Blog-Einträge
- [ ] GitHub Pages Deployment (kostenlos)
- [ ] GitHub Actions Cron-Job für automatisches Update
- [ ] Playwright-Tests über MCP für die generierte Seite

### Out of Scope

- Tailwind CSS — Template hat bereits fertiges Custom CSS
- Dynamischer Server/Backend — rein statisch, kein Hosting-Kosten
- Kommentarsystem — Reddit ist die Diskussionsplattform
- User-Accounts — öffentliche, read-only Seite
- Eigene Inhalte schreiben — nur Reddit-Kuratierung

## Context

- **Quelle:** https://www.reddit.com/r/fefe_blog_interim/ — Community-Subreddit als Ersatz während fefes Pause
- **Design-Template:** `fefe_interim.html` im Repo-Root (Cocoa HTML Export, extrahiertes Template unter `/tmp/fefe_template.html`)
- **Template-Features:** Sticky Header mit blinking cursor, Notice Bar, Posts mit Tags (Security/Politik/Wirtschaft/Netz/Gesellschaft), Sidebar mit Status/Archiv/Tags, responsive (Sidebar hidden auf Mobile), fadeIn-Animationen
- **Reddit JSON API:** Öffentliche Subreddits liefern JSON wenn man `.json` an die URL hängt — kein API-Key nötig
- **Boring Stack:** Python, Jinja2, requests/httpx, uv für Dependencies
- **Ziel:** Prototyp, schnell live, kostenlos

## Constraints

- **Hosting:** GitHub Pages only — muss statisch sein, keine Server-Kosten
- **Budget:** 0 EUR — alle Tools/APIs müssen kostenlos sein
- **Dependencies:** Python-basiert, uv als Package Manager
- **API:** Reddit public JSON API (kein OAuth, kein API Key)
- **Testing:** Playwright MCP Browser-Tools

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Custom CSS statt Tailwind | Template ist bereits fertig und schön | — Pending |
| Reddit JSON API statt PRAW/OAuth | Öffentliche Daten, kein Auth nötig, boring tech | — Pending |
| Static Site Generator (eigener) statt Hugo/Jekyll | Maximale Kontrolle, minimale Komplexität, Python-only | — Pending |
| Wilson Score für Hot-Post-Filterung | Statistisch robust, berücksichtigt Stichprobengröße | — Pending |
| GitHub Actions Cron für Updates | Kostenlos, automatisch, kein Server nötig | — Pending |

---
*Last updated: 2026-02-26 after initialization*
