// === Health ===
export interface HealthResponse {
  status: string;
  app: string;
  version: string;
}

// === Auth ===
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

// === User ===
export interface UserResponse {
  id: string;
  telegram_id: number;
  first_name: string;
  last_name: string | null;
  username: string | null;
  segment: string | null;
  timezone: string;
  language: string;
  is_premium: boolean;
  is_active: boolean;
  onboarding_step: number;
  referral_code: string | null;
  created_at: string;
}

export interface UserSettingsResponse {
  morning_reminder_time: string;
  evening_reminder_time: string;
  quiet_hours_start: string;
  quiet_hours_end: string;
  theme: string;
  daily_message_count: number;
  max_daily_messages: number;
}

export interface UserProgressResponse {
  current_level: number;
  total_xp: number;
  xp_for_next_level: number;
  xp_progress_in_level: number;
  progress_percent: number;
  coins_balance: number;
}

// === Task ===
export interface TaskResponse {
  id: string;
  user_id: string;
  title: string;
  notes: string | null;
  planned_date: string;
  due_date: string | null;
  priority: string;
  difficulty: string;
  estimated_minutes: number | null;
  category: string | null;
  goal_id: string | null;
  status: string;
  source: string;
  recurrence_rule: string | null;
  completed_at: string | null;
  xp_awarded: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCompleteResponse {
  task: TaskResponse;
  xp_awarded: number;
  total_xp: number;
  leveled_up: boolean;
  new_level: number;
  coins_earned: number;
}

// === Habit ===
export interface HabitResponse {
  id: string;
  user_id: string;
  title: string;
  type: string;
  target_value: number;
  frequency: string;
  frequency_days: number[] | null;
  reminder_time: string | null;
  icon: string;
  color: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface HabitLogResponse {
  id: string;
  habit_id: string;
  date: string;
  value: number;
  completed: boolean;
  logged_at: string;
  source: string;
  xp_awarded: number;
}

export interface HabitWithLogResponse {
  habit: HabitResponse;
  today_log: HabitLogResponse | null;
  current_streak: number;
}

// === Focus ===
export interface FocusSessionResponse {
  id: string;
  user_id: string;
  task_id: string | null;
  planned_duration: number;
  actual_duration: number;
  mode: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  xp_awarded: number;
}

export interface FocusStatsResponse {
  today_minutes: number;
  today_sessions: number;
  week_minutes: number;
  week_sessions: number;
  total_minutes: number;
  total_sessions: number;
}

export interface FocusEndResponse {
  session: FocusSessionResponse;
  xp_awarded: number;
  total_xp: number;
  leveled_up: boolean;
  new_level: number;
}

// === Mission ===
export interface MissionResponse {
  id: string;
  type: string;
  difficulty: string;
  title: string;
  description: string;
  action: string;
  target_value: number;
  current_value: number;
  reward_xp: number;
  reward_coins: number;
  status: string;
  assigned_date: string;
  completed_at: string | null;
}

// === Achievement ===
export interface AchievementResponse {
  id: string;
  key: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  requirement_type: string;
  requirement_value: number;
  reward_xp: number;
  reward_coins: number;
  progress: number;
  unlocked: boolean;
  unlocked_at: string | null;
}

// === Wallet ===
export interface WalletTransactionResponse {
  id: string;
  amount: number;
  type: string;
  source: string;
  description: string;
  created_at: string;
}

export interface WalletResponse {
  balance: number;
  freeze_tokens: number;
  transactions: WalletTransactionResponse[];
}

export interface ShopPurchaseResponse {
  ok: boolean;
  error: string | null;
  balance: number;
  freeze_tokens: number;
}

// === Chest ===
export interface ChestResponse {
  id: string;
  type: string;
  rarity: string;
  status: string;
  source: string;
  created_at: string;
}

export interface ChestOpenResponse {
  chest: ChestResponse;
  loot: {
    items: { type: string; amount: number }[];
    total_coins: number;
    total_xp: number;
    freeze_tokens: number;
  };
}

// === Streak ===
export interface StreakResponse {
  type: string;
  current_count: number;
  best_count: number;
  last_active_date: string | null;
}
