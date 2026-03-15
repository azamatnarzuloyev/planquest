"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { generatePlan, applyPlan } from "@/lib/api";
import type { DailyPlan } from "@/types";
import { Bot, Clock, Sparkles, CheckCircle2, AlertTriangle, Lightbulb, Loader2, Lock } from "lucide-react";
import { haptic } from "@/lib/telegram";
import { useRouter } from "next/navigation";

const BLOCK_ICONS: Record<string, string> = {
  task: "📌",
  habit: "🔄",
  focus_session: "🧠",
  break: "☕",
};

const BLOCK_COLORS: Record<string, string> = {
  task: "border-l-blue-500 bg-blue-950/20",
  habit: "border-l-green-500 bg-green-950/20",
  focus_session: "border-l-purple-500 bg-purple-950/20",
  break: "border-l-gray-600 bg-gray-800/30",
};

export default function AIPlannerPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [planRaw, setPlanRaw] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [tasksCreated, setTasksCreated] = useState(0);

  const isPremium = user?.is_premium;

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    setPlan(null);
    setApplied(false);
    haptic.medium();

    try {
      const result = await generatePlan();
      setPlan(result.plan);
      setPlanRaw(result.plan as unknown as Record<string, unknown>);
      setWarnings(result.validation.warnings || []);

      if (!result.validation.valid) {
        setError("AI reja yaratdi, lekin ba'zi muammolar bor: " + result.validation.errors.join(", "));
      }
      haptic.success();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Xatolik";
      // Check for 403/429
      if (typeof err === "object" && err !== null && "response" in err) {
        const resp = (err as { response?: { status?: number; data?: { detail?: string } } }).response;
        if (resp?.status === 403) {
          setError("AI faqat Premium foydalanuvchilar uchun");
        } else if (resp?.status === 429) {
          setError(resp?.data?.detail || "Kunlik limit tugadi");
        } else {
          setError(resp?.data?.detail || msg);
        }
      } else {
        setError(msg);
      }
      haptic.error();
    } finally {
      setLoading(false);
    }
  }

  async function handleApply() {
    if (!planRaw) return;
    setApplying(true);
    haptic.heavy();

    try {
      const result = await applyPlan(planRaw);
      setTasksCreated(result.tasks_created);
      setApplied(true);
      haptic.success();
    } catch {
      haptic.error();
      setError("Rejani qo'llashda xatolik");
    } finally {
      setApplying(false);
    }
  }

  // Not premium
  if (!isPremium) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-80px)] p-6">
        <div className="text-center space-y-4 max-w-xs">
          <div className="w-20 h-20 bg-gradient-to-br from-yellow-600 to-orange-600 rounded-2xl flex items-center justify-center mx-auto">
            <Lock size={32} />
          </div>
          <h2 className="text-lg font-bold">AI Planner</h2>
          <p className="text-sm text-gray-400">
            AI rejalashtirish faqat Premium foydalanuvchilar uchun.
            Premium bilan kuniga 30 ta AI reja olishingiz mumkin.
          </p>
          <button
            onClick={() => router.push("/profile")}
            className="bg-gradient-to-r from-yellow-600 to-orange-600 px-6 py-2.5 rounded-xl text-sm font-medium"
          >
            Premium haqida
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 pb-24 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
          <Bot size={20} />
        </div>
        <div>
          <h1 className="text-lg font-bold">AI Planner</h1>
          <p className="text-xs text-gray-500">Kunlik rejangizni AI bilan tuzing</p>
        </div>
      </div>

      {/* Generate button */}
      {!plan && !loading && (
        <button
          onClick={handleGenerate}
          className="w-full bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-5 text-center hover:opacity-90 active:scale-[0.98] transition-all"
        >
          <Sparkles size={28} className="mx-auto mb-2 text-yellow-300" />
          <p className="font-semibold">Bugungi rejani yaratish</p>
          <p className="text-xs text-blue-200 mt-1">AI sizning task va habitlaringiz asosida reja tuzadi</p>
        </button>
      )}

      {/* Loading */}
      {loading && (
        <div className="bg-gray-900 rounded-xl p-8 text-center">
          <Loader2 size={32} className="mx-auto mb-3 animate-spin text-blue-400" />
          <p className="text-sm text-gray-400">AI reja tayyorlamoqda...</p>
          <p className="text-xs text-gray-600 mt-1">5-10 soniya</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-950/30 border border-red-900/30 rounded-xl p-4 flex items-start gap-3">
          <AlertTriangle size={18} className="text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-red-400">{error}</p>
            <button onClick={handleGenerate} className="text-xs text-blue-400 mt-2">
              Qayta urinish →
            </button>
          </div>
        </div>
      )}

      {/* Plan preview */}
      {plan && !applied && (
        <>
          {/* Time blocks */}
          <div className="space-y-2">
            <p className="text-xs text-gray-500 font-medium uppercase tracking-widest px-1">
              Kunlik reja
            </p>
            {plan.time_blocks.map((block, i) => (
              <div
                key={i}
                className={`rounded-xl p-3 border-l-[3px] ${BLOCK_COLORS[block.type] || BLOCK_COLORS.task}`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm font-mono text-gray-400">{block.start}</span>
                  <span className="text-gray-700">→</span>
                  <span className="text-sm font-mono text-gray-400">{block.end}</span>
                  <span className="text-lg ml-1">{BLOCK_ICONS[block.type] || "📌"}</span>
                </div>
                <p className="text-sm font-medium mt-1">{block.title}</p>
                {block.mode && (
                  <span className="text-[10px] text-purple-400 bg-purple-900/30 px-2 py-0.5 rounded-full mt-1 inline-block">
                    {block.mode}
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* Suggested new tasks */}
          {plan.suggested_new_tasks.length > 0 && (
            <div className="bg-gray-900 rounded-xl p-4">
              <p className="text-xs text-gray-500 font-medium mb-3 flex items-center gap-1">
                <Lightbulb size={12} className="text-yellow-400" /> Yangi tavsiyalar
              </p>
              <div className="space-y-2">
                {plan.suggested_new_tasks.map((st, i) => (
                  <div key={i} className="flex items-center gap-3 p-2 bg-gray-800/50 rounded-lg">
                    <span className="text-lg">💡</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm truncate">{st.title}</p>
                      <p className="text-[10px] text-gray-500">{st.priority} · {st.difficulty} · {st.estimated_minutes}m</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Coaching note */}
          {plan.coaching_note && (
            <div className="bg-blue-950/20 border border-blue-900/30 rounded-xl p-3 flex items-start gap-2">
              <span className="text-lg">💬</span>
              <p className="text-sm text-blue-300">{plan.coaching_note}</p>
            </div>
          )}

          {/* Warnings */}
          {warnings.length > 0 && (
            <div className="bg-yellow-950/20 border border-yellow-900/30 rounded-xl p-3">
              <p className="text-xs text-yellow-400 font-medium mb-1">Ogohlantirishlar:</p>
              {warnings.map((w, i) => (
                <p key={i} className="text-xs text-yellow-500/70">• {w}</p>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={handleApply}
              disabled={applying}
              className="flex-1 bg-green-600 rounded-xl py-3.5 font-semibold text-sm flex items-center justify-center gap-2 hover:bg-green-500 active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {applying ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}
              Qo'llash
            </button>
            <button
              onClick={handleGenerate}
              className="bg-gray-800 rounded-xl py-3.5 px-5 text-sm hover:bg-gray-700 transition-colors"
            >
              Yangilash
            </button>
          </div>
        </>
      )}

      {/* Applied success */}
      {applied && (
        <div className="bg-green-950/20 border border-green-900/30 rounded-xl p-6 text-center space-y-3">
          <div className="text-5xl">🎉</div>
          <h3 className="font-bold text-lg text-green-400">Reja qo'llanildi!</h3>
          <p className="text-sm text-gray-400">{tasksCreated} ta yangi task yaratildi</p>
          <div className="flex gap-3 pt-2">
            <button
              onClick={() => router.push("/planner")}
              className="flex-1 bg-blue-600 rounded-xl py-3 text-sm font-medium hover:bg-blue-500 transition-colors"
            >
              Planner'ga o'tish
            </button>
            <button
              onClick={() => { setPlan(null); setApplied(false); setTasksCreated(0); }}
              className="bg-gray-800 rounded-xl py-3 px-5 text-sm hover:bg-gray-700 transition-colors"
            >
              Yangi reja
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
