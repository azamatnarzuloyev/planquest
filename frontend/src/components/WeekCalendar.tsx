"use client";

import { useMemo } from "react";

interface WeekCalendarProps {
  selectedDate: string;
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
    for (let i = -3; i <= 7; i++) {
      const d = new Date(today);
      d.setDate(today.getDate() + i);
      const dayIndex = d.getDay() === 0 ? 6 : d.getDay() - 1;
      result.push({
        date: toDateStr(d),
        dayNum: d.getDate(),
        dayName: DAY_NAMES[dayIndex],
        isToday: i === 0,
        isPast: i < 0,
        isWeekend: d.getDay() === 0 || d.getDay() === 6,
        monthShort: i === -3 || d.getDate() === 1
          ? d.toLocaleDateString("uz-UZ", { month: "short" }).slice(0, 3)
          : null,
      });
    }
    return result;
  }, []);

  return (
    <div className="relative">
      <div className="flex gap-1 overflow-x-auto pb-2 no-scrollbar scroll-smooth">
        {days.map((day) => {
          const isSelected = day.date === selectedDate;
          return (
            <button
              key={day.date}
              onClick={() => onSelectDate(day.date)}
              className={`flex flex-col items-center min-w-[42px] py-2 px-1.5 rounded-xl transition-all relative ${
                isSelected
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30 scale-105"
                  : day.isToday
                    ? "bg-gray-800 text-white ring-1 ring-blue-500/30"
                    : day.isPast
                      ? "text-gray-600 hover:bg-gray-800/40"
                      : day.isWeekend
                        ? "text-gray-500 hover:bg-gray-800/40"
                        : "text-gray-400 hover:bg-gray-800/50"
              }`}
            >
              {/* Month label */}
              {day.monthShort && (
                <span className="text-[8px] text-gray-600 absolute -top-0.5 font-medium">
                  {day.monthShort}
                </span>
              )}
              <span className={`text-[10px] font-medium ${isSelected ? "text-blue-100" : ""}`}>
                {day.dayName}
              </span>
              <span className={`text-sm font-bold mt-0.5 ${
                isSelected ? "text-white" : day.isToday ? "text-blue-400" : ""
              }`}>
                {day.dayNum}
              </span>
              {/* Today dot */}
              {day.isToday && !isSelected && (
                <div className="w-1 h-1 rounded-full bg-blue-400 mt-0.5" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
