"use client";

interface DayData {
  date: string;
  day: string;
  tasks: number;
  habits: number;
  total: number;
  is_today: boolean;
}

interface WeeklyChartProps {
  data: DayData[];
}

export default function WeeklyChart({ data }: WeeklyChartProps) {
  const maxVal = Math.max(...data.map((d) => d.total), 1);

  return (
    <div className="flex items-end justify-between gap-1.5 h-32">
      {data.map((day) => {
        const height = day.total > 0 ? Math.max((day.total / maxVal) * 100, 8) : 4;
        return (
          <div key={day.date} className="flex-1 flex flex-col items-center gap-1.5">
            {/* Count */}
            {day.total > 0 && (
              <span className="text-[10px] text-gray-500 font-mono">{day.total}</span>
            )}
            {/* Bar */}
            <div className="w-full flex flex-col justify-end" style={{ height: "80px" }}>
              <div
                className={`w-full rounded-t-md transition-all duration-500 ${
                  day.is_today
                    ? "bg-blue-500"
                    : day.total > 0
                      ? "bg-blue-600/50"
                      : "bg-gray-800"
                }`}
                style={{ height: `${height}%` }}
              />
            </div>
            {/* Day label */}
            <span
              className={`text-[10px] font-medium ${
                day.is_today ? "text-blue-400" : "text-gray-500"
              }`}
            >
              {day.day}
            </span>
          </div>
        );
      })}
    </div>
  );
}
