"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useCallback, useEffect, useState } from "react";
import { getTasks, getHabits, getStreaks, getFocusStats, completeTask, logHabit, getMissions, getChests, openChest } from "@/lib/api";
import type { TaskResponse, HabitWithLogResponse, StreakResponse, FocusStatsResponse, MissionResponse, ChestResponse } from "@/types";
import { Flame, Target, Zap, CheckCircle2, Circle, Timer, Sparkles, Gift } from "lucide-react";
import ProgressRing from "@/components/ProgressRing";
import XpToast from "@/components/XpToast";
import { useRouter } from "next/navigation";
import { haptic } from "@/lib/telegram";

export default function HomePage() {
  const { user, progress, isAuthenticated, refreshProgress } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [allTasks, setAllTasks] = useState<TaskResponse[]>([]);
  const [habits, setHabits] = useState<HabitWithLogResponse[]>([]);
  const [streaks, setStreaks] = useState<StreakResponse[]>([]);
  const [focusStats, setFocusStats] = useState<FocusStatsResponse | null>(null);
  const [missions, setMissions] = useState<MissionResponse[]>([]);
  const [chests, setChests] = useState<ChestResponse[]>([]);
  const [openingChest, setOpeningChest] = useState<string | null>(null);
  const [lootResult, setLootResult] = useState<{ coins: number; xp: number; freeze: number } | null>(null);
  const [xpToast, setXpToast] = useState<number | null>(null);

  const today = new Date().toISOString().split("T")[0];

  const loadData = useCallback(async () => {
    try {
      const [pending, all, h, s, f] = await Promise.all([
        getTasks({ date: today, status: "pending" }),
        getTasks({ date: today }),
        getHabits(),
        getStreaks(),
        getFocusStats(),
      ]);
      setTasks(pending);
      setAllTasks(all);
      setHabits(h);
      setStreaks(s);
      setFocusStats(f);
      getMissions("daily").then(setMissions).catch(() => {});
      getChests().then(setChests).catch(() => {});
    } catch (err) {
      console.error("Failed to load:", err);
    }
  }, [today]);

  useEffect(() => {
    if (isAuthenticated) loadData();
  }, [isAuthenticated, loadData]);

  async function handleCompleteTask(taskId: string) {
    try {
      haptic.medium();
      const result = await completeTask(taskId);
      if (result.xp_awarded > 0) {
        setXpToast(result.xp_awarded);
        haptic.success();
      }
      await loadData();
      await refreshProgress();
    } catch { haptic.error(); }
  }

  async function handleOpenChest(chestId: string) {
    setOpeningChest(chestId);
    haptic.heavy();
    try {
      const result = await openChest(chestId);
      setLootResult({
        coins: result.loot.total_coins,
        xp: result.loot.total_xp,
        freeze: result.loot.freeze_tokens,
      });
      setChests((prev) => prev.filter((c) => c.id !== chestId));
      await refreshProgress();
    } catch {
      haptic.error();
    } finally {
      setOpeningChest(null);
    }
  }

  async function handleLogHabit(habitId: string, targetValue: number) {
    try {
      haptic.light();
      const result = await logHabit(habitId, targetValue);
      if (result.xp_awarded > 0) {
        setXpToast(result.xp_awarded);
        haptic.success();
      }
      await loadData();
      await refreshProgress();
    } catch { haptic.error(); }
  }

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Xayrli tong";
    if (hour < 18) return "Xayrli kun";
    return "Xayrli kech";
  };

  const activityStreak = streaks.find((s) => s.type === "activity");
  const completedCount = allTasks.filter((t) => t.status === "completed").length;
  const totalCount = allTasks.length;
  const scorePercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
  const habitsCompleted = habits.filter((h) => h.today_log?.completed).length;

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen p-6">
        <div className="text-center space-y-3">
          <h1 className="text-2xl font-bold">PlanQuest</h1>
          <p className="text-gray-400">Telegram orqali kirish kerak</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      {/* XP Toast */}
      {xpToast !== null && <XpToast xp={xpToast} onDone={() => setXpToast(null)} />}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{greeting()}</p>
          <h1 className="text-xl font-bold">{user?.first_name}</h1>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-gray-800/80 px-2.5 py-1.5 rounded-full">
            <Flame size={14} className="text-orange-400" />
            <span className="text-xs font-bold">{activityStreak?.current_count || 0}</span>
          </div>
          <div className="flex items-center gap-1 bg-gray-800/80 px-2.5 py-1.5 rounded-full">
            <Zap size={14} className="text-yellow-400" />
            <span className="text-xs font-bold">Lv.{progress?.current_level || 1}</span>
          </div>
          <div className="flex items-center gap-1 bg-gray-800/80 px-2.5 py-1.5 rounded-full">
            <span className="text-xs">🪙</span>
            <span className="text-xs font-bold text-yellow-400">{progress?.coins_balance || 0}</span>
          </div>
        </div>
      </div>

      {/* Today Score + XP */}
      <div className="bg-gray-900 rounded-xl p-4 flex items-center gap-4">
        <ProgressRing
          percent={scorePercent}
          size={72}
          strokeWidth={5}
          color={scorePercent >= 80 ? "#22c55e" : scorePercent >= 50 ? "#3b82f6" : "#6b7280"}
        >
          <div className="text-center">
            <p className="text-lg font-bold">{scorePercent}%</p>
          </div>
        </ProgressRing>
        <div className="flex-1 space-y-2">
          <div>
            <p className="text-xs text-gray-400">Bugungi ball</p>
            <p className="text-sm">
              <span className="font-semibold">{completedCount}</span>
              <span className="text-gray-500">/{totalCount} task</span>
              {habits.length > 0 && (
                <span className="text-gray-500"> · {habitsCompleted}/{habits.length} habit</span>
              )}
            </p>
          </div>
          {/* XP mini bar */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-gray-500">XP</span>
              <span className="text-[10px] text-gray-500 font-mono">
                {progress?.total_xp || 0}/{progress?.xp_for_next_level || 100}
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-500"
                style={{ width: `${progress?.progress_percent || 0}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Today's Tasks (top 3 priority) */}
      <div className="bg-gray-900 rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold flex items-center gap-2 text-sm">
            <Target size={16} className="text-blue-400" />
            Bugungi vazifalar
          </h2>
          <button
            onClick={() => router.push("/planner")}
            className="text-xs text-blue-400 hover:text-blue-300"
          >
            Hammasi →
          </button>
        </div>
        {tasks.length === 0 ? (
          <p className="text-gray-500 text-sm py-2">Bugungi reja bo'sh</p>
        ) : (
          <div className="space-y-1">
            {tasks.slice(0, 3).map((task) => {
              const priorityColors: Record<string, string> = {
                critical: "border-l-red-500",
                high: "border-l-orange-500",
                medium: "border-l-blue-500",
                low: "border-l-gray-600",
              };
              return (
                <button
                  key={task.id}
                  onClick={() => handleCompleteTask(task.id)}
                  className={`flex items-center gap-3 w-full text-left p-2.5 rounded-lg hover:bg-gray-800/50 transition-colors border-l-2 ${priorityColors[task.priority] || ""}`}
                >
                  <Circle size={18} className="text-gray-600 shrink-0" />
                  <span className="text-sm flex-1 truncate">{task.title}</span>
                  {task.estimated_minutes && (
                    <span className="text-[10px] text-gray-600">{task.estimated_minutes}m</span>
                  )}
                </button>
              );
            })}
            {tasks.length > 3 && (
              <p className="text-xs text-gray-600 text-center pt-1">+{tasks.length - 3} ta yana</p>
            )}
          </div>
        )}
      </div>

      {/* Today's Habits */}
      <div className="bg-gray-900 rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-sm">🔄 Habitlar</h2>
          <button
            onClick={() => router.push("/habits")}
            className="text-xs text-blue-400 hover:text-blue-300"
          >
            Hammasi →
          </button>
        </div>
        {habits.length === 0 ? (
          <p className="text-gray-500 text-sm py-2">Habit qo'shilmagan</p>
        ) : (
          <div className="space-y-1">
            {habits.slice(0, 4).map(({ habit, today_log, current_streak }) => (
              <button
                key={habit.id}
                onClick={() => !today_log?.completed && handleLogHabit(habit.id, habit.target_value)}
                disabled={today_log?.completed}
                className={`flex items-center gap-3 w-full text-left p-2.5 rounded-lg transition-colors ${
                  today_log?.completed ? "opacity-50" : "hover:bg-gray-800/50"
                }`}
              >
                {today_log?.completed ? (
                  <CheckCircle2 size={18} className="text-green-400 shrink-0" />
                ) : (
                  <Circle size={18} className="text-gray-600 shrink-0" />
                )}
                <span className="text-sm flex-1 truncate">
                  {habit.icon} {habit.title}
                </span>
                {current_streak > 0 && (
                  <span className="text-[10px] text-orange-400 flex items-center gap-0.5">
                    <Flame size={10} /> {current_streak}
                  </span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Unopened Chests */}
      {chests.length > 0 && (
        <div className="space-y-2">
          {chests.map((c) => {
            const rarityStyles: Record<string, string> = {
              common: "from-gray-700 to-gray-600 border-gray-500",
              rare: "from-blue-900 to-indigo-800 border-blue-500",
              epic: "from-purple-900 to-pink-800 border-purple-500",
            };
            const rarityIcons: Record<string, string> = {
              common: "🎁", rare: "💎", epic: "👑",
            };
            const typeLabels: Record<string, string> = {
              daily_mission: "Kunlik missiya", weekly_mission: "Haftalik missiya",
              streak: "Streak", level: "Level",
            };
            return (
              <button
                key={c.id}
                onClick={() => handleOpenChest(c.id)}
                disabled={openingChest === c.id}
                className={`w-full bg-gradient-to-r ${rarityStyles[c.rarity] || rarityStyles.common} border rounded-xl p-4 flex items-center gap-3 hover:opacity-90 active:scale-[0.98] transition-all ${openingChest === c.id ? "animate-pulse" : ""}`}
              >
                <span className="text-3xl">{rarityIcons[c.rarity] || "🎁"}</span>
                <div className="flex-1 text-left">
                  <p className="font-semibold text-sm">{typeLabels[c.type] || c.type} chest</p>
                  <p className="text-xs text-gray-300">Ochish uchun bosing</p>
                </div>
                <Gift size={20} className="text-yellow-400 animate-bounce" />
              </button>
            );
          })}
        </div>
      )}

      {/* Loot Result Modal */}
      {lootResult && (
        <div className="fixed inset-0 bg-black/70 z-[70] flex items-center justify-center p-4" onClick={() => setLootResult(null)}>
          <div className="bg-gray-900 rounded-2xl p-6 w-full max-w-sm text-center space-y-4 animate-slide-up" onClick={(e) => e.stopPropagation()}>
            <p className="text-4xl">🎉</p>
            <h3 className="text-lg font-bold">Chest ochildi!</h3>
            <div className="space-y-2">
              {lootResult.coins > 0 && (
                <p className="text-yellow-400 font-bold">🪙 +{lootResult.coins} coins</p>
              )}
              {lootResult.xp > 0 && (
                <p className="text-blue-400 font-bold">⚡ +{lootResult.xp} XP</p>
              )}
              {lootResult.freeze > 0 && (
                <p className="text-cyan-400 font-bold">🛡️ +{lootResult.freeze} Streak Freeze</p>
              )}
            </div>
            <button
              onClick={() => setLootResult(null)}
              className="w-full bg-blue-600 rounded-xl p-3 text-sm font-medium hover:bg-blue-500 transition-colors"
            >
              Ajoyib!
            </button>
          </div>
        </div>
      )}

      {/* Focus CTA */}
      <button
        onClick={() => router.push("/focus")}
        className="w-full bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-4 flex items-center gap-3 hover:opacity-90 transition-opacity"
      >
        <Timer size={24} />
        <div className="flex-1 text-left">
          <p className="font-semibold text-sm">Fokus session boshlash</p>
          <p className="text-xs text-blue-200">
            Bugun: {focusStats?.today_minutes || 0} min · {focusStats?.today_sessions || 0} session
          </p>
        </div>
        <Sparkles size={18} className="text-yellow-300" />
      </button>

      {/* Daily Missions */}
      {missions.length > 0 && (
        <div className="bg-gray-900 rounded-xl p-4">
          <h2 className="font-semibold text-sm mb-3">🎯 Kunlik missiyalar</h2>
          <div className="space-y-2">
            {missions.map((m) => {
              const done = m.status === "completed";
              const pct = m.target_value > 0 ? Math.min(100, Math.round((m.current_value / m.target_value) * 100)) : 0;
              const difficultyColors: Record<string, string> = {
                easy: "text-green-400", medium: "text-yellow-400", stretch: "text-red-400",
              };
              return (
                <div key={m.id} className={`p-2.5 rounded-lg transition-colors ${done ? "bg-green-900/20" : "bg-gray-800/30"}`}>
                  <div className="flex items-center gap-3">
                    {done ? (
                      <CheckCircle2 size={18} className="text-green-400 shrink-0" />
                    ) : (
                      <Circle size={18} className={`shrink-0 ${difficultyColors[m.difficulty] || "text-gray-600"}`} />
                    )}
                    <span className={`text-sm flex-1 ${done ? "line-through text-gray-500" : ""}`}>{m.title}</span>
                    <span className="text-[10px] text-gray-500">+{m.reward_xp}XP +{m.reward_coins}🪙</span>
                  </div>
                  {!done && (
                    <div className="mt-1.5 ml-8">
                      <div className="flex items-center justify-between mb-0.5">
                        <span className="text-[10px] text-gray-600">{m.current_value}/{m.target_value}</span>
                        <span className="text-[10px] text-gray-600">{pct}%</span>
                      </div>
                      <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full transition-all duration-300" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
