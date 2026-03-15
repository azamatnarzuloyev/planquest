"use client";

import { useState, useEffect } from "react";
import type { TaskResponse } from "@/types";
import { X, Check, Trash2, CalendarDays, Clock, Zap, Play, ArrowRight } from "lucide-react";
import { haptic } from "@/lib/telegram";
import { useRouter } from "next/navigation";

interface TaskDetailModalProps {
  task: TaskResponse;
  onComplete: (id: string) => void;
  onReschedule: (id: string, newDate: string) => void;
  onDelete: (id: string) => void;
  onClose: () => void;
}

const PRIORITY_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  low: { label: "Past", color: "text-gray-400", bg: "bg-gray-800" },
  medium: { label: "O'rta", color: "text-blue-400", bg: "bg-blue-900/30" },
  high: { label: "Yuqori", color: "text-orange-400", bg: "bg-orange-900/30" },
  critical: { label: "Muhim", color: "text-red-400", bg: "bg-red-900/30" },
};

const DIFFICULTY_CONFIG: Record<string, { label: string; emoji: string; xp: number }> = {
  trivial: { label: "Juda oson", emoji: "🟢", xp: 5 },
  easy: { label: "Oson", emoji: "🔵", xp: 10 },
  medium: { label: "O'rta", emoji: "🟡", xp: 20 },
  hard: { label: "Qiyin", emoji: "🟠", xp: 35 },
  epic: { label: "Juda qiyin", emoji: "🔴", xp: 50 },
};

function getRelativeDate(offset: number): string {
  const d = new Date();
  d.setDate(d.getDate() + offset);
  return d.toISOString().split("T")[0];
}

const RESCHEDULE_OPTIONS = [
  { label: "Bugun", offset: 0 },
  { label: "Ertaga", offset: 1 },
  { label: "2 kundan", offset: 2 },
  { label: "Keyingi hafta", offset: 7 },
];

export default function TaskDetailModal({
  task,
  onComplete,
  onReschedule,
  onDelete,
  onClose,
}: TaskDetailModalProps) {
  const router = useRouter();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [showReschedule, setShowReschedule] = useState(false);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, []);

  const priority = PRIORITY_CONFIG[task.priority] || PRIORITY_CONFIG.medium;
  const diff = DIFFICULTY_CONFIG[task.difficulty] || DIFFICULTY_CONFIG.medium;

  const today = new Date().toISOString().split("T")[0];
  const isOverdue = task.planned_date < today && task.status === "pending";

  return (
    <div className="fixed inset-0 bg-black/60 z-[60] flex items-end" onClick={onClose}>
      <div
        className="w-full bg-gray-900 rounded-t-2xl animate-slide-up max-h-[85vh] overflow-y-auto overscroll-contain"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 bg-gray-700 rounded-full" />
        </div>

        <div className="p-5 space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              {isOverdue && (
                <span className="text-[9px] text-red-400 bg-red-900/30 px-2 py-0.5 rounded-full font-medium">
                  Muddati o'tgan
                </span>
              )}
              <h2 className="font-bold text-lg mt-1 leading-tight">{task.title}</h2>
            </div>
            <button onClick={onClose} className="text-gray-500 hover:text-white p-1 shrink-0">
              <X size={20} />
            </button>
          </div>

          {/* Info cards */}
          <div className="grid grid-cols-3 gap-2">
            <div className={`rounded-xl p-3 ${priority.bg}`}>
              <p className="text-[9px] text-gray-500 uppercase tracking-wide">Muhimlik</p>
              <p className={`text-sm font-semibold mt-0.5 ${priority.color}`}>{priority.label}</p>
            </div>
            <div className="bg-gray-800 rounded-xl p-3">
              <p className="text-[9px] text-gray-500 uppercase tracking-wide">Qiyinlik</p>
              <p className="text-sm font-semibold mt-0.5">{diff.emoji} {diff.label}</p>
            </div>
            <div className="bg-gray-800 rounded-xl p-3">
              <p className="text-[9px] text-gray-500 uppercase tracking-wide">XP</p>
              <p className="text-sm font-semibold mt-0.5 text-blue-400 flex items-center gap-1">
                <Zap size={12} /> +{diff.xp}
              </p>
            </div>
          </div>

          {/* Date + time row */}
          <div className="flex gap-2">
            <div className={`flex-1 rounded-xl p-3 flex items-center gap-2 ${isOverdue ? "bg-red-900/20 border border-red-900/30" : "bg-gray-800"}`}>
              <CalendarDays size={14} className={isOverdue ? "text-red-400" : "text-gray-500"} />
              <span className={`text-sm ${isOverdue ? "text-red-400" : ""}`}>{task.planned_date}</span>
            </div>
            {task.estimated_minutes && (
              <div className="bg-gray-800 rounded-xl p-3 flex items-center gap-2">
                <Clock size={14} className="text-gray-500" />
                <span className="text-sm">{task.estimated_minutes} min</span>
              </div>
            )}
          </div>

          {/* Category */}
          {task.category && (
            <div className="bg-gray-800 rounded-xl p-3">
              <p className="text-[9px] text-gray-500 uppercase tracking-wide">Kategoriya</p>
              <p className="text-sm mt-0.5 capitalize">{task.category}</p>
            </div>
          )}

          {/* Notes */}
          {task.notes && (
            <div className="bg-gray-800 rounded-xl p-3">
              <p className="text-[9px] text-gray-500 uppercase tracking-wide mb-1">Izoh</p>
              <p className="text-sm text-gray-300 whitespace-pre-wrap">{task.notes}</p>
            </div>
          )}

          {/* Actions — Pending */}
          {task.status === "pending" && (
            <div className="space-y-2 pt-1">
              {/* Complete */}
              <button
                onClick={() => { haptic.heavy(); onComplete(task.id); onClose(); }}
                className="w-full bg-green-600 rounded-xl py-3.5 font-semibold text-sm flex items-center justify-center gap-2 hover:bg-green-500 active:scale-[0.98] transition-all"
              >
                <Check size={18} /> Bajarildi · +{diff.xp}XP
              </button>

              {/* Focus link */}
              {task.estimated_minutes && task.estimated_minutes >= 15 && (
                <button
                  onClick={() => { router.push("/focus"); onClose(); }}
                  className="w-full bg-purple-600/20 border border-purple-700/30 rounded-xl py-3 text-sm flex items-center justify-center gap-2 text-purple-400 hover:bg-purple-600/30 transition-colors"
                >
                  <Play size={14} /> Fokus sessiya boshlash
                </button>
              )}

              {/* Reschedule */}
              {!showReschedule ? (
                <div className="flex gap-2">
                  <button
                    onClick={() => { setShowReschedule(true); haptic.light(); }}
                    className="flex-1 bg-gray-800 rounded-xl py-3 text-sm flex items-center justify-center gap-2 hover:bg-gray-700 transition-colors"
                  >
                    <CalendarDays size={14} /> Ko'chirish
                  </button>
                  {confirmDelete ? (
                    <button
                      onClick={() => { haptic.heavy(); onDelete(task.id); onClose(); }}
                      className="flex-1 bg-red-600 rounded-xl py-3 text-sm flex items-center justify-center gap-2 font-medium"
                    >
                      Tasdiqlash
                    </button>
                  ) : (
                    <button
                      onClick={() => { setConfirmDelete(true); haptic.light(); }}
                      className="bg-gray-800 rounded-xl py-3 px-4 text-sm flex items-center justify-center hover:bg-gray-700 transition-colors text-red-400"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              ) : (
                <div className="bg-gray-800 rounded-xl p-3 space-y-2">
                  <p className="text-xs text-gray-400 font-medium">Qachonga ko'chirish?</p>
                  <div className="grid grid-cols-2 gap-2">
                    {RESCHEDULE_OPTIONS.map((opt) => {
                      const targetDate = getRelativeDate(opt.offset);
                      if (targetDate === task.planned_date) return null;
                      return (
                        <button
                          key={opt.offset}
                          onClick={() => {
                            haptic.medium();
                            onReschedule(task.id, targetDate);
                            onClose();
                          }}
                          className="bg-gray-700 hover:bg-gray-600 rounded-lg py-2.5 text-xs font-medium flex items-center justify-center gap-1 transition-colors"
                        >
                          {opt.label} <ArrowRight size={10} className="text-gray-500" />
                        </button>
                      );
                    })}
                  </div>
                  <button
                    onClick={() => setShowReschedule(false)}
                    className="w-full text-xs text-gray-500 py-1 hover:text-white transition-colors"
                  >
                    Bekor qilish
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Completed state */}
          {task.status === "completed" && (
            <div className="bg-green-900/20 rounded-xl p-4 text-center border border-green-800/30">
              <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-2">
                <Check size={24} className="text-green-400" />
              </div>
              <p className="text-green-400 font-semibold">Bajarilgan</p>
              <p className="text-xs text-gray-500 mt-1">+{task.xp_awarded} XP olindi</p>
              {task.completed_at && (
                <p className="text-[10px] text-gray-600 mt-1">
                  {new Date(task.completed_at).toLocaleString("uz-UZ")}
                </p>
              )}
            </div>
          )}

          {/* Safe area */}
          <div className="h-2" />
        </div>
      </div>
    </div>
  );
}
