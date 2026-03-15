"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getTasks, createTask, completeTask, updateTask, deleteTask } from "@/lib/api";
import type { TaskResponse } from "@/types";
import { Plus, Check, Circle, AlertTriangle } from "lucide-react";
import WeekCalendar from "@/components/WeekCalendar";
import { haptic } from "@/lib/telegram";
import AddTaskSheet from "@/components/AddTaskSheet";
import TaskDetailModal from "@/components/TaskDetailModal";
import XpToast from "@/components/XpToast";

export default function PlannerPage() {
  const { isAuthenticated, refreshProgress } = useAuth();
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [overdueTasks, setOverdueTasks] = useState<TaskResponse[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [selectedTask, setSelectedTask] = useState<TaskResponse | null>(null);
  const [xpToast, setXpToast] = useState<number | null>(null);

  const today = new Date().toISOString().split("T")[0];

  const loadTasks = useCallback(async () => {
    try {
      const data = await getTasks({ date: selectedDate });
      setTasks(data);

      // Load overdue only if viewing today
      if (selectedDate === today) {
        const all = await getTasks({ status: "pending" });
        const overdue = all.filter((t) => t.planned_date < today);
        setOverdueTasks(overdue);
      } else {
        setOverdueTasks([]);
      }
    } catch {}
  }, [selectedDate, today]);

  useEffect(() => {
    if (isAuthenticated) loadTasks();
  }, [isAuthenticated, loadTasks]);

  async function handleAdd(task: { title: string; planned_date: string; priority: string; difficulty: string; estimated_minutes?: number }) {
    try {
      await createTask(task);
      setShowAdd(false);
      await loadTasks();
    } catch {}
  }

  async function handleComplete(id: string) {
    try {
      haptic.medium();
      const result = await completeTask(id);
      if (result.xp_awarded > 0) {
        setXpToast(result.xp_awarded);
        haptic.success();
      }
      await loadTasks();
      await refreshProgress();
    } catch { haptic.error(); }
  }

  async function handleReschedule(id: string, newDate: string) {
    try {
      await updateTask(id, { planned_date: newDate });
      await loadTasks();
    } catch {}
  }

  async function handleDelete(id: string) {
    try {
      await deleteTask(id);
      await loadTasks();
    } catch {}
  }

  const pending = tasks.filter((t) => t.status === "pending");
  const completed = tasks.filter((t) => t.status === "completed");

  const priorityOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };
  const sortedPending = [...pending].sort((a, b) => (priorityOrder[a.priority] ?? 2) - (priorityOrder[b.priority] ?? 2));

  const priorityBorder: Record<string, string> = {
    critical: "border-l-red-500",
    high: "border-l-orange-500",
    medium: "border-l-blue-500",
    low: "border-l-gray-600",
  };

  const difficultyXP: Record<string, number> = { trivial: 5, easy: 10, medium: 20, hard: 35, epic: 50 };

  return (
    <div className="p-4 space-y-4">
      {xpToast !== null && <XpToast xp={xpToast} onDone={() => setXpToast(null)} />}

      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">📋 Planner</h1>
        <button
          onClick={() => setShowAdd(true)}
          className="bg-blue-600 p-2.5 rounded-full hover:bg-blue-500 transition-colors shadow-lg shadow-blue-600/20"
        >
          <Plus size={18} />
        </button>
      </div>

      {/* Week calendar */}
      <WeekCalendar selectedDate={selectedDate} onSelectDate={setSelectedDate} />

      {/* Overdue carry-forward */}
      {overdueTasks.length > 0 && selectedDate === today && (
        <div className="bg-red-900/10 border border-red-900/30 rounded-xl p-3">
          <p className="text-xs text-red-400 font-medium flex items-center gap-1 mb-2">
            <AlertTriangle size={12} /> Muddati o'tgan ({overdueTasks.length})
          </p>
          <div className="space-y-1.5">
            {overdueTasks.slice(0, 3).map((task) => (
              <div key={task.id} className="flex items-center gap-2">
                <button onClick={() => handleComplete(task.id)}>
                  <Circle size={16} className="text-red-400/60 hover:text-red-300" />
                </button>
                <button
                  onClick={() => setSelectedTask(task)}
                  className="text-xs text-gray-400 truncate flex-1 text-left"
                >
                  {task.title}
                </button>
                <span className="text-[10px] text-red-400/60">{task.planned_date}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pending tasks */}
      {sortedPending.length > 0 && (
        <div className="space-y-2">
          {sortedPending.map((task) => (
            <div
              key={task.id}
              className={`bg-gray-900 rounded-xl p-3 flex items-center gap-3 border-l-2 ${priorityBorder[task.priority] || "border-l-gray-600"}`}
            >
              <button onClick={() => handleComplete(task.id)} className="shrink-0">
                <Circle size={20} className="text-gray-600 hover:text-blue-400 transition-colors" />
              </button>
              <button
                onClick={() => setSelectedTask(task)}
                className="flex-1 min-w-0 text-left"
              >
                <p className="text-sm truncate">{task.title}</p>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[10px] text-gray-600">{task.difficulty}</span>
                  {task.estimated_minutes && (
                    <span className="text-[10px] text-gray-600">· {task.estimated_minutes}m</span>
                  )}
                  <span className="text-[10px] text-blue-500/60 ml-auto">+{difficultyXP[task.difficulty] || 20}</span>
                </div>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Completed */}
      {completed.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-2">
            Bajarilgan ({completed.length})
          </p>
          <div className="space-y-1.5">
            {completed.map((task) => (
              <button
                key={task.id}
                onClick={() => setSelectedTask(task)}
                className="bg-gray-900/50 rounded-xl p-3 flex items-center gap-3 w-full text-left opacity-50"
              >
                <Check size={18} className="text-green-400 shrink-0" />
                <p className="text-sm line-through text-gray-500 truncate flex-1">{task.title}</p>
                <span className="text-[10px] text-blue-400">+{task.xp_awarded}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {pending.length === 0 && completed.length === 0 && overdueTasks.length === 0 && (
        <div className="text-center py-16">
          <p className="text-4xl mb-3">📝</p>
          <p className="text-gray-400 font-medium">Reja bo'sh</p>
          <p className="text-gray-600 text-sm mt-1">+ tugmasini bosib vazifa qo'shing</p>
        </div>
      )}

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
