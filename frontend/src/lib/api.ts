import axios from "axios";
import type {
  AchievementResponse,
  AuthResponse,
  FocusEndResponse,
  FocusSessionResponse,
  FocusStatsResponse,
  MissionResponse,
  HabitLogResponse,
  HabitResponse,
  HabitWithLogResponse,
  StreakResponse,
  TaskCompleteResponse,
  TaskResponse,
  UserProgressResponse,
  UserResponse,
  UserSettingsResponse,
  WalletResponse,
  ShopPurchaseResponse,
  ChestResponse,
  ChestOpenResponse,
  PlanResponse,
  GoalResponse,
  DecomposeResponse,
  CoachingResponse,
  RecoveryResponse,
  PlannerQuestions,
} from "@/types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor — attach JWT
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor — handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
    }
    return Promise.reject(error);
  }
);

// === Auth ===
export async function authTelegram(initData: string): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/api/auth/telegram", { init_data: initData });
  return data;
}

// === User ===
export async function getMe(): Promise<UserResponse> {
  const { data } = await api.get<UserResponse>("/api/users/me");
  return data;
}

export async function getMyProgress(): Promise<UserProgressResponse> {
  const { data } = await api.get<UserProgressResponse>("/api/users/me/progress");
  return data;
}

export async function getMySettings(): Promise<UserSettingsResponse> {
  const { data } = await api.get<UserSettingsResponse>("/api/users/me/settings");
  return data;
}

export async function updateMySettings(updates: Partial<{
  morning_reminder_time: string;
  evening_reminder_time: string;
  quiet_hours_start: string;
  quiet_hours_end: string;
  theme: string;
}>): Promise<UserSettingsResponse> {
  const { data } = await api.patch<UserSettingsResponse>("/api/users/me/settings", updates);
  return data;
}

export async function updateMe(updates: Partial<{
  timezone: string;
  language: string;
  segment: string;
}>): Promise<UserResponse> {
  const { data } = await api.patch<UserResponse>("/api/users/me", updates);
  return data;
}

// === Tasks ===
export async function getTasks(params?: { date?: string; status?: string }): Promise<TaskResponse[]> {
  const { data } = await api.get<TaskResponse[]>("/api/tasks", { params });
  return data;
}

export async function createTask(task: { title: string; planned_date: string; priority?: string; difficulty?: string; estimated_minutes?: number }): Promise<TaskResponse> {
  const { data } = await api.post<TaskResponse>("/api/tasks", task);
  return data;
}

export async function updateTask(taskId: string, updates: Partial<{ title: string; planned_date: string; priority: string; difficulty: string; estimated_minutes: number | null; notes: string | null; category: string | null }>): Promise<TaskResponse> {
  const { data } = await api.patch<TaskResponse>(`/api/tasks/${taskId}`, updates);
  return data;
}

export async function deleteTask(taskId: string): Promise<void> {
  await api.delete(`/api/tasks/${taskId}`);
}

export async function completeTask(taskId: string): Promise<TaskCompleteResponse> {
  const { data } = await api.post<TaskCompleteResponse>(`/api/tasks/${taskId}/complete`);
  return data;
}

// === Habits ===
export async function getHabits(showAll: boolean = false): Promise<HabitWithLogResponse[]> {
  const { data } = await api.get<HabitWithLogResponse[]>("/api/habits", { params: showAll ? { all: true } : {} });
  return data;
}

export async function createHabit(habit: {
  title: string;
  type: string;
  target_value?: number;
  frequency?: string;
  icon?: string;
  color?: string;
}): Promise<HabitResponse> {
  const { data } = await api.post<HabitResponse>("/api/habits", habit);
  return data;
}

export async function deleteHabit(habitId: string): Promise<void> {
  await api.delete(`/api/habits/${habitId}`);
}

export async function logHabit(habitId: string, value: number): Promise<HabitLogResponse> {
  const { data } = await api.post<HabitLogResponse>(`/api/habits/${habitId}/log`, { value });
  return data;
}

// === Focus ===
export async function startFocus(mode: string, taskId?: string): Promise<FocusSessionResponse> {
  const { data } = await api.post<FocusSessionResponse>("/api/focus/start", { mode, task_id: taskId });
  return data;
}

export async function endFocus(sessionId: string): Promise<FocusEndResponse> {
  const { data } = await api.post<FocusEndResponse>(`/api/focus/${sessionId}/end`);
  return data;
}

export async function getActiveFocus(): Promise<FocusSessionResponse | null> {
  const { data } = await api.get<FocusSessionResponse | null>("/api/focus/active");
  return data;
}

export async function getFocusStats(): Promise<FocusStatsResponse> {
  const { data } = await api.get<FocusStatsResponse>("/api/focus/stats");
  return data;
}

// === Wallet ===
export async function getWallet(): Promise<WalletResponse> {
  const { data } = await api.get<WalletResponse>("/api/wallet");
  return data;
}

export async function buyStreakFreeze(): Promise<ShopPurchaseResponse> {
  const { data } = await api.post<ShopPurchaseResponse>("/api/shop/streak-freeze");
  return data;
}

// === Chests ===
export async function getChests(): Promise<ChestResponse[]> {
  const { data } = await api.get<ChestResponse[]>("/api/chests");
  return data;
}

export async function openChest(chestId: string): Promise<ChestOpenResponse> {
  const { data } = await api.post<ChestOpenResponse>(`/api/chests/${chestId}/open`);
  return data;
}

// === Achievements ===
export async function getAchievements(): Promise<AchievementResponse[]> {
  const { data } = await api.get<AchievementResponse[]>("/api/achievements");
  return data;
}

// === Missions ===
export async function getMissions(type: "daily" | "weekly" = "daily"): Promise<MissionResponse[]> {
  const { data } = await api.get<MissionResponse[]>("/api/missions", { params: { type } });
  return data;
}

// === AI Coaching & Recovery ===
export async function getCoaching(): Promise<CoachingResponse> {
  const { data } = await api.get<CoachingResponse>("/api/ai/coach");
  return data;
}

export async function getRecoveryPlan(): Promise<RecoveryResponse> {
  const { data } = await api.post<RecoveryResponse>("/api/ai/recover");
  return data;
}

// === Goals ===
export async function getGoals(): Promise<GoalResponse[]> {
  const { data } = await api.get<GoalResponse[]>("/api/goals");
  return data;
}

export async function createGoal(goal: { title: string; description?: string; category?: string; level?: string; target_date?: string }): Promise<GoalResponse> {
  const { data } = await api.post<GoalResponse>("/api/goals", goal);
  return data;
}

export async function deleteGoal(goalId: string): Promise<void> {
  await api.delete(`/api/goals/${goalId}`);
}

export async function decomposeGoal(goalId: string): Promise<DecomposeResponse> {
  const { data } = await api.post<DecomposeResponse>(`/api/ai/goals/${goalId}/decompose`);
  return data;
}

export async function applyDecomposition(goalId: string, decomposition: Record<string, unknown>): Promise<{ tasks_created: number; weeks: number; message: string }> {
  const { data } = await api.post("/api/ai/goals/decompose/apply", { goal_id: goalId, decomposition });
  return data;
}

// === AI ===
export async function getAIQuestions(): Promise<PlannerQuestions> {
  const { data } = await api.get<{ data: PlannerQuestions }>("/api/ai/questions");
  return data.data;
}

export async function generatePlan(focus?: string, availableTime?: string, energy?: string): Promise<PlanResponse> {
  const body: Record<string, string> = {};
  if (focus) body.focus = focus;
  if (availableTime) body.available_time = availableTime;
  if (energy) body.energy = energy;
  const { data } = await api.post<PlanResponse>("/api/ai/plan", Object.keys(body).length > 0 ? body : undefined);
  return data;
}

export async function applyPlan(plan: Record<string, unknown>): Promise<{ tasks_created: number; message: string }> {
  const { data } = await api.post("/api/ai/plan/apply", { plan, apply_suggested: true });
  return data;
}

// === Stats ===
export async function getWeeklyStats(): Promise<{ date: string; day: string; tasks: number; habits: number; total: number; is_today: boolean }[]> {
  const { data } = await api.get("/api/users/me/weekly");
  return data;
}

export async function getTotalStats(): Promise<{ total_tasks_completed: number; total_habits_logged: number }> {
  const { data } = await api.get("/api/users/me/stats");
  return data;
}

// === Weekly Review ===
export async function getWeeklyReview(week?: string): Promise<Record<string, unknown>> {
  const { data } = await api.get("/api/reviews/weekly", { params: week ? { week } : {} });
  return data;
}

// === Streaks ===
export async function getStreaks(): Promise<StreakResponse[]> {
  const { data } = await api.get<StreakResponse[]>("/api/streaks");
  return data;
}

export default api;
