"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getTasks, createTask, completeTask, updateTask, deleteTask } from "@/lib/api";
import type { TaskResponse } from "@/types";
import { Plus, Check, Circle, AlertTriangle, Clock, Zap, ChevronRight, RotateCcw } from "lucide-react";
import WeekCalendar from "@/components/WeekCalendar";
import { haptic } from "@/lib/telegram";
import AddTaskSheet from "@/components/AddTaskSheet";
import TaskDetailModal from "@/components/TaskDetailModal";
import XpToast from "@/components/XpToast";

const PRIORITY_DOTS: Record<string, string> = {
  critical: "bg-red-500",
  high: "bg-orange-500",
  medium: "bg-blue-500",
  low: "bg-gray-500",
};

const PRIORITY_BORDER: Record<string, string> = {
  critical: "border-l-red-500",
  high: "border-l-orange-500",
  medium: "border-l-blue-500",
  low: "border-l-gray-700",
};

const DIFF_XP: Record<string, number> = { trivial: 5, easy: 10, medium: 20, hard: 35, epic: 50 };

export default function PlannerPage() {
  const { isAuthenticated, refreshProgress } = useAuth();
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [overdueTasks, setOverdueTasks] = useState<TaskResponse[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [selectedTask, setSelectedTask] = useState<TaskResponse | null>(null);
  const [xpToast, setXpToast] = useState<number | null>(null);
  const [completingId, setCompletingId] = useState<string | null>(null);

  const today = new Date().toISOString().split("T")[0];

  const loadTasks = useCallback(async () => {
    try {
      const data = await getTasks({ date: selectedDate });
      setTasks(data);
      if (selectedDate === today) {
        const all = await getTasks({ status: "pending" });
        setOverdueTasks(all.filter((t) => t.planned_date < today));
      } else {
        setOverdueTasks([]);
      }
    } catch {}
  }, [selectedDate, today]);

  useEffect(() => {
    if (isAuthenticated) loadTasks();
  }, [isAuthenticated, loadTasks]);

  async function handleAdd(task: { title: string; planned_date: string; priority: string; difficulty: string; estimated_minutes?: number; notes?: string; category?: string }) {
    try {
      haptic.light();
      await createTask(task);
      setShowAdd(false);
      haptic.success();
      await loadTasks();
    } catch { haptic.error(); }
  }

  async function handleComplete(id: string) {
    setCompletingId(id);
    try {
      haptic.medium();
      const result = await completeTask(id);
      if (result.xp_awarded > 0) {
        setXpToast(result.xp_awarded);
        haptic.success();
      }
      // Animate out then reload
      setTimeout(async () => {
        await loadTasks();
        await refreshProgress();
        setCompletingId(null);
      }, 400);
    } catch {
      haptic.error();
      setCompletingId(null);
    }
  }

  async function handleReschedule(id: string, newDate: string) {
    try {
      haptic.light();
      await updateTask(id, { planned_date: newDate });
      await loadTasks();
    } catch {}
  }

  async function handleDelete(id: string) {
    try {
      haptic.light();
      await deleteTask(id);
      await loadTasks();
    } catch {}
  }

  async function handleRescheduleOverdue(id: string) {
    haptic.light();
    await handleReschedule(id, today);
  }

  const pending = tasks.filter((t) => t.status === "pending");
  const completed = tasks.filter((t) => t.status === "completed");
  const priorityOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };
  const sortedPending = [...pending].sort((a, b) => (priorityOrder[a.priority] ?? 2) - (priorityOrder[b.priority] ?? 2));

  // Stats
  const totalMinutes = pending.reduce((sum, t) => sum + (t.estimated_minutes || 0), 0);
  const totalXP = pending.reduce((sum, t) => sum + (DIFF_XP[t.difficulty] || 20), 0);

  return (
    <div className="flex flex-col min-h-[calc(100vh-80px)]">
      {xpToast !== null && <XpToast xp={xpToast} onDone={() => setXpToast(null)} />}

      {/* Header */}
      <div className="p-4 pb-2">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h1 className="text-xl font-bold">📋 Planner</h1>
            <p className="text-xs text-gray-500 mt-0.5">
              {new Date(selectedDate).toLocaleDateString("uz-UZ", { weekday: "long", day: "numeric", month: "long" })}
            </p>
          </div>
          <button
            onClick={() => { setShowAdd(true); haptic.light(); }}
            className="bg-blue-600 w-11 h-11 rounded-full flex items-center justify-center hover:bg-blue-500 active:scale-90 transition-all shadow-lg shadow-blue-600/30"
          >
            <Plus size={20} strokeWidth={2.5} />
          </button>
        </div>

        {/* Week calendar */}
        <WeekCalendar selectedDate={selectedDate} onSelectDate={(d) => { setSelectedDate(d); haptic.light(); }} />
      </div>

      {/* Day summary bar */}
      {(pending.length > 0 || completed.length > 0) && (
        <div className="px-4 pb-2">
          <div className="flex items-center gap-3 bg-gray-900/60 rounded-xl px-3 py-2">
            <div className="flex items-center gap-1.5">
              <Circle size={10} className="text-blue-400" />
              <span className="text-xs text-gray-400">{pending.length} ochiq</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Check size={10} className="text-green-400" />
              <span className="text-xs text-gray-400">{completed.length} tugagan</span>
            </div>
            {totalMinutes > 0 && (
              <div className="flex items-center gap-1 ml-auto">
                <Clock size={10} className="text-gray-600" />
                <span className="text-[10px] text-gray-600">{totalMinutes}m</span>
              </div>
            )}
            <div className="flex items-center gap-1">
              <Zap size={10} className="text-yellow-500/60" />
              <span className="text-[10px] text-yellow-500/60">+{totalXP}</span>
            </div>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 px-4 pb-4 space-y-3">
        {/* Overdue carry-forward */}
        {overdueTasks.length > 0 && selectedDate === today && (
          <div className="bg-red-950/30 border border-red-900/30 rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-3 py-2 bg-red-950/40">
              <p className="text-xs text-red-400 font-medium flex items-center gap-1.5">
                <AlertTriangle size={12} /> Muddati o'tgan ({overdueTasks.length})
              </p>
            </div>
            <div className="p-2 space-y-1">
              {overdueTasks.slice(0, 5).map((task) => (
                <div key={task.id} className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-red-950/30 group">
                  <button onClick={() => handleComplete(task.id)} className="shrink-0">
                    <Circle size={16} className="text-red-400/50 hover:text-green-400 transition-colors" />
                  </button>
                  <button
                    onClick={() => setSelectedTask(task)}
                    className="text-xs text-gray-400 truncate flex-1 text-left hover:text-white transition-colors"
                  >
                    {task.title}
                  </button>
                  <button
                    onClick={() => handleRescheduleOverdue(task.id)}
                    className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Bugunga o'tkazish"
                  >
                    <RotateCcw size={12} className="text-blue-400" />
                  </button>
                  <span className="text-[9px] text-red-400/40 shrink-0">{task.planned_date.slice(5)}</span>
                </div>
              ))}
              {overdueTasks.length > 5 && (
                <p className="text-[10px] text-red-400/40 text-center py-1">
                  +{overdueTasks.length - 5} ta yana
                </p>
              )}
            </div>
          </div>
        )}

        {/* Pending tasks */}
        {sortedPending.length > 0 && (
          <div className="space-y-2">
            {sortedPending.map((task) => {
              const isCompleting = completingId === task.id;
              return (
                <div
                  key={task.id}
                  className={`bg-gray-900 rounded-xl overflow-hidden border-l-[3px] ${PRIORITY_BORDER[task.priority] || "border-l-gray-700"} transition-all duration-300 ${
                    isCompleting ? "opacity-0 scale-95 -translate-x-4" : ""
                  }`}
                >
                  <div className="flex items-center gap-3 p-3">
                    {/* Complete button */}
                    <button
                      onClick={() => handleComplete(task.id)}
                      className="shrink-0 w-6 h-6 rounded-full border-2 border-gray-600 hover:border-green-400 hover:bg-green-400/10 flex items-center justify-center transition-all active:scale-90"
                    >
                      {isCompleting && <Check size={12} className="text-green-400" />}
                    </button>

                    {/* Task info */}
                    <button
                      onClick={() => setSelectedTask(task)}
                      className="flex-1 min-w-0 text-left"
                    >
                      <p className="text-sm truncate leading-tight">{task.title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        {task.category && (
                          <span className="text-[9px] text-gray-600 bg-gray-800 px-1.5 py-0.5 rounded">
                            {task.category}
                          </span>
                        )}
                        <span className="text-[10px] text-gray-600 capitalize">{task.difficulty}</span>
                        {task.estimated_minutes && (
                          <>
                            <span className="text-[10px] text-gray-700">·</span>
                            <span className="text-[10px] text-gray-600 flex items-center gap-0.5">
                              <Clock size={8} /> {task.estimated_minutes}m
                            </span>
                          </>
                        )}
                      </div>
                    </button>

                    {/* XP badge */}
                    <div className="shrink-0 flex flex-col items-end gap-0.5">
                      <span className="text-[10px] text-blue-400/70 flex items-center gap-0.5">
                        <Zap size={8} /> {DIFF_XP[task.difficulty] || 20}
                      </span>
                      <ChevronRight size={14} className="text-gray-700" />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Completed */}
        {completed.length > 0 && (
          <div>
            <p className="text-[10px] text-gray-600 font-semibold uppercase tracking-widest mb-2 px-1">
              Bajarilgan · {completed.length}
            </p>
            <div className="space-y-1">
              {completed.map((task) => (
                <button
                  key={task.id}
                  onClick={() => setSelectedTask(task)}
                  className="bg-gray-900/40 rounded-xl p-2.5 flex items-center gap-3 w-full text-left group hover:bg-gray-900/60 transition-colors"
                >
                  <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center shrink-0">
                    <Check size={11} className="text-green-400" />
                  </div>
                  <p className="text-xs line-through text-gray-600 truncate flex-1">{task.title}</p>
                  <span className="text-[9px] text-green-500/50 opacity-0 group-hover:opacity-100 transition-opacity">
                    +{task.xp_awarded}XP
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Empty state */}
        {pending.length === 0 && completed.length === 0 && overdueTasks.length === 0 && (
          <div className="text-center py-20">
            <p className="text-5xl mb-4">📝</p>
            <p className="text-gray-400 font-semibold">Bu kunga reja yo'q</p>
            <p className="text-gray-600 text-sm mt-1 mb-6">Vazifa qo'shib boshlang</p>
            <button
              onClick={() => { setShowAdd(true); haptic.light(); }}
              className="bg-blue-600 px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-500 active:scale-95 transition-all inline-flex items-center gap-2"
            >
              <Plus size={16} /> Vazifa qo'shish
            </button>
          </div>
        )}
      </div>

      {/* Add Task Sheet */}
      {showAdd && (
        <AddTaskSheet date={selectedDate} onAdd={handleAdd} onClose={() => setShowAdd(false)} />
      )}

      {/* Task Detail Modal */}
      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          onComplete={handleComplete}
          onReschedule={handleReschedule}
          onDelete={handleDelete}
          onClose={() => setSelectedTask(null)}
        />
      )}
    </div>
  );
}
