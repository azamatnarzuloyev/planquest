"use client";

import { useMemo } from "react";

interface WeekCalendarProps {
  selectedDate: string; // YYYY-MM-DD
  onSelectDate: (date: string) => void;
}

const DAY_NAMES = ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"];

function toDateStr(d: Date): string {
  return d.toISOString().split("T")[0];
}

export default function WeekCalendar({ selectedDate, onSelectDate }: WeekCalendarProps) {
  const days = useMemo(() => {
    const today = new Date();
    const result = [];
    // Show 3 days before today and 7 days after (11 days total)
    for (let i = -3; i <= 7; i++) {
      const d = new Date(today);
      d.setDate(today.getDate() + i);
      result.push({
        date: toDateStr(d),
        dayNum: d.getDate(),
        dayName: DAY_NAMES[d.getDay() === 0 ? 6 : d.getDay() - 1],
        isToday: i === 0,
      });
    }
    return result;
  }, []);

  return (
    <div className="flex gap-1.5 overflow-x-auto pb-2 scrollbar-hide">
      {days.map((day) => {
        const isSelected = day.date === selectedDate;
        return (
          <button
            key={day.date}
            onClick={() => onSelectDate(day.date)}
            className={`flex flex-col items-center min-w-[40px] py-2 px-1.5 rounded-xl transition-all ${
              isSelected
                ? "bg-blue-600 text-white"
                : day.isToday
                  ? "bg-gray-800 text-white"
                  : "text-gray-500 hover:bg-gray-800/50"
            }`}
          >
            <span className="text-[10px] font-medium">{day.dayName}</span>
            <span className={`text-sm font-bold mt-0.5 ${isSelected ? "" : day.isToday ? "text-blue-400" : ""}`}>
              {day.dayNum}
            </span>
          </button>
        );
      })}
    </div>
  );
}
