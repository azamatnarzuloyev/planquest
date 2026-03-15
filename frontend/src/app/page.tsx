"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useCallback, useEffect, useState } from "react";
import { getTasks, getHabits, getStreaks, getFocusStats, completeTask, logHabit, getMissions, getChests, openChest } from "@/lib/api";
import type { TaskResponse, HabitWithLogResponse, StreakResponse, FocusStatsResponse, MissionResponse, ChestResponse } from "@/types";
import { Flame, CheckCircle2, Circle, Timer, Sparkles, Gift, ChevronRight, Play, Bot } from "lucide-react";
import XpToast from "@/components/XpToast";
import { useRouter } from "next/navigation";
import { haptic, getTelegramUser } from "@/lib/telegram";

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
      setTasks(pending); setAllTasks(all); setHabits(h); setStreaks(s); setFocusStats(f);
      getMissions("daily").then(setMissions).catch(() => {});
      getChests().then(setChests).catch(() => {});
    } catch {}
  }, [today]);

  useEffect(() => { if (isAuthenticated) loadData(); }, [isAuthenticated, loadData]);
  useEffect(() => { if (isAuthenticated) loadData(); }, []); // eslint-disable-line

  async function handleCompleteTask(taskId: string) {
    haptic.medium();
    try {
      const r = await completeTask(taskId);
      if (r.xp_awarded > 0) { setXpToast(r.xp_awarded); haptic.success(); }
      await loadData(); await refreshProgress();
    } catch { haptic.error(); }
  }

  async function handleOpenChest(chestId: string) {
    setOpeningChest(chestId); haptic.heavy();
    try {
      const r = await openChest(chestId);
      setLootResult({ coins: r.loot.total_coins, xp: r.loot.total_xp, freeze: r.loot.freeze_tokens });
      setChests((p) => p.filter((c) => c.id !== chestId)); await refreshProgress();
    } catch { haptic.error(); }
    finally { setOpeningChest(null); }
  }

  async function handleLogHabit(habitId: string, val: number) {
    haptic.light();
    try {
      const r = await logHabit(habitId, val);
      if (r.xp_awarded > 0) { setXpToast(r.xp_awarded); haptic.success(); }
      await loadData(); await refreshProgress();
    } catch { haptic.error(); }
  }

  const greeting = () => { const h = new Date().getHours(); return h < 12 ? "Xayrli tong" : h < 18 ? "Xayrli kun" : "Xayrli kech"; };
  const activityStreak = streaks.find((s) => s.type === "activity");
  const completedCount = allTasks.filter((t) => t.status === "completed").length;
  const totalCount = allTasks.length;
  const scorePercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
  const habitsCompleted = habits.filter((h) => h.today_log?.completed).length;
  const tgUser = getTelegramUser();
  const photoUrl = tgUser?.photo_url;
  const level = progress?.current_level || 1;
  const isNewUser = user?.created_at && (Date.now() - new Date(user.created_at).getTime()) < 86400000;

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen p-6">
        <div className="text-center space-y-3">
          <p className="text-4xl">🚀</p>
          <h1 className="text-2xl font-bold">PlanQuest</h1>
          <p className="text-gray-400 text-sm">Telegram orqali kirish kerak</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pb-24">
      {xpToast !== null && <XpToast xp={xpToast} onDone={() => setXpToast(null)} />}

      {/* === HEADER — Telegram style === */}
      <div className="px-4 pt-4 pb-3">
        <div className="flex items-center gap-3">
          {/* Avatar */}
          {photoUrl ? (
            <img src={photoUrl} alt="" className="w-11 h-11 rounded-full object-cover" />
          ) : (
            <div className="w-11 h-11 bg-blue-600 rounded-full flex items-center justify-center text-lg font-bold">
              {user?.first_name?.[0] || "?"}
            </div>
          )}
          <div className="flex-1 min-w-0">
            <p className="text-[11px] text-gray-500">{greeting()}</p>
            <p className="text-base font-semibold truncate">{user?.first_name}</p>
          </div>
          {/* Stats pills */}
          <div className="flex items-center gap-1.5">
            <div className="flex items-center gap-1 bg-orange-500/10 px-2 py-1 rounded-full">
              <Flame size={12} className="text-orange-400" />
              <span className="text-[11px] font-bold text-orange-400">{activityStreak?.current_count || 0}</span>
            </div>
            <div className="bg-gray-800 px-2 py-1 rounded-full">
              <span className="text-[11px] font-bold text-blue-400">Lv.{level}</span>
            </div>
          </div>
        </div>
      </div>

      {/* === XP BAR — thin, elegant === */}
      <div className="px-4 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-500 to-blue-400 rounded-full transition-all duration-700"
              style={{ width: `${progress?.progress_percent || 0}%` }} />
          </div>
          <span className="text-[10px] text-gray-600 font-mono shrink-0">{progress?.total_xp || 0} XP</span>
        </div>
      </div>

      {/* === WELCOME BANNER (new user only) === */}
      {isNewUser && (
        <div className="mx-4 mb-3 bg-blue-600/10 border border-blue-500/20 rounded-2xl p-4">
          <p className="text-sm font-medium">👋 Xush kelibsiz, {user?.first_name}!</p>
          <p className="text-xs text-gray-400 mt-1">Bugungi tasklar va habitlarni bajaring — har biri uchun XP olasiz</p>
        </div>
      )}

      {/* === TODAY SCORE === */}
      <div className="mx-4 mb-3 bg-gray-900 rounded-2xl p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] text-gray-500 uppercase tracking-wider font-medium">Bugungi natija</p>
            <div className="flex items-baseline gap-1.5 mt-1">
              <span className="text-3xl font-bold">{scorePercent}<span className="text-lg text-gray-500">%</span></span>
            </div>
            <p className="text-[11px] text-gray-600 mt-0.5">
              {completedCount}/{totalCount} task
              {habits.length > 0 && <span> · {habitsCompleted}/{habits.length} habit</span>}
            </p>
          </div>
          {/* Mini coins */}
          <div className="text-right">
            <p className="text-lg font-bold text-yellow-400">🪙 {progress?.coins_balance || 0}</p>
            <p className="text-[10px] text-gray-600">coinlar</p>
          </div>
        </div>
      </div>

      {/* === CHESTS === */}
      {chests.length > 0 && (
        <div className="mx-4 mb-3 space-y-2">
          {chests.map((c) => {
            const icons: Record<string, string> = { common: "🎁", rare: "💎", epic: "👑" };
            const labels: Record<string, string> = { daily_mission: "Kunlik", weekly_mission: "Haftalik", streak: "Streak", level: "Level" };
            return (
              <button key={c.id} onClick={() => handleOpenChest(c.id)} disabled={openingChest === c.id}
                className={`w-full bg-yellow-500/10 border border-yellow-500/20 rounded-2xl p-3.5 flex items-center gap-3 active:scale-[0.98] transition-all ${openingChest === c.id ? "animate-pulse" : ""}`}>
                <span className="text-2xl">{icons[c.rarity] || "🎁"}</span>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium">{labels[c.type] || c.type} chest</p>
                  <p className="text-[10px] text-gray-500">Ochish uchun bosing</p>
                </div>
                <Gift size={18} className="text-yellow-400" />
              </button>
            );
          })}
        </div>
      )}

      {/* === TASKS — Telegram list style === */}
      <div className="mx-4 mb-3">
        <div className="flex items-center justify-between mb-2 px-1">
          <p className="text-[11px] text-gray-500 uppercase tracking-wider font-medium">Bugungi vazifalar</p>
          <button onClick={() => router.push("/planner")} className="text-[11px] text-blue-400 flex items-center gap-0.5">
            Hammasi <ChevronRight size={12} />
          </button>
        </div>
        <div className="bg-gray-900 rounded-2xl overflow-hidden divide-y divide-gray-800/50">
          {tasks.length === 0 ? (
            <button onClick={() => router.push("/planner")} className="w-full p-4 text-center">
              <p className="text-sm text-gray-500">Bugungi reja bo'sh</p>
              <p className="text-xs text-blue-400 mt-1">Vazifa qo'shish →</p>
            </button>
          ) : (
            tasks.slice(0, 4).map((task) => {
              const dots: Record<string, string> = { critical: "bg-red-500", high: "bg-orange-400", medium: "bg-blue-400", low: "bg-gray-600" };
              return (
                <button key={task.id} onClick={() => handleCompleteTask(task.id)}
                  className="w-full flex items-center gap-3 px-4 py-3 active:bg-gray-800/50 transition-colors">
                  <div className={`w-2 h-2 rounded-full shrink-0 ${dots[task.priority] || dots.medium}`} />
                  <span className="text-sm flex-1 truncate text-left">{task.title}</span>
                  {task.estimated_minutes && <span className="text-[10px] text-gray-600">{task.estimated_minutes}m</span>}
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* === HABITS — compact grid === */}
      {habits.length > 0 && (
        <div className="mx-4 mb-3">
          <div className="flex items-center justify-between mb-2 px-1">
            <p className="text-[11px] text-gray-500 uppercase tracking-wider font-medium">Habitlar</p>
            <button onClick={() => router.push("/habits")} className="text-[11px] text-blue-400 flex items-center gap-0.5">
              Hammasi <ChevronRight size={12} />
            </button>
          </div>
          <div className="bg-gray-900 rounded-2xl overflow-hidden divide-y divide-gray-800/50">
            {habits.slice(0, 4).map(({ habit, today_log, current_streak }) => (
              <button key={habit.id}
                onClick={() => !today_log?.completed && handleLogHabit(habit.id, habit.target_value)}
                disabled={today_log?.completed}
                className="w-full flex items-center gap-3 px-4 py-3 active:bg-gray-800/50 transition-colors disabled:opacity-50">
                {today_log?.completed
                  ? <CheckCircle2 size={18} className="text-green-400 shrink-0" />
                  : <Circle size={18} className="text-gray-600 shrink-0" />}
                <span className="text-sm flex-1 truncate text-left">{habit.icon} {habit.title}</span>
                {current_streak > 0 && (
                  <span className="text-[10px] text-orange-400/70 flex items-center gap-0.5"><Flame size={9} />{current_streak}</span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* === QUICK ACTIONS — horizontal scroll === */}
      <div className="mx-4 mb-3 flex gap-2 overflow-x-auto no-scrollbar">
        <button onClick={() => router.push("/focus")}
          className="shrink-0 bg-purple-600/15 border border-purple-500/20 rounded-2xl px-4 py-3 flex items-center gap-2.5 active:scale-95 transition-all">
          <Play size={16} className="text-purple-400" fill="currentColor" />
          <div className="text-left">
            <p className="text-xs font-medium">Fokus</p>
            <p className="text-[10px] text-gray-500">{focusStats?.today_minutes || 0}m bugun</p>
          </div>
        </button>

        {user?.is_premium && (
          <button onClick={() => router.push("/ai-planner")}
            className="shrink-0 bg-blue-600/15 border border-blue-500/20 rounded-2xl px-4 py-3 flex items-center gap-2.5 active:scale-95 transition-all">
            <Bot size={16} className="text-blue-400" />
            <div className="text-left">
              <p className="text-xs font-medium">AI Reja</p>
              <p className="text-[10px] text-gray-500">Tuzib beradi</p>
            </div>
          </button>
        )}

        <button onClick={() => router.push("/goals")}
          className="shrink-0 bg-green-600/15 border border-green-500/20 rounded-2xl px-4 py-3 flex items-center gap-2.5 active:scale-95 transition-all">
          <Sparkles size={16} className="text-green-400" />
          <div className="text-left">
            <p className="text-xs font-medium">Maqsadlar</p>
            <p className="text-[10px] text-gray-500">Reja tuzish</p>
          </div>
        </button>
      </div>

      {/* === MISSIONS === */}
      {missions.length > 0 && (
        <div className="mx-4 mb-3">
          <p className="text-[11px] text-gray-500 uppercase tracking-wider font-medium mb-2 px-1">Kunlik missiyalar</p>
          <div className="bg-gray-900 rounded-2xl p-3 space-y-2">
            {missions.map((m) => {
              const done = m.status === "completed";
              const pct = m.target_value > 0 ? Math.min(100, Math.round((m.current_value / m.target_value) * 100)) : 0;
              return (
                <div key={m.id} className={`rounded-xl p-2.5 ${done ? "bg-green-900/10" : "bg-gray-800/40"}`}>
                  <div className="flex items-center gap-2.5">
                    {done
                      ? <CheckCircle2 size={16} className="text-green-400 shrink-0" />
                      : <Circle size={16} className="text-gray-600 shrink-0" />}
                    <span className={`text-[13px] flex-1 ${done ? "line-through text-gray-600" : ""}`}>{m.title}</span>
                    <span className="text-[9px] text-gray-600">+{m.reward_xp}XP</span>
                  </div>
                  {!done && (
                    <div className="mt-1.5 ml-7">
                      <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500/70 rounded-full transition-all" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* === LOOT MODAL === */}
      {lootResult && (
        <div className="fixed inset-0 bg-black/70 z-[70] flex items-center justify-center p-4" onClick={() => setLootResult(null)}>
          <div className="bg-gray-900 rounded-2xl p-6 w-full max-w-xs text-center space-y-4" onClick={(e) => e.stopPropagation()}>
            <p className="text-5xl">🎉</p>
            <h3 className="text-lg font-bold">Chest ochildi!</h3>
            <div className="space-y-1">
              {lootResult.coins > 0 && <p className="text-yellow-400 font-bold">🪙 +{lootResult.coins}</p>}
              {lootResult.xp > 0 && <p className="text-blue-400 font-bold">⚡ +{lootResult.xp} XP</p>}
              {lootResult.freeze > 0 && <p className="text-cyan-400 font-bold">🛡️ +{lootResult.freeze} Freeze</p>}
            </div>
            <button onClick={() => setLootResult(null)} className="w-full bg-blue-600 rounded-xl py-3 text-sm font-medium">Ajoyib!</button>
          </div>
        </div>
      )}
    </div>
  );
}
