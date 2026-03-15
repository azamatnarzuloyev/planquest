"use client";

import { useState, useEffect } from "react";
import { X } from "lucide-react";

interface AddHabitSheetProps {
  onAdd: (habit: {
    title: string;
    type: string;
    target_value?: number;
    frequency?: string;
    icon?: string;
  }) => void;
  onClose: () => void;
}

const TEMPLATES = [
  { title: "Kitob o'qish", type: "duration", target_value: 30, icon: "📚", frequency: "daily" },
  { title: "Sport", type: "yes_no", target_value: 1, icon: "💪", frequency: "daily" },
  { title: "Meditatsiya", type: "duration", target_value: 10, icon: "🧘", frequency: "daily" },
  { title: "Suv ichish", type: "count", target_value: 8, icon: "💧", frequency: "daily" },
  { title: "Kundalik yozish", type: "yes_no", target_value: 1, icon: "✍️", frequency: "daily" },
  { title: "Ertalab yugurish", type: "yes_no", target_value: 1, icon: "🏃", frequency: "weekdays" },
];

const TYPES = [
  { value: "yes_no", label: "Ha/Yo'q", desc: "Bir tap bilan" },
  { value: "count", label: "Hisob", desc: "Nechta?" },
  { value: "duration", label: "Vaqt", desc: "Necha min?" },
  { value: "avoid", label: "Oldini olish", desc: "Qilmaslik" },
];

const ICONS = ["📚", "💪", "🧘", "💧", "✍️", "🏃", "🎯", "💤", "🍎", "🧹", "💻", "🎵"];

export default function AddHabitSheet({ onAdd, onClose }: AddHabitSheetProps) {
  const [mode, setMode] = useState<"templates" | "custom">("templates");
  const [title, setTitle] = useState("");
  const [type, setType] = useState("yes_no");
  const [targetValue, setTargetValue] = useState("1");
  const [icon, setIcon] = useState("✅");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Lock body scroll when sheet is open
  useEffect(() => {
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = original;
    };
  }, []);

  async function handleSubmit() {
    if (!title.trim() || title.length < 2 || isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onAdd({
        title: title.trim(),
        type,
        target_value: parseInt(targetValue) || 1,
        icon,
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleTemplate(t: typeof TEMPLATES[0]) {
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onAdd(t);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/60 z-[60] flex items-end"
      onClick={onClose}
    >
      <div
        className="w-full bg-gray-900 rounded-t-2xl animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header — sticky */}
        <div className="flex items-center justify-between p-5 pb-3">
          <h2 className="font-bold text-lg">Yangi habit</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white p-1">
            <X size={20} />
          </button>
        </div>

        {/* Scrollable content */}
        <div
          className="px-5 pb-8 space-y-4 overflow-y-auto overscroll-contain"
          style={{ maxHeight: "calc(90vh - 60px)" }}
        >
          {/* Mode toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setMode("templates")}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                mode === "templates" ? "bg-blue-600" : "bg-gray-800 text-gray-400"
              }`}
            >
              Shablonlar
            </button>
            <button
              onClick={() => setMode("custom")}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                mode === "custom" ? "bg-blue-600" : "bg-gray-800 text-gray-400"
              }`}
            >
              O'zim yaratish
            </button>
          </div>

          {mode === "templates" ? (
            <div className="space-y-2">
              {TEMPLATES.map((t, i) => (
                <button
                  key={i}
                  onClick={() => handleTemplate(t)}
                  disabled={isSubmitting}
                  className="w-full bg-gray-800 rounded-xl p-3.5 flex items-center gap-3 hover:bg-gray-700 active:bg-gray-600 transition-colors text-left disabled:opacity-50"
                >
                  <span className="text-2xl">{t.icon}</span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{t.title}</p>
                    <p className="text-[10px] text-gray-500">
                      {t.type === "duration"
                        ? `${t.target_value} min/kun`
                        : t.type === "count"
                          ? `${t.target_value} marta/kun`
                          : "Har kuni"}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Habit nomi..."
                className="w-full bg-gray-800 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />

              <div>
                <p className="text-xs text-gray-400 mb-2">Turi</p>
                <div className="grid grid-cols-2 gap-2">
                  {TYPES.map((t) => (
                    <button
                      key={t.value}
                      onClick={() => setType(t.value)}
                      className={`p-2.5 rounded-xl text-left transition-colors ${
                        type === t.value ? "bg-blue-600" : "bg-gray-800 text-gray-400"
                      }`}
                    >
                      <p className="text-xs font-medium">{t.label}</p>
                      <p className="text-[10px] opacity-60">{t.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {(type === "count" || type === "duration") && (
                <div>
                  <p className="text-xs text-gray-400 mb-2">
                    {type === "count" ? "Maqsad soni" : "Maqsad (minutlar)"}
                  </p>
                  <input
                    type="number"
                    value={targetValue}
                    onChange={(e) => setTargetValue(e.target.value)}
                    placeholder={type === "count" ? "8" : "30"}
                    min={1}
                    className="w-full bg-gray-800 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}

              <div>
                <p className="text-xs text-gray-400 mb-2">Emoji</p>
                <div className="flex flex-wrap gap-2">
                  {ICONS.map((e) => (
                    <button
                      key={e}
                      onClick={() => setIcon(e)}
                      className={`w-10 h-10 rounded-lg text-xl flex items-center justify-center transition-colors ${
                        icon === e ? "bg-blue-600" : "bg-gray-800"
                      }`}
                    >
                      {e}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleSubmit}
                disabled={!title.trim() || title.length < 2 || isSubmitting}
                className="w-full bg-blue-600 rounded-xl py-3.5 font-medium hover:bg-blue-500 disabled:opacity-40 transition-colors"
              >
                {isSubmitting ? "Yaratilmoqda..." : "Yaratish"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
