"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getStreaks, getFocusStats, getWeeklyStats, getTotalStats, getAchievements } from "@/lib/api";
import type { StreakResponse, FocusStatsResponse, AchievementResponse } from "@/types";
import { Flame, Zap, Clock, Trophy, CheckCircle, Target, Repeat } from "lucide-react";
import ProgressRing from "@/components/ProgressRing";
import WeeklyChart from "@/components/WeeklyChart";

const LEVEL_TITLES: Record<number, string> = {
  1: "Yangi boshlovchi",
  2: "Yangi boshlovchi",
  3: "Yangi boshlovchi",
  4: "Yangi boshlovchi",
  5: "Beginner Planner",
  10: "Rising Star",
  15: "Consistent Worker",
  20: "Productivity Pro",
  25: "Goal Crusher",
  30: "Deep Worker",
  40: "Legendary Planner",
  50: "Master of Productivity",
};

function getLevelTitle(level: number): string {
  const keys = Object.keys(LEVEL_TITLES).map(Number).sort((a, b) => b - a);
  for (const k of keys) {
    if (level >= k) return LEVEL_TITLES[k];
  }
  return "Yangi boshlovchi";
}

interface WeekDay {
  date: string;
  day: string;
  tasks: number;
  habits: number;
  total: number;
  is_today: boolean;
}

interface TotalStats {
  total_tasks_completed: number;
  total_habits_logged: number;
}

export default function ProgressPage() {
  const { progress, isAuthenticated } = useAuth();
  const [streaks, setStreaks] = useState<StreakResponse[]>([]);
  const [focusStats, setFocusStats] = useState<FocusStatsResponse | null>(null);
  const [weeklyData, setWeeklyData] = useState<WeekDay[]>([]);
  const [totalStats, setTotalStats] = useState<TotalStats | null>(null);
  const [achievements, setAchievements] = useState<AchievementResponse[]>([]);
  const [achFilter, setAchFilter] = useState<string>("all");

  const loadData = useCallback(async () => {
    try {
      const [s, f, w, t] = await Promise.all([
        getStreaks(),
        getFocusStats(),
        getWeeklyStats(),
        getTotalStats(),
      ]);
      setStreaks(s);
      setFocusStats(f);
      setWeeklyData(w);
      setTotalStats(t);
      getAchievements().then(setAchievements).catch(() => {});
    } catch {}
  }, []);

  useEffect(() => {
    if (isAuthenticated) loadData();
  }, [isAuthenticated, loadData]);

  const activity = streaks.find((s) => s.type === "activity");
  const focusStreak = streaks.find((s) => s.type === "focus");
  const level = progress?.current_level || 1;

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-xl font-bold">📊 Progress</h1>

      {/* Level Card */}
      <div className="bg-gray-900 rounded-xl p-5">
        <div className="flex items-center gap-4">
          <ProgressRing
            percent={progress?.progress_percent || 0}
            size={76}
            strokeWidth={5}
            color="#3b82f6"
          >
            <span className="text-xl font-bold">{level}</span>
          </ProgressRing>
          <div className="flex-1">
            <p className="font-bold text-lg">Level {level}</p>
            <p className="text-xs text-blue-400">{getLevelTitle(level)}</p>
            <p className="text-[10px] text-gray-500 mt-1">
              {progress?.total_xp || 0} / {progress?.xp_for_next_level || 100} XP
            </p>
          </div>
          <div className="text-right">
            <p className="text-yellow-400 font-bold text-lg">🪙 {progress?.coins_balance || 0}</p>
            <p className="text-[10px] text-gray-500">coinlar</p>
          </div>
        </div>
        {/* XP bar */}
        <div className="w-full h-2.5 bg-gray-800 rounded-full overflow-hidden mt-4">
          <div
            className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full transition-all duration-700"
            style={{ width: `${progress?.progress_percent || 0}%` }}
          />
        </div>
      </div>

      {/* Streaks */}
      <div className="grid grid-cols-3 gap-2">
        <div className="bg-gray-900 rounded-xl p-3 text-center">
          <Flame size={22} className="text-orange-400 mx-auto mb-1" />
          <p className="text-xl font-bold">{activity?.current_count || 0}</p>
          <p className="text-[10px] text-gray-500">Activity</p>
          <p className="text-[9px] text-gray-700">Best: {activity?.best_count || 0}</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-3 text-center">
          <Zap size={22} className="text-purple-400 mx-auto mb-1" />
          <p className="text-xl font-bold">{focusStreak?.current_count || 0}</p>
          <p className="text-[10px] text-gray-500">Focus</p>
          <p className="text-[9px] text-gray-700">Best: {focusStreak?.best_count || 0}</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-3 text-center">
          <Clock size={22} className="text-blue-400 mx-auto mb-1" />
          <p className="text-xl font-bold">{focusStats?.today_minutes || 0}</p>
          <p className="text-[10px] text-gray-500">Min bugun</p>
          <p className="text-[9px] text-gray-700">Hafta: {focusStats?.week_minutes || 0}</p>
        </div>
      </div>

      {/* Weekly Chart */}
      <div className="bg-gray-900 rounded-xl p-4">
        <h2 className="font-semibold text-sm mb-4">Haftalik faollik</h2>
        {weeklyData.length > 0 ? (
          <WeeklyChart data={weeklyData} />
        ) : (
          <div className="h-32 flex items-center justify-center text-gray-600 text-sm">
            Ma'lumot yo'q
          </div>
        )}
      </div>

      {/* Total Stats */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-900 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle size={16} className="text-green-400" />
            <span className="text-[10px] text-gray-400 uppercase">Jami tasklar</span>
          </div>
          <p className="text-2xl font-bold">{totalStats?.total_tasks_completed || 0}</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Repeat size={16} className="text-blue-400" />
            <span className="text-[10px] text-gray-400 uppercase">Jami habitlar</span>
          </div>
          <p className="text-2xl font-bold">{totalStats?.total_habits_logged || 0}</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Target size={16} className="text-purple-400" />
            <span className="text-[10px] text-gray-400 uppercase">Jami fokus</span>
          </div>
          <p className="text-2xl font-bold">{focusStats?.total_sessions || 0}</p>
          <p className="text-[10px] text-gray-600">{focusStats?.total_minutes || 0} min</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Flame size={16} className="text-orange-400" />
            <span className="text-[10px] text-gray-400 uppercase">Eng yaxshi streak</span>
          </div>
          <p className="text-2xl font-bold">{activity?.best_count || 0}</p>
          <p className="text-[10px] text-gray-600">kun</p>
        </div>
      </div>

      {/* Achievements */}
      {achievements.length > 0 && (
        <div className="bg-gray-900 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-sm flex items-center gap-2">
              <Trophy size={16} className="text-yellow-400" />
              Yutuqlar
              <span className="text-xs text-gray-500">
                {achievements.filter((a) => a.unlocked).length}/{achievements.length}
              </span>
            </h2>
          </div>

          {/* Category filter */}
          <div className="flex gap-1.5 mb-3 overflow-x-auto pb-1 no-scrollbar">
            {[
              { key: "all", label: "Hammasi" },
              { key: "tasks", label: "📋 Tasks" },
              { key: "habits", label: "🔄 Habits" },
              { key: "focus", label: "🧠 Focus" },
              { key: "streaks", label: "🔥 Streaks" },
              { key: "missions", label: "🎯 Missions" },
              { key: "levels", label: "⭐ Levels" },
            ].map((f) => (
              <button
                key={f.key}
                onClick={() => setAchFilter(f.key)}
                className={`px-2.5 py-1 rounded-full text-[11px] whitespace-nowrap transition-colors ${
                  achFilter === f.key ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Achievement grid */}
          <div className="space-y-2">
            {achievements
              .filter((a) => achFilter === "all" || a.category === achFilter)
              .map((a) => {
                const pct = a.requirement_value > 0
                  ? Math.min(100, Math.round((a.progress / a.requirement_value) * 100))
                  : 0;
                return (
                  <div
                    key={a.id}
                    className={`p-3 rounded-xl transition-all ${
                      a.unlocked
                        ? "bg-gradient-to-r from-yellow-900/20 to-orange-900/20 border border-yellow-800/30"
                        : "bg-gray-800/40"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className={`text-2xl ${a.unlocked ? "" : "grayscale opacity-40"}`}>{a.icon}</span>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium ${a.unlocked ? "text-yellow-400" : "text-gray-400"}`}>
                          {a.name}
                        </p>
                        <p className="text-[10px] text-gray-500 truncate">{a.description}</p>
                      </div>
                      <div className="text-right shrink-0">
                        {a.unlocked ? (
                          <span className="text-xs text-green-400">✅</span>
                        ) : (
                          <span className="text-[10px] text-gray-600">{a.progress}/{a.requirement_value}</span>
                        )}
                      </div>
                    </div>
                    {!a.unlocked && (
                      <div className="mt-2">
                        <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500/60 rounded-full transition-all duration-300"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <div className="flex justify-between mt-0.5">
                          <span className="text-[9px] text-gray-600">{pct}%</span>
                          <span className="text-[9px] text-gray-600">+{a.reward_xp}XP +{a.reward_coins}🪙</span>
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
