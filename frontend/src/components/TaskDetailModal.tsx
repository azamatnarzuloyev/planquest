"use client";

import { useState, useEffect } from "react";
import type { TaskResponse } from "@/types";
import { X, Check, Trash2, CalendarDays, Timer } from "lucide-react";

interface TaskDetailModalProps {
  task: TaskResponse;
  onComplete: (id: string) => void;
  onReschedule: (id: string, newDate: string) => void;
  onDelete: (id: string) => void;
  onClose: () => void;
}

const PRIORITY_LABELS: Record<string, { label: string; color: string }> = {
  low: { label: "Past", color: "text-gray-400" },
  medium: { label: "O'rta", color: "text-blue-400" },
  high: { label: "Yuqori", color: "text-orange-400" },
  critical: { label: "Muhim", color: "text-red-400" },
};

const DIFFICULTY_LABELS: Record<string, string> = {
  trivial: "Juda oson",
  easy: "Oson",
  medium: "O'rta",
  hard: "Qiyin",
  epic: "Juda qiyin",
};

export default function TaskDetailModal({
  task,
  onComplete,
  onReschedule,
  onDelete,
  onClose,
}: TaskDetailModalProps) {
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = original; };
  }, []);

  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const tomorrowStr = tomorrow.toISOString().split("T")[0];

  const priority = PRIORITY_LABELS[task.priority] || PRIORITY_LABELS.medium;

  return (
    <div className="fixed inset-0 bg-black/60 z-[60] flex items-end" onClick={onClose}>
      <div
        className="w-full bg-gray-900 rounded-t-2xl p-5 space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-lg flex-1 pr-4">{task.title}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Info */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-800 rounded-xl p-3">
            <p className="text-[10px] text-gray-500 uppercase">Muhimlik</p>
            <p className={`text-sm font-medium ${priority.color}`}>{priority.label}</p>
          </div>
          <div className="bg-gray-800 rounded-xl p-3">
            <p className="text-[10px] text-gray-500 uppercase">Qiyinlik</p>
            <p className="text-sm font-medium">{DIFFICULTY_LABELS[task.difficulty] || task.difficulty}</p>
          </div>
          <div className="bg-gray-800 rounded-xl p-3">
            <p className="text-[10px] text-gray-500 uppercase">Sana</p>
            <p className="text-sm font-medium">{task.planned_date}</p>
          </div>
          {task.estimated_minutes && (
            <div className="bg-gray-800 rounded-xl p-3">
              <p className="text-[10px] text-gray-500 uppercase">Vaqt</p>
              <p className="text-sm font-medium">{task.estimated_minutes} min</p>
            </div>
          )}
        </div>

        {task.notes && (
          <div className="bg-gray-800 rounded-xl p-3">
            <p className="text-[10px] text-gray-500 uppercase mb-1">Izoh</p>
            <p className="text-sm text-gray-300">{task.notes}</p>
          </div>
        )}

        {/* Actions */}
        {task.status === "pending" && (
          <div className="space-y-2">
            <button
              onClick={() => { onComplete(task.id); onClose(); }}
              className="w-full bg-green-600 rounded-xl py-3 font-medium flex items-center justify-center gap-2 hover:bg-green-500"
            >
              <Check size={18} /> Bajarildi
            </button>

            <div className="flex gap-2">
              <button
                onClick={() => { onReschedule(task.id, tomorrowStr); onClose(); }}
                className="flex-1 bg-gray-800 rounded-xl py-3 text-sm flex items-center justify-center gap-2 hover:bg-gray-700"
              >
                <CalendarDays size={16} /> Ertaga
              </button>

              {confirmDelete ? (
                <button
                  onClick={() => { onDelete(task.id); onClose(); }}
                  className="flex-1 bg-red-600 rounded-xl py-3 text-sm flex items-center justify-center gap-2"
                >
                  Tasdiqlash
                </button>
              ) : (
                <button
                  onClick={() => setConfirmDelete(true)}
                  className="flex-1 bg-gray-800 rounded-xl py-3 text-sm flex items-center justify-center gap-2 hover:bg-gray-700 text-red-400"
                >
                  <Trash2 size={16} /> O'chirish
                </button>
              )}
            </div>
          </div>
        )}

        {task.status === "completed" && (
          <div className="bg-green-900/20 rounded-xl p-3 text-center border border-green-800/30">
            <p className="text-green-400 font-medium">✅ Bajarilgan</p>
            <p className="text-xs text-gray-400 mt-1">+{task.xp_awarded} XP</p>
          </div>
        )}
      </div>
    </div>
  );
}
