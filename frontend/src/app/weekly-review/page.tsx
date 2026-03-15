"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getWeeklyReview } from "@/lib/api";
import { CheckCircle, Clock, Flame, Zap, Target, BarChart3 } from "lucide-react";

interface ReviewData {
  week: string;
  monday: string;
  sunday: string;
  tasks: { total: number; completed: number; pending: number; completion_rate: number };
  habits: { completed: number; logged: number };
  focus: { minutes: number; sessions: number };
  xp_earned: number;
  level: number;
  streak: number;
  daily: { date: string; day: string; tasks: number; is_today: boolean; is_future: boolean }[];
}

export default function WeeklyReviewPage() {
  const { isAuthenticated } = useAuth();
  const [data, setData] = useState<ReviewData | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      getWeeklyReview().then((d) => setData(d as unknown as ReviewData)).catch(() => {});
    }
  }, [isAuthenticated]);

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-gray-500">Yuklanmoqda...</p>
      </div>
    );
  }

  const maxDayTasks = Math.max(...data.daily.map((d) => d.tasks), 1);

  return (
    <div className="p-4 pb-24 space-y-4">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-xl font-bold">📊 Haftalik ko'rib chiqish</h1>
        <p className="text-xs text-gray-500 mt-1">{data.monday} — {data.sunday}</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-900 rounded-xl p-4 text-center">
          <CheckCircle size={22} className="text-green-400 mx-auto mb-2" />
          <p className="text-2xl font-bold">{data.tasks.completed}</p>
          <p className="text-[10px] text-gray-500">Task bajarildi</p>
          <p className="text-xs text-green-400 mt-1">{data.tasks.completion_rate}%</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-4 text-center">
          <Target size={22} className="text-blue-400 mx-auto mb-2" />
          <p className="text-2xl font-bold">{data.habits.completed}</p>
          <p className="text-[10px] text-gray-500">Habit bajarildi</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-4 text-center">
          <Clock size={22} className="text-purple-400 mx-auto mb-2" />
          <p className="text-2xl font-bold">{data.focus.minutes}</p>
          <p className="text-[10px] text-gray-500">Fokus daqiqa</p>
          <p className="text-xs text-gray-600 mt-1">{data.focus.sessions} sessiya</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-4 text-center">
          <Zap size={22} className="text-yellow-400 mx-auto mb-2" />
          <p className="text-2xl font-bold">+{data.xp_earned}</p>
          <p className="text-[10px] text-gray-500">XP olindi</p>
          <p className="text-xs text-gray-600 mt-1">Level {data.level}</p>
        </div>
      </div>

      {/* Streak */}
      <div className="bg-gradient-to-r from-orange-900/20 to-red-900/20 border border-orange-800/30 rounded-xl p-4 flex items-center gap-4">
        <Flame size={28} className="text-orange-400" />
        <div>
          <p className="font-bold text-lg">{data.streak} kun</p>
          <p className="text-xs text-gray-400">Joriy streak</p>
        </div>
      </div>

      {/* Daily chart */}
      <div className="bg-gray-900 rounded-xl p-4">
        <h2 className="text-sm font-semibold mb-4 flex items-center gap-2">
          <BarChart3 size={14} className="text-blue-400" /> Kunlik faollik
        </h2>
        <div className="flex items-end justify-between gap-1 h-28">
          {data.daily.map((d) => {
            const height = maxDayTasks > 0 ? (d.tasks / maxDayTasks) * 100 : 0;
            return (
              <div key={d.date} className="flex-1 flex flex-col items-center gap-1">
                <span className="text-[9px] text-gray-600">{d.tasks || ""}</span>
                <div className="w-full flex items-end" style={{ height: "80px" }}>
                  <div
                    className={`w-full rounded-t transition-all duration-300 ${
                      d.is_today ? "bg-blue-500" : d.is_future ? "bg-gray-800" : d.tasks > 0 ? "bg-blue-600/60" : "bg-gray-800/40"
                    }`}
                    style={{ height: `${Math.max(d.tasks > 0 ? 8 : 2, height)}%` }}
                  />
                </div>
                <span className={`text-[10px] font-medium ${d.is_today ? "text-blue-400" : "text-gray-600"}`}>
                  {d.day}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Completion summary */}
      <div className="bg-gray-900 rounded-xl p-4 text-center">
        <p className="text-3xl font-bold mb-1">
          {data.tasks.completion_rate >= 80 ? "🎉" : data.tasks.completion_rate >= 50 ? "👍" : "💪"}
        </p>
        <p className="text-sm font-medium">
          {data.tasks.completion_rate >= 80
            ? "Ajoyib hafta bo'ldi!"
            : data.tasks.completion_rate >= 50
              ? "Yaxshi hafta! Davom eting."
              : "Keyingi hafta yaxshiroq bo'ladi!"}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {data.tasks.completed} task, {data.habits.completed} habit, {data.focus.minutes} min fokus
        </p>
      </div>
    </div>
  );
}
