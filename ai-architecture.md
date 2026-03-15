# PlanQuest AI Architecture Extension Document

**Status:** Production Design Specification
**Access Level:** Premium Users Only
**Version:** 1.0

---

## SECTION 1 — AI ARCHITECTURE GOALS

### Why Multi-Agent Instead of Single Assistant

A single generic AI assistant creates three critical problems in a productivity platform:

1. **Prompt bloat.** A single system prompt that covers planning, coaching, goal decomposition, recovery, mission design, and motivational copy becomes 3000+ tokens of instructions. Every call pays for context it doesn't need.

2. **Quality degradation.** When one prompt tries to do everything, each capability degrades. A planner that also coaches also motivates produces mediocre results across all three.

3. **Unpredictable outputs.** A single assistant may decide to coach when asked to plan, or suggest missions when asked for recovery. Specialized agents produce predictable, schema-compliant outputs because each agent has one job.

PlanQuest needs **deterministic product logic wrapped with advisory AI** — not an AI that runs the product.

### What Problems the AI Layer Solves

| Problem | Current State | AI Solution |
|---------|--------------|-------------|
| Users don't know what to plan | Empty planner page | Planner Agent generates daily/weekly plans from goals + habits |
| Big goals feel overwhelming | User creates "Learn Python" and stalls | Goal Breakdown Agent decomposes into weekly milestones + daily tasks |
| Missed days cause abandonment | User misses 2 days, streak breaks, user churns | Recovery Agent creates catch-up plan that's realistic |
| Users plateau after 2 weeks | Engagement drops at day 14-21 | Coaching Agent identifies patterns and gives actionable insights |
| Missions feel generic | Same mission templates for everyone | Mission Design Agent creates personalized missions based on behavior |
| Notifications feel robotic | Static template text | Motivation Copy Agent generates personalized, contextual messages |

### Responsibility Boundary

**Backend-owned deterministic logic (AI MUST NOT control):**
- XP calculation formulas
- Level progression math
- Streak increment/break logic
- Coin earning/spending accounting
- Wallet transaction recording
- Achievement unlock conditions
- Mission completion validation
- Reminder scheduling and delivery
- Analytics aggregation
- Auth and session management

**AI-owned advisory logic:**
- Suggesting which tasks to do today
- Suggesting time blocks for tasks
- Breaking goals into sub-tasks
- Generating recovery plans after missed days
- Identifying productivity patterns
- Generating personalized coaching insights
- Suggesting personalized missions
- Writing motivational copy for notifications

The AI **suggests**. The backend **validates**. The user **approves**. The backend **executes**.

---

## SECTION 2 — RECOMMENDED AI ARCHITECTURE MODEL

### Architecture Options Evaluated

**Option A: Single Assistant**
- One LLM call with a large system prompt
- Pros: Simple implementation
- Cons: Prompt bloat, unpredictable outputs, no specialization
- Verdict: **Rejected** — does not scale for 6+ capabilities

**Option B: Orchestrator + Specialized Agents**
- Central router decides which agent to call
- Each agent has focused prompt + schema
- Pros: Predictable outputs, efficient token usage, independent scaling
- Cons: Slightly more infrastructure
- Verdict: **Recommended**

**Option C: Tool-Calling Agent (ReAct pattern)**
- Single agent that calls backend tools in a loop
- Pros: Flexible reasoning
- Cons: Unpredictable call chains, hard to control costs, latency spikes
- Verdict: **Rejected** — too unpredictable for a product with strict output contracts

**Option D: Workflow Graph (LangGraph style)**
- DAG-based agent orchestration with conditional edges
- Pros: Maximum control, visualizable flows
- Cons: Over-engineered for current scale, complex debugging
- Verdict: **Deferred** — consider at 500K+ users when agent interactions become complex

### Final Recommended Model

**Orchestrator + Specialized Agents with Tool Functions**

```
User Request
    ↓
[Premium Check]
    ↓
[Orchestrator]
    ├── route to Planner Agent
    ├── route to Goal Breakdown Agent
    ├── route to Recovery Agent
    ├── route to Coaching Agent
    ├── route to Mission Design Agent
    └── route to Motivation Copy Agent
            ↓
    [Tool Functions] ← read-only access to backend data
            ↓
    [Structured Output]
            ↓
    [Validation Layer]
            ↓
    [User Preview / Approval]
            ↓
    [Backend Action via existing API]
```

Each agent:
- Has its own system prompt (200-400 tokens)
- Receives only relevant context (not full user history)
- Returns strict JSON schema
- Cannot write to database
- Cannot call other agents (only orchestrator can)

---

## SECTION 3 — AI LAYER POSITION INSIDE CURRENT SYSTEM

### Current Architecture Stack

```
┌─────────────────────────────────────────┐
│           Telegram Bot (aiogram)         │
│           Telegram Mini App (Next.js)    │
├─────────────────────────────────────────┤
│           FastAPI Backend                │
│  ┌─────────────────────────────────┐    │
│  │  API Routes Layer               │    │
│  │  /api/tasks, /api/habits, etc.  │    │
│  ├─────────────────────────────────┤    │
│  │  Domain Services Layer          │    │
│  │  task_service, habit_service,   │    │
│  │  xp_service, streak_service,    │    │
│  │  mission_service, etc.          │    │
│  ├─────────────────────────────────┤    │
│  │  Data Layer                     │    │
│  │  PostgreSQL + Redis + Celery    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Extended Architecture with AI Layer

```
┌─────────────────────────────────────────┐
│           Telegram Bot (aiogram)         │
│           Telegram Mini App (Next.js)    │
├─────────────────────────────────────────┤
│           FastAPI Backend                │
│  ┌─────────────────────────────────┐    │
│  │  API Routes Layer               │    │
│  │  /api/tasks, /api/habits, ...   │    │
│  │  /api/ai/plan, /api/ai/coach,   │    │  ← NEW AI endpoints
│  │  /api/ai/goals, /api/ai/recover │    │
│  ├─────────────────────────────────┤    │
│  │  ┌───────────────────────────┐  │    │
│  │  │  AI SERVICE LAYER (NEW)   │  │    │  ← Sits BETWEEN routes and domain
│  │  │  ┌─────────────────────┐  │  │    │
│  │  │  │  Orchestrator       │  │  │    │
│  │  │  ├─────────────────────┤  │  │    │
│  │  │  │  Agents (6)         │  │  │    │
│  │  │  ├─────────────────────┤  │  │    │
│  │  │  │  Tool Functions     │──┼──┼────┼── READ-ONLY access to domain services
│  │  │  ├─────────────────────┤  │  │    │
│  │  │  │  Validators         │  │  │    │
│  │  │  ├─────────────────────┤  │  │    │
│  │  │  │  Provider (Claude)  │  │  │    │
│  │  │  └─────────────────────┘  │  │    │
│  │  └───────────────────────────┘  │    │
│  ├─────────────────────────────────┤    │
│  │  Domain Services Layer          │    │  ← UNCHANGED
│  │  task_service, habit_service... │    │
│  ├─────────────────────────────────┤    │
│  │  Data Layer                     │    │  ← UNCHANGED
│  │  PostgreSQL + Redis + Celery    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Key Integration Points

1. **AI routes** (`/api/ai/*`) are new FastAPI routes that call the AI orchestrator
2. **AI tool functions** have **read-only** access to existing domain services (task_service, habit_service, etc.)
3. **AI never writes to database** — validated outputs are returned to the route, which calls existing domain services to create/update entities
4. **Premium middleware** checks user subscription before any AI route
5. **Bot integration** — bot commands like `/plan` call the same AI service layer
6. **Mini App integration** — AI screens call `/api/ai/*` endpoints

### What Does NOT Change

- All existing routes remain unchanged
- All domain services remain unchanged
- All models/migrations remain unchanged
- XP, streak, wallet, achievement logic remains unchanged
- Celery tasks remain unchanged
- Bot command handlers remain unchanged (new ones are added)

---

## SECTION 4 — AGENT DEFINITIONS

### Agent 1: Planner Agent

**Purpose:** Generate structured daily or weekly plans based on user context.

**Inputs:**
- User segment (student/freelancer/developer/entrepreneur)
- User timezone
- Today's date, day of week
- Active tasks (pending, with priority/difficulty/estimated_minutes)
- Active habits (with today's completion status)
- Overdue tasks from previous days
- Focus session stats (today/week averages)
- Current streak count
- Available time estimate (derived from recent focus patterns)

**Outputs (strict JSON):**
```json
{
  "plan_type": "daily",
  "date": "2026-03-15",
  "time_blocks": [
    {
      "start": "09:00",
      "end": "09:30",
      "type": "task",
      "task_id": "uuid-existing-task",
      "title": "Review project docs"
    },
    {
      "start": "09:30",
      "end": "10:00",
      "type": "habit",
      "habit_id": "uuid-existing-habit",
      "title": "Meditation"
    },
    {
      "start": "10:00",
      "end": "10:50",
      "type": "focus_session",
      "mode": "deep_50",
      "linked_task_id": "uuid-existing-task",
      "title": "Deep work: API development"
    }
  ],
  "suggested_new_tasks": [
    {
      "title": "Review yesterday's incomplete work",
      "priority": "high",
      "difficulty": "easy",
      "estimated_minutes": 15
    }
  ],
  "coaching_note": "Bugun 3 ta overdue task bor. Ularni birinchi navbatda bajaring."
}
```

**When Called:**
- User opens AI Planner screen in Mini App
- User sends `/plan` bot command
- Morning reminder triggers auto-plan generation (background)

**Allowed:**
- Read existing tasks, habits, goals
- Suggest time blocks using existing tasks
- Suggest 0-3 new tasks
- Reference existing habits in schedule

**NOT Allowed:**
- Create tasks directly in database
- Modify task priorities
- Complete tasks
- Award XP or coins
- Modify streaks

---

### Agent 2: Goal Breakdown Agent

**Purpose:** Decompose a high-level goal into weekly milestones and daily actionable tasks.

**Inputs:**
- Goal title and description (user-provided)
- Goal deadline (if set)
- User segment
- Current active task count (to avoid overload)
- User's average daily task completion rate

**Outputs (strict JSON):**
```json
{
  "goal_title": "Python o'rganish",
  "total_weeks": 8,
  "milestones": [
    {
      "week": 1,
      "title": "Python asoslari",
      "tasks": [
        {
          "title": "Python o'rnatish va muhit sozlash",
          "difficulty": "easy",
          "estimated_minutes": 30,
          "day_offset": 1
        },
        {
          "title": "O'zgaruvchilar va ma'lumot turlari",
          "difficulty": "medium",
          "estimated_minutes": 45,
          "day_offset": 2
        }
      ]
    }
  ]
}
```

**When Called:**
- User creates a new goal and taps "AI bilan rejalashtirish"
- User edits existing goal and requests breakdown

**Allowed:**
- Read user's current goals and task load
- Generate milestone structure
- Suggest daily tasks per milestone

**NOT Allowed:**
- Create goals or tasks in database
- Set deadlines without user approval
- Override existing task priorities

---

### Agent 3: Recovery Agent

**Purpose:** Create a realistic recovery plan when user misses 1+ days.

**Inputs:**
- Days missed (1-7)
- Overdue tasks with priorities
- Habits missed during gap
- Streak status (broken or frozen)
- User's typical daily capacity
- User's current emotional context (if available from coaching)

**Outputs (strict JSON):**
```json
{
  "recovery_type": "gentle",
  "missed_days": 2,
  "plan": {
    "today": {
      "focus": "Eng muhim 2 ta taskni bajaring",
      "tasks_to_prioritize": ["uuid-1", "uuid-2"],
      "tasks_to_reschedule": [
        {"task_id": "uuid-3", "new_date": "2026-03-17"}
      ],
      "tasks_to_archive": ["uuid-4"],
      "reduced_habit_target": true
    },
    "tomorrow": {
      "focus": "Normal rejimga qaytish",
      "return_to_normal": true
    }
  },
  "motivation": "2 kun o'tkazib yubordingiz — bu normal. Bugun faqat 2 ta eng muhim ishni bajaring."
}
```

**When Called:**
- User returns after 1+ days of inactivity
- System detects gap and triggers recovery suggestion
- User explicitly requests `/recover`

**Allowed:**
- Read overdue tasks
- Suggest task rescheduling
- Suggest task archiving
- Reduce habit targets temporarily

**NOT Allowed:**
- Actually reschedule tasks
- Archive tasks
- Modify streak counts
- Award "comeback" XP

---

### Agent 4: Coaching Agent

**Purpose:** Analyze user productivity patterns and provide actionable coaching insights.

**Inputs:**
- Last 14 days task completion data
- Last 14 days habit completion data
- Focus session patterns (time of day, duration, completion rate)
- Streak history
- XP earning pattern
- Task difficulty distribution
- Overdue task frequency

**Outputs (strict JSON):**
```json
{
  "insights": [
    {
      "type": "pattern",
      "icon": "clock",
      "title": "Eng samarali vaqtingiz: 10:00-12:00",
      "description": "Bu vaqtda task completion rate 85%. Qiyin tasklarni shu vaqtga rejalashtiring.",
      "action_suggestion": "schedule_hard_tasks_morning"
    },
    {
      "type": "warning",
      "icon": "alert",
      "title": "Habit consistency pasaymoqda",
      "description": "Oxirgi 3 kunda 2/5 habit loglangan. Habitlar sonini 3 taga kamaytiring.",
      "action_suggestion": "reduce_habits"
    },
    {
      "type": "achievement",
      "icon": "trophy",
      "title": "Focus vaqtingiz oshmoqda",
      "description": "Bu hafta o'rtacha 45 min/kun. O'tgan haftaga nisbatan 20% ko'p.",
      "action_suggestion": null
    }
  ],
  "burnout_risk": "low",
  "overall_trend": "improving"
}
```

**When Called:**
- User opens Coaching tab in Mini App
- Weekly coaching summary (Celery scheduled)
- User sends `/coach`

**Allowed:**
- Read all analytics data
- Identify patterns
- Suggest behavioral changes
- Warn about burnout risk

**NOT Allowed:**
- Modify any user data
- Change habit configurations
- Adjust difficulty settings
- Send notifications directly

---

### Agent 5: Mission Design Agent

**Purpose:** Generate personalized daily/weekly missions based on user behavior patterns.

**Inputs:**
- User segment
- Last 7 days activity summary
- Underused features (e.g., focus sessions never used, habits inconsistent)
- Current streak count
- User's average metrics
- Active mission list (to avoid duplicates)

**Outputs (strict JSON):**
```json
{
  "suggested_missions": [
    {
      "title": "50 daqiqa fokus sessiya",
      "description": "Bugun bitta deep work sessiya qiling",
      "action": "focus_minutes",
      "target_value": 50,
      "difficulty": "medium",
      "reward_xp": 35,
      "reward_coins": 15,
      "reasoning": "User hech qachon 50 min fokus qilmagan — behavior shaping"
    }
  ]
}
```

**When Called:**
- Daily mission generation (Celery, midnight) — replaces random template selection for premium users
- User requests custom mission via Mini App

**Allowed:**
- Read user behavior data
- Suggest mission parameters
- Suggest XP/coin rewards within defined bounds (min/max)

**NOT Allowed:**
- Create missions directly
- Set rewards outside allowed bounds
- Bypass daily mission limits

---

### Agent 6: Motivation Copy Agent

**Purpose:** Generate personalized, contextual motivational text for notifications and UI.

**Inputs:**
- Notification type (morning_reminder, evening_summary, streak_warning, achievement_unlock)
- User first name
- Current streak count
- Today's progress (tasks done, habits done)
- Recent milestone (if any)
- User segment
- Time of day

**Outputs (strict JSON):**
```json
{
  "message": "Xayrli tong, Azamat! 🔥 12 kunlik streak'ingiz kuchli. Bugun 3 ta task rejada — birinchisini hozir boshlang!",
  "tone": "energetic",
  "cta_text": "Boshlash",
  "cta_action": "open_planner"
}
```

**When Called:**
- Morning/evening reminder generation (Celery)
- Achievement unlock notification
- Streak milestone notification
- Re-engagement message (user inactive 3+ days)

**Allowed:**
- Read user context for personalization
- Generate text in user's language (Uzbek/Russian/English)

**NOT Allowed:**
- Include false statistics
- Promise specific rewards
- Manipulate urgency dishonestly
- Generate text longer than 280 characters

---

## SECTION 5 — ORCHESTRATOR DESIGN

### Request Flow

```
1. API Route receives request
     ↓
2. Premium check middleware
     ↓
3. Rate limit check (Redis: max 30 AI calls/day for premium)
     ↓
4. Orchestrator.handle(request_type, user_id, params)
     ↓
5. Orchestrator determines agent(s)
     ↓
6. Context builder assembles minimal context for chosen agent
     ↓
7. Agent called via provider (Claude API)
     ↓
8. Response parsed and validated
     ↓
9. Validated response returned to route
     ↓
10. Route returns preview to user
```

### Routing Logic

The orchestrator uses a simple deterministic router — NOT an LLM-based router:

```python
ROUTE_MAP = {
    "daily_plan":      [PlannerAgent],
    "weekly_plan":     [PlannerAgent],
    "goal_breakdown":  [GoalBreakdownAgent],
    "recovery":        [RecoveryAgent],
    "coaching":        [CoachingAgent],
    "custom_missions": [MissionDesignAgent],
    "notification":    [MotivationCopyAgent],
    "full_review":     [CoachingAgent, PlannerAgent],  # multi-agent
}
```

No LLM is needed to route — the request type is always explicit.

### Multi-Agent Calls

For `full_review`:
1. CoachingAgent runs first (produces insights)
2. PlannerAgent runs second (receives coaching insights as additional context)
3. Results merged into single response

Agents run **sequentially** when dependent, **parallel** when independent.

### Failure Handling

| Failure Type | Response |
|-------------|----------|
| LLM timeout (>15s) | Return cached previous plan if available, else "AI hozir band" |
| Invalid JSON from LLM | Retry once with stricter prompt, else return error |
| Schema validation failure | Retry once, else return partial valid data |
| Rate limit exceeded | Return "Kunlik limit tugadi (30/30)" |
| Provider API error | Return cached or template-based fallback |

### Avoiding Unnecessary AI Calls

- **Cache daily plans** in Redis (key: `ai:plan:{user_id}:{date}`, TTL: 4 hours)
- **Skip coaching** if user has <3 days of data
- **Skip recovery** if user missed 0 days
- **Reuse motivation copy** if context hasn't changed (same streak, same task count)
- **Batch notification copy** — generate all notification variants in one call instead of per-user

---

## SECTION 6 — TOOL / FUNCTION INTERFACE DESIGN

### Tool: get_user_context

**Purpose:** Assemble comprehensive user context for any agent.

**Inputs:** `user_id: UUID, context_type: str` (plan/coach/recover/mission)

**Outputs:** UserContext object with only fields relevant to context_type

**Safety:** Read-only. No writes. No sensitive data (no tokens, passwords, billing).

---

### Tool: get_active_tasks

**Purpose:** Fetch user's pending tasks, optionally filtered by date range.

**Inputs:** `user_id, date_from, date_to, status_filter, limit`

**Outputs:** List of `{id, title, priority, difficulty, estimated_minutes, planned_date, category}`

**Safety:** Returns max 50 tasks. Strips internal fields (xp_awarded, source, etc.).

---

### Tool: get_active_habits

**Purpose:** Fetch user's active habits with today's completion status.

**Inputs:** `user_id`

**Outputs:** List of `{id, title, type, target_value, today_completed, current_streak}`

**Safety:** Read-only. Max 20 habits.

---

### Tool: get_overdue_tasks

**Purpose:** Fetch tasks where planned_date < today and status = pending.

**Inputs:** `user_id, max_days_back (default 7)`

**Outputs:** List of overdue tasks with days_overdue field.

**Safety:** Max 7 days lookback. Max 30 tasks.

---

### Tool: get_analytics_summary

**Purpose:** Fetch aggregated analytics for coaching.

**Inputs:** `user_id, period_days (7 or 14)`

**Outputs:**
```json
{
  "avg_tasks_per_day": 3.2,
  "avg_habits_per_day": 2.1,
  "avg_focus_minutes_per_day": 42,
  "task_completion_rate": 0.73,
  "most_productive_hour": 10,
  "streak_current": 8,
  "streak_best": 14,
  "burnout_indicators": {
    "declining_completion": false,
    "reduced_focus_time": false,
    "missed_habits_increasing": true
  }
}
```

**Safety:** Aggregated data only. No raw event logs. No PII.

---

### Tool: get_user_goals

**Purpose:** Fetch user's active goals (when goal system is implemented).

**Inputs:** `user_id, status_filter`

**Outputs:** List of `{id, title, deadline, progress_percent, linked_task_count}`

**Safety:** Read-only. Max 10 goals.

---

### Tool: validate_plan

**Purpose:** Check AI-generated plan against business rules.

**Inputs:** `plan: DailyPlan | WeeklyPlan`

**Outputs:** `{valid: bool, errors: list[str], warnings: list[str]}`

**Safety rules checked:**
- No more than 15 tasks per day
- No more than 10 hours of scheduled time
- No tasks scheduled outside 06:00-23:00
- All referenced task_ids must exist
- All referenced habit_ids must exist
- No duplicate time blocks

---

### Tool: map_to_entities

**Purpose:** Convert validated AI plan into backend-ready create/update requests.

**Inputs:** `validated_plan, user_id`

**Outputs:** List of `TaskCreate`, `TaskUpdate`, `TimeBlock` objects ready for domain service calls.

**Safety:** Only produces request objects — does not execute them. Final execution is in the route handler after user approval.

---

## SECTION 7 — AI INPUT CONTEXT DESIGN

### Context Per Agent Type

| Field | Planner | Goal | Recovery | Coach | Mission | Motivation |
|-------|---------|------|----------|-------|---------|------------|
| user_segment | yes | yes | no | yes | yes | yes |
| timezone | yes | no | no | no | no | yes |
| today_date | yes | no | yes | yes | yes | yes |
| active_tasks | yes (all) | no | overdue only | last 14d | no | count only |
| habits | yes | no | missed only | last 14d | yes | count only |
| goals | yes | yes | no | no | no | no |
| streak | yes | no | yes | yes | yes | yes |
| focus_stats | yes | no | no | yes | yes | no |
| analytics | no | no | no | yes | yes | no |
| available_time | yes | no | no | no | no | no |
| burnout_risk | no | no | yes | yes | no | no |
| first_name | no | no | no | no | no | yes |

### Token Optimization Rules

1. **Never send task descriptions or notes** — title + priority + difficulty is sufficient
2. **Never send completed task history** — send aggregated counts only
3. **Never send raw event logs** — send analytics summaries
4. **Truncate task titles to 50 chars** in context
5. **Max 20 tasks in context** — sort by priority, take top 20
6. **Max 10 habits in context**
7. **Use compact date format** — "2026-03-15" not full ISO timestamp
8. **Remove null/empty fields** from context objects

### Estimated Token Usage Per Agent

| Agent | System Prompt | Context | Expected Output | Total |
|-------|--------------|---------|-----------------|-------|
| Planner | ~350 | ~800 | ~600 | ~1750 |
| Goal Breakdown | ~300 | ~400 | ~800 | ~1500 |
| Recovery | ~300 | ~500 | ~400 | ~1200 |
| Coaching | ~400 | ~600 | ~500 | ~1500 |
| Mission Design | ~300 | ~400 | ~300 | ~1000 |
| Motivation Copy | ~200 | ~200 | ~100 | ~500 |

Average: **~1250 tokens per call**
At Haiku pricing: ~$0.0003 per call
30 calls/day/user: ~$0.009/day/user = ~$0.27/month/user

---

## SECTION 8 — OUTPUT CONTRACTS

### Contract: DailyPlan

```json
{
  "$schema": "DailyPlan",
  "plan_type": "daily",          // enum: daily
  "date": "YYYY-MM-DD",         // ISO date
  "time_blocks": [               // array, 0-20 items
    {
      "start": "HH:MM",         // 24h format
      "end": "HH:MM",           // must be after start
      "type": "task|habit|focus_session|break",
      "task_id": "uuid|null",   // required if type=task
      "habit_id": "uuid|null",  // required if type=habit
      "title": "string",        // max 100 chars
      "mode": "string|null"     // focus mode if type=focus_session
    }
  ],
  "suggested_new_tasks": [       // array, 0-3 items
    {
      "title": "string",        // max 100 chars
      "priority": "low|medium|high|critical",
      "difficulty": "trivial|easy|medium|hard|epic",
      "estimated_minutes": 5-180
    }
  ],
  "coaching_note": "string"     // max 200 chars, optional
}
```

### Contract: WeeklyPlan

```json
{
  "$schema": "WeeklyPlan",
  "week_start": "YYYY-MM-DD",   // Monday
  "days": [                      // array, 5-7 items
    {
      "date": "YYYY-MM-DD",
      "focus_theme": "string",   // max 50 chars
      "task_ids": ["uuid"],      // existing tasks to schedule
      "suggested_tasks": [       // 0-3 per day
        { "title": "string", "priority": "string", "difficulty": "string" }
      ]
    }
  ],
  "weekly_goals": [              // 1-3 items
    "string"
  ],
  "weekly_focus_target_minutes": 100-600
}
```

### Contract: GoalDecomposition

```json
{
  "$schema": "GoalDecomposition",
  "goal_title": "string",
  "total_weeks": 1-52,
  "milestones": [                // 1-12 items
    {
      "week": 1,
      "title": "string",        // max 100 chars
      "tasks": [                 // 1-7 per milestone
        {
          "title": "string",
          "difficulty": "string",
          "estimated_minutes": 5-180,
          "day_offset": 1-7      // which day of the week
        }
      ]
    }
  ]
}
```

### Contract: RecoveryPlan

```json
{
  "$schema": "RecoveryPlan",
  "recovery_type": "gentle|moderate|full",
  "missed_days": 1-30,
  "plan": {
    "today": {
      "focus": "string",        // max 100 chars
      "tasks_to_prioritize": ["uuid"],      // 1-5 existing task IDs
      "tasks_to_reschedule": [
        { "task_id": "uuid", "new_date": "YYYY-MM-DD" }
      ],
      "tasks_to_archive": ["uuid"],         // 0-10
      "reduced_habit_target": true
    },
    "next_days": [               // 0-3 future days
      {
        "date": "YYYY-MM-DD",
        "focus": "string",
        "return_to_normal": true
      }
    ]
  },
  "motivation": "string"        // max 200 chars
}
```

### Contract: CoachingInsights

```json
{
  "$schema": "CoachingInsights",
  "insights": [                  // 2-5 items
    {
      "type": "pattern|warning|achievement|suggestion",
      "icon": "clock|alert|trophy|bulb|chart|fire",
      "title": "string",        // max 80 chars
      "description": "string",  // max 200 chars
      "action_suggestion": "string|null"
    }
  ],
  "burnout_risk": "low|medium|high",
  "overall_trend": "improving|stable|declining"
}
```

### Contract: MissionSuggestions

```json
{
  "$schema": "MissionSuggestions",
  "suggested_missions": [       // 1-5 items
    {
      "title": "string",        // max 100 chars
      "description": "string",  // max 200 chars
      "action": "tasks_completed|habits_logged|focus_minutes|focus_sessions|streak_days",
      "target_value": 1-100,
      "difficulty": "easy|medium|stretch",
      "reward_xp": 10-100,      // bounded
      "reward_coins": 5-50,     // bounded
      "reasoning": "string"     // why this mission, max 100 chars
    }
  ]
}
```

### Contract: MotivationCopy

```json
{
  "$schema": "MotivationCopy",
  "message": "string",          // max 280 chars
  "tone": "energetic|calm|supportive|celebratory|urgent",
  "cta_text": "string|null",   // max 20 chars
  "cta_action": "open_planner|open_habits|open_focus|open_progress|null"
}
```

---

## SECTION 9 — VALIDATION LAYER

### Validation Pipeline

```
AI Raw Output (string)
    ↓
Step 1: JSON Parse
    - If fails → retry once with "Return valid JSON" appended
    - If fails again → return error
    ↓
Step 2: Schema Validation (Pydantic model)
    - Check all required fields present
    - Check all types correct
    - Check enum values valid
    - Check string lengths within bounds
    - Check numeric ranges
    ↓
Step 3: Business Rule Validation
    - All task_ids exist and belong to user
    - All habit_ids exist and belong to user
    - No more than 15 tasks per day
    - No more than 10 hours scheduled
    - Time blocks don't overlap
    - Dates are in the future (not past)
    - Reward values within allowed bounds
    - No duplicate mission actions
    ↓
Step 4: Sanitization
    - Strip HTML/markdown from text fields
    - Truncate strings to max length
    - Remove any fields not in schema
    ↓
Validated Output → Return to route
```

### Workload Realism Check

```python
MAX_TASKS_PER_DAY = 15
MAX_SCHEDULED_MINUTES = 600  # 10 hours
MAX_FOCUS_SESSIONS = 5
MIN_BREAK_BETWEEN_SESSIONS = 5  # minutes

def check_workload(plan: DailyPlan) -> list[str]:
    warnings = []
    total_minutes = sum(block.duration for block in plan.time_blocks)
    if total_minutes > MAX_SCHEDULED_MINUTES:
        warnings.append("Kunlik reja 10 soatdan oshib ketdi")
    focus_count = sum(1 for b in plan.time_blocks if b.type == "focus_session")
    if focus_count > MAX_FOCUS_SESSIONS:
        warnings.append("5 tadan ortiq fokus sessiya")
    return warnings
```

### Duplicate Prevention

Before creating tasks from AI suggestions:
1. Fuzzy match title against existing tasks (Levenshtein distance < 3)
2. Check exact title match
3. If duplicate found → skip and log warning

---

## SECTION 10 — USER APPROVAL FLOW

### Flow: Mini App

```
User taps "AI bilan rejalashtirish"
    ↓
Frontend calls POST /api/ai/plan {type: "daily"}
    ↓
Backend: orchestrator → planner agent → validate → return preview
    ↓
Frontend shows Plan Preview screen:
    - Time blocks as cards
    - Existing tasks highlighted
    - New suggested tasks marked with "NEW" badge
    - Coaching note at bottom
    - Buttons: [Hammasi qo'shish] [Tahrirlash] [Bekor qilish]
    ↓
User can:
    a) Accept all → POST /api/ai/plan/apply {plan_id}
    b) Edit → modify time blocks, remove suggestions → POST /api/ai/plan/apply {plan_id, modifications}
    c) Cancel → no action
    ↓
Backend /apply route:
    - Creates new tasks via task_service
    - Does NOT modify existing tasks (only schedules them)
    - Returns confirmation
```

### Flow: Telegram Bot

```
User sends /plan
    ↓
Bot calls orchestrator → planner agent → validate
    ↓
Bot sends formatted plan as message:
    "📋 Bugungi reja:
     09:00 - Review docs (mavjud)
     10:00 - 50 min fokus sessiya
     11:00 - API yozish (mavjud)

     💡 Yangi: 'Review yesterday's work' (15 min)

     [✅ Qo'llash] [❌ Bekor]"
    ↓
User taps [✅ Qo'llash]
    ↓
Bot calls backend to apply plan
    ↓
Bot confirms: "✅ Reja qo'llanildi! 3 ta task rejalashtirildi."
```

### Flow: Goal Decomposition

```
User creates goal "Python o'rganish" in Mini App
    ↓
"AI bilan bo'lish" button appears
    ↓
POST /api/ai/goals/breakdown {goal_title, deadline}
    ↓
Returns milestone + task tree
    ↓
Preview screen shows:
    - Week-by-week milestones
    - Tasks per milestone
    - Total estimated time
    - [Hammasi qo'shish] [Tahrirlash] [Bekor]
    ↓
User approves → tasks created via task_service with goal_id link
```

---

## SECTION 11 — AI SAFETY AND GUARDRAILS

### Hard Rules

| Rule | Enforcement |
|------|-------------|
| Max 15 tasks per day | Validator rejects plans exceeding limit |
| Max 10 hours scheduled | Validator rejects overloaded plans |
| No tasks before 06:00 or after 23:00 | Time block validation |
| No direct DB writes | AI service has no DB session, only read-only tool functions |
| No XP/coin manipulation | AI output schemas have no XP/coin fields (except bounded mission rewards) |
| No streak modification | Streak service not exposed to AI layer |
| No hidden actions | Every AI action requires explicit user approval |
| Mission rewards bounded | XP: 10-100, Coins: 5-50 per mission |
| Rate limited | 30 AI calls/day per premium user |
| No PII in prompts | Tool functions strip sensitive fields |

### Prompt Safety

Each agent system prompt includes:
```
IMPORTANT RULES:
- You are an advisory AI. You suggest, you do not execute.
- Never include XP amounts, coin amounts, or level information in plans.
- Never promise specific rewards to the user.
- Never suggest more than 15 tasks per day.
- Never suggest focus sessions longer than 120 minutes.
- If the user seems burned out (declining metrics), suggest LESS work, not more.
- Always respond in the specified JSON schema. No additional text.
```

### Fallback Behavior (AI Unavailable)

| Scenario | Fallback |
|----------|----------|
| Claude API down | Show "AI hozir ishlamayapti. Keyinroq urinib ko'ring." |
| Planner unavailable | Show static template: "Bugungi rejangizni o'zingiz tuzib oling" |
| Mission agent unavailable | Use existing random template selection |
| Motivation agent unavailable | Use existing static notification templates |
| Recovery agent unavailable | Show generic recovery tips (hardcoded) |

AI must never be a single point of failure. The platform works fully without AI — AI enhances it.

---

## SECTION 12 — OBSERVABILITY AND COST CONTROL

### Logging

Every AI call logs:
```json
{
  "request_id": "uuid",
  "user_id": "uuid",
  "agent": "planner",
  "model": "claude-haiku-4-5",
  "input_tokens": 823,
  "output_tokens": 412,
  "latency_ms": 2340,
  "status": "success|error|timeout|validation_fail",
  "cached": false,
  "retry_count": 0,
  "timestamp": "2026-03-15T10:23:45Z"
}
```

Stored in: `ai_request_logs` table (PostgreSQL)

### Metrics Dashboard

| Metric | Measurement |
|--------|-------------|
| AI calls per day | COUNT(ai_request_logs) per day |
| Average latency | AVG(latency_ms) per agent |
| Success rate | COUNT(success) / COUNT(*) per agent |
| Plan acceptance rate | COUNT(plans applied) / COUNT(plans generated) |
| Token usage per day | SUM(input_tokens + output_tokens) |
| Cost per day | tokens × pricing |
| Cache hit rate | COUNT(cached=true) / COUNT(*) |
| Retry rate | COUNT(retry_count > 0) / COUNT(*) |

### Cost Control

**Model Routing Strategy:**

| Agent | Default Model | Rationale |
|-------|--------------|-----------|
| Planner | claude-haiku-4-5 | Structured output, speed matters |
| Goal Breakdown | claude-haiku-4-5 | Structured output |
| Recovery | claude-haiku-4-5 | Simple logic |
| Coaching | claude-sonnet-4-6 | Needs deeper analysis |
| Mission Design | claude-haiku-4-5 | Template-like output |
| Motivation Copy | claude-haiku-4-5 | Short text generation |

**Cost estimate at scale:**
- 1000 premium users × 15 calls/day avg
- 15,000 calls/day × 1250 avg tokens
- ~18.75M tokens/day
- At Haiku pricing (~$0.25/M input, $1.25/M output)
- ~$10-15/day = ~$300-450/month for 1000 premium users
- Revenue at $5/mo/user = $5000/month
- AI cost = 6-9% of revenue ✓

### Caching Strategy

| Cache Key | TTL | Invalidation |
|-----------|-----|-------------|
| `ai:plan:{user_id}:{date}` | 4 hours | Task created/completed/deleted |
| `ai:coach:{user_id}:{week}` | 24 hours | Weekly reset |
| `ai:missions:{user_id}:{date}` | 12 hours | Mission completed |
| `ai:motivation:{type}:{context_hash}` | 6 hours | Context change |

### Retry Policy

- Max 1 retry per call
- Retry only on: timeout, invalid JSON, 5xx from provider
- Do NOT retry on: 4xx, rate limit, valid but empty response
- Backoff: 2 seconds before retry

---

## SECTION 13 — RECOMMENDED FOLDER / MODULE STRUCTURE

```
app/
  ai/
    __init__.py

    orchestrator/
      __init__.py
      router.py          # Deterministic request → agent routing
      orchestrator.py     # Main entry point, handles multi-agent flows
      rate_limiter.py     # Redis-based per-user rate limiting

    agents/
      __init__.py
      base.py             # BaseAgent abstract class
      planner.py          # PlannerAgent
      goal_breakdown.py   # GoalBreakdownAgent
      recovery.py         # RecoveryAgent
      coaching.py         # CoachingAgent
      mission_design.py   # MissionDesignAgent
      motivation.py       # MotivationCopyAgent

    prompts/
      __init__.py
      planner.py          # System prompt + few-shot examples
      goal_breakdown.py
      recovery.py
      coaching.py
      mission_design.py
      motivation.py

    tools/
      __init__.py
      context.py          # UserContext builder
      tasks.py            # get_active_tasks, get_overdue_tasks
      habits.py           # get_active_habits
      analytics.py        # get_analytics_summary
      goals.py            # get_user_goals

    schemas/
      __init__.py
      plans.py            # DailyPlan, WeeklyPlan Pydantic models
      goals.py            # GoalDecomposition
      recovery.py         # RecoveryPlan
      coaching.py         # CoachingInsights
      missions.py         # MissionSuggestions
      motivation.py       # MotivationCopy
      context.py          # UserContext, AnalyticsSummary

    validators/
      __init__.py
      plan_validator.py   # Time block, workload, ID existence checks
      schema_validator.py # JSON → Pydantic parsing
      business_rules.py   # Max tasks, reward bounds, etc.
      sanitizer.py        # Strip HTML, truncate, remove extra fields

    providers/
      __init__.py
      base.py             # BaseProvider abstract class
      claude.py           # Claude/Anthropic API wrapper
      cache.py            # Redis cache layer

    services/
      __init__.py
      ai_service.py       # High-level service (used by routes)
      plan_service.py     # Plan generation + apply logic
      coach_service.py    # Coaching flow

    mappers/
      __init__.py
      plan_mapper.py      # AI plan → TaskCreate/Update objects
      mission_mapper.py   # AI missions → Mission create objects
      goal_mapper.py      # AI decomposition → Goal/Task objects

    models/
      __init__.py
      ai_request_log.py   # AI call logging model
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `orchestrator/` | Route requests, manage multi-agent flows, rate limit |
| `agents/` | Individual agent logic — prompt assembly + response parsing |
| `prompts/` | System prompts as Python strings/templates. Versioned. |
| `tools/` | Read-only data access functions for agents |
| `schemas/` | Pydantic models for AI input/output contracts |
| `validators/` | Validate AI outputs against business rules |
| `providers/` | LLM API abstraction (swap Claude for other models easily) |
| `services/` | High-level business logic combining agents + validation |
| `mappers/` | Convert validated AI output to backend entity requests |
| `models/` | Database models for AI-specific tables (logs) |

---

## SECTION 14 — ROLLOUT PLAN

### Phase 1: Foundation + Planner Agent (Weeks 1-2)

**Build:**
- AI module structure
- Claude provider with retry/cache
- Rate limiter
- Request logging model + migration
- Planner Agent (daily plan only)
- Plan validator
- Plan preview API endpoint
- Plan apply API endpoint
- Mini App: AI Planner screen (preview + approve)
- Bot: `/plan` command
- Premium check middleware

**Why first:** Planning is the highest-value AI feature. It directly reduces the #1 churn cause (empty planner, user doesn't know what to do).

### Phase 2: Goal Breakdown + Recovery (Weeks 3-4)

**Build:**
- Goal Breakdown Agent
- Recovery Agent
- Goal model (if not yet built)
- Goal decomposition API + UI
- Recovery detection logic (missed days trigger)
- Recovery preview + apply flow
- Bot: `/recover` command

**Why second:** Goal decomposition converts one-time goal creators into daily task completers. Recovery prevents churn after missed days.

### Phase 3: Coaching + Mission Agent (Weeks 5-6)

**Build:**
- Coaching Agent
- Mission Design Agent
- Analytics summary tool (aggregation queries)
- Coaching insights screen in Mini App
- Personalized mission generation (replace random templates for premium)
- Weekly coaching summary (Celery scheduled)
- Bot: `/coach` command

**Why third:** Coaching and personalized missions increase engagement depth. Users must have 2+ weeks of data before coaching is meaningful.

### Phase 4: Motivation Agent + Optimization (Weeks 7-8)

**Build:**
- Motivation Copy Agent
- Integration with reminder system (personalized notification text)
- Weekly plan support in Planner Agent
- A/B test framework for AI vs template notifications
- Cost optimization (batching, caching tuning)
- Observability dashboard

**Why last:** Motivation copy is enhancement, not core. Weekly planning builds on daily. Optimization requires production data.

---

## SECTION 15 — FINAL CTO RECOMMENDATION

### Architecture Decision

Use **Orchestrator + Specialized Agents** architecture with **Claude Haiku as default model** and **Claude Sonnet for coaching only**.

### Key Design Principles

1. **AI is advisory, not authoritative.** AI suggests plans, the user approves, the backend executes. AI never touches XP, streaks, coins, or any deterministic system.

2. **AI is optional.** The platform works fully without AI. AI failure = graceful fallback, not product failure.

3. **AI is premium.** Rate limited to 30 calls/day. This controls costs and creates clear premium value.

4. **Strict output contracts.** Every agent returns validated JSON matching a Pydantic schema. No free-form text responses that the frontend has to parse.

5. **Read-only data access.** AI tools can read user data through curated functions. They cannot write. The only write path is: AI output → validation → user approval → backend route → domain service.

6. **Minimal context.** Each agent receives only the fields it needs. A motivation agent doesn't need task details. A planner doesn't need analytics history. This saves tokens and improves output quality.

7. **Deterministic routing.** The orchestrator uses a simple map, not an LLM, to decide which agent to call. This is predictable, fast, and free.

### Cost Projection

| Scale | Premium Users | AI Calls/Day | Monthly Cost | Monthly Revenue | AI/Revenue |
|-------|--------------|-------------|-------------|----------------|------------|
| Early | 100 | 1,500 | $30 | $500 | 6% |
| Growth | 1,000 | 15,000 | $350 | $5,000 | 7% |
| Scale | 10,000 | 150,000 | $3,000 | $50,000 | 6% |
| Large | 100,000 | 1,500,000 | $25,000 | $500,000 | 5% |

AI cost stays under 10% of revenue at all scales. This is sustainable.

### Implementation Priority

Start with Planner Agent. It has the highest user impact, simplest implementation, and validates the entire AI pipeline (provider → agent → validator → preview → apply).

If Planner Agent works well and users engage with it, proceed to Phase 2. If not, iterate on the planner before adding more agents.

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| AI generates bad plans | Strict validation + user approval required |
| AI costs spike | Rate limiting + caching + model routing |
| Claude API goes down | Fallback to templates, platform works without AI |
| Users don't use AI features | AI is enhancement, not dependency. Premium has other value too. |
| AI outputs become stale | Cache TTLs + invalidation on user actions |

### Final Statement

The AI layer should feel like a **smart assistant inside the planner**, not a separate product. It should make the existing features more accessible and reduce the cognitive load of planning. If the AI disappeared tomorrow, users would miss the convenience but the product would still work perfectly.

Build it as an extension. Not a replacement.
