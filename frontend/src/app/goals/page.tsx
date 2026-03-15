"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getGoals, createGoal, deleteGoal, decomposeGoal, applyDecomposition } from "@/lib/api";
import type { GoalResponse, DecomposeResponse } from "@/types";
import { Plus, Target, Trash2, X, Bot, Loader2, CheckCircle2, Calendar, ChevronDown } from "lucide-react";
import { haptic } from "@/lib/telegram";
import ProgressRing from "@/components/ProgressRing";

const CATEGORIES = [
  { value: "work", label: "💼 Ish" },
  { value: "study", label: "📚 O'qish" },
  { value: "health", label: "💪 Salomatlik" },
  { value: "personal", label: "🏠 Shaxsiy" },
  { value: "project", label: "🚀 Loyiha" },
  { value: "finance", label: "💰 Moliya" },
];

const LEVELS = [
  { value: "weekly", label: "Haftalik" },
  { value: "monthly", label: "Oylik" },
  { value: "yearly", label: "Yillik" },
];

const LEVEL_ICONS: Record<string, string> = { yearly: "🏆", monthly: "📅", weekly: "📋" };

export default function GoalsPage() {
  const { user, isAuthenticated } = useAuth();
  const [goals, setGoals] = useState<GoalResponse[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("personal");
  const [level, setLevel] = useState("monthly");
  const [targetDate, setTargetDate] = useState("");
  const [creating, setCreating] = useState(false);

  // AI decompose
  const [decompGoalId, setDecompGoalId] = useState<string | null>(null);
  const [decompResult, setDecompResult] = useState<DecomposeResponse | null>(null);
  const [decompLoading, setDecompLoading] = useState(false);
  const [decompApplying, setDecompApplying] = useState(false);
  const [decompApplied, setDecompApplied] = useState(false);
  const [expandedMilestone, setExpandedMilestone] = useState<number | null>(null);

  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const loadGoals = useCallback(async () => {
    try {
      const data = await getGoals();
      setGoals(data);
    } catch {}
  }, []);

  useEffect(() => {
    if (isAuthenticated) loadGoals();
  }, [isAuthenticated, loadGoals]);

  useEffect(() => {
    if (showAdd || decompGoalId) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [showAdd, decompGoalId]);

  async function handleCreate() {
    if (!title.trim() || creating) return;
    setCreating(true);
    haptic.medium();
    try {
      await createGoal({
        title: title.trim(),
        description: description.trim(),
        category,
        level,
        target_date: targetDate || undefined,
      });
      haptic.success();
      setShowAdd(false);
      setTitle(""); setDescription(""); setTargetDate("");
      await loadGoals();
    } catch { haptic.error(); }
    finally { setCreating(false); }
  }

  async function handleDelete(id: string) {
    haptic.heavy();
    await deleteGoal(id);
    setConfirmDelete(null);
    await loadGoals();
  }

  async function handleDecompose(goalId: string) {
    setDecompGoalId(goalId);
    setDecompResult(null);
    setDecompApplied(false);
    setDecompLoading(true);
    haptic.medium();
    try {
      const result = await decomposeGoal(goalId);
      setDecompResult(result);
      haptic.success();
    } catch {
      haptic.error();
      setDecompGoalId(null);
    } finally {
      setDecompLoading(false);
    }
  }

  async function handleApplyDecomp() {
    if (!decompGoalId || !decompResult) return;
    setDecompApplying(true);
    haptic.heavy();
    try {
      await applyDecomposition(decompGoalId, decompResult.decomposition as unknown as Record<string, unknown>);
      setDecompApplied(true);
      haptic.success();
      await loadGoals();
    } catch { haptic.error(); }
    finally { setDecompApplying(false); }
  }

  const isPremium = user?.is_premium;

  return (
    <div className="p-4 pb-24 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">🎯 Maqsadlar</h1>
          <p className="text-xs text-gray-500 mt-0.5">{goals.length} ta maqsad</p>
        </div>
        <button
          onClick={() => { setShowAdd(true); haptic.light(); }}
          className="bg-blue-600 w-11 h-11 rounded-full flex items-center justify-center hover:bg-blue-500 active:scale-90 transition-all shadow-lg shadow-blue-600/30"
        >
          <Plus size={20} strokeWidth={2.5} />
        </button>
      </div>

      {/* Goals list */}
      {goals.length > 0 ? (
        <div className="space-y-3">
          {goals.map((g) => (
            <div key={g.id} className="bg-gray-900 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <ProgressRing percent={g.progress_percent} size={48} strokeWidth={3} color={g.progress_percent >= 100 ? "#22c55e" : "#3b82f6"}>
                  <span className="text-[10px] font-bold">{Math.round(g.progress_percent)}%</span>
                </ProgressRing>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span>{LEVEL_ICONS[g.level] || "📌"}</span>
                    <p className="text-sm font-semibold truncate">{g.title}</p>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] text-gray-500">{CATEGORIES.find(c => c.value === g.category)?.label || g.category}</span>
                    <span className="text-[10px] text-gray-600">·</span>
                    <span className="text-[10px] text-gray-500">{g.linked_tasks_done}/{g.linked_tasks_total} task</span>
                    {g.target_date && (
                      <>
                        <span className="text-[10px] text-gray-600">·</span>
                        <span className="text-[10px] text-gray-500 flex items-center gap-0.5">
                          <Calendar size={8} /> {g.target_date}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 shrink-0">
                  {isPremium && (
                    <button
                      onClick={() => handleDecompose(g.id)}
                      className="text-purple-400 hover:text-purple-300 p-1 transition-colors"
                      title="AI bilan bo'lish"
                    >
                      <Bot size={16} />
                    </button>
                  )}
                  {confirmDelete === g.id ? (
                    <button onClick={() => handleDelete(g.id)} className="text-[10px] bg-red-600 px-2 py-1 rounded-lg">Ha</button>
                  ) : (
                    <button onClick={() => setConfirmDelete(g.id)} className="text-gray-700 hover:text-red-400 p-1 transition-colors">
                      <Trash2 size={13} />
                    </button>
                  )}
                </div>
              </div>

              {/* Progress bar */}
              <div className="mt-3 w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${g.progress_percent >= 100 ? "bg-green-500" : "bg-blue-500"}`}
                  style={{ width: `${Math.min(100, g.progress_percent)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <p className="text-5xl mb-4">🎯</p>
          <p className="text-gray-400 font-semibold">Hali maqsad yo'q</p>
          <p className="text-gray-600 text-sm mt-1 mb-6">Katta maqsad qo'ying, AI bo'laklarga bo'lib beradi</p>
          <button
            onClick={() => { setShowAdd(true); haptic.light(); }}
            className="bg-blue-600 px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-500 active:scale-95 transition-all inline-flex items-center gap-2"
          >
            <Plus size={16} /> Maqsad qo'shish
          </button>
        </div>
      )}

      {/* Add Goal Sheet */}
      {showAdd && (
        <div className="fixed inset-0 bg-black/60 z-[60] flex items-end" onClick={() => setShowAdd(false)}>
          <div className="w-full bg-gray-900 rounded-t-2xl animate-slide-up max-h-[85vh] overflow-y-auto overscroll-contain" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-center pt-3 pb-1"><div className="w-10 h-1 bg-gray-700 rounded-full" /></div>
            <div className="p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="font-bold text-lg">Yangi maqsad</h2>
                <button onClick={() => setShowAdd(false)} className="text-gray-500 p-1"><X size={20} /></button>
              </div>

              <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Maqsad nomi" maxLength={200}
                className="w-full bg-gray-800 rounded-xl px-4 py-3.5 text-sm outline-none focus:ring-2 focus:ring-blue-500" autoFocus />

              <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Tavsif (ixtiyoriy)" maxLength={500} rows={2}
                className="w-full bg-gray-800 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500 resize-none" />

              <div>
                <p className="text-xs text-gray-500 mb-2">Davr</p>
                <div className="flex gap-2">
                  {LEVELS.map((l) => (
                    <button key={l.value} onClick={() => { setLevel(l.value); haptic.light(); }}
                      className={`flex-1 py-2.5 rounded-xl text-xs font-medium transition-all ${level === l.value ? "bg-blue-600" : "bg-gray-800 text-gray-400"}`}>
                      {l.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs text-gray-500 mb-2">Kategoriya</p>
                <div className="flex gap-1.5 flex-wrap">
                  {CATEGORIES.map((c) => (
                    <button key={c.value} onClick={() => { setCategory(c.value); haptic.light(); }}
                      className={`px-3 py-1.5 rounded-lg text-xs transition-all ${category === c.value ? "bg-blue-600" : "bg-gray-800 text-gray-400"}`}>
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs text-gray-500 mb-2">Muddat (ixtiyoriy)</p>
                <input type="date" value={targetDate} onChange={(e) => setTargetDate(e.target.value)}
                  className="w-full bg-gray-800 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
              </div>

              <button onClick={handleCreate} disabled={!title.trim() || creating}
                className="w-full bg-blue-600 rounded-xl py-3.5 font-semibold text-sm hover:bg-blue-500 active:scale-[0.98] transition-all disabled:opacity-30">
                {creating ? "Yaratilmoqda..." : "Maqsad yaratish"}
              </button>

              <div className="h-2" />
            </div>
          </div>
        </div>
      )}

      {/* AI Decompose Modal */}
      {decompGoalId && (
        <div className="fixed inset-0 bg-black/60 z-[60] flex items-end" onClick={() => { setDecompGoalId(null); setDecompResult(null); }}>
          <div className="w-full bg-gray-900 rounded-t-2xl animate-slide-up max-h-[90vh] overflow-y-auto overscroll-contain" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-center pt-3 pb-1"><div className="w-10 h-1 bg-gray-700 rounded-full" /></div>
            <div className="p-5 space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
                  <Bot size={20} />
                </div>
                <div>
                  <h2 className="font-bold">AI Dekompozitsiya</h2>
                  <p className="text-xs text-gray-500">Maqsadni bosqichlarga bo'lish</p>
                </div>
              </div>

              {/* Loading */}
              {decompLoading && (
                <div className="text-center py-8">
                  <Loader2 size={32} className="mx-auto mb-3 animate-spin text-purple-400" />
                  <p className="text-sm text-gray-400">AI tahlil qilmoqda...</p>
                </div>
              )}

              {/* Result */}
              {decompResult && !decompApplied && (
                <>
                  <div className="bg-purple-950/20 border border-purple-900/30 rounded-xl p-3">
                    <p className="text-xs text-purple-400 font-medium">
                      {decompResult.decomposition.total_weeks} hafta · {decompResult.decomposition.milestones.length} bosqich
                    </p>
                    {decompResult.decomposition.summary && (
                      <p className="text-sm text-gray-300 mt-1">{decompResult.decomposition.summary}</p>
                    )}
                  </div>

                  {/* Milestones */}
                  <div className="space-y-2">
                    {decompResult.decomposition.milestones.map((ms) => (
                      <div key={ms.week} className="bg-gray-800 rounded-xl overflow-hidden">
                        <button
                          onClick={() => setExpandedMilestone(expandedMilestone === ms.week ? null : ms.week)}
                          className="w-full p-3 flex items-center gap-3 text-left"
                        >
                          <span className="text-xs bg-blue-600 px-2 py-0.5 rounded font-bold shrink-0">H{ms.week}</span>
                          <p className="text-sm font-medium flex-1 truncate">{ms.title}</p>
                          <span className="text-[10px] text-gray-500">{ms.tasks.length} task</span>
                          <ChevronDown size={14} className={`text-gray-500 transition-transform ${expandedMilestone === ms.week ? "rotate-180" : ""}`} />
                        </button>
                        {expandedMilestone === ms.week && (
                          <div className="px-3 pb-3 space-y-1.5">
                            {ms.tasks.map((t, i) => (
                              <div key={i} className="flex items-center gap-2 p-2 bg-gray-900/50 rounded-lg">
                                <span className="text-[10px] text-gray-600 w-6">K{t.day_offset}</span>
                                <p className="text-xs flex-1 truncate">{t.title}</p>
                                <span className="text-[9px] text-gray-600">{t.estimated_minutes}m</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3">
                    <button onClick={handleApplyDecomp} disabled={decompApplying}
                      className="flex-1 bg-green-600 rounded-xl py-3.5 font-semibold text-sm flex items-center justify-center gap-2 hover:bg-green-500 active:scale-[0.98] transition-all disabled:opacity-50">
                      {decompApplying ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}
                      Qo'llash
                    </button>
                    <button onClick={() => { setDecompGoalId(null); setDecompResult(null); }}
                      className="bg-gray-800 rounded-xl py-3.5 px-5 text-sm hover:bg-gray-700 transition-colors">
                      Bekor
                    </button>
                  </div>
                </>
              )}

              {/* Applied */}
              {decompApplied && (
                <div className="text-center py-6 space-y-3">
                  <p className="text-4xl">🎉</p>
                  <h3 className="font-bold text-green-400">Tasklar yaratildi!</h3>
                  <p className="text-sm text-gray-400">Planner'da ko'rishingiz mumkin</p>
                  <button onClick={() => { setDecompGoalId(null); setDecompResult(null); }}
                    className="bg-blue-600 px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-500 transition-colors">
                    Yopish
                  </button>
                </div>
              )}

              <div className="h-2" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
