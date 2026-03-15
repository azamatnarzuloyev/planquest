"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { applyPlan } from "@/lib/api";
import type { DailyPlan, SuggestedTask, TimeBlock } from "@/types";
import { Bot, CheckCircle2, Loader2, Lock, Trash2, Clock, Send, RefreshCw } from "lucide-react";
import { haptic } from "@/lib/telegram";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

const MAX_USER_MESSAGES = 5;

const BLOCK_ICONS: Record<string, string> = { task: "📌", habit: "🔄", focus_session: "🧠", break: "☕" };
const BLOCK_COLORS: Record<string, string> = {
  task: "border-l-blue-500", habit: "border-l-green-500",
  focus_session: "border-l-purple-500", break: "border-l-gray-600",
};

interface ChatMsg {
  role: "user" | "assistant";
  content: string;
  suggestions?: string[];
}

export default function AIPlannerPage() {
  const { user } = useAuth();
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [planRaw, setPlanRaw] = useState<Record<string, unknown> | null>(null);
  const [editingBlocks, setEditingBlocks] = useState<TimeBlock[]>([]);
  const [editingSuggested, setEditingSuggested] = useState<SuggestedTask[]>([]);
  const [applying, setApplying] = useState(false);
  const [tasksCreated, setTasksCreated] = useState(0);
  const [phase, setPhase] = useState<"chat" | "preview" | "applied">("chat");
  const [error, setError] = useState<string | null>(null);

  const userMsgCount = messages.filter((m) => m.role === "user").length;
  const isPremium = user?.is_premium;

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);
  useEffect(() => { if (isPremium) setTimeout(() => inputRef.current?.focus(), 500); }, [isPremium]);

  if (!isPremium) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-80px)] p-6">
        <div className="text-center space-y-4 max-w-xs">
          <div className="w-20 h-20 bg-gradient-to-br from-yellow-600 to-orange-600 rounded-2xl flex items-center justify-center mx-auto"><Lock size={32} /></div>
          <h2 className="text-lg font-bold">AI Planner</h2>
          <p className="text-sm text-gray-400">AI rejalashtirish faqat Premium foydalanuvchilar uchun.</p>
          <button onClick={() => router.push("/profile")} className="bg-gradient-to-r from-yellow-600 to-orange-600 px-6 py-2.5 rounded-xl text-sm font-medium">Premium haqida</button>
        </div>
      </div>
    );
  }

  async function callAI(msgs: ChatMsg[], forcePlan: boolean = false) {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post("/api/ai/chat-plan", {
        messages: msgs.map((m) => ({ role: m.role, content: m.content })),
        force_plan: forcePlan,
      });
      const response = data.response;

      if (response.type === "question") {
        setMessages([...msgs, { role: "assistant", content: response.message, suggestions: response.suggestions || [] }]);
      } else if (response.type === "plan") {
        setMessages([...msgs, { role: "assistant", content: response.summary || response.coaching_note || "Reja tayyor!" }]);
        setPlan(response as DailyPlan);
        setPlanRaw(response);
        setEditingBlocks([...(response.time_blocks || [])]);
        setEditingSuggested([...(response.suggested_new_tasks || [])]);
        setPhase("preview");
        haptic.success();
      }
    } catch {
      setError("AI hozir ishlamayapti. Keyinroq urinib ko'ring.");
      haptic.error();
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage(text: string) {
    if (!text.trim() || loading) return;
    haptic.light();
    const newMsgs: ChatMsg[] = [...messages, { role: "user", content: text.trim() }];
    setMessages(newMsgs);
    setInput("");
    await callAI(newMsgs);
  }

  async function handleFinalize() {
    haptic.medium();
    // Add system message and force plan
    const finalMsgs: ChatMsg[] = [...messages, { role: "user", content: "Shu ma'lumotlar asosida reja yaratib ber" }];
    setMessages(finalMsgs);
    await callAI(finalMsgs, true);
  }

  async function handleApply() {
    if (!planRaw) return;
    setApplying(true);
    haptic.heavy();
    try {
      const modified = { ...planRaw, time_blocks: editingBlocks, suggested_new_tasks: editingSuggested };
      const result = await applyPlan(modified);
      setTasksCreated(result.tasks_created);
      setPhase("applied");
      haptic.success();
    } catch { haptic.error(); }
    finally { setApplying(false); }
  }

  function handleReset() {
    setMessages([]); setPlan(null); setPlanRaw(null); setPhase("chat");
    setError(null); setInput(""); setEditingBlocks([]); setEditingSuggested([]);
    setTimeout(() => inputRef.current?.focus(), 300);
  }

  const reachedLimit = userMsgCount >= MAX_USER_MESSAGES;

  return (
    <div className="flex flex-col h-[calc(100vh-80px)]">
      {/* Header */}
      <div className="p-4 pb-2 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
            <Bot size={20} />
          </div>
          <div className="flex-1">
            <h1 className="text-lg font-bold">AI Planner</h1>
            <p className="text-xs text-gray-500">
              {phase === "chat"
                ? userMsgCount === 0 ? "Buguningizni tasvirlang" : `${userMsgCount}/${MAX_USER_MESSAGES}`
                : phase === "preview" ? "Rejani tahrirlang" : ""}
            </p>
          </div>
          {messages.length > 0 && (
            <button onClick={handleReset} className="text-gray-600 hover:text-white p-1.5 transition-colors" title="Yangidan boshlash">
              <RefreshCw size={16} />
            </button>
          )}
        </div>
      </div>

      {error && <div className="mx-4 mb-2 bg-red-950/30 border border-red-900/30 rounded-xl p-3 text-sm text-red-400 shrink-0">{error}</div>}

      {/* === CHAT === */}
      {phase === "chat" && (
        <>
          <div className="flex-1 overflow-y-auto px-4 space-y-3 py-2">
            {/* Empty state */}
            {messages.length === 0 && !loading && (
              <div className="text-center py-8 space-y-4">
                <p className="text-5xl">🤖</p>
                <p className="text-sm text-gray-300 font-medium">Bugun qanday kun o'tkazmoqchisiz?</p>
                <p className="text-xs text-gray-600 max-w-[260px] mx-auto">Nima qilmoqchi ekaningizni yozing — AI sizga reja tuzib beradi</p>
                <div className="flex flex-wrap justify-center gap-2 pt-1">
                  {[
                    "Bugun loyiha ustida ishlashim kerak",
                    "Yengil kun, dam olaman",
                    "Deadline bor, ko'p ish bor",
                    "O'qishga fokus qilaman",
                  ].map((s) => (
                    <button key={s} onClick={() => sendMessage(s)}
                      className="bg-gray-800 hover:bg-gray-700 px-3 py-2 rounded-xl text-xs text-gray-400 transition-all active:scale-95">
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Messages */}
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                  msg.role === "user" ? "bg-blue-600 rounded-br-sm" : "bg-gray-800 rounded-bl-sm"
                }`}>
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                  {msg.suggestions && msg.suggestions.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2.5">
                      {msg.suggestions.map((s, j) => (
                        <button key={j} onClick={() => sendMessage(s)} disabled={loading || reachedLimit}
                          className="bg-gray-700 hover:bg-gray-600 px-3 py-1.5 rounded-full text-[11px] text-gray-300 transition-all active:scale-95 disabled:opacity-40">
                          {s}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Bottom area */}
          <div className="p-3 shrink-0 border-t border-gray-800/50 space-y-2">
            {/* Limit reached — finalize button */}
            {reachedLimit && !loading && (
              <div className="space-y-2">
                <p className="text-xs text-center text-gray-500">So'rovlar limiti ({MAX_USER_MESSAGES}/{MAX_USER_MESSAGES})</p>
                <div className="flex gap-2">
                  <button onClick={handleFinalize}
                    className="flex-1 bg-purple-600 rounded-xl py-3 text-sm font-semibold hover:bg-purple-500 active:scale-[0.98] transition-all flex items-center justify-center gap-2">
                    <CheckCircle2 size={16} /> Yakunlash — reja yaratish
                  </button>
                  <button onClick={handleReset}
                    className="bg-gray-800 rounded-xl py-3 px-4 text-sm hover:bg-gray-700 transition-colors">
                    <RefreshCw size={16} />
                  </button>
                </div>
              </div>
            )}

            {/* Normal input */}
            {!reachedLimit && (
              <div className="flex gap-2">
                <input ref={inputRef} type="text" value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") sendMessage(input); }}
                  placeholder={userMsgCount === 0 ? "Bugun nima qilmoqchisiz?" : "Davom eting..."}
                  disabled={loading}
                  className="flex-1 bg-gray-800 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50" />
                <button onClick={() => sendMessage(input)}
                  disabled={!input.trim() || loading}
                  className="bg-purple-600 w-11 h-11 rounded-xl flex items-center justify-center hover:bg-purple-500 active:scale-90 transition-all disabled:opacity-30">
                  <Send size={18} />
                </button>
              </div>
            )}

            {/* Finalize early button (after 2+ messages) */}
            {userMsgCount >= 2 && !reachedLimit && !loading && (
              <button onClick={handleFinalize}
                className="w-full text-xs text-purple-400 hover:text-purple-300 py-1 transition-colors">
                Yakunlash va reja yaratish →
              </button>
            )}
          </div>
        </>
      )}

      {/* === PREVIEW === */}
      {phase === "preview" && plan && (
        <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-4 py-2">
          {(plan.summary || plan.coaching_note) && (
            <div className="bg-purple-950/20 border border-purple-900/30 rounded-xl p-4">
              <p className="text-xs text-purple-400 font-medium mb-1">🤖 AI izohi</p>
              <p className="text-sm">{plan.summary || plan.coaching_note}</p>
            </div>
          )}

          {editingBlocks.length > 0 && (
            <div>
              <p className="text-[10px] text-gray-600 font-semibold uppercase tracking-widest mb-2 px-1">Kunlik reja · {editingBlocks.length}</p>
              <div className="space-y-1.5">
                {editingBlocks.map((b, i) => (
                  <div key={i} className={`bg-gray-900 rounded-xl p-3 border-l-[3px] ${BLOCK_COLORS[b.type] || "border-l-gray-600"} flex items-center gap-3`}>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] font-mono text-gray-500">{b.start}–{b.end}</span>
                        <span>{BLOCK_ICONS[b.type] || "📌"}</span>
                      </div>
                      <p className="text-sm mt-0.5 truncate">{b.title}</p>
                    </div>
                    <button onClick={() => { setEditingBlocks((p) => p.filter((_, j) => j !== i)); haptic.light(); }}
                      className="text-gray-700 hover:text-red-400 p-1.5 transition-colors"><Trash2 size={14} /></button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {editingSuggested.length > 0 && (
            <div>
              <p className="text-[10px] text-gray-600 font-semibold uppercase tracking-widest mb-2 px-1">💡 Yangi tasklar</p>
              <div className="space-y-1.5">
                {editingSuggested.map((st, i) => (
                  <div key={i} className="bg-gray-900 rounded-xl p-3 flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm">{st.title}</p>
                      <span className="text-[10px] text-gray-600 flex items-center gap-1"><Clock size={8} />{st.estimated_minutes}m · {st.difficulty}</span>
                    </div>
                    <button onClick={() => { setEditingSuggested((p) => p.filter((_, j) => j !== i)); haptic.light(); }}
                      className="text-gray-700 hover:text-red-400 p-1.5 transition-colors"><Trash2 size={14} /></button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={handleApply} disabled={applying}
              className="flex-1 bg-green-600 rounded-xl py-3.5 font-semibold text-sm flex items-center justify-center gap-2 hover:bg-green-500 active:scale-[0.98] transition-all disabled:opacity-50">
              {applying ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />} Tasdiqlash
            </button>
            <button onClick={handleReset} className="bg-gray-800 rounded-xl py-3.5 px-5 text-sm hover:bg-gray-700 transition-colors">Qayta</button>
          </div>
        </div>
      )}

      {/* === APPLIED === */}
      {phase === "applied" && (
        <div className="flex-1 flex items-center justify-center px-4">
          <div className="bg-green-950/20 border border-green-900/30 rounded-xl p-6 text-center space-y-3 w-full max-w-sm">
            <p className="text-5xl">🎉</p>
            <h3 className="font-bold text-lg text-green-400">Reja qo'llanildi!</h3>
            <p className="text-sm text-gray-400">{tasksCreated} ta yangi task yaratildi</p>
            <div className="flex gap-3 pt-2">
              <button onClick={() => router.push("/planner")} className="flex-1 bg-blue-600 rounded-xl py-3 text-sm font-medium hover:bg-blue-500 transition-colors">Planner</button>
              <button onClick={handleReset} className="bg-gray-800 rounded-xl py-3 px-5 text-sm hover:bg-gray-700 transition-colors">Yangi</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
