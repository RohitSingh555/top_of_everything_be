# Completed Tasks & Phases Log

This file tracks all completed phases and tasks to prevent duplication of work. Always check this file before beginning a new phase.

### [DONE] Phase 0 — Design & Foundation
- **Summary**: Set up project scaffolding. Created `rankr-frontend` (Next.js 14) and `rankr-backend` (FastAPI). Built 5 static HTML mockups in `rankr-mockups` to validate the UI design.

### [DONE] Phase 1 — Backend Core (Auth + Users + Entities)
- **Summary**: Implemented database models and migrations. Created JWT authentication system (register, login, refresh). Implemented User Profiles, follow/unfollow logic, and Entity search with a seeding script.

### [DONE] Phase 2 — Rankings Engine
- **Summary**: Created Ranking, RankingItem, RankingVersion, Like, and Comment models. Built full CRUD API for rankings including reordering items, publishing, liking, and commenting.

### [DONE] Phase 3 — Public Experience
- **Summary**: Scaffolded public frontend pages (`app/[username]/page.tsx`, `app/[username]/[slug]/page.tsx`), integrated global API client (`api.ts`), Auth store (`authStore.ts`), and Login/Register components. Started local dev environment with Docker.
