# PlanQuest — Gamified Productivity Planner for Telegram

## Production-Grade Product Requirements Document (PRD)

**Product:** PlanQuest — Gamified Planner Platform
**Platform:** Telegram Bot + Telegram Mini App (Hybrid)
**Scale target:** 1M+ users
**Document type:** Development-ready PRD for engineering and product teams
**Version:** 2.0
**Date:** 2026-03-15

---

# SECTION 1 — PRODUCT VISION

## 1.1 What is a Gamified Planner Platform

A gamified planner platform is a productivity system that wraps task management, habit tracking, focus sessions, and goal planning inside a behavioral reward structure. Every productive action a user takes — completing a task, logging a habit, finishing a focus session — triggers a measurable reward: XP, coins, streak continuation, achievement progress, or mission completion.

The critical distinction from a traditional planner: the system does not passively store tasks. It actively drives the user to complete them through psychological reinforcement loops.

The system operates on this principle: **productivity is the game, and real-life outcomes are the reward.**

## 1.2 Why Traditional Planners Fail

Traditional planners (Todoist, Google Tasks, Apple Reminders, Notion) fail at retention because they rely on a single psychological mechanism: **intrinsic motivation**. They assume the user already wants to be organized. They provide no external reinforcement when a task is completed. There is no visible consequence for missing a day. There is no progression system that compounds effort into visible growth.

The failure pattern is consistent across all traditional planners:

1. User downloads the app with high motivation
2. User creates tasks for 3–7 days
3. User misses 1–2 days
4. No system response to the miss — no recovery prompt, no streak warning, no comeback incentive
5. User stops opening the app
6. Retention collapses after D14

Data from the productivity app industry shows:

- Average D30 retention for planners: 8–12%
- Average D30 retention for gamified apps (Duolingo model): 25–40%
- The difference is entirely attributable to behavioral design, not feature count

Traditional planners treat productivity as a **database problem** (store and retrieve tasks). A gamified planner treats productivity as a **behavior change problem** (create, reinforce, and sustain productive habits).

## 1.3 How Gamification Increases Engagement

Gamification works because it exploits three core psychological drives defined in Self-Determination Theory (SDT):

**Autonomy** — the user chooses their tasks, goals, and habits. The system does not prescribe behavior. It provides structure and rewards for user-defined actions.

**Competence** — the XP bar, level system, and achievement badges create a visible record of growing capability. A Level 15 user sees concrete proof that they have been consistently productive for weeks.

**Relatedness** — streaks, challenges, and shared progress cards create social accountability. The user is not planning alone. They are part of a system that recognizes and rewards their effort.

The gamification layer adds four mechanisms that traditional planners lack:

1. **Variable reward schedule** — missions and chests provide unpredictable rewards, triggering dopamine release similar to slot machine mechanics but tied to productive action
2. **Loss aversion** — streak systems create a psychological cost for missing a day, which is more motivating than the benefit of completing one
3. **Progress visualization** — XP bars, level numbers, and achievement counts create a tangible sense of forward movement that raw task lists cannot provide
4. **Identity reinforcement** — titles like "Deep Worker" or "Goal Hunter" reinforce the user's self-image as a productive person, which drives future behavior

## 1.4 Why Telegram is a Powerful Distribution Channel

Telegram has specific properties that make it the optimal platform for this product:

**Zero-install distribution.** A Telegram bot requires no app store download. The user clicks a link, presses Start, and is onboarded. This eliminates the highest-friction step in mobile app acquisition.

**Built-in notification channel.** The bot sends messages directly into the user's chat list — the same interface they check 50–100 times per day. No push notification permission required. No notification settings to configure. The reminder appears alongside messages from friends and channels.

**Mini App capability.** Telegram Mini Apps support full web application UX inside the Telegram container. This means rich dashboards, charts, drag-and-drop interfaces, and complex UI — without forcing the user to leave Telegram.

**Viral distribution primitives.** Telegram supports deep links, inline sharing, forwarded messages, and group integration. A user can share their streak card, challenge link, or referral code without leaving the platform.

**Demographics match.** Telegram's core user base (CIS, Middle East, Southeast Asia, Latin America, parts of Europe) heavily overlaps with the demographics most underserved by existing productivity tools — students, freelancers, and early-career professionals in emerging markets.

**Payment infrastructure.** Telegram Stars and Telegram Payments API provide built-in monetization without external payment processors.

## 1.5 Daily Motivation System

The system motivates users daily through a layered approach:

**Layer 1 — Morning activation.** At the user's configured time, the bot sends a morning planning prompt. This message shows yesterday's score, today's pending tasks, and today's missions. It includes inline buttons for quick task completion and a deep link to the Mini App planner.

**Layer 2 — Micro-reward feedback.** Every completed action triggers an immediate visual reward in the chat or Mini App: XP animation, streak continuation confirmation, mission progress update. The gap between action and reward must be less than 500ms.

**Layer 3 — Progress accumulation.** The dashboard always shows the user's current level, XP progress to next level, active streak count, and weekly completion percentage. These numbers only go up with effort, creating a ratchet effect.

**Layer 4 — Evening reflection.** The daily summary message shows what was accomplished, XP earned, and streak status. It frames the day as a success (even partial completion) and sets up tomorrow's plan.

**Layer 5 — Recovery on miss.** If the user misses a day, the system does not punish. It sends a recovery message with a reduced daily plan, a comeback chest incentive, and framing that normalizes occasional misses.

## 1.6 The Behavioral Loop

The core loop that drives retention:

```
TRIGGER (reminder / notification / habit)
    ↓
ACTION (complete task / log habit / run focus session)
    ↓
REWARD (XP / coins / streak / mission progress / achievement)
    ↓
PROGRESS (level up / weekly stats / goal completion %)
    ↓
INVESTMENT (streak length / level height / achievement collection)
    ↓
RETURN (loss aversion on streak / curiosity on next mission / social comparison)
    ↓
[loop repeats]
```

The investment phase is critical. As the user accumulates streaks, levels, and achievements, the cost of abandoning the system increases. A user with a 45-day streak and Level 22 has significant psychological investment that makes them unlikely to stop.

This is the same retention mechanism that makes Duolingo's D365 retention approximately 8x higher than comparable language learning apps without gamification.

---

# SECTION 2 — TARGET USER SEGMENTS

## 2.1 Students (ages 16–25)

### Main problems
- Exam preparation is unstructured and driven by last-minute panic
- Study sessions lack focus — frequent phone checking and social media interruption
- No system for tracking study hours or measuring preparation progress
- Procrastination is the default behavior, especially for long-term assignments
- Difficulty breaking large academic goals (semester GPA, thesis, certification) into daily actions

### Planning behavior
- Plans are made in bursts (Sunday evening or exam week) and abandoned within 2–3 days
- Prefers short planning horizons (today, this week) over long-term structure
- Uses informal tools: phone notes, paper lists, calendar reminders
- Responsive to peer comparison and social accountability

### Motivation triggers
- Competition with peers (leaderboard)
- Visual progress toward exam readiness
- Streak as proof of consistency (shareable to study groups)
- Focus timer as anti-procrastination tool
- Achievement badges for study milestones

### Key product features they will value
- Pomodoro focus timer with study session tracking
- Exam countdown planner (AI generates study schedule from exam date)
- Study streak with daily minimum threshold
- Subject-tagged tasks for organized review
- Shareable study streak cards for social proof
- Weekly study hours analytics

## 2.2 Freelancers (ages 22–40)

### Main problems
- Multiple clients with overlapping deadlines create cognitive overload
- No separation between urgent client work and important personal development
- Inconsistent work patterns — some days 12 hours, other days 0
- Difficulty tracking how time is actually spent versus how it should be spent
- Invoicing and delivery tracking is disconnected from daily planning

### Planning behavior
- Plans around deadlines and deliverables rather than habits
- Needs project-level grouping of tasks
- Values weekly review to assess workload balance
- Prefers planning in 1–3 hour blocks rather than minute-level scheduling

### Motivation triggers
- Delivery streak (consecutive weeks of on-time deliveries)
- Weekly productivity score compared to personal average
- Focus time analytics showing deep work vs shallow work ratio
- Revenue-linked goal tracking (optional)

### Key product features they will value
- Project/client task grouping
- Weekly review with workload balance analysis
- Focus session tracking with daily/weekly totals
- Deadline-aware task prioritization
- AI weekly planner that balances client work with personal goals
- Carry-forward queue for tasks that slip

## 2.3 Entrepreneurs (ages 25–45)

### Main problems
- Too many priorities competing for limited time
- Strategic goals (quarterly OKRs, product milestones) disconnect from daily execution
- Context switching between product, sales, hiring, operations
- No clear system for evaluating whether daily actions align with quarterly goals
- Decision fatigue from constant prioritization

### Planning behavior
- Top-down planner: starts with big goals, needs help decomposing to weekly/daily actions
- Reviews progress weekly or biweekly, not daily
- Delegates tasks but needs personal execution tracking
- Values "top 3 priorities" models over long task lists

### Motivation triggers
- Goal completion percentage (quarterly/monthly progress bars)
- Strategic alignment score (are daily tasks linked to goals?)
- Weekly review insights showing execution vs plan
- AI-generated priority recommendations

### Key product features they will value
- Goal hierarchy (yearly → quarterly → monthly → weekly → daily tasks)
- AI goal decomposition (break "launch product" into weekly milestones)
- Top 3 daily priorities mode
- Weekly strategic review with alignment scoring
- Focus time tracking per goal category
- Monthly progress reports

## 2.4 Developers (ages 20–35)

### Main problems
- Deep work is frequently interrupted by meetings, Slack, and context switches
- Personal learning goals (new language, open source, side project) never get scheduled
- Sprint-like work rhythm at job does not extend to personal productivity
- Difficulty balancing job tasks with personal growth tasks

### Planning behavior
- Comfortable with structured systems (already uses Jira, Linear, GitHub Issues at work)
- Prefers minimal UI with keyboard-shortcut-like efficiency
- Values data and analytics over motivational messaging
- Plans in sprints: sets weekly goals, evaluates completion rate

### Motivation triggers
- Build streak (consecutive days of completing at least one dev task)
- Focus time analytics (deep work hours per week)
- Sprint completion rate (weekly task completion percentage)
- Achievement system for learning milestones

### Key product features they will value
- Fast task capture (bot command or single-tap in Mini App)
- Sprint-style weekly planning with completion metrics
- Focus timer optimized for deep work (50 min and 90 min modes)
- Learning goal tracking with progress indicators
- Minimal, data-dense dashboard
- GitHub-style contribution heatmap

## 2.5 General Productivity Users (ages 18–50)

### Main problems
- Wants to build better habits but lacks a system that sustains motivation
- Has tried multiple productivity apps and abandoned all of them
- Needs external motivation structure — cannot rely on discipline alone
- Morning and evening routines are aspirational but inconsistent

### Planning behavior
- Simple daily lists with 3–7 items
- Responds to reminders and nudges more than self-initiated planning
- Values emotional reward (feeling of accomplishment) over data
- Prefers pre-built templates over blank-slate planning

### Motivation triggers
- Streak preservation (loss aversion is the strongest motivator)
- Level progression (visible long-term growth)
- Daily missions that provide clear direction
- Achievement collection (completionist drive)
- Beautiful progress visualization

### Key product features they will value
- Morning/evening routine templates
- Daily missions that tell them exactly what to do
- Streak system with freeze protection
- Beautiful progress UI with animations
- Simple habit tracking (yes/no checkmarks)
- AI-generated daily plan when they don't know what to do

---

# SECTION 3 — PRODUCT CORE FEATURES

## 3.1 Task Management

### Behavior
A task is a single actionable item with a planned completion date. Tasks are the fundamental unit of productivity in the system. Every task has properties that determine its XP reward, its scheduling priority, and its relationship to higher-level goals.

### User interaction

**Creating a task:**
- Bot: user sends `/add Buy groceries tomorrow` or taps "Add task" inline button
- Mini App: taps FAB (floating action button), types title, selects date, optionally sets priority/difficulty/estimate/goal link
- Minimum required: title + date. All other fields optional with smart defaults.

**Completing a task:**
- Bot: inline button "Done" on task reminder or daily plan message
- Mini App: single tap on task checkbox
- Completion triggers: XP award animation, mission progress check, streak update, sound/haptic feedback

**Rescheduling a task:**
- Bot: inline button "Tomorrow" or "Pick date" on reminder
- Mini App: drag to different date or tap reschedule in task detail
- Rescheduled tasks are tagged internally for carry-forward ratio analytics

**Recurring tasks:**
- User sets recurrence: daily, weekdays, weekly, biweekly, monthly, custom
- System generates next occurrence after completion or day-end
- Recurring tasks maintain their own streak (consecutive completions)

### Internal logic

```
Task {
  id: UUID
  user_id: UUID
  title: string (max 200 chars)
  notes: string (max 2000 chars, optional)
  planned_date: date
  due_date: date (optional, for hard deadlines)
  priority: enum [low, medium, high, critical]
  difficulty: enum [trivial, easy, medium, hard, epic]
  estimated_minutes: int (optional, default null)
  category_id: UUID (optional)
  goal_id: UUID (optional, links to goal hierarchy)
  recurrence_rule: string (RRULE format, optional)
  status: enum [pending, completed, skipped, archived]
  completed_at: timestamp (null until completed)
  created_at: timestamp
  source: enum [bot, mini_app, ai_plan]
  xp_awarded: int (calculated at completion)
}
```

**XP calculation at completion:**

```
base_xp = difficulty_map[task.difficulty]
  // trivial: 5, easy: 10, medium: 20, hard: 35, epic: 50

multipliers:
  if task.priority == critical: × 1.5
  if completed on planned_date (same-day bonus): × 1.2
  if linked to active goal: × 1.15
  if completed during focus session: × 1.25

final_xp = floor(base_xp × product(applicable_multipliers))
daily_cap: 500 XP from tasks (prevents farming)
```

**Overdue handling:**
- Tasks past planned_date but not completed: auto-surfaced in "carry forward" tray
- After 3 days overdue: bot sends nudge "You have 4 overdue tasks. Reschedule or complete?"
- After 7 days overdue: task auto-suggested for archival
- Overdue tasks reduce planning accuracy metric

### UX expectations
- Task creation must complete in under 3 seconds (bot) or 5 seconds (Mini App with all fields)
- Completion animation must play within 200ms of tap
- Task list must load in under 1 second on 3G connection
- Swipe gestures: right to complete, left to reschedule
- Completed tasks show strikethrough with XP pill badge

## 3.2 Habit Tracking

### Behavior
A habit is a recurring behavior the user wants to build or maintain. Unlike tasks, habits do not have a completion date — they have a frequency and a tracking mechanism. Habits generate streaks, which are the strongest retention mechanism in the system.

### User interaction

**Creating a habit:**
- Bot: `/habit Read 30 minutes daily` parsed into habit with duration target
- Mini App: dedicated habit creation screen with type selector, frequency, reminder time, icon

**Logging a habit:**
- Bot: inline button on daily habit reminder — "Done", "Skip", "Partial"
- Mini App: single tap on habit card (yes/no type), counter increment (count type), or duration entry (time type)

**Viewing habit performance:**
- Mini App: heatmap calendar (GitHub-style), streak counter, consistency percentage, best streak record

### Supported habit types

| Type | Input | Example | Completion rule |
|------|-------|---------|-----------------|
| Yes/No | Single tap | "Meditate" | Logged = complete |
| Count | Number entry | "Drink 8 glasses of water" | Count >= target |
| Duration | Minutes entry | "Read for 30 minutes" | Minutes >= target |
| Avoid | Single tap for success | "No social media before noon" | Logged as maintained |

### Internal logic

```
Habit {
  id: UUID
  user_id: UUID
  title: string
  type: enum [yes_no, count, duration, avoid]
  target_value: int (1 for yes/no, count target, minutes target)
  frequency: enum [daily, weekdays, mon_wed_fri, tue_thu_sat, weekly, custom]
  frequency_days: int[] (for custom, e.g. [1,3,5] = Mon/Wed/Fri)
  reminder_time: time (optional)
  icon: string (emoji or icon id)
  color: string (hex)
  status: enum [active, paused, archived]
  created_at: timestamp
}

HabitLog {
  id: UUID
  habit_id: UUID
  user_id: UUID
  date: date
  value: int (1 for yes/no, count for count, minutes for duration)
  completed: boolean (value >= habit.target_value)
  logged_at: timestamp
  source: enum [bot, mini_app]
}
```

**Streak calculation:**
- Streak = count of consecutive scheduled days where `completed = true`
- If a scheduled day has no log by end of day → streak breaks (unless freeze token used)
- Paused habits do not break streak (pause days excluded from schedule)
- Streak freeze: consumes 1 freeze token, preserves streak for 1 missed day, max 1 freeze per 7 days for free users, max 2 per 7 days for premium

**XP from habits:**

```
base_xp = type_map[habit.type]
  // yes_no: 5, count: 8, duration: 10, avoid: 7

streak_multiplier:
  streak 1-6: × 1.0
  streak 7-13: × 1.1
  streak 14-29: × 1.2
  streak 30-59: × 1.3
  streak 60-89: × 1.4
  streak 90+: × 1.5

daily_habit_xp_cap: 100 XP
```

### UX expectations
- Habit logging must be completable in 1 tap (yes/no) or 2 taps (count/duration entry + confirm)
- Heatmap must be visible on habit detail screen without scrolling
- Streak number must be prominently displayed on every habit card
- Streak break must show recovery option immediately (not just a loss message)
- Habit reminder in bot must include inline "Done" button — no need to open Mini App

## 3.3 Focus Sessions

### Behavior
A focus session is a timed, distraction-free work period. The user starts a timer, optionally links it to a task, works until the timer ends, and receives XP based on duration and completion. Focus sessions are the primary mechanism for tracking deep work time.

### User interaction

**Starting a session:**
- Bot: `/focus 25` starts a 25-minute session. `/focus 50 Write blog post` starts a 50-minute session linked to a task.
- Mini App: Focus screen with mode selector (25 / 50 / 90 / custom minutes), optional task link, start button.

**During a session:**
- Mini App shows: countdown timer, linked task name, motivational micro-copy, pause button
- Bot sends: nothing during session (no interruption). If user messages bot, bot responds "Focus session active. {X} minutes remaining."

**Ending a session:**
- Timer completion triggers: celebration animation, XP award, session summary
- Early quit (user stops before timer): partial XP (proportional to time completed, minimum 50% duration required)
- Summary shows: duration, XP earned, linked task status, daily focus total

**Session summary prompt (bot):**
After session ends, bot sends:
```
Focus session complete!
Duration: 50 min
XP earned: +35 XP
Daily focus total: 1h 15m

[Mark task done] [Start another] [Take a break]
```

### Internal logic

```
FocusSession {
  id: UUID
  user_id: UUID
  task_id: UUID (optional)
  planned_duration: int (minutes)
  actual_duration: int (minutes, calculated from start/end)
  mode: enum [pomodoro_25, deep_50, ultra_90, custom]
  status: enum [active, completed, abandoned]
  started_at: timestamp
  ended_at: timestamp (null while active)
  xp_awarded: int
}
```

**XP calculation:**

```
if actual_duration < planned_duration × 0.5:
  xp = 0 (session too short, counts as abandoned)
elif actual_duration < planned_duration:
  xp = floor(base_xp × (actual_duration / planned_duration))
else:
  xp = base_xp

base_xp by mode:
  pomodoro_25: 15
  deep_50: 30
  ultra_90: 50
  custom: floor(planned_minutes × 0.6)

if linked task completed after session: bonus +10 XP
daily_focus_xp_cap: 200 XP
```

### UX expectations
- Timer must continue counting even if user switches Telegram chats (Mini App background state handling)
- Timer screen must be minimal: large countdown number, task name, pause button, nothing else
- Session completion animation must feel rewarding (confetti, XP popup, sound if enabled)
- Break timer option after session completion (5 min short break, 15 min long break)
- Daily focus stats visible on home screen: total minutes today, session count, comparison to weekly average

## 3.4 Reminders

### Behavior
Reminders are proactive bot messages that prompt the user to take a specific action. They are the primary re-engagement mechanism. Every reminder must be actionable — it must include inline buttons that allow the user to complete the action without opening the Mini App.

### Reminder types and timing

| Type | Default time | Content | Buttons |
|------|-------------|---------|---------|
| Morning plan | 08:00 user local | Today's top 3 tasks, habits due, missions | [Open planner] [AI plan] [Quick add] |
| Task reminder | User-set or 2h before due | Task title + deadline | [Done] [Focus] [Tomorrow] |
| Habit reminder | User-set per habit | Habit name + current streak | [Done] [Skip] [Open habits] |
| Focus suggestion | 14:00 user local | "Good time for a focus session?" | [25 min] [50 min] [Not now] |
| Evening summary | 21:00 user local | Day score, tasks done, XP earned, streak | [Tomorrow's plan] [Progress] |
| Weekly review | Sunday 18:00 user local | Week stats, goal progress | [Open review] [Skip] |
| Comeback | After 48h inactivity | Recovery message + incentive | [Quick plan] [Small win] |
| Streak warning | 20:00 if no activity | "Your {X}-day streak needs 1 action" | [Quick task] [Log habit] |

### Internal logic — Reminder Engine

```
ReminderRule {
  id: UUID
  user_id: UUID
  type: enum [morning, task, habit, focus_suggest, evening, weekly, comeback, streak_warn]
  time: time (user local timezone)
  enabled: boolean
  last_sent: timestamp
  cooldown_minutes: int (minimum gap between sends of same type)
}
```

**Anti-spam rules:**
- Maximum 6 bot messages per day per user (across all reminder types)
- If multiple reminders collide within 30 minutes: batch into digest message
- Quiet hours: no messages between 23:00–07:00 user local time (configurable)
- If user has not read last 3 bot messages (Telegram read receipts): reduce frequency by 50%
- Comeback messages: max 1 per 48 hours, stop after 3 unanswered

**Relevance-based prioritization:**
When daily message budget is reached, prioritize:
1. Streak warning (loss aversion — highest retention impact)
2. Task with hard deadline today
3. Habit reminder for active streak > 7 days
4. Morning plan
5. Evening summary
6. Focus suggestion

### UX expectations
- Every reminder must be completable with inline buttons — zero-friction completion
- Task reminder "Done" button must complete the task and show XP in the same message (edit original message with result)
- Messages must feel personal, not robotic — use user's name, reference specific tasks/habits
- Tone: encouraging, not nagging. "You're 1 task away from a perfect day" not "You have incomplete tasks"

## 3.5 Goal Hierarchy

### Behavior
Goals provide the "why" behind daily tasks. The system supports a four-level hierarchy:

```
Yearly Goal
  └── Monthly Goal (milestone)
       └── Weekly Objective
            └── Daily Tasks
```

Each level rolls up progress to the parent. Completing daily tasks advances weekly objectives, which advance monthly goals, which advance yearly goals. This creates a direct visible link between today's actions and long-term aspirations.

### User interaction

**Creating a goal:**
- Mini App only (too complex for bot). Goal creation wizard:
  1. Category selection (study, work, business, health, finance, personal, creative)
  2. Goal title and description
  3. Target date (monthly/yearly)
  4. Success criteria (measurable outcome)
  5. AI decomposition option: "Break this down into monthly milestones"

**Viewing goal progress:**
- Mini App Progress screen: goal cards with progress percentage, linked task completion rate, time remaining
- Goal detail: shows sub-goals, linked tasks, completion timeline

**AI goal decomposition:**
User enters: "Pass AWS Solutions Architect exam by June"
AI generates:
- Monthly milestones: study domains, practice tests, review cycles
- Weekly objectives: specific chapters, labs, quizzes
- Suggested daily tasks: study blocks with topics
User reviews and applies (one tap to create all suggested entities)

### Internal logic

```
Goal {
  id: UUID
  user_id: UUID
  parent_goal_id: UUID (null for top-level)
  title: string
  description: string (optional)
  category: enum [study, work, business, health, finance, personal, creative]
  level: enum [yearly, monthly, weekly]
  target_date: date
  success_criteria: string (optional)
  progress_percent: int (0–100, calculated)
  status: enum [active, completed, abandoned, paused]
  created_at: timestamp
}
```

**Progress calculation:**
- If goal has sub-goals: progress = average(sub_goal.progress_percent)
- If goal has only linked tasks: progress = (completed_tasks / total_tasks) × 100
- If goal has both: progress = weighted average (sub-goals 60%, tasks 40%)
- Completed sub-goal = 100%, abandoned sub-goal excluded from calculation

**Dormant goal detection:**
- If a goal has no linked task completed in 14 days → mark as "dormant"
- Bot sends dormant goal alert: "Your goal '{title}' hasn't had activity in 2 weeks. [Create task] [Pause goal] [Get AI plan]"

### UX expectations
- Goal progress must update in real-time when a linked task is completed
- Progress percentage must be visible on goal card without opening detail
- Goal hierarchy must be navigable: tap yearly goal → see monthly milestones → see weekly objectives → see tasks
- AI decomposition results must be editable before applying (user can remove/modify suggestions)

## 3.6 Analytics and Progress Insights

### Behavior
Analytics transform raw activity data into actionable insights. The system provides three layers of analytics: real-time dashboard, periodic summaries, and AI-generated insights.

### Metrics tracked

| Metric | Calculation | Display |
|--------|------------|---------|
| Daily completion rate | completed_tasks / planned_tasks × 100 | Percentage + trend arrow |
| Weekly active days | days with at least 1 meaningful action | Count out of 7 |
| Focus minutes | sum(focus_session.actual_duration) | Daily, weekly, monthly totals |
| Habit consistency | completed_days / scheduled_days × 100 | Per habit and overall |
| Planning accuracy | tasks_completed_on_planned_date / total_tasks | Percentage |
| Carry-forward ratio | rescheduled_tasks / total_tasks | Percentage (lower is better) |
| Streak records | max consecutive days per type | Current + best ever |
| Productivity time windows | completion timestamps clustered | "Your peak hours: 9-11 AM" |
| Goal alignment | tasks linked to goals / total tasks | Percentage |

### Output layers

**Real-time (Mini App dashboard):**
- Today's score (0–100 based on planned vs completed)
- XP progress bar to next level
- Active streak count
- Weekly completion trend (mini bar chart, last 7 days)

**Daily summary (bot message, evening):**
- Tasks: X completed, Y remaining
- Habits: X/Y logged
- Focus: X minutes
- XP earned today: +XX
- Streak status: maintained / at risk
- Tone: celebratory if good day, encouraging if partial, recovery-focused if missed

**Weekly review (Mini App, dedicated screen):**
- Completion rate vs last week
- Most productive day
- Focus time distribution by category
- Habit consistency per habit
- Goal progress changes
- AI insight: "You complete 40% more tasks when you use the morning planner. Consider planning every morning."
- Action items for next week (AI-generated)

**Monthly review (Mini App, premium feature):**
- Month-over-month trends
- Achievement highlights
- Goal progress summary
- Habit heatmap for the month
- Focus time total and comparison
- AI coaching message with recommendations

### UX expectations
- Dashboard must load within 1.5 seconds including charts
- Charts must be interactive (tap bar to see daily detail)
- Weekly review must be completable in under 3 minutes
- AI insights must be specific and actionable, not generic ("Focus more" is unacceptable, "Schedule a 50-min focus session for your 'AWS Study' tasks on Tuesday and Thursday mornings" is acceptable)

---

# SECTION 4 — TELEGRAM UX MODEL

## 4.1 Hybrid Architecture

The platform operates as a **Telegram Bot + Telegram Mini App hybrid**. This is not a convenience choice — it is a structural requirement. Neither component alone can deliver the retention and UX depth needed for 1M+ scale.

### Why pure bot fails
A pure bot interface can handle quick actions (add task, complete task, check streak) but cannot deliver:
- Rich dashboard with charts and progress visualization
- Drag-and-drop task reordering
- Complex habit heatmaps
- Multi-step goal creation wizards
- Settings screens with many configuration options
- Reward inventory and cosmetic shop

Bot UI is limited to: text messages, inline buttons (max 8 per row, max 100 per message), and inline keyboards. This is insufficient for a productivity power tool.

### Why pure Mini App fails
A pure Mini App can deliver rich UX but cannot deliver:
- Proactive notifications (Mini App cannot send push notifications independently)
- Quick capture without opening the app (Mini App requires user to navigate to it)
- Daily re-engagement (user must remember to open the Mini App)
- Quick-response actions (opening Mini App takes 2–3 seconds, bot message is instant)

### Why hybrid works
The hybrid model creates a **notification-driven engagement loop with depth-on-demand**:

1. Bot sends reminder → user sees it in chat list (zero friction)
2. User completes quick action via inline button (1 tap)
3. For deeper engagement, user taps "Open Dashboard" → Mini App opens (rich UX)
4. Mini App work triggers events → bot confirms results later

The bot is the **engagement engine**. The Mini App is the **value delivery engine**.

## 4.2 Bot Responsibilities

### Onboarding
- Welcome message when user starts bot
- 3-step onboarding: select segment → create first task → set reminder time
- Deep link to Mini App for extended setup

### Quick capture
- `/add [task title] [date]` — create task from chat
- `/habit [habit name] [frequency]` — create habit from chat
- `/focus [minutes]` — start focus session
- `/today` — show today's plan with inline completion buttons
- `/stats` — show quick stats (streak, level, daily XP)

### Reminders and notifications
- All reminder types from Section 3.4
- Achievement unlock notifications
- Level-up celebrations
- Streak milestone messages (7, 14, 30, 60, 90, 180, 365 days)
- Mission completion notifications

### Daily lifecycle messages
- Morning: planning prompt
- Midday: focus suggestion (if no focus session today)
- Evening: daily summary
- (All times configurable per user)

### Re-engagement
- Comeback messages after inactivity
- "Your friend [name] just hit Level 10!" (if referral connection exists)
- Weekly review reminder
- New feature announcements

### Callback handling
- All inline button presses processed as Telegram callback queries
- Callback response must edit original message to show result (not send new message)
- Callback timeout handling: if processing takes > 3 seconds, show "Processing..." answer first

## 4.3 Mini App Responsibilities

### Dashboard (Home screen)
- Today's productivity score
- Top 3 priority tasks with completion toggles
- Active habits due today
- Current streak display
- Daily mission progress (3 missions)
- AI suggestion card ("Based on your schedule, focus on X first")
- Quick-start focus button

### Planner
- Calendar date selector (swipeable week view)
- Daily and weekly tab toggle
- Task list with drag-and-drop reordering
- Add task FAB with quick-add and detailed-add modes
- Filter by: category, priority, goal, status
- Carry-forward tray: overdue tasks from previous days
- Batch actions: complete multiple, reschedule multiple

### Habit management
- Habit cards with today's status and streak count
- One-tap logging for all habit types
- Habit detail: heatmap, statistics, streak history, edit
- Add habit with templates (popular habits pre-configured)
- Reorder habits by priority

### Focus interface
- Mode selector with time presets
- Full-screen timer with minimal UI
- Task linker (optional)
- Session history with daily/weekly totals
- Break timer between sessions

### Progress and analytics
- XP bar and level indicator
- Achievement gallery with locked/unlocked states
- Weekly stats dashboard with charts
- Monthly heatmap
- Goal progress overview
- Performance insights (AI-generated)

### Profile
- Avatar (Telegram profile photo)
- Current title (earned through achievements)
- Level and XP display
- Coin wallet balance
- Cosmetic inventory (themes, badge frames, title collection)
- Streak freeze token count
- Premium status and management
- Settings: timezone, reminder times, notification preferences, theme

### AI planning interface
- Prompt input: "Plan my week" / "Help me study for X" / "I missed 3 days, help me catch up"
- Context display: available time, active goals, pending tasks
- Plan preview: structured task/time-block cards
- Apply/edit/discard buttons
- History of generated plans

### Settings
- Timezone (auto-detected, manually adjustable)
- Reminder schedule per type
- Quiet hours
- Theme (light/dark/system)
- Language
- Data export
- Account deletion

## 4.4 Technical interaction model

```
User ←→ Telegram Client
         ├── Bot messages (webhook → Backend → Telegram Bot API)
         └── Mini App (HTTPS → Frontend → Backend API)

Bot → Backend:
  - Webhook receives updates (messages, callbacks, inline queries)
  - Backend processes, updates DB, returns response
  - Backend sends proactive messages via Bot API (reminders, notifications)

Mini App → Backend:
  - Frontend loaded as Telegram Mini App (WebApp)
  - Auth via Telegram initData verification (HMAC-SHA256)
  - REST API calls for all CRUD operations
  - WebSocket for real-time updates (timer sync, XP animations)

Shared state:
  - Same PostgreSQL database
  - Same Redis for sessions/cache
  - Same event bus for cross-concern updates
  - Action in bot immediately reflected in Mini App and vice versa
```

---

# SECTION 5 — USER JOURNEY

## 5.1 Onboarding (Day 0, minutes 0–5)

### Entry point
User clicks a deep link (from referral, social share, or direct search). Telegram opens the bot chat.

### Step 1 — Welcome (bot message)
```
Welcome to PlanQuest!

I'm your productivity companion. I help you plan your day,
build habits, and level up your life.

What describes you best?

[Student] [Freelancer] [Entrepreneur] [Developer] [Other]
```

User taps segment button. System stores segment for personalization.

### Step 2 — First task (bot message)
```
Great! Let's create your first task.

What's one thing you want to accomplish today?
Just type it — for example: "Read chapter 3" or "Write project proposal"
```

User types task title. System creates task with today's date, medium priority, medium difficulty.

```
Task created: "Read chapter 3"
Planned for today.

+10 XP for your first task!

[Open planner] [Add another task] [Set up habits]
```

### Step 3 — Reminder setup (bot message)
```
When should I send your morning planning message?

[7:00] [8:00] [9:00] [10:00] [Custom]
```

User selects time. Onboarding complete.

```
You're all set!

Tomorrow at 8:00 AM I'll send your daily plan.
Complete tasks, build streaks, and level up!

Your current stats:
Level 1 | 10 XP | 0-day streak

[Open Dashboard] — see your full planner
```

### Activation metrics
- Onboarding completion target: > 70% of users who press Start
- First task creation target: > 60% of users who complete onboarding
- Time to complete onboarding: < 2 minutes

## 5.2 First Task Completion (Day 0–1)

### Trigger
Morning reminder or user re-opens bot chat.

### Flow
1. User sees their task in morning plan or directly in chat history
2. User taps "Done" inline button
3. Bot edits message:
```
✓ Read chapter 3 — Complete!
+20 XP earned
Level 1 → 30/100 XP

[Add next task] [Open planner]
```

### Emotional impact
First completion must feel significant. XP animation, congratulatory copy. This is the moment the user first experiences the reward loop.

## 5.3 First Habit (Day 1–3)

### Trigger
After 2–3 task completions, bot suggests habits:
```
You've been completing tasks consistently!

Want to build a daily habit? Here are popular ones:

[Read 30 min] [Exercise] [Meditate] [Journal] [Custom]
```

### Flow
1. User selects or creates a habit
2. System creates habit with daily frequency
3. Next day, bot includes habit in morning plan
4. User logs habit via inline button
5. Streak counter appears: "Day 1"

## 5.4 First Streak (Day 3–7)

### Trigger
User maintains activity for 3+ consecutive days.

### Milestones
- Day 3: "3-day streak! You're building momentum. +5 bonus XP"
- Day 7: "1 WEEK STREAK! Achievement unlocked: 'First Week'. +50 bonus XP, +20 coins. [Share card]"

### Psychology
By day 7, loss aversion activates. The user now has something to lose (their streak), which is a stronger motivator than something to gain (XP). This is the retention inflection point.

## 5.5 Daily Planner Loop (ongoing)

The daily loop is the core engagement cycle:

```
08:00 — Morning plan arrives (bot)
         User reviews tasks, habits, missions
         User completes quick items via bot buttons

10:00 — User opens Mini App for detailed planning
         Reorders tasks, adds new ones, checks goal progress

14:00 — Focus suggestion arrives (bot)
         User starts 50-min focus session
         Completes linked task

18:00 — User logs remaining habits via bot buttons

21:00 — Evening summary arrives (bot)
         User sees day score, XP earned, streak status
         User taps "Tomorrow's plan" to prep next day
```

### Key design principle
The user should never need to "remember" to use the system. The system reaches out to the user at the right times with the right actions. The user's job is to respond, not to initiate.

## 5.6 Weekly Review Loop (weekly)

### Trigger
Sunday evening, bot sends weekly review prompt.

### Flow (Mini App)
1. Week overview: tasks completed, habits logged, focus time, XP earned
2. Goal progress: which goals advanced, which stalled
3. AI insight: "Your completion rate is highest on Tuesday and Wednesday. Consider scheduling your hardest tasks on those days."
4. Next week planning: carry-forward tasks, set weekly objectives, adjust habits
5. Review completion: +30 XP, weekly review achievement progress

### Retention impact
Weekly review creates a ritual. Users who complete weekly review have 2.3x higher D30 retention than users who skip it (based on comparable product data).

## 5.7 Long-term Engagement Loop (month 2+)

### What keeps users after novelty fades

1. **Streak investment** — A 45-day streak has 45 days of accumulated psychological value. Breaking it feels like real loss.

2. **Level identity** — A Level 25 user sees themselves as "someone who uses PlanQuest." The tool becomes part of their identity.

3. **Achievement collection** — Completionist users pursue locked achievements. "92% complete" drives them to 100%.

4. **Goal progress** — Long-term goals (yearly, quarterly) create ongoing reason to continue. Abandoning the tool means abandoning visible goal progress.

5. **Social accountability** — Shared challenges, friend streaks, and accountability groups create external commitment devices.

6. **Evolving missions** — Mission system generates new challenges based on user behavior, preventing repetitiveness.

7. **Seasonal events** — Time-limited challenges, special achievements, and themed missions create urgency and novelty.

---

# SECTION 6 — GAMIFICATION MODEL

## 6.1 XP System

### Philosophy
XP is the universal measure of productive effort. Every meaningful action earns XP. XP accumulates into levels, which serve as the primary visible progression marker.

### XP sources and base values

| Action | Base XP | Notes |
|--------|---------|-------|
| Task: trivial | 5 | Quick items |
| Task: easy | 10 | Standard tasks |
| Task: medium | 20 | Moderate effort |
| Task: hard | 35 | Significant effort |
| Task: epic | 50 | Major deliverable |
| Habit: yes/no | 5 | Simple check |
| Habit: count-based | 8 | Counted target |
| Habit: duration | 10 | Time-based |
| Habit: avoid | 7 | Resistance-based |
| Focus: 25 min | 15 | Pomodoro |
| Focus: 50 min | 30 | Deep work |
| Focus: 90 min | 50 | Ultra focus |
| Daily review complete | 10 | Morning plan engagement |
| Weekly review complete | 30 | Strategic reflection |
| Mission: daily | 15–25 | Per mission |
| Mission: weekly | 40–80 | Per mission |
| Achievement unlock | varies | 25–200 per achievement |
| Referral activation | 100 | Invited user completes onboarding |

### XP Multipliers

| Multiplier | Condition | Value |
|-----------|-----------|-------|
| Same-day execution | Task completed on planned_date | × 1.2 |
| Goal-linked | Task linked to active goal | × 1.15 |
| Focus completion | Task completed during focus session | × 1.25 |
| Priority boost | Critical priority task | × 1.5 |
| Streak multiplier | Active streak 7+ days | × 1.1 |
| Streak multiplier | Active streak 30+ days | × 1.2 |
| Streak multiplier | Active streak 90+ days | × 1.3 |
| Combo | Multiple multipliers stack | Multiplicative |

### Anti-abuse guardrails

| Rule | Limit | Purpose |
|------|-------|---------|
| Daily task XP cap | 500 | Prevents creating 100 trivial tasks |
| Daily habit XP cap | 100 | Prevents creating 20 dummy habits |
| Daily focus XP cap | 200 | Prevents running fake sessions |
| Minimum task title length | 3 characters | Prevents empty task farming |
| Duplicate task detection | Same title within 24h flagged | Prevents copy-paste farming |
| Rapid completion detection | > 10 tasks completed in 5 min triggers review | Catches bulk-create-complete |
| Focus minimum duration | 50% of planned time | Prevents start-stop farming |

## 6.2 Levels

### Progression curve

The XP required for each level follows a modified exponential curve that starts fast and gradually slows:

```
Level 1: 0 XP (starting level)
Level 2: 100 XP (achievable day 1)
Level 3: 250 XP (day 2)
Level 4: 450 XP (day 3)
Level 5: 700 XP (end of week 1 for engaged user)
Level 10: 3,000 XP (week 2–3)
Level 15: 8,000 XP (month 1)
Level 20: 18,000 XP (month 2)
Level 25: 35,000 XP (month 3)
Level 30: 60,000 XP (month 4–5)
Level 40: 150,000 XP (month 8–10)
Level 50: 350,000 XP (month 14–18)
Level 100: 2,000,000 XP (multi-year power user)

Formula: required_xp(level) = floor(50 × level^1.8)
```

### Level-up rewards

| Level | Reward |
|-------|--------|
| Every level | +coins (level × 10) |
| Level 5 | Bronze badge frame, title "Beginner Planner" |
| Level 10 | Silver badge frame, title "Rising Star", 1 chest key |
| Level 15 | Title "Consistent Worker", 2 streak freeze tokens |
| Level 20 | Gold badge frame, title "Productivity Pro", 2 chest keys |
| Level 25 | Title "Goal Crusher", exclusive theme |
| Level 30 | Platinum badge frame, title "Deep Worker", 3 chest keys |
| Level 40 | Diamond badge frame, title "Legendary Planner" |
| Level 50 | Title "Master of Productivity", unique profile animation |

### Level-up notification (bot)
```
LEVEL UP!

You've reached Level 15: "Consistent Worker"

Rewards earned:
+150 coins
+2 streak freeze tokens
New title unlocked: "Consistent Worker"

[View profile] [Share level-up card]
```

## 6.3 Coin Economy

### Earning coins

| Source | Amount |
|--------|--------|
| Level-up | level × 10 |
| Daily mission set complete (3/3) | 15 |
| Weekly mission set complete (4/4) | 50 |
| Achievement unlock | 10–100 (varies) |
| Chest loot | 5–50 (random) |
| 7-day streak milestone | 25 |
| 30-day streak milestone | 100 |
| Referral activation | 50 |
| Comeback success (return after 3+ day absence, complete 3 tasks) | 30 |

### Spending coins

| Item | Cost | Effect |
|------|------|--------|
| Streak freeze token | 50 | Preserves streak for 1 missed day |
| Profile theme | 100–300 | Visual customization |
| Badge frame | 150–500 | Profile border decoration |
| Title unlock | 200–1000 | Display title options |
| Chest key | 75 | Opens a reward chest |
| AI bonus generation | 100 | 1 extra AI plan generation |
| Premium 3-day trial | 500 | Temporary premium access |

### Economy balance principles

1. **Deficit economy**: Spending options must always exceed earning rate. Users should feel coins are scarce enough to value, but abundant enough to be useful.
2. **No productivity purchases**: Coins cannot buy XP, levels, or task completions. Productivity must be earned.
3. **Cosmetic priority**: Most expensive items are cosmetic (themes, frames, titles). Functional items (freeze tokens, AI generations) are cheaper.
4. **Inflation control**: As user levels increase, coin earning rate increases. New spending options at higher levels absorb surplus.
5. **Premium overlap**: Some items purchasable with coins OR included in premium subscription. Premium users still earn and spend coins for exclusive items.

## 6.4 Streak System

### Streak types

| Streak | Qualification | Display |
|--------|--------------|---------|
| Activity streak | At least 1 meaningful action per day | Main streak counter, flame icon |
| Habit streak | Specific habit completed on all scheduled days | Per-habit counter |
| Focus streak | At least 1 focus session per day | Focus screen counter |
| Planning streak | Morning plan reviewed (opened morning message or Mini App planner) | Planner screen counter |

### Activity streak rules
- **Qualification**: 1 meaningful action = task completed OR habit logged OR focus session completed (minimum 50% duration) OR weekly review completed
- **Day boundary**: user's timezone, midnight to midnight
- **Grace period**: none for free users. Premium users get 1 automatic grace per 30 days.
- **Streak freeze**: costs 50 coins OR 1 freeze token. Manually activated before day ends, or auto-activated if user has "auto-freeze" enabled (premium). Maximum 1 freeze per 7 days (free), 2 per 7 days (premium).

### Streak recovery mechanics
When a streak breaks:
1. Immediate bot message: "Your {X}-day streak ended. But you can come back stronger."
2. Comeback chest offered: complete 3 actions in next 2 days → receive chest with coins + XP bonus
3. "Phoenix" achievement progress: tracks successful comebacks
4. No shaming language — framing is always recovery-oriented

### Streak milestones and rewards

| Streak days | Reward | Message |
|-------------|--------|---------|
| 3 | +5 bonus XP daily | "Momentum building!" |
| 7 | +25 coins, share card | "1 week! Incredible discipline." |
| 14 | +50 coins, badge | "2 weeks of consistency." |
| 30 | +100 coins, title, share card | "30 days. You've built a real habit." |
| 60 | +200 coins, exclusive frame | "60 days. Top 5% of users." |
| 90 | +300 coins, achievement | "90 days. Legendary consistency." |
| 180 | +500 coins, unique theme | "Half a year. Extraordinary." |
| 365 | +1000 coins, legendary title, unique animation | "One year. Master of discipline." |

## 6.5 Missions

### Daily missions
Every day at midnight (user's timezone), the system generates 3 daily missions tailored to the user.

**Mission generation algorithm:**
1. Mission 1 (guaranteed easy): always achievable — e.g., "Complete 1 task" or "Log 1 habit"
2. Mission 2 (behavior-shaping): encourages underused feature — e.g., if user never uses focus, "Start a focus session"
3. Mission 3 (stretch): slightly above user's recent average — e.g., if user averages 3 tasks/day, "Complete 4 tasks"

**Daily mission rewards:**
- Per mission: 15–25 XP (scaling with difficulty)
- All 3 complete: +15 bonus coins, bonus XP animation
- Mission set completion tracked for weekly stats

### Weekly missions
Generated every Monday. 4 missions spanning the week.

**Examples:**
- "Complete 15 tasks this week" (based on user's average)
- "Maintain habit streak for 7 days"
- "Log 90 minutes of focus time"
- "Complete a weekly review"

**Weekly mission rewards:**
- Per mission: 40–80 XP
- All 4 complete: +50 coins, weekly chest

### Mission selection rules
- Never generate impossible missions (check user's task count, active habits, etc.)
- Never repeat exact same mission configuration two days in a row
- Difficulty adapts: if user completes all 3 daily missions for 5 consecutive days, next day's missions are slightly harder
- If user fails missions 3 days in a row, next day's missions are slightly easier
- Missions must use features the user has set up (don't require focus session if user has never used focus — instead suggest "Try your first focus session")

## 6.6 Achievements

### Achievement categories and examples

**Starter achievements:**
| Name | Requirement | XP | Coins |
|------|------------|-----|-------|
| First Step | Complete first task | 25 | 10 |
| Habit Seed | Create first habit | 25 | 10 |
| Focus Initiate | Complete first focus session | 25 | 10 |
| Planning Mind | Open planner for first time | 15 | 5 |
| Goal Setter | Create first goal | 25 | 10 |

**Consistency achievements:**
| Name | Requirement | XP | Coins |
|------|------------|-----|-------|
| 7-Day Warrior | 7-day activity streak | 50 | 25 |
| Iron Will | 30-day activity streak | 150 | 100 |
| Unstoppable | 90-day activity streak | 300 | 200 |
| Year of Power | 365-day activity streak | 1000 | 500 |
| Habit Machine | Any habit streak reaches 30 | 100 | 50 |

**Planner mastery achievements:**
| Name | Requirement | XP | Coins |
|------|------------|-----|-------|
| Task Centurion | 100 tasks completed | 100 | 50 |
| Task Commander | 500 tasks completed | 200 | 100 |
| Planning Accuracy | 80%+ on-time completion for 4 weeks | 150 | 75 |
| Zero Carry Forward | Complete all daily tasks for 5 consecutive days | 100 | 50 |

**Focus achievements:**
| Name | Requirement | XP | Coins |
|------|------------|-----|-------|
| Deep Worker | 10 hours total focus time | 100 | 50 |
| Focus Master | 50 hours total focus time | 200 | 100 |
| Marathon Mind | Complete a 90-minute focus session | 75 | 30 |
| Focus Streak 7 | 7-day focus streak | 100 | 50 |

**Goal achievements:**
| Name | Requirement | XP | Coins |
|------|------------|-----|-------|
| Goal Achiever | Complete first goal | 100 | 50 |
| Quarterly Champion | Complete a monthly goal | 150 | 75 |
| Vision Realized | Complete a yearly goal | 500 | 250 |

**Comeback achievements:**
| Name | Requirement | XP | Coins |
|------|------------|-----|-------|
| Phoenix | Return after 3+ day absence and complete 3 tasks | 50 | 30 |
| Resilient | 3 successful comebacks | 100 | 50 |
| Never Give Up | 10 successful comebacks | 200 | 100 |

**Social achievements:**
| Name | Requirement | XP | Coins |
|------|------------|-----|-------|
| Recruiter | First referral activation | 100 | 50 |
| Team Builder | 5 referral activations | 200 | 100 |
| Challenge Accepted | Complete first social challenge | 75 | 30 |

### Achievement system rules
- All achievements are tracked in real-time via event system
- Progress is visible: "Task Centurion: 73/100 tasks"
- Unlock triggers bot notification with share option
- Achievements are permanent — never revoked
- Hidden achievements exist for surprise moments (e.g., "Night Owl" — complete task between 2–4 AM)

## 6.7 Reward Chests

### Chest types

| Chest | Source | Contents |
|-------|--------|----------|
| Daily chest | Complete all 3 daily missions | 10–30 coins, 5–15 bonus XP |
| Weekly chest | Complete all 4 weekly missions | 30–100 coins, cosmetic chance (10%) |
| Streak chest | Reach streak milestone (7, 14, 30, 60, 90) | 25–200 coins, freeze token chance (20%), cosmetic chance (15%) |
| Comeback chest | Return and complete 3 tasks after absence | 20–50 coins, 1 freeze token |
| Level chest | Every 5 levels | 50–200 coins, cosmetic item (guaranteed at levels 10, 20, 30, 40, 50) |

### Chest opening mechanic
- Chests appear in inventory
- Basic chests open immediately (tap to reveal)
- Premium chests require a key (earned through level-ups or purchased with coins)
- Opening animation: satisfying reveal sequence (1–2 seconds)
- Loot displayed with rarity indicators (common, rare, epic)

### Loot table design principles
- No real-money value in loot (prevents gambling classification)
- All items are cosmetic or minor utility (freeze tokens)
- Duplicate protection: if user already owns a cosmetic, coins are awarded instead
- Transparency: loot probabilities visible in settings/FAQ

---

# SECTION 7 — AI PLANNING SYSTEM

## 7.1 AI Use Cases

### Use case 1: Daily plan generation
**Trigger:** User taps "AI Plan" in morning message or Mini App
**Input context:**
- User's active goals and their deadlines
- Pending tasks (including overdue carry-forwards)
- Today's scheduled habits
- User's available time (configured or inferred from historical completion patterns)
- Day of week (workday vs weekend patterns)
- User's peak productivity hours (from analytics)
- Recent completion rate (to calibrate load)

**Output:** Structured daily plan with tasks ordered by priority and time blocks

### Use case 2: Weekly plan adjustment
**Trigger:** During weekly review or explicit request
**Input context:**
- Last week's completion data
- Active goals and their progress rates
- Upcoming deadlines
- Carry-forward task queue
- Habit consistency data

**Output:** Adjusted weekly objectives, redistributed tasks, updated priorities

### Use case 3: Goal decomposition
**Trigger:** User creates a new goal and requests AI breakdown
**Input context:**
- Goal title, description, target date
- User segment (student, freelancer, etc.)
- Existing goals and tasks (to avoid conflicts)
- User's typical daily capacity

**Output:** Monthly milestones → weekly objectives → suggested tasks

### Use case 4: Missed-day recovery plan
**Trigger:** User returns after 2+ days of inactivity
**Input context:**
- Days missed
- Overdue tasks
- Broken streaks
- Goals at risk

**Output:** Reduced recovery plan that prioritizes highest-impact tasks, suggests archiving low-priority overdue items, and sets realistic targets for the next 3 days

### Use case 5: Productivity coaching
**Trigger:** Weekly review or explicit request
**Input context:**
- 4-week trend data
- Habit consistency patterns
- Focus time patterns
- Completion rate by day of week and time of day
- Goal progress velocity

**Output:** 2–3 specific, actionable coaching insights with suggested behavior changes

## 7.2 AI Output Format

The AI must never produce free-text advice. All AI output must be structured data that maps to system entities.

### Daily plan output schema

```json
{
  "plan_type": "daily",
  "date": "2026-03-16",
  "time_blocks": [
    {
      "start": "09:00",
      "end": "09:30",
      "type": "planning",
      "description": "Review and prioritize today's tasks"
    },
    {
      "start": "09:30",
      "end": "11:00",
      "type": "focus_session",
      "duration_minutes": 90,
      "linked_task": {
        "title": "Write API documentation for auth module",
        "priority": "high",
        "difficulty": "hard",
        "goal_link": "Complete project documentation by March 30"
      }
    },
    {
      "start": "11:00",
      "end": "11:15",
      "type": "break"
    }
  ],
  "suggested_tasks": [
    {
      "title": "Review pull request from team",
      "priority": "high",
      "difficulty": "medium",
      "estimated_minutes": 30,
      "reason": "Blocking teammate, deadline today"
    },
    {
      "title": "Prepare weekly client update",
      "priority": "medium",
      "difficulty": "easy",
      "estimated_minutes": 20,
      "reason": "Recurring Friday deliverable"
    }
  ],
  "habits_reminder": [
    "Read 30 minutes (current streak: 12 days)",
    "Exercise (current streak: 5 days)"
  ],
  "coaching_note": "You tend to complete more tasks in the morning. Consider scheduling your hardest task before 11 AM.",
  "total_estimated_load_minutes": 240,
  "capacity_assessment": "moderate"
}
```

### Goal decomposition output schema

```json
{
  "plan_type": "goal_decomposition",
  "goal": "Pass AWS Solutions Architect exam by June 2026",
  "monthly_milestones": [
    {
      "month": "April",
      "title": "Complete compute and networking domains",
      "objectives": [
        "Study EC2, ECS, Lambda chapters",
        "Complete 2 hands-on labs",
        "Pass domain practice quiz with 80%+"
      ]
    },
    {
      "month": "May",
      "title": "Complete remaining domains + practice exams",
      "objectives": [
        "Study storage, database, security chapters",
        "Complete all hands-on labs",
        "Take 3 full practice exams",
        "Review weak areas from practice results"
      ]
    },
    {
      "month": "June (week 1–2)",
      "title": "Final review and exam",
      "objectives": [
        "Review all flagged topics",
        "Take 2 final practice exams",
        "Schedule and take real exam"
      ]
    }
  ],
  "suggested_habits": [
    {
      "title": "AWS study session",
      "type": "duration",
      "target_minutes": 45,
      "frequency": "weekdays"
    }
  ],
  "weekly_tasks_template": [
    {
      "title": "Study [chapter name] — 45 min",
      "difficulty": "medium",
      "frequency": "3x per week"
    },
    {
      "title": "Practice quiz on [domain]",
      "difficulty": "easy",
      "frequency": "1x per week"
    }
  ]
}
```

## 7.3 AI Constraints and Guardrails

### Load management
- Daily plan total estimated time must not exceed user's configured available hours (default: 6 hours productive time)
- Maximum tasks in daily plan: 8 (based on productivity research showing cognitive load limits)
- If user has 15 pending tasks, AI selects top 5–8 by priority and deadline, moves rest to future days
- AI must not schedule tasks during user's configured quiet hours or blocked time

### Realism enforcement
- If user's historical completion rate is 60%, AI plans for 60% capacity, not 100%
- New users (< 7 days) get lighter plans (3–5 tasks) to build confidence
- After missed days, first recovery day plan is 50% of normal load
- AI explicitly labels tasks as "must-do today" vs "if time allows"

### User approval
- AI-generated plans are always previews — never auto-applied
- User must tap "Apply plan" to create tasks/time blocks in their actual planner
- User can edit any suggested item before applying
- User can discard entire plan without consequence

### Context privacy
- AI receives only structured data (goals, tasks, habits, stats) — never raw chat messages
- AI context is assembled server-side, not sent from client
- User can view exactly what context was sent to AI (transparency screen)
- No personal data beyond productivity metrics sent to AI provider

## 7.4 AI Feature Gating

| Feature | Free tier | Premium tier |
|---------|-----------|-------------|
| Daily plan generation | 3 per week | Unlimited |
| Weekly plan adjustment | 1 per week | Unlimited |
| Goal decomposition | 1 per month | Unlimited |
| Recovery plan | Always available | Always available |
| Coaching insights | Basic (weekly review summary) | Advanced (detailed weekly + monthly) |

### Cost management
- Each AI generation costs approximately $0.01–0.05 (depending on context size)
- Free tier limit prevents cost overrun from non-paying users
- Premium tier cost absorbed by subscription revenue
- AI responses cached for 24 hours — same request returns cached result
- Context window optimization: send only relevant data, not full user history

---

# SECTION 8 — VIRAL GROWTH MECHANISMS

## 8.1 Referral System

### Mechanics
- Every user has a unique referral link: `t.me/PlanQuestBot?start=ref_[USER_CODE]`
- When a referred user completes onboarding (creates first task):
  - Referrer receives: 100 XP + 50 coins + "Recruiter" achievement progress
  - Referred user receives: 50 bonus coins (welcome bonus)
- When referred user reaches Day 7 active:
  - Referrer receives: additional 50 XP + 25 coins
  - This delayed reward incentivizes referring quality users, not just anyone

### Referral tracking

```
Referral {
  id: UUID
  referrer_user_id: UUID
  referred_user_id: UUID
  referral_code: string
  status: enum [clicked, onboarded, activated_d7, churned]
  created_at: timestamp
  activated_at: timestamp
}
```

### Anti-abuse
- Maximum 50 referral rewards per user (prevents bot-farming)
- Referred user must be a unique Telegram account (Telegram user ID uniqueness)
- Self-referral detection: same device/IP flagged for review
- Referral rewards delayed 24 hours (manual review for suspicious patterns)

## 8.2 Shareable Progress Cards

### Card types

**Streak card:**
Visual card showing:
- User's name and avatar
- Streak count with flame animation
- "I've been productive for 30 days straight on PlanQuest"
- QR code / deep link to bot

**Level-up card:**
- "I just reached Level 15: Consistent Worker"
- Level badge and title
- Total XP earned
- Deep link

**Weekly win card:**
- "My week in PlanQuest:"
- Tasks completed, habits logged, focus minutes
- Weekly score
- Deep link

**Challenge completion card:**
- Challenge name and description
- Completion badge
- Deep link to join same challenge

### Technical implementation
- Cards generated server-side as PNG images (consistent rendering across devices)
- Shared via Telegram inline share or copied as image to other platforms
- Each card contains unique tracking link for attribution
- Card generation cached (same card valid for 24 hours)

### Distribution channels
- Telegram: forward to chat, share to group, post in channel
- Instagram/Twitter: download image, auto-generated caption with hashtag
- WhatsApp/other: image + link sharing

## 8.3 Social Challenges

### Challenge types

**Time-limited sprint:**
- "7-Day Focus Sprint" — complete 1 focus session every day for 7 days
- Open to all users, self-join
- Participants see shared progress board
- Completion reward: 100 XP, 50 coins, "Sprint Finisher" badge
- Challenge shared via link: `t.me/PlanQuestBot?start=challenge_[ID]`

**Head-to-head challenge:**
- User invites friend to 7-day task completion competition
- Both users see each other's daily completion count
- Winner gets 75 coins, loser gets 25 coins (both rewarded for participating)
- Creates direct engagement between users

**Group challenge:**
- Small group (3–10 users) sets a collective goal
- "Complete 100 tasks as a group this week"
- Group progress bar visible to all members
- Collective completion unlocks group chest (split rewards)

### Challenge generation
- System generates 2–3 active public challenges at all times
- New challenges rotate weekly
- Seasonal challenges during events (New Year, exam seasons, etc.)
- Users can create private challenges with custom parameters

## 8.4 Friend Leaderboards

### Design
- Opt-in only — users must explicitly join leaderboard
- Friends-only scope (not global) — prevents demotivation from hardcore users
- Weekly reset — fresh competition every Monday
- Scoring: weekly XP earned (not cumulative level)

### Leaderboard display
- Mini App: dedicated tab within Progress screen
- Shows: rank, name, avatar, weekly XP, change from last week
- Top 3 highlighted with crown/medal icons
- User's position always visible (even if not in top 10)

### Privacy
- Users control visibility: show to friends / hide from leaderboard
- No public profile pages — leaderboard visible only to participants
- User can leave leaderboard at any time

## 8.5 Accountability Groups

### Concept
Small private groups (2–5 users) with shared visibility into weekly goals and completion.

### Mechanics
- Creator invites members via bot deep link
- Each member sets 3 weekly goals visible to group
- Daily summary shared to group: "Azamat completed 4/5 tasks today"
- Weekly group review: who hit their goals, group completion rate
- Group streak: days where all members were active

### Implementation priority
- Phase 5 feature (not MVP)
- Requires group messaging capability
- Can leverage Telegram group chats for notifications

## 8.6 Viral loop analysis

```
User joins
  → Uses product, reaches streak milestone
  → Receives shareable card + referral prompt
  → Shares to friends / social media
  → Friend clicks link, joins bot
  → Friend completes onboarding
  → Referrer gets reward notification
  → Referrer motivated to invite more
  → [loop repeats]

Target K-factor: 0.3–0.5 (each user brings 0.3–0.5 new users)
Combined with paid acquisition, this creates sustainable growth.
```

---

# SECTION 9 — MONETIZATION STRATEGY

## 9.1 Free Tier

The free tier must be a fully functional productivity tool. Users must never feel that free-tier limitations block their core productivity.

**Included in free:**
- Unlimited tasks
- Up to 5 active habits
- Focus sessions (all modes)
- Basic streak system (no auto-freeze)
- Basic XP and levels
- Daily missions (3 per day)
- Weekly missions (4 per week)
- Basic achievements
- Morning/evening bot reminders
- Mini App dashboard
- Weekly review (basic)
- AI daily plan: 3 per week
- AI goal decomposition: 1 per month
- Streak freeze: purchasable with coins, max 1 per 7 days
- Referral system
- Shareable cards

## 9.2 Premium Subscription

**Price point:** $3.99/month or $29.99/year (37% annual discount)
**Payment:** Telegram Stars + external payment fallback

**Premium includes everything in free, plus:**

| Feature | Free | Premium |
|---------|------|---------|
| Active habits | 5 | Unlimited |
| AI daily plans | 3/week | Unlimited |
| AI weekly plans | 1/week | Unlimited |
| AI goal decomposition | 1/month | Unlimited |
| AI coaching insights | Basic weekly | Advanced weekly + monthly |
| Streak freeze | 1 per 7 days | 2 per 7 days + 1 auto-freeze per month |
| Weekly review | Basic stats | Full analytics + AI insights |
| Monthly review | Not available | Full monthly analysis |
| Custom themes | 2 basic themes | All themes + custom colors |
| Habit analytics | Basic consistency % | Heatmap, best time analysis, trend |
| Focus analytics | Basic daily total | Time-of-day analysis, category breakdown |
| Goal hierarchy | 2 levels | Full 4-level hierarchy |
| Export | Not available | CSV/JSON export of all data |
| Priority support | Standard | Fast response |
| Badge: Premium | No | Visible premium badge on profile |
| Exclusive challenges | No | Premium-only challenges and achievements |
| Ad-free | N/A (no ads) | N/A (no ads) |

### Premium conversion strategy
- Premium features are visible but locked (user sees the button, taps, gets upgrade prompt)
- Soft paywall: show premium analytics preview with blurred data + "Upgrade to see full insights"
- Free trial: 7 days after reaching Level 5 (user is already engaged)
- Coin-purchasable trial: 500 coins for 3-day premium access (lets users earn their way to trial)
- Annual plan highlighted as better value with "Save 37%" badge

### Premium retention
- Monthly "Premium Member Report" with advanced analytics
- Exclusive monthly challenge (premium-only)
- Premium anniversary rewards (1 month: 100 coins, 6 months: 500 coins, 1 year: 1000 coins + exclusive title)

## 9.3 AI Usage Tiers

AI costs are the primary variable cost. Gating ensures sustainability:

| Tier | AI generations / month | Price |
|------|----------------------|-------|
| Free | ~15 (3/week daily + 1 monthly decomp) | $0 |
| Premium | ~100 | Included in $3.99/month |
| AI Power Pack | +50 additional | $1.99 one-time top-up |

### Cost modeling
- Average AI generation cost: $0.02
- Free user AI cost: $0.30/month
- Premium user AI cost: $2.00/month
- Premium subscription revenue: $3.99/month
- AI cost as % of premium revenue: ~50% (acceptable, as other features have near-zero marginal cost)

## 9.4 Cosmetic Purchases

**Available for coins (earned) or Stars (purchased):**
- Profile themes: 100–300 coins or 50–150 Stars
- Badge frames: 150–500 coins or 75–250 Stars
- Title packs: 200–1000 coins or 100–500 Stars
- Seasonal limited items: Stars-only (creates urgency)

**Revenue impact:** Small but high-margin. Primarily serves as a coin sink and engagement driver rather than a revenue center.

## 9.5 Future Revenue Streams (post-scale)

### Team plans ($9.99/user/month)
- Shared workspace for small teams (2–10)
- Team challenges and leaderboards
- Manager dashboard with team productivity overview
- Team goal tracking

### Education plans
- Bulk licensing for universities and study groups
- Exam planning templates
- Instructor dashboard

### B2B productivity tools
- Company-branded instance
- Integration with project management tools
- Compliance and reporting features

## 9.6 Monetization philosophy

**Core principle: productivity value must never be gated.**

A free user must be able to:
- Create unlimited tasks and complete them
- Track habits (up to 5 is sufficient for most users)
- Run focus sessions
- Maintain streaks
- Earn XP and level up

Premium sells three things:
1. **Depth** — more analytics, more habits, more goal levels
2. **Intelligence** — more AI planning, coaching, insights
3. **Convenience** — auto-freeze, export, advanced customization

This ensures that users never feel the product is holding their productivity hostage for payment.

---

# SECTION 10 — PRODUCT METRICS

## 10.1 North Star Metric

### Weekly Structured Active Users (WSAU)

**Definition:** A user who performs at least 3 meaningful actions in a calendar week.

**Meaningful actions:**
- Complete a task
- Log a habit
- Complete a focus session (≥ 50% planned duration)
- Complete a weekly review
- Apply an AI-generated plan

**Why WSAU, not DAU or MAU:**
- DAU is noisy — a user who opens the bot but does nothing counts as active
- MAU is too forgiving — a user who acts once in 30 days is not truly engaged
- WSAU captures **real value consumption** — 3 actions/week means the user is genuinely using the system for productivity, not just receiving notifications

**Target trajectory:**
- Month 1 (soft launch): 500 WSAU
- Month 3: 5,000 WSAU
- Month 6: 25,000 WSAU
- Month 12: 100,000 WSAU
- Month 24: 500,000 WSAU

## 10.2 Activation Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Onboarding completion | User completes segment selection + first task | > 70% |
| First task created | User creates at least 1 task within first session | > 65% |
| First task completed | User completes a task within 24 hours of signup | > 45% |
| First habit created | User creates a habit within first 7 days | > 35% |
| First streak day | User achieves Day 1 streak (any type) | > 50% |
| Activation (composite) | User completes 3 tasks + 1 habit log within first 7 days | > 30% |

### Measurement
- Track via event pipeline: `user.onboarding_completed`, `task.created`, `task.completed`, `habit.created`, `habit.logged`
- Funnel analysis: onboarding → first task → first completion → first habit → activation
- Segment analysis: activation rate by user segment (student vs freelancer vs entrepreneur)

## 10.3 Retention Metrics

| Metric | Definition | Target (mature product) |
|--------|-----------|------------------------|
| D1 retention | User performs action on day after signup | > 55% |
| D7 retention | User performs action on day 7 after signup | > 35% |
| D14 retention | User performs action on day 14 | > 28% |
| D30 retention | User performs action on day 30 | > 22% |
| D90 retention | User performs action on day 90 | > 15% |
| Week-over-week retention | WSAU this week / WSAU last week | > 85% |
| Resurrection rate | Previously churned users who return per month | > 5% |

### Measurement
- Cohort-based retention curves (grouped by signup week)
- Segment-based retention (which user types retain best)
- Feature correlation: retention rate for users who [use focus/create habits/link goals] vs users who don't
- Streak as retention proxy: users with streak > 7 have 3x D30 retention

## 10.4 Engagement Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Tasks completed / active user / week | Average tasks completed by WSAU | > 8 |
| Habits logged / active user / day | Average habit logs per active day | > 1.5 |
| Focus minutes / active user / week | Average focus time per WSAU | > 60 min |
| Daily mission completion rate | Missions completed / missions generated | > 50% |
| Weekly review completion rate | Weekly reviews done / weekly review prompts | > 30% |
| Bot message engagement rate | Callback actions / bot messages sent | > 25% |
| Mini App sessions / user / week | Average Mini App opens per WSAU | > 4 |
| Average session duration (Mini App) | Time spent in Mini App per session | > 3 min |

## 10.5 Virality Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Invite send rate | Users who share referral link / total active users | > 10% |
| Referral activation rate | Referred users who complete onboarding / referral link clicks | > 25% |
| K-factor | (invites sent × conversion rate) / total users | > 0.3 |
| Share card generation rate | Cards generated / active users per week | > 5% |
| Challenge participation rate | Users in active challenge / total active users | > 8% |

## 10.6 Revenue Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Free → premium conversion | Premium subscribers / total registered users | > 4% |
| Trial → paid conversion | Paid after trial / trial users | > 35% |
| Premium churn (monthly) | Cancelled subscriptions / total premium users | < 8% |
| ARPU (all users) | Total revenue / total registered users | > $0.15 |
| ARPPU (paying users) | Total revenue / paying users | > $3.50 |
| LTV (premium user) | Average revenue per premium user over lifetime | > $25 |
| Payback period | CAC / monthly ARPU | < 6 months |

---

# SECTION 11 — MVP FEATURE PRIORITY

## 11.1 Must-Have (Phase 1 — launch blocker)

These features are required for the product to deliver its core value proposition: a gamified productivity planner in Telegram.

| Feature | Justification |
|---------|--------------|
| Telegram bot with webhook | Foundation — all bot interactions depend on this |
| User auth via Telegram initData | Security — required for all user operations |
| Task CRUD (create, read, update, delete) | Core value — users must be able to manage tasks |
| Task completion with XP award | Core loop — completing tasks must feel rewarding |
| Daily planner view (Mini App) | Core UX — users need to see and manage their day |
| Basic habit tracking (yes/no type) | Second core loop — habits drive daily returns |
| Activity streak | Primary retention mechanism — loss aversion hook |
| Morning plan reminder (bot) | Engagement driver — daily re-entry trigger |
| Evening summary (bot) | Reflection — closes daily loop, previews tomorrow |
| XP and basic level system | Progression — visible reward for cumulative effort |
| Mini App shell (home + planner + habits + progress + profile) | UX platform — all rich interactions need this |
| Basic onboarding flow | Activation — first 2 minutes determine retention |
| Timezone handling | Correctness — reminders must arrive at right local time |

## 11.2 Should-Have (Phase 1.5 — add within 2–4 weeks of launch)

These features significantly improve retention and engagement but are not launch blockers.

| Feature | Justification |
|---------|--------------|
| Focus timer (Pomodoro) | Deep work tracking — strong engagement signal |
| Daily missions (3 per day) | Direction — tells users what to do, not just what they could do |
| Weekly review (basic) | Ritual creation — highest-correlation retention feature |
| Task reminders (per-task) | Re-engagement — prevents tasks from being forgotten |
| Habit streak (per-habit) | Stronger habit attachment — per-habit investment |
| Count and duration habit types | Broader habit coverage — yes/no insufficient for many habits |
| Basic achievements (starter set) | Discovery — gives new users progression milestones |
| AI daily plan (limited) | Differentiator — reduces planning friction significantly |
| Recurring tasks | Practical need — many tasks repeat weekly/daily |
| Streak freeze (coin-purchasable) | Recovery — prevents permanent streak loss |

## 11.3 Later Features (Phase 2–6)

| Feature | Phase | Justification |
|---------|-------|--------------|
| Full achievement system | 2 | Requires sufficient event infrastructure |
| Coin economy + spending | 2 | Needs achievement/mission systems first |
| Weekly missions | 2 | Daily missions must prove engagement first |
| Reward chests | 2 | Depends on coin economy |
| Goal hierarchy (4 levels) | 3 | Users need basic planning before goal management |
| AI goal decomposition | 3 | Requires goal system |
| AI weekly planner | 3 | Requires weekly review data |
| AI recovery plans | 3 | Requires comeback detection |
| Profile customization (cosmetics) | 4 | Engagement polish, not core functionality |
| Wallet and shop | 4 | Depends on full coin economy |
| Monthly reviews | 4 | Needs 30+ days of user data |
| Referral system | 5 | Requires stable product before inviting others |
| Shareable cards | 5 | Needs visual identity established |
| Social challenges | 5 | Requires multi-user infrastructure |
| Friend leaderboard | 5 | Requires social graph |
| Accountability groups | 5 | Requires group messaging |
| Premium subscription | 4–5 | Needs enough premium features to justify price |
| Telegram Stars payment | 4–5 | Requires premium tier |
| Team plans | 6 | Post-scale feature |
| Analytics warehouse | 6 | Post-scale infrastructure |

---

# SECTION 12 — PRODUCT DEVELOPMENT ROADMAP

## Phase 0 — Discovery and Design (weeks 1–3)

### Deliverables
- Finalized PRD (this document, reviewed and approved)
- Complete user flow diagrams for bot + Mini App
- Wireframes for all Mini App screens (Home, Planner, Habits, Progress, Profile)
- Bot message template library (all reminder types, onboarding, summaries)
- Event model specification (all domain events and their handlers)
- Database schema v1 (ER diagram + migration scripts)
- API specification (OpenAPI/Swagger for all endpoints)
- Gamification formula spreadsheet (XP values, level curve, coin economy balance)
- Tracking plan (all analytics events with properties)
- Technical architecture diagram
- Design system (colors, typography, component library for Mini App)

### Exit criteria
- Engineering team can begin implementation without product questions
- All edge cases documented (timezone, streak breaks, overdue tasks, etc.)
- Gamification economy validated via spreadsheet simulation

### Team required
- Product lead
- Designer
- Technical lead (for architecture review)

---

## Phase 1 — MVP Core (weeks 4–13, approximately 10 weeks)

### Build scope
| Component | Details |
|-----------|---------|
| Telegram bot | Webhook setup, command handling, callback processing, message sending |
| Auth system | Telegram initData verification, session management, user creation |
| Task engine | CRUD, completion with XP, recurring tasks, overdue detection |
| Habit engine | CRUD, daily logging (yes/no), streak calculation |
| Focus timer | Session lifecycle, linked task, XP award |
| Streak system | Activity streak tracking, break detection, milestone events |
| XP/Level system | XP calculation with multipliers, level progression, level-up events |
| Reminder engine | Scheduled job system, morning/evening/task/habit reminders, timezone handling |
| Mini App frontend | Home, Planner, Habits, Progress, Profile screens |
| Daily summary | Evening bot message with day stats |
| Onboarding | 3-step bot flow + Mini App extended setup |
| Event system | Domain event bus for cross-module communication |
| Admin tools | Basic user lookup, stats dashboard, message broadcast |

### Team required
- 1 senior backend engineer (bot + API + event system + gamification)
- 1 frontend engineer (Mini App)
- 1 designer (ongoing UI polish)
- 1 product lead (QA + decisions)
- 1 QA/ops (testing + deployment)

### Milestones
- Week 6: bot functional (onboarding, task CRUD, basic reminders)
- Week 8: Mini App shell functional (home, planner, habits working with API)
- Week 10: gamification layer working (XP, levels, streaks)
- Week 12: integration testing, reminder reliability testing
- Week 13: alpha deploy to 50–100 test users

### Exit criteria
- Core loop functional: create task → complete → earn XP → streak maintained
- Bot reminders deliver at correct local time
- Mini App loads in < 2 seconds on 3G
- No critical bugs in 48-hour soak test
- Activation rate > 50% in test group

---

## Phase 2 — Gamification Engine (weeks 14–19, approximately 6 weeks)

### Build scope
| Component | Details |
|-----------|---------|
| Mission system | Daily mission generation, weekly missions, progress tracking, rewards |
| Achievement system | Full achievement catalog, event-driven tracking, unlock notifications |
| Coin economy | Earning sources, spending (streak freeze, cosmetics), balance tracking |
| Reward chests | Chest generation, loot tables, opening mechanic |
| Enhanced streaks | Per-habit streaks, focus streak, streak milestones |
| Anti-abuse | XP caps, rapid completion detection, duplicate task detection |
| Mission UI | Mini App mission display, progress indicators |
| Achievement UI | Achievement gallery, locked/unlocked states, progress bars |

### Exit criteria
- Daily mission completion rate > 40%
- D7 retention improved by > 15% vs Phase 1 baseline
- Coin economy stable (no hyperinflation)
- Anti-abuse rules catching 95%+ of obvious farming attempts

---

## Phase 3 — AI Assistant (weeks 20–25, approximately 6 weeks)

### Build scope
| Component | Details |
|-----------|---------|
| AI service | LLM integration, prompt engineering, structured output parsing |
| Daily planner AI | Context assembly, plan generation, plan preview UI |
| Goal system | Goal hierarchy (4 levels), CRUD, progress calculation |
| Goal decomposition AI | Goal → milestones → objectives → tasks breakdown |
| Recovery planner AI | Missed-day detection, reduced-load recovery plan |
| Weekly review enhanced | AI insights, coaching messages, next-week recommendations |
| AI feature gating | Free/premium tier limits, usage tracking |

### Exit criteria
- AI daily plan acceptance rate > 60% (users apply the plan)
- AI plan generation latency < 5 seconds
- Goal decomposition produces reasonable plans (manual review by product team)
- AI cost per active user < $0.50/month

---

## Phase 4 — Rich Progression and UI Polish (weeks 26–31, approximately 6 weeks)

### Build scope
| Component | Details |
|-----------|---------|
| Profile customization | Themes, badge frames, title selection |
| Wallet and shop | Coin spending UI, item catalog, purchase flow |
| Monthly review | Monthly stats aggregation, AI monthly report |
| Enhanced analytics | Charts, heatmaps, trend analysis, time-of-day insights |
| Animation polish | Level-up animations, XP popups, streak flame, chest opening |
| Premium subscription | Paywall UI, Telegram Stars integration, premium entitlement system |
| Premium features | Advanced analytics, unlimited AI, extra freezes, themes |

### Exit criteria
- Free → premium conversion > 3%
- User-reported satisfaction with UI quality (in-app survey) > 4.0/5.0
- Monthly review completion rate > 20% (premium users)
- Shop transaction volume validates coin economy

---

## Phase 5 — Viral and Social (weeks 32–39, approximately 8 weeks)

### Build scope
| Component | Details |
|-----------|---------|
| Referral system | Link generation, tracking, dual-sided rewards |
| Shareable cards | Server-side card generation, sharing flow, attribution |
| Social challenges | Challenge creation, participation, progress tracking |
| Friend leaderboard | Friend connections, weekly XP leaderboard |
| Accountability groups | Group creation, shared goals, group notifications |
| Growth analytics | K-factor tracking, referral funnel, share attribution |

### Exit criteria
- K-factor > 0.2
- Referral activation rate > 20%
- At least 5% of active users participating in a challenge
- Share card generation > 3% of active users per week

---

## Phase 6 — Scale and Optimization (week 40+, ongoing)

### Build scope
| Component | Details |
|-----------|---------|
| Performance optimization | Database query optimization, caching layer, CDN for Mini App |
| Notification optimization | Send-time optimization, engagement-based frequency tuning |
| A/B testing framework | Feature flags, experiment assignment, metric comparison |
| Analytics warehouse | Event data pipeline to analytical database, BI dashboards |
| AI cost optimization | Response caching, context compression, model selection per use case |
| Rate limiting and throttling | Per-user API limits, Telegram API throughput management |
| Service extraction | Extract notification service, gamification processor from monolith |
| Monitoring and alerting | SLOs, error budgets, PagerDuty integration |
| Internationalization | Multi-language support (ru, en, uz, tr, ar as initial set) |

### Exit criteria (rolling)
- API p95 latency < 200ms
- Bot message delivery reliability > 99.5%
- System uptime > 99.9%
- Notification opt-out rate < 5%
- AI cost per generation declining quarter-over-quarter

---

## Timeline Summary

| Phase | Duration | Cumulative | Key milestone |
|-------|----------|-----------|---------------|
| Phase 0 | 3 weeks | Week 3 | Development-ready spec complete |
| Phase 1 | 10 weeks | Week 13 | MVP live with alpha users |
| Phase 2 | 6 weeks | Week 19 | Full gamification active |
| Phase 3 | 6 weeks | Week 25 | AI assistant live |
| Phase 4 | 6 weeks | Week 31 | Premium subscription launched |
| Phase 5 | 8 weeks | Week 39 | Viral loops active |
| Phase 6 | Ongoing | Week 40+ | Scale and optimize |

**Total time to full feature set: approximately 9–10 months.**
**Time to revenue-generating product (Phase 4): approximately 7–8 months.**
**Time to first users (Phase 1 alpha): approximately 3 months.**

---

# APPENDIX A — BOT COMMAND REFERENCE

| Command | Behavior |
|---------|----------|
| `/start` | Onboarding or welcome back message |
| `/add [title] [date]` | Create task (date optional, defaults to today) |
| `/today` | Show today's plan with inline buttons |
| `/habits` | Show today's habits with log buttons |
| `/focus [minutes]` | Start focus session |
| `/stats` | Quick stats: level, XP, streak, weekly score |
| `/review` | Open weekly review in Mini App |
| `/plan` | Request AI daily plan |
| `/settings` | Link to Mini App settings |
| `/help` | Command list and support link |

---

# APPENDIX B — KEY TECHNICAL DECISIONS

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Modular monolith with event bus | Fastest to build, easy to extract services later |
| Backend language | Python (FastAPI) | Best Telegram bot libraries, strong async support, AI SDK ecosystem |
| Frontend | React + TypeScript + Tailwind | Telegram Mini App is a web app; React is the most productive choice |
| Database | PostgreSQL | ACID compliance, JSON support, proven at scale |
| Cache | Redis | Session storage, rate limiting, leaderboard sorted sets, job queues |
| Task queue | Celery with Redis broker | Reminder scheduling, event processing, AI generation jobs |
| AI provider | Claude API (Anthropic) | Structured output quality, cost efficiency, tool use for plans |
| Hosting | Docker containers on VPS → Kubernetes at scale | Cost-effective early, horizontally scalable later |
| Monitoring | Sentry (errors) + Prometheus/Grafana (metrics) | Industry standard, sufficient for all phases |

---

# APPENDIX C — CRITICAL EDGE CASES

| Edge case | Handling |
|-----------|---------|
| User changes timezone | Recalculate all reminder times, streak day boundary adjustment, no streak penalty for transition day |
| Task created for past date | Reject with message "Can't plan for the past. Want to add it for today?" |
| Streak freeze used but user was actually active | Freeze token not consumed (check happens before consumption) |
| Focus session — user kills Telegram app mid-session | Session auto-ends after planned duration + 5 min buffer; partial XP awarded if > 50% elapsed |
| AI generates invalid plan (too many tasks, past dates) | Server-side validation layer rejects and retries with stricter constraints |
| User deletes Telegram account | Data retention policy: anonymize after 30 days, delete after 90 days |
| Two devices — action on bot and Mini App simultaneously | Optimistic locking on critical operations (task completion, coin spending) |
| Midnight timezone edge — user acts at 23:59 | Action counts for current day; if streak check runs at 00:00 and action was at 23:59, streak preserved |
| Referral loop — A refers B, B refers A | Only first referral relationship recorded; loop detection prevents double rewards |

---

*End of PRD. This document is the single source of truth for product decisions. All implementation questions should be resolved by referencing this document first.*


