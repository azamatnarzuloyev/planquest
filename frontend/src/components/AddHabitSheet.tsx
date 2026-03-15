"use client";

import { useState, useEffect, useRef } from "react";
import { X } from "lucide-react";
import { haptic } from "@/lib/telegram";

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
  { title: "Kod yozish", type: "duration", target_value: 60, icon: "💻", frequency: "weekdays" },
  { title: "Yaxshi uxlash", type: "yes_no", target_value: 1, icon: "😴", frequency: "daily" },
];

const TYPES = [
  { value: "yes_no", label: "Ha/Yo'q", desc: "Bir tap bilan bajariladi", emoji: "✅" },
  { value: "count", label: "Hisob", desc: "Nechta bajarilganini kiritasiz", emoji: "🔢" },
  { value: "duration", label: "Vaqt", desc: "Necha daqiqa sarfladingiz", emoji: "⏱️" },
];

const FREQUENCIES = [
  { value: "daily", label: "Har kuni", desc: "7/7 kun" },
  { value: "weekdays", label: "Ish kunlari", desc: "Du-Ju" },
  { value: "3_per_week", label: "Haftada 3", desc: "Ixtiyoriy 3 kun" },
  { value: "custom", label: "Maxsus", desc: "O'zim tanlash" },
];

const WEEK_DAYS = [
  { key: 0, label: "Du" },
  { key: 1, label: "Se" },
  { key: 2, label: "Cho" },
  { key: 3, label: "Pa" },
  { key: 4, label: "Ju" },
  { key: 5, label: "Sha" },
  { key: 6, label: "Ya" },
];

const ICONS = ["📚", "💪", "🧘", "💧", "✍️", "🏃", "💻", "🎯", "😴", "🍎", "🧹", "🎵", "🌅", "🧠", "🎨", "📱"];

const TARGET_PRESETS: Record<string, number[]> = {
  count: [3, 5, 8, 10, 15, 20],
  duration: [5, 10, 15, 20, 30, 45, 60, 90],
};

export default function AddHabitSheet({ onAdd, onClose }: AddHabitSheetProps) {
  const [step, setStep] = useState<"choose" | "custom">("choose");
  const [title, setTitle] = useState("");
  const [type, setType] = useState("yes_no");
  const [targetValue, setTargetValue] = useState(1);
  const [frequency, setFrequency] = useState("daily");
  const [customDays, setCustomDays] = useState<number[]>([0, 1, 2, 3, 4]);
  const [icon, setIcon] = useState("✅");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, []);

  useEffect(() => {
    if (step === "custom") {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [step]);

  async function handleSubmit() {
    if (!title.trim() || title.length < 2 || isSubmitting) return;
    setIsSubmitting(true);
    haptic.medium();
    try {
      await onAdd({
        title: title.trim(),
        type,
        target_value: type === "yes_no" ? 1 : targetValue,
        frequency,
        icon,
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleTemplate(t: typeof TEMPLATES[0]) {
    if (isSubmitting) return;
    setIsSubmitting(true);
    haptic.medium();
    try {
      await onAdd(t);
    } finally {
      setIsSubmitting(false);
    }
  }

  function toggleDay(day: number) {
    haptic.light();
    setCustomDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day].sort()
    );
  }

  return (
    <div className="fixed inset-0 bg-black/60 z-[60] flex items-end" onClick={onClose}>
      <div
        className="w-full bg-gray-900 rounded-t-2xl animate-slide-up max-h-[92vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-1 shrink-0">
          <div className="w-10 h-1 bg-gray-700 rounded-full" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 shrink-0">
          <h2 className="font-bold text-lg">
            {step === "choose" ? "Yangi habit" : "Habit sozlash"}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white p-1">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto overscroll-contain px-5 pb-8">
          {step === "choose" ? (
            <div className="space-y-4">
              {/* Templates */}
              <div>
                <p className="text-xs text-gray-500 mb-2 font-medium">Tayyor shablonlar</p>
                <div className="grid grid-cols-2 gap-2">
                  {TEMPLATES.map((t, i) => (
                    <button
                      key={i}
                      onClick={() => handleTemplate(t)}
                      disabled={isSubmitting}
                      className="bg-gray-800 hover:bg-gray-700 active:scale-[0.97] rounded-xl p-3 text-left transition-all disabled:opacity-50"
                    >
                      <span className="text-2xl">{t.icon}</span>
                      <p className="text-sm font-medium mt-1.5">{t.title}</p>
                      <p className="text-[10px] text-gray-500 mt-0.5">
                        {t.type === "duration" ? `${t.target_value} min` : t.type === "count" ? `${t.target_value} marta` : "Har kuni"}
                        {t.frequency === "weekdays" ? " · Du-Ju" : ""}
                      </p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Custom button */}
              <button
                onClick={() => { setStep("custom"); haptic.light(); }}
                className="w-full bg-blue-600/10 border border-blue-600/30 rounded-xl py-3.5 text-sm text-blue-400 font-medium hover:bg-blue-600/20 transition-colors"
              >
                O'zim yaratish →
              </button>
            </div>
          ) : (
            <div className="space-y-5">
              {/* Title + icon */}
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    const idx = ICONS.indexOf(icon);
                    setIcon(ICONS[(idx + 1) % ICONS.length]);
                    haptic.light();
                  }}
                  className="w-12 h-12 bg-gray-800 rounded-xl flex items-center justify-center text-2xl shrink-0 hover:bg-gray-700 transition-colors"
                >
                  {icon}
                </button>
                <input
                  ref={inputRef}
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Habit nomi"
                  maxLength={50}
                  className="flex-1 bg-gray-800 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Icon picker (collapsed, tap emoji to cycle) */}
              <div className="flex gap-1.5 flex-wrap">
                {ICONS.map((e) => (
                  <button
                    key={e}
                    onClick={() => { setIcon(e); haptic.light(); }}
                    className={`w-9 h-9 rounded-lg text-lg flex items-center justify-center transition-all ${
                      icon === e ? "bg-blue-600 scale-110" : "bg-gray-800/60 hover:bg-gray-800"
                    }`}
                  >
                    {e}
                  </button>
                ))}
              </div>

              {/* Type */}
              <div>
                <p className="text-xs text-gray-500 mb-2 font-medium">Turi</p>
                <div className="space-y-1.5">
                  {TYPES.map((t) => (
                    <button
                      key={t.value}
                      onClick={() => { setType(t.value); haptic.light(); if (t.value === "count") setTargetValue(5); if (t.value === "duration") setTargetValue(30); }}
                      className={`w-full p-3 rounded-xl text-left flex items-center gap-3 transition-all ${
                        type === t.value ? "bg-blue-600 ring-2 ring-blue-400 ring-offset-1 ring-offset-gray-900" : "bg-gray-800"
                      }`}
                    >
                      <span className="text-xl">{t.emoji}</span>
                      <div>
                        <p className="text-sm font-medium">{t.label}</p>
                        <p className="text-[10px] text-gray-400">{t.desc}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Target value */}
              {type !== "yes_no" && (
                <div>
                  <p className="text-xs text-gray-500 mb-2 font-medium">
                    {type === "count" ? "Kunlik maqsad" : "Kunlik vaqt (daqiqa)"}
                  </p>
                  <div className="flex gap-1.5 flex-wrap">
                    {(TARGET_PRESETS[type] || []).map((v) => (
                      <button
                        key={v}
                        onClick={() => { setTargetValue(v); haptic.light(); }}
                        className={`px-3.5 py-2 rounded-xl text-sm font-medium transition-all ${
                          targetValue === v ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400"
                        }`}
                      >
                        {type === "duration" && v >= 60 ? `${v / 60}h` : v}
                        {type === "duration" && v < 60 ? " min" : ""}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Frequency */}
              <div>
                <p className="text-xs text-gray-500 mb-2 font-medium">Qanchalik tez-tez?</p>
                <div className="grid grid-cols-2 gap-2">
                  {FREQUENCIES.map((f) => (
                    <button
                      key={f.value}
                      onClick={() => { setFrequency(f.value); haptic.light(); }}
                      className={`p-3 rounded-xl text-left transition-all ${
                        frequency === f.value ? "bg-blue-600" : "bg-gray-800 text-gray-400"
                      }`}
                    >
                      <p className="text-sm font-medium">{f.label}</p>
                      <p className="text-[10px] opacity-70">{f.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Custom days picker */}
              {frequency === "custom" && (
                <div>
                  <p className="text-xs text-gray-500 mb-2 font-medium">Qaysi kunlar?</p>
                  <div className="flex gap-1.5">
                    {WEEK_DAYS.map((d) => (
                      <button
                        key={d.key}
                        onClick={() => toggleDay(d.key)}
                        className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all ${
                          customDays.includes(d.key)
                            ? "bg-blue-600 text-white"
                            : "bg-gray-800 text-gray-500"
                        }`}
                      >
                        {d.label}
                      </button>
                    ))}
                  </div>
                  <p className="text-[10px] text-gray-600 mt-1 text-center">
                    {customDays.length} kun tanlandi
                  </p>
                </div>
              )}

              {/* Submit */}
              <button
                onClick={handleSubmit}
                disabled={!title.trim() || title.length < 2 || isSubmitting}
                className="w-full bg-blue-600 rounded-xl py-3.5 font-semibold text-sm hover:bg-blue-500 active:scale-[0.98] transition-all disabled:opacity-30 disabled:pointer-events-none"
              >
                {isSubmitting ? "Yaratilmoqda..." : "Habit yaratish"}
              </button>

              {/* Back */}
              <button
                onClick={() => setStep("choose")}
                className="w-full text-xs text-gray-500 py-1 hover:text-white transition-colors"
              >
                ← Shablonlarga qaytish
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
