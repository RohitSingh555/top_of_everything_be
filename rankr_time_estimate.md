# ⏱️ Rankr — Build Time Estimate (With AI Assistance)

> **Goal:** Full social ranking platform with insane modern UI
> **Stack:** Next.js + FastAPI + PostgreSQL + Redis
> **Mode:** AI-assisted, ~6–8 hrs/day

---

## Phase-by-Phase Breakdown

| Phase | What | Time |
|-------|------|------|
| **0** | Scaffold + design system + mockups | 2–3 days |
| **1** | Auth + users + entities backend | 2–3 days |
| **2** | Rankings engine (full CRUD) | 2–3 days |
| **3** | Public frontend (ranking page, profile, auth UI) | 3–4 days |
| **4** | Social layer (feed, follow, notifications) | 3–4 days |
| **5** | Game modes (blind ranking + battles) | 3–4 days |
| **6** | Discovery + community rankings + search | 2–3 days |
| **7** | Polish, SEO, moderation, animations | 3–5 days |

### ✅ Total: ~3–4 weeks (working seriously, 6–8 hrs/day)

---

## ⚠️ Honest Caveats

### Things that will eat time

- 🎨 **"Insane modern UI"** is actually the biggest time sink
  - Framer Motion animations
  - Getting glassmorphism right
  - Mobile responsiveness
  - Micro-interactions
  - Budget **~40% of total time** just on this

- 🖱️ **Drag and drop** (ranking editor) is always finicky
  - Expect a full day just on getting it to feel right

- 🔐 **Auth edge cases** always take longer than expected
  - Refresh tokens, protected routes, race conditions

- 🃏 **Blind Ranking UI** (split-panel placement interaction)
  - Complex to build and even harder to make feel good

### Things that go faster than expected

- ✅ Backend CRUD with FastAPI + SQLAlchemy is very boilerplate
- ✅ Feed and social layer are straightforward once DB is set up
- ✅ SEO with Next.js App Router is almost automatic

---

## 📅 Realistic Milestones

```
Week 1 → Working auth + create/view a ranking (ugly but functional)
Week 2 → Beautiful profile + ranking pages + feed
Week 3 → Blind ranking + battles + compare working
Week 4 → Polish, animations, SEO, moderation → Launch-ready
```

---

## 🚨 The Real Bottleneck

The backend is not the hard part.

> Making the **ranking editor** feel smooth, the **blind ranking** feel like a game, and the **feed** look premium — that's where **50% of the real work** is.

### The 3 UI moments that define the product:

1. **Drag items in the ranking editor** — must feel silky, responsive, satisfying
2. **Finishing a blind ranking** — the dramatic reveal of your final list
3. **A vs B battle choice** — the winning card must feel punchy and alive

If these 3 interactions feel great, the whole product feels great.

---

## 🚀 Fastest Path to Start

Run these two prompts **today in parallel**:

- **Prompt 0.1** — Frontend scaffold (Next.js + design system)
- **Prompt 0.2** — Backend scaffold (FastAPI + Docker + PostgreSQL)

Once the design system is locked in Phase 0, every subsequent UI phase moves 2x faster.

---

> See `implementation_plan.md` for the full phase-by-phase build prompts.
