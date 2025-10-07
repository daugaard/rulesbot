# PRD: Ads Sub-System for RulesBot.ai

## Overview

We want to introduce a lightweight ads system to **RulesBot.ai** that enables initial monetization. The system should serve **contextual ads** based on the board game a user is interacting with, or fallback to **general ads** if no contextual ads exist.

Ads will be primarily **Amazon affiliate links** at launch.

The ads system must be manageable through Django Admin and provide basic analytics (impressions and clicks).


## Goals

1. **Serve Ads in Context**

   * Ads tied to a specific board game appear on that game’s chat pages.
   * Generic ads serve as a fallback.

2. **Ad Management**

   * Admins define ads via the Django Admin interface.
   * Each ad includes:

     * Title (string)
     * Description (short ad copy)
     * Image (optional, file or URL)
     * Link (URL, affiliate-friendly)
     * Associated Game (optional, foreign key or null)
     * Weight (integer, controls likelihood of being served)

3. **Tracking & Analytics**

   * Log ad impressions (every time an ad is displayed).
   * Log ad clicks (when a user clicks the ad link).
   * Provide reporting (impressions & clicks per ad).
   * Show analytics in Django Admin (custom dashboard or extended admin list view).

## Non-Goals

* Real-time bidding or external ad networks.
* User-level ad targeting (beyond game context).
* Complex A/B testing or frequency capping.


## Functional Requirements

### 1. Ad Model

* `Ad`

  * `id` (UUID / AutoField)
  * `title` (CharField, max 255)
  * `description` (TextField, short length e.g. 500 chars)
  * `image` (ImageField or URLField, optional)
  * `link` (URLField)
  * `game` (ForeignKey to Game model, nullable, blank = generic ad)
  * `weight` (PositiveIntegerField, default=1) → higher = more likely to show
  * `created_at`, `updated_at`

### 2. Serving Ads

* When a user is on a **chat page**:

  1. Check if ads exist for the current game.
  2. If yes, select one ad randomly using **weighted random selection**.
  3. If no, select a weighted random generic ad.
* Ads should be rendered with:

  * Title
  * Description
  * Optional image
  * Clickable link (redirect via tracking endpoint, not direct).
* Placement: **Sidebar** in MVP. Later integration directly into chat messages.

### 3. Tracking

* **Impressions:** Logged each time an ad is served to a user (raw count, not unique).
* **Clicks:** Logged when a user clicks an ad (use a redirect endpoint like `/ads/click/<ad_id>`).

**Models**:

* `AdImpression`

  * `id`
  * `ad` (ForeignKey to Ad)
  * `timestamp`

* `AdClick`

  * `id`
  * `ad` (ForeignKey to Ad)
  * `timestamp`

### 4. Admin Integration

* Ads managed via Django Admin.
* Inline image upload or URL entry for ad images.
* Impressions and clicks viewable per ad:

  * Extra columns in the Ads list view (e.g., "Impressions", "Clicks", "CTR").
  * Custom admin dashboard page with a summary (total impressions, total clicks, CTR).

## Technical Requirements

* **Framework:** Django (follow project’s `agents.md` best practices).
* **Weighted Random Selection:** Implement custom selection logic using the `weight` field rather than `order_by("?")`.
* **Tracking:**

  * Impressions logged in the backend when rendering ad context.
  * Clicks logged via a redirect view that increments clicks then redirects to target URL.
* **Dashboard:**

  * Either extend Django Admin with a custom report page or add metrics inline in the ads list display.

## User Experience (UX)

* **Frontend Display**:

  * Ad displayed in the **sidebar** of the chat page.
  * Title bold, description regular text, optional image thumbnail, CTA link.
* **Click Handling**:

  * Clicking ad always routes through tracking redirect.

## Future Enhancements (Not in MVP)

* Support multiple ad formats (carousel, banner).
* Add expiration dates for ads.
* Add frequency capping (limit impressions per user).
* Import/export ads via CSV/JSON.
* Placement integration into the chat flow itself.

## Open Questions

* Should CTR thresholds or performance auto-disable low-performing ads?
* Should weights be capped or free-form integers?
* Should we add a scheduling option (e.g., only run ad during certain dates)?

## Agent Progress Tracking

The implementing agent should define its own phases and tasks to complete this PRD and add them here.

When done, mark the phase as complete.

### Phase 1: Core Infrastructure ⏳
- [x] Create ads Django app
- [x] Create Ad model with all fields (title, description, image, link, game FK, weight)
- [x] Create AdImpression tracking model
- [x] Create AdClick tracking model
- [x] Add ads app to INSTALLED_APPS
- [x] Create and run migrations
- [x] Write model tests (Ad, AdImpression, AdClick)

### Phase 2: Ad Selection & Serving Logic ✅
- [x] Implement weighted random ad selection service
- [x] Create ad serving function (context-aware: game-specific vs generic)
- [x] Inject ad context directly in chat view (view_chat_session)
- [x] Log impressions when ad is served
- [x] Write tests for weighted selection algorithm
- [x] Write tests for game-specific vs generic fallback logic
- [x] Update chat template to display ads in sidebar
- [x] Create ads URL structure (placeholder for Phase 3)

### Phase 3: Click Tracking ⏳
- [x] Create URL patterns for ads app
- [x] Implement ad click tracking redirect view (/ads/click/<ad_id>)
- [x] Log clicks and redirect to target URL
- [x] Write tests for click tracking and redirect behavior

### Phase 4: Django Admin Integration ✅
- [x] Register Ad model in Django admin
- [x] Add custom admin list display with basic fields
- [x] Create analytics dashboard view with time-based filtering
- [x] Implement custom analytics template with CTR display
- [x] Add time-based metric methods to Ad model
- [x] Write comprehensive tests for analytics view

### Phase 5: Frontend Display ⏳
- [ ] Update chat.html template to display ads in sidebar
- [ ] Style ad component (title, description, image, CTA link)
- [ ] Ensure clicks route through tracking endpoint
- [ ] Write integration tests for ad display on chat pages

### Phase 6: End-to-End Testing & Validation ⏳
- [ ] Test ad creation via admin
- [ ] Test weighted random selection (game-specific and generic)
- [ ] Test impression logging
- [ ] Test click tracking and redirect
- [ ] Verify analytics display in admin
- [ ] Run full test suite and ensure all tests pass
