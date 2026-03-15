"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getHabits, logHabit, createHabit, deleteHabit } from "@/lib/api";
import type { HabitWithLogResponse } from "@/types";
import { CheckCircle2, Circle, Flame, Plus, Trash2, Minus, PlusIcon } from "lucide-react";
import AddHabitSheet from "@/components/AddHabitSheet";
import { haptic } from "@/lib/telegram";
import XpToast from "@/components/XpToast";

const FREQ_LABELS: Record<string, string> = {
  daily: "Har kuni",
  weekdays: "Du-Ju",
  "3_per_week": "Haftada 3",
  custom: "Maxsus",
};

export default function HabitsPage() {
  const { isAuthenticated, refreshProgress } = useAuth();
  const [habits, setHabits] = useState<HabitWithLogResponse[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [inputHabit, setInputHabit] = useState<{ id: string; type: string; target: number; current: number } | null>(null);
  const [inputValue, setInputValue] = useState(0);
  const [xpToast, setXpToast] = useState<number | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [loggingId, setLoggingId] = useState<string | null>(null);

  const loadHabits = useCallback(async () => {
    try {
      const data = await getHabits(true); // all=true — habits page barcha habitlarni ko'rsatadi
      setHabits(data);
    } catch {}
  }, []);

  useEffect(() => {
    if (isAuthenticated) loadHabits();
  }, [isAuthenticated, loadHabits]);

  useEffect(() => {
    if (showAdd || inputHabit) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [showAdd, inputHabit]);

  async function handleLog(habitId: string, value: number) {
    setLoggingId(habitId);
    try {
      haptic.light();
      const result = await logHabit(habitId, value);
      if (result.xp_awarded > 0) {
        setXpToast(result.xp_awarded);
        haptic.success();
      }
      await loadHabits();
      await refreshProgress();
    } catch { haptic.error(); }
    finally { setLoggingId(null); }
  }

  function handleTapHabit(h: HabitWithLogResponse) {
    if (h.today_log?.completed) return;

    if (h.habit.type === "yes_no" || h.habit.type === "avoid") {
      handleLog(h.habit.id, h.habit.target_value);
      return;
    }

    // count/duration — show stepper
    setInputHabit({
      id: h.habit.id,
      type: h.habit.type,
      target: h.habit.target_value,
      current: h.today_log?.value || 0,
    });
    setInputValue(h.today_log?.value || h.habit.target_value);
  }

  function handleInputSubmit() {
    if (!inputHabit || inputValue <= 0) return;
    handleLog(inputHabit.id, inputValue);
    setInputHabit(null);
  }

  async function handleAdd(habit: { title: string; type: string; target_value?: number; frequency?: string; icon?: string }) {
    try {
      haptic.medium();
      await createHabit(habit);
      setShowAdd(false);
      haptic.success();
      await loadHabits();
    } catch { haptic.error(); }
  }

  async function handleDelete(habitId: string) {
    try {
      haptic.heavy();
      await deleteHabit(habitId);
      setConfirmDelete(null);
      await loadHabits();
    } catch {}
  }

  const done = habits.filter((h) => h.today_log?.completed);
  const pending = habits.filter((h) => !h.today_log?.completed);
  const progressPct = habits.length > 0 ? Math.round((done.length / habits.length) * 100) : 0;

  return (
    <div className="flex flex-col">
      {xpToast !== null && <XpToast xp={xpToast} onDone={() => setXpToast(null)} />}

      <div className="p-4 pb-24 space-y-4 flex-1">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">🔄 Habitlar</h1>
            <p className="text-gray-500 text-xs mt-0.5">
              {done.length}/{habits.length} bajarildi
            </p>
          </div>
          <button
            onClick={() => { setShowAdd(true); haptic.light(); }}
            className="bg-blue-600 w-11 h-11 rounded-full flex items-center justify-center hover:bg-blue-500 active:scale-90 transition-all shadow-lg shadow-blue-600/30"
          >
            <Plus size={20} strokeWidth={2.5} />
          </button>
        </div>

        {/* Progress bar */}
        {habits.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[10px] text-gray-500">Bugungi progress</span>
              <span className={`text-xs font-bold ${progressPct === 100 ? "text-green-400" : "text-gray-400"}`}>
                {progressPct}%
              </span>
            </div>
            <div className="w-full h-2.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700 ${
                  progressPct === 100 ? "bg-green-500" : "bg-blue-500"
                }`}
                style={{ width: `${progressPct}%` }}
              />
            </div>
          </div>
        )}

        {/* Pending habits */}
        {pending.length > 0 && (
          <div className="space-y-2">
            {pending.map(({ habit, current_streak, today_log }) => {
              const isLogging = loggingId === habit.id;
              const currentVal = today_log?.value || 0;
              const showProgress = (habit.type === "count" || habit.type === "duration") && currentVal > 0;
              const progressWidth = showProgress ? Math.min(100, (currentVal / habit.target_value) * 100) : 0;

              return (
                <div
                  key={habit.id}
                  className={`bg-gray-900 rounded-xl overflow-hidden transition-all ${isLogging ? "scale-[0.98] opacity-70" : ""}`}
                >
                  {/* Progress underline for count/duration */}
                  {showProgress && (
                    <div className="w-full h-0.5 bg-gray-800">
                      <div className="h-full bg-blue-500 transition-all duration-300" style={{ width: `${progressWidth}%` }} />
                    </div>
                  )}

                  <div className="p-4 flex items-center gap-3">
                    {/* Tap circle */}
                    <button
                      onClick={() => handleTapHabit({ habit, today_log, current_streak })}
                      disabled={isLogging}
                      className="shrink-0 w-7 h-7 rounded-full border-2 border-gray-600 hover:border-green-400 hover:bg-green-400/10 flex items-center justify-center transition-all active:scale-90"
                    />

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium leading-tight">
                        {habit.icon} {habit.title}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[10px] text-gray-600">
                          {habit.type === "count"
                            ? `${currentVal}/${habit.target_value}`
                            : habit.type === "duration"
                              ? `${currentVal}/${habit.target_value} min`
                              : FREQ_LABELS[habit.frequency] || "Har kuni"}
                        </span>
                        {habit.type === "yes_no" && habit.frequency !== "daily" && (
                          <span className="text-[10px] text-gray-700">
                            {FREQ_LABELS[habit.frequency]}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Streak badge */}
                    {current_streak > 0 && (
                      <div className="flex items-center gap-1 text-orange-400 bg-orange-400/10 px-2 py-1 rounded-full shrink-0">
                        <Flame size={11} />
                        <span className="text-[11px] font-bold">{current_streak}</span>
                      </div>
                    )}

                    {/* Delete */}
                    {confirmDelete === habit.id ? (
                      <div className="flex items-center gap-1 shrink-0">
                        <button
                          onClick={() => handleDelete(habit.id)}
                          className="text-[10px] bg-red-600 px-2.5 py-1 rounded-lg font-medium"
                        >
                          Ha
                        </button>
                        <button
                          onClick={() => setConfirmDelete(null)}
                          className="text-[10px] bg-gray-800 px-2.5 py-1 rounded-lg"
                        >
                          Yo'q
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => { setConfirmDelete(habit.id); haptic.light(); }}
                        className="text-gray-800 hover:text-red-400 transition-colors shrink-0 p-1"
                      >
                        <Trash2 size={13} />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Completed habits */}
        {done.length > 0 && (
          <div>
            <p className="text-[10px] text-gray-600 font-semibold uppercase tracking-widest mb-2 px-1">
              Bajarilgan · {done.length}
            </p>
            <div className="space-y-1.5">
              {done.map(({ habit, current_streak, today_log }) => (
                <div
                  key={habit.id}
                  className="bg-gray-900/40 rounded-xl p-3 flex items-center gap-3"
                >
                  <div className="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center shrink-0">
                    <CheckCircle2 size={14} className="text-green-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-500">{habit.icon} {habit.title}</p>
                    {today_log && (habit.type === "count" || habit.type === "duration") && (
                      <p className="text-[10px] text-gray-600">
                        {today_log.value}{habit.type === "duration" ? " min" : ""} / {habit.target_value}
                      </p>
                    )}
                  </div>
                  {current_streak > 0 && (
                    <span className="text-[10px] text-orange-400/60 flex items-center gap-0.5">
                      <Flame size={9} /> {current_streak}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty state */}
        {habits.length === 0 && (
          <div className="text-center py-20">
            <p className="text-5xl mb-4">🔄</p>
            <p className="text-gray-400 font-semibold">Hali habit yo'q</p>
            <p className="text-gray-600 text-sm mt-1 mb-6">Odat hosil qilishni boshlang</p>
            <button
              onClick={() => { setShowAdd(true); haptic.light(); }}
              className="bg-blue-600 px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-500 active:scale-95 transition-all inline-flex items-center gap-2"
            >
              <Plus size={16} /> Habit qo'shish
            </button>
          </div>
        )}
      </div>

      {/* Count/Duration stepper modal */}
      {inputHabit && (
        <div className="fixed inset-0 bg-black/60 z-[60] flex items-center justify-center p-6" onClick={() => setInputHabit(null)}>
          <div className="bg-gray-900 rounded-2xl p-6 w-full max-w-xs space-y-5" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-bold text-center text-lg">
              {inputHabit.type === "count" ? "Nechta?" : "Necha daqiqa?"}
            </h3>

            {/* Stepper */}
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => { setInputValue(Math.max(1, inputValue - (inputHabit.type === "duration" ? 5 : 1))); haptic.light(); }}
                className="w-12 h-12 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 active:scale-90 transition-all"
              >
                <Minus size={20} />
              </button>
              <div className="text-center min-w-[80px]">
                <p className="text-4xl font-bold">{inputValue}</p>
                <p className="text-[10px] text-gray-500 mt-1">
                  {inputHabit.type === "duration" ? "daqiqa" : "ta"}
                </p>
              </div>
              <button
                onClick={() => { setInputValue(inputValue + (inputHabit.type === "duration" ? 5 : 1)); haptic.light(); }}
                className="w-12 h-12 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 active:scale-90 transition-all"
              >
                <PlusIcon size={20} />
              </button>
            </div>

            {/* Target reference */}
            <div className="flex justify-center">
              <span className={`text-xs px-3 py-1 rounded-full ${
                inputValue >= inputHabit.target
                  ? "bg-green-900/30 text-green-400"
                  : "bg-gray-800 text-gray-500"
              }`}>
                Maqsad: {inputHabit.target} {inputHabit.type === "duration" ? "min" : ""}
              </span>
            </div>

            {/* Quick presets */}
            {inputHabit.type === "duration" && (
              <div className="flex gap-2 justify-center">
                {[5, 10, 15, 30, 45, 60].map((v) => (
                  <button
                    key={v}
                    onClick={() => { setInputValue(v); haptic.light(); }}
                    className={`px-2.5 py-1 rounded-lg text-xs transition-all ${
                      inputValue === v ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-500"
                    }`}
                  >
                    {v}m
                  </button>
                ))}
              </div>
            )}

            {/* Submit */}
            <button
              onClick={handleInputSubmit}
              disabled={inputValue <= 0}
              className="w-full bg-green-600 rounded-xl py-3.5 font-semibold text-sm hover:bg-green-500 active:scale-[0.98] transition-all disabled:opacity-40"
            >
              Saqlash
            </button>
          </div>
        </div>
      )}

      {/* Add Habit Sheet */}
      {showAdd && <AddHabitSheet onAdd={handleAdd} onClose={() => setShowAdd(false)} />}
    </div>
  );
}
