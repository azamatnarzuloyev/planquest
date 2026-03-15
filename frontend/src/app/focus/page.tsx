"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { startFocus, endFocus, getActiveFocus, getFocusStats, getTasks } from "@/lib/api";
import type { FocusEndResponse, FocusSessionResponse, FocusStatsResponse, TaskResponse } from "@/types";
import { haptic } from "@/lib/telegram";
import { Play, Pause, Square, Clock, Zap, Link, ChevronDown, Trophy, Timer, Flame } from "lucide-react";

type FocusMode = "pomodoro_25" | "deep_50" | "ultra_90" | "custom";

interface ModeOption {
  key: FocusMode;
  label: string;
  minutes: number;
  icon: string;
}

const MODES: ModeOption[] = [
  { key: "pomodoro_25", label: "Pomodoro", minutes: 25, icon: "🍅" },
  { key: "deep_50", label: "Deep Work", minutes: 50, icon: "🧠" },
  { key: "ultra_90", label: "Ultra", minutes: 90, icon: "🚀" },
  { key: "custom", label: "Custom", minutes: 0, icon: "⚙️" },
];

const BREAK_OPTIONS = [
  { label: "5 min tanaffus", minutes: 5 },
  { label: "15 min tanaffus", minutes: 15 },
];

type Phase = "select" | "active" | "paused" | "completed" | "break";

export default function FocusPage() {
  // State
  const [phase, setPhase] = useState<Phase>("select");
  const [mode, setMode] = useState<FocusMode>("pomodoro_25");
  const [customMinutes, setCustomMinutes] = useState(30);
  const [linkedTaskId, setLinkedTaskId] = useState<string | undefined>();
  const [showTaskPicker, setShowTaskPicker] = useState(false);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [session, setSession] = useState<FocusSessionResponse | null>(null);
  const [endResult, setEndResult] = useState<FocusEndResponse | null>(null);
  const [stats, setStats] = useState<FocusStatsResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Timer state
  const [elapsed, setElapsed] = useState(0); // seconds elapsed
  const [plannedSeconds, setPlannedSeconds] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number>(0);
  const pausedElapsedRef = useRef<number>(0);

  // Break timer
  const [breakSeconds, setBreakSeconds] = useState(0);
  const [breakTotal, setBreakTotal] = useState(0);
  const breakTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Load stats and check active session on mount
  useEffect(() => {
    getFocusStats().then(setStats).catch(() => {});
    getActiveFocus().then((s) => {
      if (s) {
        setSession(s);
        const startedAt = new Date(s.started_at).getTime();
        const elapsedSoFar = Math.floor((Date.now() - startedAt) / 1000);
        setElapsed(elapsedSoFar);
        setPlannedSeconds(s.planned_duration * 60);
        startTimeRef.current = Date.now() - elapsedSoFar * 1000;
        pausedElapsedRef.current = 0;
        setPhase("active");
        startTimer();
      }
    }).catch(() => {});

    const today = new Date().toISOString().split("T")[0];
    getTasks({ date: today, status: "pending" }).then(setTasks).catch(() => {});

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (breakTimerRef.current) clearInterval(breakTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const startTimer = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      const now = Date.now();
      setElapsed(Math.floor((now - startTimeRef.current) / 1000));
    }, 200);
  }, []);

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  // Get planned duration for selected mode
  function getPlannedMinutes(): number {
    if (mode === "custom") return customMinutes;
    return MODES.find((m) => m.key === mode)?.minutes || 25;
  }

  // --- Actions ---
  async function handleStart() {
    setLoading(true);
    haptic.medium();
    try {
      const planned = getPlannedMinutes();
      const s = await startFocus(mode, linkedTaskId);
      setSession(s);
      setPlannedSeconds(planned * 60);
      setElapsed(0);
      startTimeRef.current = Date.now();
      pausedElapsedRef.current = 0;
      setPhase("active");
      startTimer();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Xatolik";
      haptic.error();
      alert(msg);
    } finally {
      setLoading(false);
    }
  }

  function handlePause() {
    haptic.light();
    stopTimer();
    pausedElapsedRef.current = elapsed;
    setPhase("paused");
  }

  function handleResume() {
    haptic.light();
    startTimeRef.current = Date.now() - pausedElapsedRef.current * 1000;
    startTimer();
    setPhase("active");
  }

  async function handleEnd() {
    if (!session) return;
    setLoading(true);
    haptic.heavy();
    stopTimer();
    try {
      const result = await endFocus(session.id);
      setEndResult(result);
      setPhase("completed");
      // Refresh stats
      getFocusStats().then(setStats).catch(() => {});
    } catch {
      haptic.error();
    } finally {
      setLoading(false);
    }
  }

  function handleStartBreak(minutes: number) {
    haptic.light();
    setBreakTotal(minutes * 60);
    setBreakSeconds(minutes * 60);
    setPhase("break");
    if (breakTimerRef.current) clearInterval(breakTimerRef.current);
    breakTimerRef.current = setInterval(() => {
      setBreakSeconds((prev) => {
        if (prev <= 1) {
          if (breakTimerRef.current) clearInterval(breakTimerRef.current);
          haptic.success();
          setPhase("select");
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }

  function handleReset() {
    haptic.light();
    setPhase("select");
    setSession(null);
    setEndResult(null);
    setElapsed(0);
    setLinkedTaskId(undefined);
    if (breakTimerRef.current) clearInterval(breakTimerRef.current);
  }

  // --- Formatters ---
  function formatTime(totalSeconds: number): string {
    const m = Math.floor(totalSeconds / 60);
    const s = totalSeconds % 60;
    return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  }

  // Remaining time (countdown)
  const remaining = Math.max(0, plannedSeconds - elapsed);
  const progressPercent = plannedSeconds > 0 ? Math.min(100, (elapsed / plannedSeconds) * 100) : 0;
  const isOvertime = elapsed > plannedSeconds;

  // SVG ring
  const ringRadius = 120;
  const ringCircumference = 2 * Math.PI * ringRadius;
  const ringOffset = ringCircumference - (progressPercent / 100) * ringCircumference;

  const linkedTask = tasks.find((t) => t.id === linkedTaskId);

  return (
    <div className="flex flex-col min-h-[calc(100vh-80px)]">
      {/* === SELECT PHASE === */}
      {phase === "select" && (
        <div className="flex-1 p-4 space-y-5">
          {/* Daily stats */}
          {stats && (
            <div className="flex gap-3">
              <div className="flex-1 bg-gray-900 rounded-xl p-3 text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Timer size={14} className="text-blue-400" />
                  <span className="text-xs text-gray-400">Bugun</span>
                </div>
                <p className="text-lg font-bold">{stats.today_minutes}<span className="text-xs text-gray-500 ml-1">min</span></p>
              </div>
              <div className="flex-1 bg-gray-900 rounded-xl p-3 text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Flame size={14} className="text-orange-400" />
                  <span className="text-xs text-gray-400">Sessiyalar</span>
                </div>
                <p className="text-lg font-bold">{stats.today_sessions}</p>
              </div>
              <div className="flex-1 bg-gray-900 rounded-xl p-3 text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Clock size={14} className="text-green-400" />
                  <span className="text-xs text-gray-400">Hafta</span>
                </div>
                <p className="text-lg font-bold">{stats.week_minutes}<span className="text-xs text-gray-500 ml-1">min</span></p>
              </div>
            </div>
          )}

          {/* Mode selector */}
          <div>
            <h2 className="text-sm font-semibold text-gray-400 mb-3">Rejim tanlang</h2>
            <div className="grid grid-cols-4 gap-2">
              {MODES.map((m) => (
                <button
                  key={m.key}
                  onClick={() => { setMode(m.key); haptic.light(); }}
                  className={`rounded-xl p-3 text-center transition-all ${
                    mode === m.key
                      ? "bg-blue-600 ring-2 ring-blue-400 scale-105"
                      : "bg-gray-900 hover:bg-gray-800"
                  }`}
                >
                  <span className="text-xl">{m.icon}</span>
                  <p className="text-xs font-medium mt-1">{m.label}</p>
                  {m.minutes > 0 && <p className="text-[10px] text-gray-400">{m.minutes} min</p>}
                </button>
              ))}
            </div>
          </div>

          {/* Custom duration slider */}
          {mode === "custom" && (
            <div className="bg-gray-900 rounded-xl p-4">
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Davomiylik</span>
                <span className="text-sm font-bold text-blue-400">{customMinutes} min</span>
              </div>
              <input
                type="range"
                min={5}
                max={180}
                step={5}
                value={customMinutes}
                onChange={(e) => setCustomMinutes(Number(e.target.value))}
                className="w-full accent-blue-500"
              />
              <div className="flex justify-between text-[10px] text-gray-600 mt-1">
                <span>5 min</span>
                <span>180 min</span>
              </div>
            </div>
          )}

          {/* Task linker */}
          <div>
            <button
              onClick={() => setShowTaskPicker(!showTaskPicker)}
              className="w-full bg-gray-900 rounded-xl p-4 flex items-center gap-3 hover:bg-gray-800 transition-colors"
            >
              <Link size={18} className="text-blue-400 shrink-0" />
              <div className="flex-1 text-left">
                <p className="text-sm">
                  {linkedTask ? linkedTask.title : "Taskga ulash (ixtiyoriy)"}
                </p>
                {linkedTask && <p className="text-xs text-gray-500">+10 XP bonus</p>}
              </div>
              <ChevronDown size={16} className={`text-gray-500 transition-transform ${showTaskPicker ? "rotate-180" : ""}`} />
            </button>

            {showTaskPicker && (
              <div className="mt-2 bg-gray-900 rounded-xl overflow-hidden max-h-48 overflow-y-auto overscroll-contain">
                {linkedTaskId && (
                  <button
                    onClick={() => { setLinkedTaskId(undefined); setShowTaskPicker(false); haptic.light(); }}
                    className="w-full p-3 text-left text-sm text-red-400 border-b border-gray-800 hover:bg-gray-800"
                  >
                    ✕ Ulashni bekor qilish
                  </button>
                )}
                {tasks.length === 0 && (
                  <p className="p-3 text-sm text-gray-500 text-center">Bugun uchun task yo'q</p>
                )}
                {tasks.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => { setLinkedTaskId(t.id); setShowTaskPicker(false); haptic.light(); }}
                    className={`w-full p-3 text-left text-sm border-b border-gray-800 hover:bg-gray-800 transition-colors ${
                      linkedTaskId === t.id ? "bg-blue-900/30 text-blue-400" : ""
                    }`}
                  >
                    {t.title}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Start button */}
          <button
            onClick={handleStart}
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl p-4 flex items-center justify-center gap-3 text-lg font-bold hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50"
          >
            <Play size={24} fill="white" />
            Boshlash — {getPlannedMinutes()} min
          </button>
        </div>
      )}

      {/* === ACTIVE / PAUSED PHASE === */}
      {(phase === "active" || phase === "paused") && (
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          {/* Timer ring */}
          <div className="relative w-[280px] h-[280px]">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 280 280">
              {/* Background ring */}
              <circle
                cx="140" cy="140" r={ringRadius}
                fill="none" stroke="#1f2937" strokeWidth="8"
              />
              {/* Progress ring */}
              <circle
                cx="140" cy="140" r={ringRadius}
                fill="none"
                stroke={isOvertime ? "#ef4444" : "#3b82f6"}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={ringCircumference}
                strokeDashoffset={ringOffset}
                className="transition-all duration-200"
              />
            </svg>

            {/* Center content */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <p className={`text-5xl font-mono font-bold ${isOvertime ? "text-red-400" : ""}`}>
                {isOvertime ? "+" : ""}{formatTime(isOvertime ? elapsed - plannedSeconds : remaining)}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                {isOvertime ? "Overtime" : `${formatTime(elapsed)} / ${formatTime(plannedSeconds)}`}
              </p>
              {phase === "paused" && (
                <p className="text-sm text-yellow-400 mt-1 animate-pulse">⏸ Pauza</p>
              )}
            </div>
          </div>

          {/* Mode label */}
          <p className="text-sm text-gray-400 mt-4">
            {MODES.find((m) => m.key === mode)?.icon} {MODES.find((m) => m.key === mode)?.label}
            {linkedTask && <span className="text-blue-400"> · {linkedTask.title}</span>}
          </p>

          {/* Controls */}
          <div className="flex items-center gap-6 mt-8">
            {phase === "active" ? (
              <button
                onClick={handlePause}
                className="w-16 h-16 bg-yellow-600 rounded-full flex items-center justify-center hover:bg-yellow-500 active:scale-95 transition-all"
              >
                <Pause size={28} fill="white" />
              </button>
            ) : (
              <button
                onClick={handleResume}
                className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center hover:bg-green-500 active:scale-95 transition-all"
              >
                <Play size={28} fill="white" />
              </button>
            )}

            <button
              onClick={handleEnd}
              disabled={loading}
              className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center hover:bg-red-500 active:scale-95 transition-all disabled:opacity-50"
            >
              <Square size={24} fill="white" />
            </button>
          </div>

          <p className="text-xs text-gray-600 mt-4">
            {elapsed < 120 ? "Kamida 2 daqiqa ishlang" : "Tugatish uchun ■ bosing"}
          </p>
        </div>
      )}

      {/* === COMPLETED PHASE === */}
      {phase === "completed" && endResult && (
        <div className="flex-1 flex flex-col items-center justify-center p-4 space-y-6">
          {/* Celebration */}
          <div className="text-6xl animate-bounce">🎉</div>
          <h2 className="text-xl font-bold">Ajoyib ish!</h2>

          {/* Summary card */}
          <div className="w-full max-w-sm bg-gray-900 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Davomiylik</span>
              <span className="font-bold">{endResult.session.actual_duration} min</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Rejim</span>
              <span className="font-medium">
                {MODES.find((m) => m.key === endResult.session.mode)?.icon}{" "}
                {MODES.find((m) => m.key === endResult.session.mode)?.label || endResult.session.mode}
              </span>
            </div>
            <div className="h-px bg-gray-800" />
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400 flex items-center gap-1">
                <Zap size={14} className="text-yellow-400" /> XP olindi
              </span>
              <span className="font-bold text-yellow-400">+{endResult.xp_awarded} XP</span>
            </div>
            {endResult.leveled_up && (
              <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 rounded-xl p-3 text-center">
                <Trophy size={20} className="text-yellow-400 mx-auto mb-1" />
                <p className="text-sm font-bold text-yellow-400">Level {endResult.new_level} ga chiqdingiz!</p>
              </div>
            )}
            {endResult.session.status === "abandoned" && (
              <p className="text-xs text-gray-500 text-center">
                Sessiya juda qisqa edi (2 min dan kam). XP berilmadi.
              </p>
            )}
          </div>

          {/* Break options */}
          <div className="w-full max-w-sm">
            <p className="text-xs text-gray-500 text-center mb-3">Tanaffus olasizmi?</p>
            <div className="flex gap-3">
              {BREAK_OPTIONS.map((b) => (
                <button
                  key={b.minutes}
                  onClick={() => handleStartBreak(b.minutes)}
                  className="flex-1 bg-gray-800 rounded-xl p-3 text-center hover:bg-gray-700 transition-colors"
                >
                  <p className="text-sm font-medium">{b.label}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Back */}
          <button
            onClick={handleReset}
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            Yangi sessiya boshlash →
          </button>
        </div>
      )}

      {/* === BREAK PHASE === */}
      {phase === "break" && (
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          <p className="text-lg text-gray-400 mb-4">☕ Tanaffus</p>

          {/* Break ring */}
          <div className="relative w-[200px] h-[200px]">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 200 200">
              <circle cx="100" cy="100" r="85" fill="none" stroke="#1f2937" strokeWidth="6" />
              <circle
                cx="100" cy="100" r="85"
                fill="none" stroke="#22c55e" strokeWidth="6" strokeLinecap="round"
                strokeDasharray={2 * Math.PI * 85}
                strokeDashoffset={2 * Math.PI * 85 - (breakTotal > 0 ? (breakSeconds / breakTotal) : 0) * 2 * Math.PI * 85}
                className="transition-all duration-200"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <p className="text-4xl font-mono font-bold text-green-400">{formatTime(breakSeconds)}</p>
            </div>
          </div>

          <button
            onClick={handleReset}
            className="mt-8 text-sm text-gray-400 hover:text-white transition-colors"
          >
            Tanaffusni tugatish
          </button>
        </div>
      )}
    </div>
  );
}
