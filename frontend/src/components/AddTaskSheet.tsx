"use client";

import { useState, useEffect, useRef } from "react";
import { X, Clock, Zap, ChevronDown, Bookmark, StickyNote } from "lucide-react";
import { haptic } from "@/lib/telegram";

interface AddTaskSheetProps {
  date: string;
  onAdd: (task: {
    title: string;
    planned_date: string;
    priority: string;
    difficulty: string;
    estimated_minutes?: number;
    notes?: string;
    category?: string;
  }) => void;
  onClose: () => void;
}

const PRIORITIES = [
  { value: "low", label: "Past", color: "bg-gray-600", ring: "ring-gray-500" },
  { value: "medium", label: "O'rta", color: "bg-blue-600", ring: "ring-blue-500" },
  { value: "high", label: "Yuqori", color: "bg-orange-500", ring: "ring-orange-400" },
  { value: "critical", label: "Muhim", color: "bg-red-500", ring: "ring-red-400" },
];

const DIFFICULTIES = [
  { value: "trivial", label: "Juda oson", xp: 5, emoji: "🟢" },
  { value: "easy", label: "Oson", xp: 10, emoji: "🔵" },
  { value: "medium", label: "O'rta", xp: 20, emoji: "🟡" },
  { value: "hard", label: "Qiyin", xp: 35, emoji: "🟠" },
  { value: "epic", label: "Juda qiyin", xp: 50, emoji: "🔴" },
];

const TIME_PRESETS = [5, 10, 15, 25, 30, 45, 60, 90, 120];

const CATEGORIES = [
  { value: "work", label: "💼 Ish", color: "bg-blue-900/40 border-blue-700/40" },
  { value: "study", label: "📚 O'qish", color: "bg-purple-900/40 border-purple-700/40" },
  { value: "health", label: "💪 Salomatlik", color: "bg-green-900/40 border-green-700/40" },
  { value: "personal", label: "🏠 Shaxsiy", color: "bg-yellow-900/40 border-yellow-700/40" },
  { value: "project", label: "🚀 Loyiha", color: "bg-cyan-900/40 border-cyan-700/40" },
];

const QUICK_TEMPLATES = [
  { title: "📧 Email tekshirish", priority: "low", difficulty: "trivial", minutes: 10 },
  { title: "📋 Meeting tayyorgarlik", priority: "medium", difficulty: "easy", minutes: 15 },
  { title: "💻 Kod yozish", priority: "high", difficulty: "hard", minutes: 60 },
  { title: "📖 Kitob o'qish", priority: "low", difficulty: "easy", minutes: 30 },
  { title: "🏃 Sport", priority: "medium", difficulty: "medium", minutes: 45 },
  { title: "📝 Hisobot yozish", priority: "high", difficulty: "medium", minutes: 30 },
];

export default function AddTaskSheet({ date, onAdd, onClose }: AddTaskSheetProps) {
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState("medium");
  const [difficulty, setDifficulty] = useState("medium");
  const [minutes, setMinutes] = useState<number | null>(null);
  const [notes, setNotes] = useState("");
  const [category, setCategory] = useState<string | null>(null);
  const [showMore, setShowMore] = useState(false);
  const [showTemplates, setShowTemplates] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    setTimeout(() => inputRef.current?.focus(), 300);
    return () => { document.body.style.overflow = ""; };
  }, []);

  function handleSubmit() {
    if (!title.trim() || title.length < 2) return;
    haptic.medium();
    onAdd({
      title: title.trim(),
      planned_date: date,
      priority,
      difficulty,
      estimated_minutes: minutes || undefined,
      notes: notes.trim() || undefined,
      category: category || undefined,
    });
  }

  function applyTemplate(t: typeof QUICK_TEMPLATES[0]) {
    haptic.light();
    setTitle(t.title);
    setPriority(t.priority);
    setDifficulty(t.difficulty);
    setMinutes(t.minutes);
    setShowTemplates(false);
  }

  const selectedDiff = DIFFICULTIES.find((d) => d.value === difficulty);

  return (
    <div className="fixed inset-0 bg-black/60 z-[60] flex items-end" onClick={onClose}>
      <div
        className="w-full bg-gray-900 rounded-t-2xl animate-slide-up max-h-[90vh] overflow-y-auto overscroll-contain"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Handle bar */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 bg-gray-700 rounded-full" />
        </div>

        <div className="p-5 space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-lg">Yangi vazifa</h2>
            <button onClick={onClose} className="text-gray-500 hover:text-white p-1">
              <X size={20} />
            </button>
          </div>

          {/* Quick Templates */}
          {showTemplates && !title && (
            <div>
              <p className="text-xs text-gray-500 mb-2">Tez qo'shish</p>
              <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
                {QUICK_TEMPLATES.map((t, i) => (
                  <button
                    key={i}
                    onClick={() => applyTemplate(t)}
                    className="shrink-0 bg-gray-800 hover:bg-gray-700 rounded-xl px-3 py-2 text-xs transition-colors whitespace-nowrap"
                  >
                    {t.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Title Input */}
          <div className="relative">
            <input
              ref={inputRef}
              type="text"
              value={title}
              onChange={(e) => { setTitle(e.target.value); setShowTemplates(false); }}
              placeholder="Nima qilish kerak?"
              maxLength={100}
              className="w-full bg-gray-800 rounded-xl px-4 py-3.5 text-sm outline-none focus:ring-2 focus:ring-blue-500 pr-12"
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            />
            {title.length > 0 && (
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-gray-600">
                {title.length}/100
              </span>
            )}
          </div>

          {/* Priority — pill style */}
          <div>
            <p className="text-xs text-gray-500 mb-2">Muhimlik</p>
            <div className="flex gap-2">
              {PRIORITIES.map((p) => (
                <button
                  key={p.value}
                  onClick={() => { setPriority(p.value); haptic.light(); }}
                  className={`flex-1 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    priority === p.value
                      ? `${p.color} text-white ring-2 ${p.ring} ring-offset-1 ring-offset-gray-900 scale-105`
                      : "bg-gray-800 text-gray-400 hover:bg-gray-750"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Difficulty — with XP preview */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs text-gray-500">Qiyinlik</p>
              <p className="text-xs text-blue-400 flex items-center gap-1">
                <Zap size={10} /> +{selectedDiff?.xp || 20} XP
              </p>
            </div>
            <div className="flex gap-1.5">
              {DIFFICULTIES.map((d) => (
                <button
                  key={d.value}
                  onClick={() => { setDifficulty(d.value); haptic.light(); }}
                  className={`flex-1 py-2 rounded-xl text-[11px] font-medium transition-all flex flex-col items-center gap-0.5 ${
                    difficulty === d.value
                      ? "bg-blue-600 text-white scale-105"
                      : "bg-gray-800 text-gray-400 hover:bg-gray-750"
                  }`}
                >
                  <span>{d.emoji}</span>
                  <span>{d.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Time — preset chips */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Clock size={12} className="text-gray-500" />
              <p className="text-xs text-gray-500">Taxminiy vaqt</p>
              {minutes && (
                <button onClick={() => setMinutes(null)} className="text-[10px] text-red-400 ml-auto">
                  Tozalash
                </button>
              )}
            </div>
            <div className="flex gap-1.5 flex-wrap">
              {TIME_PRESETS.map((t) => (
                <button
                  key={t}
                  onClick={() => { setMinutes(t); haptic.light(); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    minutes === t
                      ? "bg-blue-600 text-white"
                      : "bg-gray-800 text-gray-400 hover:bg-gray-750"
                  }`}
                >
                  {t >= 60 ? `${t / 60}h` : `${t}m`}
                </button>
              ))}
            </div>
          </div>

          {/* Expand more options */}
          <button
            onClick={() => { setShowMore(!showMore); haptic.light(); }}
            className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-300 transition-colors w-full"
          >
            <ChevronDown size={14} className={`transition-transform ${showMore ? "rotate-180" : ""}`} />
            {showMore ? "Kamroq" : "Ko'proq sozlamalar"}
          </button>

          {showMore && (
            <div className="space-y-4 animate-fade-in">
              {/* Category */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Bookmark size={12} className="text-gray-500" />
                  <p className="text-xs text-gray-500">Kategoriya</p>
                </div>
                <div className="flex gap-1.5 flex-wrap">
                  {CATEGORIES.map((c) => (
                    <button
                      key={c.value}
                      onClick={() => { setCategory(category === c.value ? null : c.value); haptic.light(); }}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${
                        category === c.value
                          ? `${c.color} text-white`
                          : "bg-gray-800 border-transparent text-gray-400"
                      }`}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <StickyNote size={12} className="text-gray-500" />
                  <p className="text-xs text-gray-500">Izoh</p>
                </div>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Qo'shimcha ma'lumot..."
                  maxLength={500}
                  rows={3}
                  className="w-full bg-gray-800 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>
            </div>
          )}

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={!title.trim() || title.length < 2}
            className="w-full bg-blue-600 rounded-xl py-3.5 font-semibold text-sm hover:bg-blue-500 active:scale-[0.98] transition-all disabled:opacity-30 disabled:pointer-events-none flex items-center justify-center gap-2"
          >
            Qo'shish
            {minutes && <span className="text-blue-200 text-xs">· {minutes}m</span>}
            {selectedDiff && <span className="text-blue-200 text-xs">· +{selectedDiff.xp}XP</span>}
          </button>

          {/* Safe area spacer */}
          <div className="h-2" />
        </div>
      </div>
    </div>
  );
}
