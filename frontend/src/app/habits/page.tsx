"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getHabits, logHabit, createHabit, deleteHabit } from "@/lib/api";
import type { HabitWithLogResponse } from "@/types";
import { CheckCircle2, Circle, Flame, Plus, Trash2 } from "lucide-react";
import AddHabitSheet from "@/components/AddHabitSheet";
import { haptic } from "@/lib/telegram";
import XpToast from "@/components/XpToast";

export default function HabitsPage() {
  const { isAuthenticated, refreshProgress } = useAuth();
  const [habits, setHabits] = useState<HabitWithLogResponse[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [inputHabit, setInputHabit] = useState<{ id: string; type: string; target: number } | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [xpToast, setXpToast] = useState<number | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const loadHabits = useCallback(async () => {
    try {
      const data = await getHabits();
      setHabits(data);
    } catch {}
  }, []);

  useEffect(() => {
    if (isAuthenticated) loadHabits();
  }, [isAuthenticated, loadHabits]);

  // Lock body scroll when modal/sheet open
  useEffect(() => {
    if (showAdd || inputHabit) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [showAdd, inputHabit]);

  async function handleLog(habitId: string, value: number) {
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
  }

  function handleTapHabit(h: HabitWithLogResponse) {
    if (h.today_log?.completed) return;

    // yes_no and avoid — instant log
    if (h.habit.type === "yes_no" || h.habit.type === "avoid") {
      handleLog(h.habit.id, h.habit.target_value);
      return;
    }

    // count/duration — show input
    setInputHabit({ id: h.habit.id, type: h.habit.type, target: h.habit.target_value });
    setInputValue("");
  }

  function handleInputSubmit() {
    if (!inputHabit || !inputValue) return;
    const val = parseInt(inputValue);
    if (isNaN(val) || val <= 0) return;
    handleLog(inputHabit.id, val);
    setInputHabit(null);
    setInputValue("");
  }

  async function handleAdd(habit: { title: string; type: string; target_value?: number; icon?: string }) {
    try {
      await createHabit(habit);
      setShowAdd(false);
      await loadHabits();
    } catch {}
  }

  async function handleDelete(habitId: string) {
    try {
      await deleteHabit(habitId);
      setConfirmDelete(null);
      await loadHabits();
    } catch {}
  }

  const done = habits.filter((h) => h.today_log?.completed);
  const pending = habits.filter((h) => !h.today_log?.completed);

  const typeLabels: Record<string, string> = {
    yes_no: "Tap",
    count: "Hisob",
    duration: "Min",
    avoid: "Tap",
  };

  return (
    <div className="p-4 space-y-4">
      {xpToast !== null && <XpToast xp={xpToast} onDone={() => setXpToast(null)} />}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">🔄 Habitlar</h1>
          <p className="text-gray-500 text-xs mt-0.5">
            {done.length}/{habits.length} bajarildi
          </p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="bg-blue-600 p-2.5 rounded-full hover:bg-blue-500 transition-colors shadow-lg shadow-blue-600/20"
        >
          <Plus size={18} />
        </button>
      </div>

      {/* Progress bar */}
      {habits.length > 0 && (
        <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 rounded-full transition-all duration-500"
            style={{ width: `${habits.length > 0 ? (done.length / habits.length) * 100 : 0}%` }}
          />
        </div>
      )}

      {/* Pending habits */}
      {pending.length > 0 && (
        <div className="space-y-2">
          {pending.map(({ habit, current_streak, today_log }) => (
            <div
              key={habit.id}
              className="bg-gray-900 rounded-xl p-4 flex items-center gap-3"
            >
              <button
                onClick={() => handleTapHabit({ habit, today_log, current_streak })}
                className="shrink-0"
              >
                <Circle size={24} className="text-gray-600 hover:text-green-400 transition-colors" />
              </button>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">
                  {habit.icon} {habit.title}
                </p>
                <p className="text-[10px] text-gray-500">
                  {habit.type === "count"
                    ? `0 / ${habit.target_value}`
                    : habit.type === "duration"
                      ? `0 / ${habit.target_value} min`
                      : typeLabels[habit.type]}
                </p>
              </div>
              {current_streak > 0 && (
                <div className="flex items-center gap-1 text-orange-400 bg-orange-400/10 px-2 py-1 rounded-full">
                  <Flame size={12} />
                  <span className="text-xs font-bold">{current_streak}</span>
                </div>
              )}
              <button
                onClick={() => setConfirmDelete(confirmDelete === habit.id ? null : habit.id)}
                className="text-gray-700 hover:text-red-400 transition-colors shrink-0"
              >
                <Trash2 size={14} />
              </button>
              {confirmDelete === habit.id && (
                <button
                  onClick={() => handleDelete(habit.id)}
                  className="text-[10px] bg-red-600 px-2 py-1 rounded-lg"
                >
                  O'chirish
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Completed habits */}
      {done.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-2">
            Bajarilgan
          </p>
          <div className="space-y-2">
            {done.map(({ habit, current_streak, today_log }) => (
              <div
                key={habit.id}
                className="bg-gray-900/50 rounded-xl p-4 flex items-center gap-3 opacity-50"
              >
                <CheckCircle2 size={24} className="text-green-400 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm">{habit.icon} {habit.title}</p>
                  {today_log && (habit.type === "count" || habit.type === "duration") && (
                    <p className="text-[10px] text-gray-500">
                      {today_log.value}{habit.type === "duration" ? " min" : ""} / {habit.target_value}
                    </p>
                  )}
                </div>
                {current_streak > 0 && (
                  <span className="text-xs text-orange-400 flex items-center gap-0.5">
                    <Flame size={10} /> {current_streak}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {habits.length === 0 && (
        <div className="text-center py-16">
          <p className="text-4xl mb-3">🔄</p>
          <p className="text-gray-400 font-medium">Hali habit yo'q</p>
          <p className="text-gray-600 text-sm mt-1">+ tugmasini bosib qo'shing</p>
        </div>
      )}

      {/* Count/Duration input modal */}
      {inputHabit && (
        <div className="fixed inset-0 bg-black/60 z-[60] flex items-center justify-center p-6" onClick={() => setInputHabit(null)}>
          <div className="bg-gray-900 rounded-2xl p-5 w-full max-w-sm space-y-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-bold text-center">
              {inputHabit.type === "count" ? "Nechta?" : "Necha minut?"}
            </h3>
            <input
              type="number"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={String(inputHabit.target)}
              min={1}
              className="w-full bg-gray-800 rounded-xl px-4 py-3 text-center text-2xl font-bold outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
              onKeyDown={(e) => e.key === "Enter" && handleInputSubmit()}
            />
            <p className="text-center text-xs text-gray-500">
              Maqsad: {inputHabit.target} {inputHabit.type === "duration" ? "min" : ""}
            </p>
            <button
              onClick={handleInputSubmit}
              disabled={!inputValue}
              className="w-full bg-green-600 rounded-xl py-3 font-medium hover:bg-green-500 disabled:opacity-40"
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
