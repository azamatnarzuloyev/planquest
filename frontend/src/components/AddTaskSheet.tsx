"use client";

import { useState, useEffect } from "react";
import { X } from "lucide-react";

interface AddTaskSheetProps {
  date: string;
  onAdd: (task: {
    title: string;
    planned_date: string;
    priority: string;
    difficulty: string;
    estimated_minutes?: number;
  }) => void;
  onClose: () => void;
}

const PRIORITIES = [
  { value: "low", label: "Past", color: "bg-gray-600" },
  { value: "medium", label: "O'rta", color: "bg-blue-600" },
  { value: "high", label: "Yuqori", color: "bg-orange-500" },
  { value: "critical", label: "Muhim", color: "bg-red-500" },
];

const DIFFICULTIES = [
  { value: "trivial", label: "Juda oson" },
  { value: "easy", label: "Oson" },
  { value: "medium", label: "O'rta" },
  { value: "hard", label: "Qiyin" },
  { value: "epic", label: "Juda qiyin" },
];

export default function AddTaskSheet({ date, onAdd, onClose }: AddTaskSheetProps) {
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState("medium");
  const [difficulty, setDifficulty] = useState("medium");
  const [minutes, setMinutes] = useState("");

  // Lock body scroll
  useEffect(() => {
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = original; };
  }, []);

  function handleSubmit() {
    if (!title.trim() || title.length < 3) return;
    onAdd({
      title: title.trim(),
      planned_date: date,
      priority,
      difficulty,
      estimated_minutes: minutes ? parseInt(minutes) : undefined,
    });
  }

  return (
    <div className="fixed inset-0 bg-black/60 z-[60] flex items-end" onClick={onClose}>
      <div
        className="w-full bg-gray-900 rounded-t-2xl p-5 space-y-4 animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-lg">Yangi vazifa</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Title */}
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Vazifa nomi..."
          className="w-full bg-gray-800 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          autoFocus
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        />

        {/* Priority */}
        <div>
          <p className="text-xs text-gray-400 mb-2">Muhimlik</p>
          <div className="flex gap-2">
            {PRIORITIES.map((p) => (
              <button
                key={p.value}
                onClick={() => setPriority(p.value)}
                className={`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${
                  priority === p.value
                    ? `${p.color} text-white`
                    : "bg-gray-800 text-gray-400"
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Difficulty */}
        <div>
          <p className="text-xs text-gray-400 mb-2">Qiyinlik</p>
          <div className="flex gap-1.5">
            {DIFFICULTIES.map((d) => (
              <button
                key={d.value}
                onClick={() => setDifficulty(d.value)}
                className={`flex-1 py-2 rounded-lg text-[10px] font-medium transition-all ${
                  difficulty === d.value
                    ? "bg-blue-600 text-white"
                    : "bg-gray-800 text-gray-400"
                }`}
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>

        {/* Estimated time */}
        <div>
          <p className="text-xs text-gray-400 mb-2">Taxminiy vaqt (min)</p>
          <input
            type="number"
            value={minutes}
            onChange={(e) => setMinutes(e.target.value)}
            placeholder="30"
            min={1}
            max={480}
            className="w-full bg-gray-800 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={!title.trim() || title.length < 3}
          className="w-full bg-blue-600 rounded-xl py-3.5 font-medium hover:bg-blue-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Qo'shish
        </button>
      </div>
    </div>
  );
}
