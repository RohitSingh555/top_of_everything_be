# Social Ranking Platform — Full Implementation Plan

> **"Rank anything. Discover everyone's taste."**
> 
> A social platform where users build a public profile around ranked opinions, discover people with similar/different taste, and engage through battles, blind rankings, and comparison.

---

## Architecture Overview

```
                    Next.js (App Router, TypeScript)
                           │
                           ▼
                    FastAPI REST API
                           │
          ┌────────────────┼──────────────────┐
          ▼                ▼                  ▼
      PostgreSQL          Redis         S3-Compatible
      (primary DB)     (cache/queue)   (media storage)
          │
          ▼
   Background Workers (ARQ/Celery)
          ├── Community ranking calculation
          ├── Notification dispatch
          ├── Search indexing
          └── Moderation queue
```

**Stack:**
- **Frontend:** Next.js 14+ (App Router), TypeScript, Tailwind CSS, shadcn/ui, Framer Motion
- **Backend:** FastAPI, SQLAlchemy 2.x, Alembic (migrations), Pydantic v2
- **Database:** PostgreSQL 16
- **Cache:** Redis 7
- **Auth:** JWT (access + refresh tokens) or Auth0/Clerk
- **Storage:** Cloudflare R2 / AWS S3
- **Search:** PostgreSQL FTS (Phase 1), Typesense (Phase 4+)
- **Infra:** Docker Compose (dev), Railway/Render/Fly.io (prod), Cloudflare CDN

---

## URL Structure

```
/                          → Home feed
/explore                   → Discovery
/[username]               → User profile
/[username]/[ranking-slug] → Individual ranking page
/r/[topic]                → Topic page (e.g. /r/movies)
/battle/[id]              → Live battle session
/blind/[id]               → Blind ranking session
/compare/[user1]/[user2]  → Side-by-side comparison
```

---

## Core Data Models

### User & Profile
```
User: id, email, username, password_hash, is_verified, created_at
Profile: user_id, display_name, avatar_url, bio, website, follower_count, following_count, ranking_count
```

### Entities (searchable items)
```
Entity: id, name, type (movie/game/book/person/place/product/other), aliases[], image_url, metadata(JSON), external_ids(JSON), created_at
```

### Rankings
```
Ranking: id, slug, user_id, title, description, type (standard/blind/battle/community), category, size (3-100), visibility (public/unlisted/followers/private), status (draft/published), created_at, updated_at, published_at, view_count, like_count

RankingItem: id, ranking_id, entity_id, position, note, created_at, updated_at

RankingVersion: id, ranking_id, snapshot(JSON), created_at, change_summary

RankingView: id, ranking_id, viewer_id (nullable), ip_hash, viewed_at
```

### Social
```
Follow: follower_id, following_id, created_at
Like: user_id, ranking_id, created_at
Comment: id, ranking_id, user_id, content, parent_id (for threads), created_at

Challenge: id, challenger_id, target_ranking_id, challenger_ranking_id, status, created_at
```

### Games
```
Battle: id, ranking_id (optional), user_id, items[], comparisons[], result_ranking_id, status, created_at
BlindRanking: id, ranking_id (optional), user_id, items[], decisions[], result_ranking_id, status, created_at
```

### Moderation
```
Report: id, reporter_id, target_type (ranking/comment/user), target_id, reason, status, created_at
Block: blocker_id, blocked_id, created_at
```

---

## Phase Breakdown

---

# [DONE] Phase 0 — Design & Foundation
**Goal:** Design system, screens, and project scaffolding. No database yet.

---

# [DONE] Phase 1 — Backend Core (Auth + Users + Entities)
**Goal:** Working API for auth, user profiles, and entity search.

---

# [DONE] Phase 2 — Rankings Engine
**Goal:** Full CRUD for rankings and ranking items.

---

# [DONE] Phase 3 — Public Experience
**Goal:** Profile pages, public ranking pages, shareable URLs, basic search.

---

# Phase 4 — Social Layer
**Goal:** Follow, like, comment, challenge, feed.

---

# Phase 5 — Game Modes
**Goal:** Blind ranking and ranking battles.

---

# Phase 6 — Discovery & Community
**Goal:** Trending, topic pages, community rankings, compare.

---

# Phase 7 — Polish & Launch
**Goal:** SEO, notifications, moderation, analytics, performance.

---

## Detailed Phase Prompts

---

## PHASE 0 — Design & Foundation

### Prompt 0.1 — Project Scaffold (Frontend)

```
Create a new Next.js 14 project with App Router and TypeScript inside the directory ./rankr-frontend.

Run: npx -y create-next-app@latest ./rankr-frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*" --no-eslint

After scaffolding:
1. Install dependencies:
   - framer-motion
   - @radix-ui/react-dialog
   - @radix-ui/react-dropdown-menu
   - @radix-ui/react-avatar
   - @radix-ui/react-tooltip
   - @radix-ui/react-tabs
   - class-variance-authority
   - clsx
   - tailwind-merge
   - lucide-react
   - @tanstack/react-query
   - axios
   - zustand
   - next-themes

2. Set up globals.css with a dark-mode-first design system using CSS variables for:
   - Background colors (deep navy/charcoal dark theme)
   - Primary color (vibrant purple/violet accent)
   - Text colors
   - Border colors
   - Card colors
   
3. Create lib/utils.ts with cn() helper using clsx + tailwind-merge.

4. Configure next.config.js to allow external image domains.

5. Create the base layout app/layout.tsx with:
   - Dark theme default via next-themes
   - Inter font from Google Fonts
   - QueryClientProvider wrapper
   - A global Navbar component (placeholder for now)

Design direction: Premium dark social app. Think Linear meets Letterboxd. Use deep slate/charcoal backgrounds (#0f1117), violet/purple accents (#7c3aed), clean white typography. Cards with subtle glass morphism borders.
```

---

### Prompt 0.2 — Project Scaffold (Backend)

```
Create a FastAPI backend project in ./rankr-backend with the following structure:

rankr-backend/
  app/
    __init__.py
    main.py
    config.py
    database.py
    auth/
      __init__.py
      router.py
      service.py
      schemas.py
      utils.py
    users/
      __init__.py
      router.py
      service.py
      repository.py
      schemas.py
      models.py
    profiles/
      __init__.py
      router.py
      service.py
      repository.py
      schemas.py
      models.py
    rankings/
      (empty, created in Phase 2)
    entities/
      (empty, created in Phase 1)
    social/
      (empty, created in Phase 4)
    common/
      __init__.py
      exceptions.py
      pagination.py
      dependencies.py
  alembic/
    (standard alembic structure)
  tests/
    conftest.py
  requirements.txt
  .env.example
  docker-compose.yml
  Dockerfile

requirements.txt must include:
fastapi==0.111.0
uvicorn[standard]==0.30.1
sqlalchemy==2.0.30
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.7.1
pydantic-settings==2.3.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
redis==5.0.4
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.7

docker-compose.yml must define:
- postgres:16 service (port 5432, POSTGRES_DB=rankr, POSTGRES_USER=rankr, POSTGRES_PASSWORD=rankr)
- redis:7 service (port 6379)
- api service pointing to ./rankr-backend (port 8000)

config.py must use pydantic-settings with:
DATABASE_URL, REDIS_URL, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ENVIRONMENT, ALLOWED_ORIGINS

main.py must:
- Create FastAPI app with title "Rankr API"
- Mount CORS middleware (origins from config)
- Include routers from each module
- Add /health endpoint returning {"status": "ok"}

database.py must:
- Create async SQLAlchemy engine
- Provide get_db dependency
- Create Base declarative base
```

---

### Prompt 0.3 — Design System Screens (Static HTML Mockups)

```
Create 5 static HTML mockup files (no framework, just HTML + CSS + vanilla JS) in ./rankr-mockups/ to validate the design before coding components:

1. home.html — Home feed
   - Top: "What are you ranking today?" search bar, [Blind Rank] [Battle] buttons
   - Trending section: Cards showing top-ranked items from trending rankings
   - Feed section: Cards of rankings by followed users
   - Feed card shows: avatar, username, ranking title, top 3-5 items, like/comment/share counts

2. create.html — Ranking creation flow
   - Step 1: Single large input "What do you want to rank?" with example hints
   - Step 2: Items editor — left panel (available/suggested items), right panel (ranked list 1-N)
   - Drag handles on ranked items
   - Search field to find entities
   - Save Draft / Publish buttons

3. ranking.html — Individual ranking page
   - Header: title, creator avatar, created date, like/share/comment count
   - Ranked items displayed as large cards: position number, entity image, name, optional "Why?" note
   - Comment section at bottom

4. profile.html — User profile page
   - Cover area: avatar, username, bio, follower/following/rankings counts, Follow button
   - Rankings grid: cards organized by category
   - Taste bars visualization (movies, gaming, tech, etc.)

5. blind.html — Blind ranking flow
   - Full-screen card showing one item
   - "Where does this rank?" prompt
   - Position selector (large clickable number grid 1-N)
   - Progress indicator: "Item 4 of 10"
   - Cannot go back UI

Design system: Deep charcoal dark (#0f1117), violet accent (#7c3aed), card backgrounds (#1a1d2e), subtle borders (rgba(255,255,255,0.08)), Inter font. Use Framer Motion style smooth transitions conceptually. Make it feel premium — large typography, generous spacing, beautiful ranking position indicators.
```

---

## PHASE 1 — Backend Core

### Prompt 1.1 — Database Models & Migrations

```
In the rankr-backend FastAPI project, implement SQLAlchemy models and Alembic migrations for the core tables.

Create these SQLAlchemy models:

--- app/users/models.py ---
class User(Base):
    __tablename__ = "users"
    id: UUID (primary key, default uuid4)
    email: str (unique, not null)
    username: str (unique, not null, max 30 chars)
    password_hash: str (nullable — for OAuth users)
    is_verified: bool (default False)
    is_active: bool (default True)
    created_at: datetime (server_default=now)
    updated_at: datetime (onupdate=now)
    
    relationship → Profile (one-to-one)
    relationship → Rankings (one-to-many)
    relationship → Followers (via Follow)

class Profile(Base):
    __tablename__ = "profiles"
    id: UUID
    user_id: UUID (FK users.id, unique)
    display_name: str (nullable)
    avatar_url: str (nullable)
    bio: str (nullable, max 500)
    website: str (nullable)
    follower_count: int (default 0)
    following_count: int (default 0)
    ranking_count: int (default 0)
    created_at, updated_at

class Follow(Base):
    __tablename__ = "follows"
    follower_id: UUID (FK users.id)
    following_id: UUID (FK users.id)
    created_at: datetime
    PK: (follower_id, following_id)

--- app/entities/models.py ---
class Entity(Base):
    __tablename__ = "entities"
    id: UUID
    name: str (not null, indexed)
    type: str (not null) — e.g. "movie", "game", "book", "person", "place", "product", "music", "pokemon", "other"
    aliases: ARRAY(str) (nullable)
    image_url: str (nullable)
    description: str (nullable)
    metadata: JSONB (nullable) — flexible extra data
    external_ids: JSONB (nullable) — {"imdb": "tt0816692", "tmdb": "157336"}
    is_verified: bool (default False)
    created_by: UUID (FK users.id, nullable)
    created_at: datetime
    updated_at: datetime
    
    Index on name for full-text search
    Index on type

After creating models:
1. Run alembic init alembic (if not done)
2. Configure alembic env.py to use SQLAlchemy models
3. Generate initial migration: alembic revision --autogenerate -m "initial_models"
4. Apply: alembic upgrade head
5. Verify tables exist in PostgreSQL
```

---

### Prompt 1.2 — Authentication System

```
Implement JWT-based authentication in rankr-backend.

--- app/auth/utils.py ---
Implement:
- hash_password(password: str) → str using passlib bcrypt
- verify_password(plain: str, hashed: str) → bool
- create_access_token(data: dict, expires_delta: timedelta) → str using python-jose
- create_refresh_token(data: dict) → str (longer expiry, e.g. 30 days)
- decode_token(token: str) → dict (raises HTTPException 401 if invalid/expired)

--- app/auth/schemas.py ---
- RegisterRequest: email, username, password (min 8 chars)
- LoginRequest: email, password
- TokenResponse: access_token, refresh_token, token_type="bearer"
- RefreshRequest: refresh_token

--- app/auth/service.py ---
- register_user(db, data: RegisterRequest) → User
  - Check email uniqueness
  - Check username uniqueness (alphanumeric + underscore only, 3-30 chars)
  - Hash password
  - Create User row
  - Create Profile row (display_name = username)
  - Return User
- login_user(db, data: LoginRequest) → TokenResponse
  - Find user by email
  - Verify password
  - Return tokens
- refresh_tokens(refresh_token: str) → TokenResponse
  - Decode refresh token
  - Return new token pair

--- app/auth/router.py ---
POST /auth/register → RegisterRequest → TokenResponse (201)
POST /auth/login → LoginRequest → TokenResponse
POST /auth/refresh → RefreshRequest → TokenResponse
GET /auth/me → returns current user (protected)

--- app/common/dependencies.py ---
async def get_current_user(token: str from Bearer header, db) → User
  - Decode token, fetch user, verify is_active
  - Raise 401 if invalid
async def get_optional_user(token: Optional[str], db) → Optional[User]
  - Same but returns None instead of raising

Write pytest tests in tests/test_auth.py covering:
- Register success
- Register with duplicate email/username (422)
- Login success
- Login with wrong password (401)
- Access protected route with valid token
- Access protected route with expired token (401)
```

---

### Prompt 1.3 — User Profiles & Entity System

```
Implement user profile management and the entity (item) system.

--- app/users/router.py ---
GET /users/{username} → public profile (no auth required)
PATCH /users/me → update own profile (auth required)
  - Updatable: display_name, bio, website, avatar_url
GET /users/{username}/followers → paginated list
GET /users/{username}/following → paginated list
POST /users/{username}/follow → follow (auth required)
DELETE /users/{username}/follow → unfollow (auth required)

Follow endpoint must:
- Add Follow row
- Increment Profile.follower_count for followed user
- Increment Profile.following_count for current user
- Return 409 if already following
Unfollow: reverse operations.

--- app/users/schemas.py ---
UserPublicProfile: username, display_name, avatar_url, bio, follower_count, following_count, ranking_count, created_at
ProfileUpdateRequest: display_name?, bio?, website?, avatar_url?

--- app/entities/router.py ---
GET /entities/search?q={query}&type={type}&limit=20 → list of entities
  - PostgreSQL ILIKE search on name and aliases
  - Filter by type if provided
  - Return top 20 matches
POST /entities → create entity (auth required)
  - Any logged-in user can suggest an entity
  - Mark is_verified=False initially
GET /entities/{id} → entity detail

--- app/entities/schemas.py ---
EntityBase: name, type, image_url?, description?, metadata?, external_ids?
EntityCreate extends EntityBase
EntityPublic: id + all fields + is_verified

Seed the database with at least 200 starter entities across categories:
- 50 popular movies (name, type="movie", external imdb ID)
- 50 popular games (type="game")
- 50 Pokémon (type="pokemon")
- 50 programming languages/tools (type="technology")

Create a seed script at app/scripts/seed_entities.py using the above data hardcoded.
```

---

## PHASE 2 — Rankings Engine

### Prompt 2.1 — Ranking Models & Core CRUD

```
Add ranking-related SQLAlchemy models to rankr-backend.

--- app/rankings/models.py ---

class Ranking(Base):
    __tablename__ = "rankings"
    id: UUID
    slug: str (unique, indexed) — auto-generated from title + short random suffix
    user_id: UUID (FK users.id)
    title: str (not null, max 200)
    description: str (nullable, max 2000)
    type: str (default "standard") — "standard"|"blind"|"battle"|"community"
    category: str (nullable) — "movies"|"games"|"books"|"music"|"food"|"tech"|"sports"|"anime"|"other"
    size: int (not null) — number of items expected (3,5,10,20,25,50,100)
    visibility: str (default "public") — "public"|"unlisted"|"followers"|"private"
    status: str (default "draft") — "draft"|"published"
    view_count: int (default 0)
    like_count: int (default 0)
    comment_count: int (default 0)
    created_at, updated_at, published_at (nullable)
    
    relationship → items (RankingItem, ordered by position)
    relationship → user

class RankingItem(Base):
    __tablename__ = "ranking_items"
    id: UUID
    ranking_id: UUID (FK rankings.id, cascade delete)
    entity_id: UUID (FK entities.id, nullable) — nullable for custom items
    custom_name: str (nullable) — if no entity, user typed a custom item
    custom_image_url: str (nullable)
    position: int (not null, 1-indexed)
    note: str (nullable, max 1000) — the "Why?" text
    created_at, updated_at
    
    Unique constraint: (ranking_id, position)
    Index on ranking_id

class RankingVersion(Base):
    __tablename__ = "ranking_versions"
    id: UUID
    ranking_id: UUID (FK rankings.id, cascade delete)
    version_number: int
    snapshot: JSONB — full ranking state at that point
    change_summary: str (nullable) — "Moved Interstellar from #5 to #1"
    created_at

class Like(Base):
    __tablename__ = "likes"
    user_id: UUID (FK users.id)
    ranking_id: UUID (FK rankings.id)
    created_at: datetime
    PK: (user_id, ranking_id)

class Comment(Base):
    __tablename__ = "comments"
    id: UUID
    ranking_id: UUID (FK rankings.id)
    user_id: UUID (FK users.id)
    content: str (not null, max 1000)
    parent_id: UUID (FK comments.id, nullable) — for replies
    created_at, updated_at

Generate and apply migration.
```

---

### Prompt 2.2 — Ranking Service & Router

```
Implement the full rankings API.

--- app/rankings/service.py ---

create_ranking(db, user_id, data: RankingCreateRequest) → Ranking
  - Generate slug from title (slugify + 6-char random suffix for uniqueness)
  - Create Ranking row
  - If items provided, create RankingItem rows
  - Increment Profile.ranking_count
  - Return ranking with items

update_ranking(db, ranking_id, user_id, data: RankingUpdateRequest) → Ranking
  - Verify ownership
  - Update fields
  - If items changed, diff and update positions
  - Save RankingVersion snapshot

publish_ranking(db, ranking_id, user_id) → Ranking
  - Set status="published", published_at=now
  - Require at least 2 items

reorder_items(db, ranking_id, user_id, items: list[{item_id, position}]) → list[RankingItem]
  - Verify ownership
  - Validate no duplicate positions
  - Update all positions in single transaction
  - Save version snapshot

delete_ranking(db, ranking_id, user_id) → None
  - Verify ownership
  - Cascade delete items, versions, likes, comments

get_ranking(db, ranking_id_or_slug, viewer_user_id) → Ranking | None
  - Respect visibility rules:
    - "private": only owner
    - "followers": owner + followers
    - "unlisted": anyone with slug
    - "public": everyone
  - Increment view_count (async, rate-limited by IP+user)

--- app/rankings/router.py ---

POST /rankings → create (auth required)
GET /rankings/{slug} → get public ranking
PATCH /rankings/{slug} → update (auth, owner only)
DELETE /rankings/{slug} → delete (auth, owner only)
POST /rankings/{slug}/publish → publish (auth, owner only)
POST /rankings/{slug}/unpublish → revert to draft
PATCH /rankings/{slug}/items → reorder items (send full ordered list)
POST /rankings/{slug}/items → add item
DELETE /rankings/{slug}/items/{item_id} → remove item
PATCH /rankings/{slug}/items/{item_id} → update item note/position
POST /rankings/{slug}/like → toggle like (auth required)
GET /rankings/{slug}/likes → list likers
POST /rankings/{slug}/comments → post comment (auth required)
GET /rankings/{slug}/comments → get comments (public)
DELETE /rankings/{slug}/comments/{comment_id} → delete own comment

GET /users/{username}/rankings → all public rankings for user
  - Filter by: category, status=published
  - Paginate: limit=20, cursor-based

--- app/rankings/schemas.py ---
RankingCreateRequest: title, description?, category?, size (3-100), visibility="public", items?: list[ItemInput]
ItemInput: entity_id? | custom_name, position, note?
RankingUpdateRequest: title?, description?, category?, visibility?, size?
RankingPublic: all fields + items (ordered) + user (username, avatar)
RankingItemPublic: id, position, entity (name, image_url, type), custom_name?, note?

Write tests covering:
- Create ranking (with and without items)
- Cannot view private ranking as non-owner
- Reorder items validates positions
- Like/unlike toggle
- Comment on ranking
```

---

## PHASE 3 — Public Experience (Frontend)

### Prompt 3.1 — Frontend API Client & Auth

```
In rankr-frontend, set up the API client and authentication.

1. Create lib/api.ts:
   - Axios instance pointing to NEXT_PUBLIC_API_URL
   - Request interceptor: attach Bearer token from localStorage
   - Response interceptor: on 401, attempt refresh token, retry request, on second 401 clear tokens and redirect to /login

2. Create lib/auth.ts:
   - login(email, password) → stores access + refresh tokens in localStorage
   - logout() → clear tokens, redirect home
   - register(email, username, password) → calls /auth/register
   - getMe() → GET /auth/me
   - isAuthenticated() → check if valid token exists

3. Create stores/authStore.ts using Zustand:
   - State: user, isLoading, isAuthenticated
   - Actions: setUser, logout, initAuth (call getMe on mount)

4. Create app/(auth)/login/page.tsx — Login page
   - Email + password form
   - "Don't have an account? Sign up" link
   - Submit → call login() → redirect to home
   - Beautiful dark card design, violet gradient submit button

5. Create app/(auth)/register/page.tsx — Registration page
   - Email, username, password fields
   - Username field: real-time validation (alphanumeric/underscore, 3-30 chars)
   - Submit → register → redirect to home
   
6. Create components/layout/Navbar.tsx:
   - Left: Rankr logo (bold, violet gradient text)
   - Center: Search bar (routes to /explore?q=...)
   - Right: If authenticated: notification bell, avatar dropdown (profile/settings/logout). If not: Login + Sign Up buttons.
   - Sticky, glassmorphism background (backdrop-blur)
```

---

### Prompt 3.2 — Ranking Page (Public)

```
Create the public ranking page at app/[username]/[slug]/page.tsx in rankr-frontend.

This is the most important page — it must be beautiful.

Data fetching:
- SSR with generateMetadata for SEO
- Fetch GET /rankings/{slug}
- If 404, return Next.js notFound()
- If private/restricted, show "This ranking is private" message

Layout:
- Full-width hero header:
  - Ranking title in large bold type (48px+)
  - Creator avatar + username + "created X days ago"
  - Visibility badge, category badge
  - Action buttons: Like (with animated heart), Share, Comment count
  
- Ranked items list:
  Each item is a card with:
  - Large position number (#1, #2...) with a gradient that shifts gold→silver→bronze for top 3
  - Entity image (or placeholder) on the left
  - Entity name (large), type badge
  - "Why?" note if present (styled as a quote)
  - Hover state: subtle glow, slight scale

- Animate items in on page load: staggered fade-up animation using Framer Motion

- Comment section:
  - Comments displayed as conversation
  - If authenticated: comment input box
  - Reply threads (1 level deep)

- "Create your own" CTA at the bottom:
  "Disagree? Create your own Top X [category]" → routes to /create with pre-filled context

Social preview meta tags (OG/Twitter):
- og:title: "Rohit's Top 10 Movies"
- og:description: "1. Interstellar 2. The Dark Knight 3. Inception..."
- og:image: dynamically generated (placeholder URL initially, real OG image service later)
```

---

### Prompt 3.3 — Profile Page

```
Create the user profile page at app/[username]/page.tsx.

Data fetching (SSR):
- GET /users/{username} → profile data
- GET /users/{username}/rankings?status=published&limit=20

Components:

--- ProfileHeader ---
- Large avatar (80px) with violet ring
- Display name (large) + @username (muted)
- Bio text
- Follower count | Following count | Rankings count (clickable)
- Follow/Unfollow button (if not own profile, if authenticated)
- Edit Profile button (if own profile)

--- TasteBars ---
Visual representation of categories this user ranks in.
Calculate from their published rankings: count rankings per category.
Display as horizontal bars with category icon + label + bar fill.
Example: 🎬 Movies ████████░░ (8 rankings)
Animate bars on mount using Framer Motion.

--- RankingsGrid ---
Group rankings by category.
Each category section: category name header + horizontal scroll of ranking cards.
Ranking card: title, size (#10, #50, etc.), cover image collage (top 3 item images), like count.
On click → navigate to ranking page.

--- EmptyState ---
If profile has no rankings: "No rankings yet. Follow them to see when they rank something."

Tabs: All | Movies | Games | Books | Music | Food | Tech | Other
Filter rankings by selected category tab.
```

---

## PHASE 4 — Social Layer

### Prompt 4.1 — Home Feed & Discovery

```
Build the home feed at app/page.tsx and the explore page.

--- Backend additions first ---
Add these endpoints to rankr-backend:

GET /feed/home (auth required)
  - Returns paginated feed of rankings from followed users
  - Ordered by published_at DESC
  - Limit 20 per page, cursor-based pagination
  - Each item: ranking summary + creator info + engagement counts

GET /feed/trending
  - No auth required
  - Rankings with high view/like velocity in last 48 hours
  - Algorithm: (view_count * 0.3 + like_count * 0.7) / hours_since_published^1.5
  - Limit 20

GET /feed/new
  - Recently published public rankings
  - Ordered by published_at DESC

GET /feed/categories
  - Returns list of active categories with ranking counts

--- Frontend: app/page.tsx ---
If authenticated: show personalized home feed (followed users first, then trending)
If not: show trending + discovery CTA

Layout:

TOP SECTION:
Large hero prompt: "What are you ranking today?"
Search input (large, prominent): placeholder "Search movies, games, books, anything..."
Below: [🃏 Blind Rank] [⚔️ Start a Battle] quick action buttons

TRENDING SECTION:
Horizontal scroll of trending topic chips: 🔥 Movies · 🎮 Games · 🤖 AI Tools · ...
Below: 3-column grid of trending ranking cards

FOLLOWING FEED (if authenticated):
Infinite scroll of feed cards:

FeedCard component:
- Avatar + username + "created a new ranking · 2h ago"
- Ranking title (large)
- Preview: top 5 items as a styled mini-list
- Bottom: ❤️ {count} 💬 {count} ↗ Share

EXPLORE PAGE (app/explore/page.tsx):
- Category browser: icon grid (Movies, Games, Books, Music, Food, Tech, Sports, Anime, Travel, Other)
- Clicking category → /r/[category] page
- Search results when query provided
- "People you might like" section (users with most rankings)
```

---

### Prompt 4.2 — Challenge System & Notifications

```
Implement ranking challenges and basic notifications.

--- Backend: app/rankings/challenges.py ---

Models (add to rankings/models.py):
class Challenge(Base):
    __tablename__ = "challenges"
    id: UUID
    challenger_id: UUID (FK users.id)
    target_ranking_id: UUID (FK rankings.id)
    challenger_ranking_id: UUID (FK rankings.id, nullable — filled when they create their ranking)
    message: str (nullable, max 500)
    status: str — "pending"|"accepted"|"declined"|"completed"
    created_at, updated_at

Endpoints:
POST /rankings/{slug}/challenge
  - Creates challenge: challenger_id=current_user, target_ranking_id=slug's ranking
  - Sends notification to ranking owner
  - Returns challenge with share URL

GET /challenges/{id}
  - Returns challenge info + both rankings (for comparison)
  
PATCH /challenges/{id}/accept
  - Target user creates their own ranking, links it to challenge
  
--- Backend: app/notifications/models.py ---
class Notification(Base):
    __tablename__ = "notifications"
    id: UUID
    user_id: UUID (FK users.id) — recipient
    type: str — "like"|"comment"|"follow"|"challenge"|"reply"
    actor_id: UUID (FK users.id) — who triggered it
    target_type: str — "ranking"|"comment"|"challenge"
    target_id: UUID
    is_read: bool (default False)
    created_at: datetime

Endpoints:
GET /notifications → list unread + recent read (auth required)
POST /notifications/mark-read → mark all as read
GET /notifications/unread-count → integer count (for navbar badge)

Create notification helper function:
create_notification(db, user_id, type, actor_id, target_type, target_id)
Call this from: like service, comment service, follow service, challenge service.

--- Frontend ---
NotificationBell component in Navbar:
- Shows unread count badge (red dot with number)
- Click → dropdown showing recent notifications
- Each notification: actor avatar + text + time ago
  "Aman liked your Top 10 Movies"
  "Neha commented on your ranking"
  "Someone challenged your Top 10 Movies"
- "Mark all read" button
- Polls /notifications/unread-count every 30 seconds (simple polling for MVP, WebSocket later)
```

---

## PHASE 5 — Game Modes

### Prompt 5.1 — Blind Ranking Mode

```
Implement blind ranking — the signature feature.

--- Backend: app/blind_rankings/ ---

Models:
class BlindRankingSession(Base):
    __tablename__ = "blind_ranking_sessions"
    id: UUID
    user_id: UUID (FK users.id)
    topic: str — e.g. "Top 10 Movies"
    category: str
    items: JSONB — ordered list of entity_ids/custom items to rank
    decisions: JSONB — list of {item_id, chosen_position, timestamp}
    current_index: int (default 0) — which item is next
    total_items: int
    status: str — "in_progress"|"completed"|"abandoned"
    result_ranking_id: UUID (FK rankings.id, nullable) — created on completion
    created_at, updated_at

Endpoints:
POST /blind-rankings/start
  Request: { topic: str, category: str, size: int (3-100), item_ids?: [UUID] }
  - If item_ids not provided, suggest random items from entity pool for that category
  - Shuffle items randomly
  - Create session with status="in_progress"
  - Return session_id + first item to rank

GET /blind-rankings/{session_id}/next
  - Returns: current_item (entity data), current_index, total_items, current_partial_ranking[]
  - current_partial_ranking: sorted items decided so far
  - available_positions: list of valid positions for this item

POST /blind-rankings/{session_id}/decide
  Request: { position: int }
  - Record decision for current_index
  - Increment current_index
  - If current_index == total_items → set status="completed", generate final ranking
  - Return: { next_item?, is_complete: bool, partial_ranking[] }

POST /blind-rankings/{session_id}/complete
  - Create a Ranking + RankingItems from the session's decisions
  - Link result_ranking_id
  - Return the created ranking

--- How positions work ---
When user sees item N:
- They see their current partial list (N-1 items)
- They choose where to INSERT item N (before position 1, between 1 and 2, ... after last)
- All subsequent items shift down
- They CANNOT go back or change previous decisions

--- Frontend: app/blind/[sessionId]/page.tsx ---

Full-screen immersive experience.

Step 1 — Setup screen:
- "Start a Blind Ranking"
- Search/select topic or choose from suggestions
- Select size (10, 20, 50 options)
- Large START button

Step 2 — Ranking screen (main loop):
Layout:
  LEFT PANEL (40%): Current partial ranking (items decided so far)
    - Displayed as mini ranked list
    - Shows gaps where new item could go (highlighted on hover)
    
  RIGHT PANEL (60%): Current item to place
    - Large item card (entity image, name, type)
    - "Item 4 of 10"
    - Progress bar at top
    - "Where does this rank?" subtitle
    - Position selector: vertical list showing current ranking with "Insert here" hover zones
    
Interaction:
- User hovers/taps between items on the left panel → see highlighted insert zone
- Click insert zone → item animates into position, next item slides in from right
- Framer Motion: smooth card transitions, satisfying placement animation

Step 3 — Completion screen:
- "🔒 Ranking Locked!" 
- Dramatic reveal animation: items slide in from bottom, numbered 1-N
- Share button: "Share your blind ranking"
- Compare button: "See how others ranked this"
- "Create a detailed version" → takes to ranking editor with this as starting point
```

---

### Prompt 5.2 — Ranking Battles (Pairwise Comparison)

```
Implement ranking battles — pairwise A vs B comparisons that produce a ranking.

Algorithm: Modified merge sort / Elo-style pairwise. For N items, expect ~N*log(N) comparisons. Use simplified: always pick the comparison that gives most information (compare items with similar implicit rank).

--- Backend: app/battles/ ---

Models:
class BattleSession(Base):
    __tablename__ = "battle_sessions"
    id: UUID
    user_id: UUID (FK users.id)
    topic: str
    category: str
    item_ids: JSONB — list of entity/custom item IDs
    comparisons: JSONB — list of {item_a_id, item_b_id, winner_id, timestamp}
    scores: JSONB — running Elo/score per item
    total_items: int
    comparisons_done: int (default 0)
    estimated_total: int — ~N*log2(N) for guidance
    status: str — "in_progress"|"completed"
    result_ranking_id: UUID (nullable)
    created_at

Endpoints:
POST /battles/start
  Request: { topic, category, size, item_ids?: [UUID] }
  - Create session
  - Return session_id + first pair to compare

GET /battles/{session_id}/next-pair
  - Compute next best pair to compare using current scores
  - Return: { item_a: entity, item_b: entity, comparisons_done, estimated_total }
  - If estimated_total comparisons done → signal completion

POST /battles/{session_id}/choose
  Request: { winner_id: UUID }
  - Record comparison
  - Update Elo scores: winner +32 * (1 - expected), loser -32 * (1 - expected)
  - Increment comparisons_done
  - Return: { next_pair?, is_complete: bool, current_ranking[] }

POST /battles/{session_id}/finish
  - Can finish early (enough comparisons done)
  - Sort items by final Elo score
  - Create Ranking + RankingItems
  - Return ranking

--- Frontend: app/battle/[sessionId]/page.tsx ---

Battle UI — must feel like a game.

Step 1 — Setup: topic, items, START

Step 2 — Battle screen:
- FULL SCREEN split: LEFT vs RIGHT
- Left: large entity card for item A (image, name)
- Right: large entity card for item B (image, name)
- Center: "VS" in big gradient text
- Bottom: progress bar "17 / ~45 comparisons"
- "Skip" option (with limit, penalizes score slightly)

Interaction on choose:
- Winning card: scale up, green glow animation
- Losing card: scale down, fade slightly, slide away
- New pair slides in from sides

When complete:
- "⚔️ Battle complete!"
- Show final ranking with satisfying reveal animation (same as blind ranking completion)
- Share / Compare / Publish buttons

Allow user to stop early: "Finish and rank with current data"
```

---

### Prompt 5.3 — Ranking Comparison (Compare Mode)

```
Build the ranking comparison feature.

--- Backend ---
GET /compare?user1={username}&user2={username}&slug1={slug}&slug2={slug}
  - Fetch both rankings
  - Compute comparison:
    - For each item in BOTH rankings: get rank in each
    - Sort by biggest disagreement (abs(rank1 - rank2))
    - Items only in one ranking: show as "not ranked" in other
  - Return:
    {
      user1: { username, avatar },
      user2: { username, avatar },
      items: [{ entity, rank1, rank2, difference }],
      agreement_score: float (0-100) — % of shared items ranked within 3 positions,
      biggest_disagreements: top 5 items with largest rank differences,
      agreements: top 5 items where both users ranked similarly
    }

--- Frontend: app/compare/[username1]/[username2]/page.tsx ---

Side-by-side comparison table:

Header:
  [User1 Avatar] vs [User2 Avatar]
  "You agree on 67% of ranked items"
  
Tabs: All Items | Biggest Disagreements | Strong Agreements | Only in Mine | Only in Theirs

Table columns:
  Item | User1's Rank | Position difference (bar) | User2's Rank

Color coding:
  - Agreement (diff ≤ 2): green
  - Mild disagreement (diff 3-5): yellow  
  - Strong disagreement (diff > 5): red

Biggest Disagreements section:
  Each item shown as a featured card:
  "Avatar: You ranked it #8, they ranked it #2. Difference: 6 positions"
  Comment button → opens a discussion thread about that specific item

"Challenge this ranking" CTA → lets user create their own ranking to counter

Also create a shareable compare URL that anyone can view publicly.
```

---

## PHASE 6 — Discovery & Community

### Prompt 6.1 — Topic Pages & Community Rankings

```
Build topic/category pages and community aggregate rankings.

--- Backend: app/community/ ---

Community ranking algorithm:
- For a given topic (e.g. "Top Movies"), collect all public rankings in that category
- For each entity that appears across rankings: calculate Borda count
  Borda count: if ranking has N items, item at position k gets (N - k + 1) points
- Sum Borda points across all rankings
- Sort by total Borda points
- Only include entities that appear in ≥ 5 rankings (minimum threshold)
- Cache result in Redis for 1 hour (key: "community:{category}:{size_bucket}")

Endpoints:
GET /community/{category}
  Returns: community ranking for that category (top 50)
  Includes: ranking_count (how many people ranked this category), entity list with scores

GET /topics
  Returns: list of all active topics with:
  - ranking_count (total rankings in this category)
  - top_entities (top 3 entities in community ranking)
  - trending_score (new rankings in last 7 days)

GET /topics/{topic}/rankings
  Returns: paginated list of individual rankings in this topic (public only)
  Sort by: trending | popular | recent

--- Frontend: app/r/[topic]/page.tsx ---

Topic page layout:

HERO:
- Topic title (e.g. "Movies") with large icon
- "{N} people have ranked movies on Rankr"
- "Create your Movie Ranking" CTA button

COMMUNITY RANKING section:
- "Community Top 50 Movies" — based on {N} rankings
- Displayed as the standard ranking list (same beautiful cards)
- Small note: "Based on Borda count from {N} individual rankings"

INDIVIDUAL RANKINGS section:
- Tabs: 🔥 Trending | ⭐ Popular | 🕐 Recent
- Grid of ranking cards

"People who rank [topic]" section:
- Row of user avatars with their top-ranked item
- Follow button on each

--- Frontend: app/explore/page.tsx ---
Grid of all topic cards:
Each card: topic icon (emoji), name, ranking count, top 3 entities preview
Hover: slight lift effect with glow
```

---

### Prompt 6.2 — Ranking Creation Flow (Full UX)

```
Build the complete ranking creation experience at app/create/page.tsx.

This is the most important creation UX. Make it feel like a game, not a form.

STEP 1 — "What are you ranking?"
- Full-screen step with single large input
- Placeholder: "Top 10 Movies, Top 50 Pokémon, Top 25 Programming Languages..."
- Below input: quick-start suggestions as large clickable chips:
  🎬 Top 10 Movies · 🎮 Top 10 Games · 🤖 Top 10 AI Tools · ⚡ Top 50 Pokémon
- User types: system detects category + size using simple regex/keyword matching
  "Top 10 Pokémon" → category: pokemon, size: 10
  "Top 50 Movies" → category: movies, size: 50
  "My favorite restaurants" → category: food, size: 10 (default)
- Auto-detected values shown below: "Category: Movies · Size: 10 · [Change]"
- Next button → Step 2

STEP 2 — Add Items
LAYOUT: Two-column editor (on desktop)

LEFT COLUMN — "Available Items":
- Search input: "Search for items to add..."
- Search results from GET /entities/search?q=...&type={category}
- Suggested items (top entities for this category, not yet added)
- Each result: entity image + name + [+] add button
- "Create custom item" at bottom (for items not in database)

RIGHT COLUMN — "Your Ranking" (the ordered list):
- Title at top (editable inline)
- Drag-and-drop ranked list
- Position numbers (#1, #2...) as large, styled labels
- Each item: drag handle, entity image, name, × remove, optional note field
- Empty slots shown as dashed placeholders: "Drop or click to add your #3"
- Bottom: "+ Add another item"

State: Items can be dragged between left and right panels (react-beautiful-dnd or @dnd-kit/core)

MOBILE LAYOUT: Single column — add items first (search + add to list), then reorder list below.

BOTTOM BAR:
- Left: [Save Draft]  
- Right: [Publish]
- Progress: "7 / 10 items added"

On Publish:
- Validate: at least 2 items, title not empty
- Call POST /rankings
- Then POST /rankings/{slug}/publish
- Redirect to ranking page with confetti animation

CREATE MODES BAR at top:
[✏️ Standard] [🃏 Blind] [⚔️ Battle]
Switching to Blind/Battle routes to their respective flow pages.
```

---

## PHASE 7 — Polish & Launch

### Prompt 7.1 — SEO & OG Image Generation

```
Implement SEO and Open Graph image generation.

--- Backend: app/seo/og_images.py ---
Use Pillow to generate OG images for rankings dynamically.

POST /og/{ranking_slug}
Returns a PNG image (1200x630):
- Dark background (#0f1117)
- Rankr logo/wordmark top left
- Large ranking title
- Creator avatar + username
- Top 3-5 items listed with positions
- Bottom: "rankr.app" watermark
Cache generated images in Redis or object storage for 24 hours.

--- Frontend SEO ---
In app/[username]/[slug]/page.tsx, implement generateMetadata:
export async function generateMetadata({ params }) {
  const ranking = await fetchRanking(params.slug)
  return {
    title: `${ranking.user.username}'s ${ranking.title} | Rankr`,
    description: `${ranking.user.username} ranked: 1. ${item1} 2. ${item2} 3. ${item3}...`,
    openGraph: {
      title: ranking.title,
      description: top items preview,
      images: [`${API_URL}/og/${ranking.slug}`],
      type: 'website'
    },
    twitter: {
      card: 'summary_large_image',
      ...same
    }
  }
}

Also implement:
- robots.txt: allow all except /api/, /create, /settings
- sitemap.xml endpoint: GET /sitemap.xml → lists all public ranking URLs + profile URLs
  - Only include rankings with status=published, visibility=public, at least 3 items
  - Limit to 50,000 URLs initially
  - Prioritize by view_count

Add JSON-LD structured data to ranking pages:
{
  "@type": "Article",
  "headline": "Rohit's Top 10 Movies",
  "author": { "@type": "Person", "name": "Rohit" },
  "datePublished": "...",
  "description": "..."
}
```

---

### Prompt 7.2 — Search System

```
Implement full search across rankings, users, and entities.

--- Backend: app/search/ ---

GET /search?q={query}&type={all|ranking|user|entity}&limit=20&offset=0

type=all returns combined results (rankings + users + entities)
type=ranking: search ranking titles and descriptions
type=user: search username and display_name
type=entity: search entity names and aliases

PostgreSQL implementation:
1. For entity search: 
   WHERE to_tsvector('english', name || ' ' || COALESCE(description,'')) @@ plainto_tsquery('english', :q)
   OR name ILIKE '%' || :q || '%'
   Add GIN index on to_tsvector for entities.name

2. For ranking search:
   WHERE status='published' AND visibility='public'
   AND to_tsvector('english', title || ' ' || COALESCE(description,'')) @@ plainto_tsquery('english', :q)
   OR title ILIKE '%' || :q || '%'

3. For user search:
   WHERE username ILIKE '%' || :q || '%'
   OR display_name ILIKE '%' || :q || '%'

Response schema:
{
  rankings: [{ id, slug, title, user, item_count, like_count }],
  users: [{ username, display_name, avatar_url, ranking_count, follower_count }],
  entities: [{ id, name, type, image_url }],
  total_count: int
}

--- Frontend ---
Search page: app/search/page.tsx
- URL-based: /search?q=batman&type=all
- Tabs: All | Rankings | People | Items
- Results update on query change (debounced 300ms)

Search bar in Navbar:
- On focus: show recent searches (localStorage) and trending searches
- On type: debounced call to GET /search?q=... → show dropdown suggestions
- Entity suggestions show type badge
- Press Enter → navigate to /search?q=...
- Click entity → navigate to /r/{entity.type}?highlight={entity.id}
```

---

### Prompt 7.3 — Moderation & Safety

```
Implement basic moderation and safety features.

--- Backend: app/moderation/ ---

Models:
class Report(Base):
    __tablename__ = "reports"
    id: UUID
    reporter_id: UUID (FK users.id)
    target_type: str — "ranking"|"comment"|"user"|"entity"
    target_id: UUID
    reason: str — "spam"|"harassment"|"inappropriate"|"copyright"|"misinformation"|"other"
    description: str (nullable, max 500)
    status: str — "pending"|"reviewed"|"resolved"|"dismissed"
    reviewed_by: UUID (nullable, FK users.id) — moderator
    created_at, updated_at

class BlockedUser(Base):
    __tablename__ = "blocked_users"
    blocker_id: UUID
    blocked_id: UUID
    created_at: datetime
    PK: (blocker_id, blocked_id)

Endpoints:
POST /reports → create report (auth required)
POST /users/{username}/block → block user
DELETE /users/{username}/block → unblock
GET /users/me/blocked → list blocked users

Content filtering:
Add a simple profanity filter on:
- ranking titles
- item names
- comments
- usernames
- bios
Use better-profanity Python library or a simple wordlist.
Raise 422 with clear message if flagged content detected.

Rate limiting (use slowapi with Redis):
- POST /rankings: 10 per hour per user
- POST /rankings/{slug}/comments: 30 per hour per user
- POST /auth/register: 5 per hour per IP
- POST /auth/login: 10 per hour per IP
- POST /reports: 20 per hour per user

Block behavior:
- When user A blocks user B:
  - A cannot see B's rankings in feed
  - B cannot comment on A's rankings
  - Both profiles hidden from each other
Apply blocking filter to feed and comment queries.

--- Frontend ---
Add Report button (⋯ menu) to:
- Feed cards
- Ranking pages
- Comment items
- User profiles

ReportModal component:
- Select reason from dropdown
- Optional description textarea
- Submit → POST /reports → "Thank you for your report" toast

Block user: in profile page ⋯ menu → "Block @username" → confirm dialog
```

---

### Prompt 7.4 — Performance & Analytics

```
Implement performance optimizations and basic analytics tracking.

--- Backend Performance ---

1. Redis caching layer (app/common/cache.py):
   Implement cache decorator:
   @cache(key="trending_feed", ttl=300)
   async def get_trending_rankings(db): ...
   
   Cache these endpoints:
   - GET /feed/trending → TTL 5 minutes
   - GET /community/{category} → TTL 60 minutes
   - GET /topics → TTL 10 minutes
   - GET /entities/search?q=... → TTL 15 minutes (per unique query)

2. Database indexes (add migration):
   - rankings: (user_id, status, visibility, published_at)
   - rankings: (status, visibility, published_at) for trending
   - ranking_items: (ranking_id, position)
   - follows: (follower_id), (following_id)
   - likes: (ranking_id), (user_id)
   - comments: (ranking_id, created_at)
   - entities: GIN index on to_tsvector(name)

3. View count batching:
   Instead of DB write on every view:
   - Increment Redis counter: INCR "views:{ranking_id}"
   - Background worker runs every 5 minutes: flush Redis view counts to DB
   
4. Pagination: all list endpoints use cursor-based pagination (not offset).
   Cursor = base64({"id": last_item_id, "published_at": "...ISO..."})

--- Backend Analytics ---
Add app/analytics/ module.

Track these events in a simple analytics table:
class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id: UUID
    user_id: UUID (nullable)
    event_type: str — "ranking_created"|"ranking_published"|"blind_started"|"blind_completed"|"battle_started"|"battle_completed"|"share"|"ranking_viewed"|"profile_viewed"
    properties: JSONB
    created_at: datetime

Create helper: track_event(db, event_type, user_id=None, **properties)
Call from relevant service methods.

GET /analytics/me (auth required) — user's own stats:
- Total rankings created
- Total views received
- Total likes received
- Most popular ranking
- Completion rate (blind rankings completed / started)

--- Frontend Performance ---
1. Implement Next.js Image optimization for all entity images
2. Add loading.tsx skeleton screens for all main pages
3. Implement infinite scroll on feed (Intersection Observer API)
4. Add error.tsx boundaries on all route segments
5. React.lazy + Suspense for heavy components (battle, blind ranking)
6. Implement service worker for offline support of cached rankings (next-pwa or manual)
```

---

### Prompt 7.5 — Final Polish & Launch Checklist

```
Final polish pass and launch preparation.

--- Animations & Micro-interactions (Framer Motion) ---

1. Feed cards: staggered fade-up on mount (staggerChildren: 0.05)
2. Ranking items: drag and drop with scale animation on grab, spring animation on drop
3. Position number change: animate the number rolling when position changes
4. Like button: heart scale pulse + particle burst (3 small hearts float up and fade)
5. Follow button: morphs from "Follow" → spinning → "Following ✓"
6. Blind ranking card transition: new item slides in from right, decided item flies to its slot on the left
7. Battle choice: winner card scales up + green glow, loser fades + shrinks, then transition
8. Profile page: taste bars animate from 0 to their value on scroll-into-view
9. Page transitions: fade between routes using AnimatePresence

--- Empty States ---
Create beautiful empty states for:
- Empty feed: "Follow some people to see their rankings. Or explore trending →"
- No rankings on profile: "No rankings yet. Start ranking!"
- No search results: "No results for '{query}'. Try a different search."
- Error state: "Something went wrong. Try refreshing."
Each has an illustration (simple SVG) and a CTA button.

--- Settings Page (app/settings/page.tsx) ---
Sections:
- Profile: edit display_name, bio, website, avatar upload
- Account: change email, change password, connected accounts
- Privacy: default ranking visibility (public/unlisted/private)
- Notifications: toggle email notifications for likes/comments/follows/challenges
- Data: Export my data (JSON), Delete account (with confirmation)

--- Landing Page for logged-out users ---
Replace basic home with marketing landing page:
Hero: "Rank Anything. Discover Everyone's Taste."
Subheading: "Create top lists, discover what others think, and find people with your taste."
3 feature highlights: Normal Ranking · Blind Ranking · Ranking Battles
Social proof: "Join {N} people ranking everything" (hardcode initially)
CTA: "Start Ranking — It's Free"
Below fold: Showcase of 3 beautiful ranking examples (real data from platform)
Footer: About | Privacy | Terms | Twitter | Discord

--- Pre-launch Checklist ---
□ Environment variables documented in .env.example
□ HTTPS configured (SSL certificate)
□ Database backups configured (daily)
□ Error tracking set up (Sentry for both Next.js and FastAPI)
□ Rate limiting verified on all mutation endpoints  
□ robots.txt allows only public content
□ All images use Next.js Image component with proper sizes
□ API response times < 200ms for cached endpoints, < 500ms uncached
□ Mobile responsive: test all pages at 375px, 768px, 1280px
□ Accessibility: all interactive elements keyboard-navigable, proper ARIA labels
□ Privacy policy and Terms of Service pages exist (even if minimal)
□ Moderation report flow tested end-to-end
□ Seed 50+ high-quality rankings across 5 categories before launch
□ Test the complete "magic moment" flow: create → share → compare → follow
```

---

## Summary Table

| Phase | Duration | Goal | Key Deliverables |
|-------|----------|------|-----------------|
| 0 | 1 week | Foundation | Scaffold, design system, mockups |
| 1 | 1 week | Backend core | Auth, users, entities |
| 2 | 1 week | Rankings engine | Full ranking CRUD |
| 3 | 1 week | Public frontend | Ranking page, profile, auth UI |
| 4 | 1 week | Social layer | Feed, follow, notifications, challenges |
| 5 | 1 week | Game modes | Blind ranking, battles, compare |
| 6 | 1 week | Discovery | Topic pages, community rankings, search |
| 7 | 1 week | Polish & launch | SEO, moderation, performance, animations |

**Total: ~8 weeks to launch-ready MVP**

---

## The Magic Moment to Optimize For

> User finishes a Blind Ranking → sees their final ranked list → hits Share → friend opens link → friend disagrees → friend creates their own → they compare → friend follows user → loop repeats.

Every sprint should ask: **does this feature make the loop faster, more fun, or more shareable?**
