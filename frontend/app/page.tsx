"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, LoaderCircle, CheckCircle, Circle, AlertCircle } from "lucide-react";
import { getHealth, getRoles, saveOnboarding, getProgressSummary, completeTopic, resetDemo } from "@/lib/api";
import type { Role, ProgressSummaryOut } from "@/types";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

type ViewState = "loading" | "error" | "onboarding" | "dashboard";

export default function Home() {
  const [viewState, setViewState] = useState<ViewState>("loading");
  const [errorMessage, setErrorMessage] = useState("");
  
  const [roles, setRoles] = useState<Role[]>([]);
  const [progressSummary, setProgressSummary] = useState<ProgressSummaryOut | null>(null);

  // Onboarding state
  const [selectedRole, setSelectedRole] = useState<number | null>(null);
  const [targetDate, setTargetDate] = useState<string>("");
  const [isStartingRoute, setIsStartingRoute] = useState(false);

  // Dashboard state
  const [isCompletingTopic, setIsCompletingTopic] = useState<number | null>(null);
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  async function loadInitialData() {
    try {
      setViewState("loading");
      await getHealth();
      const summary = await getProgressSummary();
      if (summary.selected_role) {
        setProgressSummary(summary);
        setViewState("dashboard");
      } else {
        const rolesData = await getRoles();
        setRoles(rolesData);
        setViewState("onboarding");
      }
    } catch (e: unknown) {
      setErrorMessage(e instanceof Error ? e.message : "Failed to load data. Is the backend running?");
      setViewState("error");
    }
  }

  async function handleStartRoute() {
    if (!selectedRole || !targetDate) return;
    try {
      setIsStartingRoute(true);
      await saveOnboarding({ role_id: selectedRole, target_date: targetDate, name: "Demo User" });
      const summary = await getProgressSummary();
      setProgressSummary(summary);
      setViewState("dashboard");
    } catch (e: unknown) {
      setErrorMessage(e instanceof Error ? e.message : "Failed to start route.");
      setViewState("error");
    } finally {
      setIsStartingRoute(false);
    }
  }

  async function handleCompleteTopic(topicId: number) {
    if (isCompletingTopic) return;
    try {
      setIsCompletingTopic(topicId);
      const updatedSummary = await completeTopic(topicId);
      setProgressSummary(updatedSummary);
    } catch (e: unknown) {
      alert("Failed to complete topic: " + (e instanceof Error ? e.message : String(e)));
    } finally {
      setIsCompletingTopic(null);
    }
  }

  async function handleReset() {
    if (isResetting) return;
    try {
      setIsResetting(true);
      await resetDemo();
      setTargetDate("");
      setSelectedRole(null);
      await loadInitialData();
    } catch (e: unknown) {
      alert("Failed to reset: " + (e instanceof Error ? e.message : String(e)));
    } finally {
      setIsResetting(false);
    }
  }

  if (viewState === "loading") {
    return (
      <div className="flex h-screen items-center justify-center bg-background text-foreground">
        <LoaderCircle className="h-10 w-10 animate-spin text-accent" />
      </div>
    );
  }

  if (viewState === "error") {
    return (
      <div className="flex h-screen items-center justify-center bg-background text-foreground p-8">
        <div className="flex flex-col items-center rounded-3xl border border-red-500/20 bg-red-500/5 px-8 py-10 text-center max-w-md shadow-2xl">
          <AlertCircle className="h-12 w-12 text-red-400 mb-4" />
          <h2 className="text-xl font-semibold text-red-100 mb-2">Connection Error</h2>
          <p className="text-red-200/80 mb-8">{errorMessage}</p>
          <button 
            onClick={loadInitialData} 
            className="px-6 py-2.5 bg-red-500/20 hover:bg-red-500/30 text-red-100 font-medium rounded-xl transition-colors border border-red-500/30"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (viewState === "onboarding") {
    return (
      <div className="flex flex-1 flex-col bg-[radial-gradient(ellipse_at_top,_rgba(124,107,245,0.15),_transparent_60%)] min-h-screen p-4 sm:p-6 lg:p-8">
        <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col justify-center py-10 sm:py-16">
          <div className="text-center">
            <span className="px-3 py-1 text-xs font-semibold tracking-[0.2em] text-accent-soft uppercase rounded-full border border-accent/20 bg-accent/10">RoleRoute</span>
            <h1 className="mt-6 text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-white">
              Choose your target role
            </h1>
            <p className="mt-4 text-base sm:text-lg leading-7 text-slate-300 max-w-2xl mx-auto">
              Select a career goal and set a target date to generate a personalized, structured learning path.
            </p>
          </div>

          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {roles.map(r => (
              <button
                key={r.id}
                onClick={() => setSelectedRole(r.id)}
                className={`p-6 sm:p-8 rounded-3xl border text-left transition-all duration-200 shadow-xl ${
                  selectedRole === r.id 
                    ? "border-accent bg-accent/10 shadow-accent/20 ring-1 ring-accent" 
                    : "border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/20"
                }`}
              >
                <div className="flex flex-col h-full">
                  <h3 className="text-xl font-semibold text-white">{r.name}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-slate-400 flex-1">{r.description}</p>
                  
                  {selectedRole === r.id && (
                    <div className="mt-6 flex items-center gap-2 text-sm font-medium text-accent-soft">
                      <CheckCircle2 className="w-4 h-4" />
                      Selected
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>

          {selectedRole && (
            <div className="mt-16 flex flex-col items-center animate-in fade-in slide-in-from-bottom-8 duration-500">
              <div className="p-6 sm:p-8 rounded-3xl border border-white/10 bg-white/5 shadow-2xl backdrop-blur-sm w-full max-w-md">
                <label className="block text-sm font-medium text-slate-300 mb-3 text-center">
                  When do you want to be internship-ready?
                </label>
                <input 
                  type="date" 
                  value={targetDate}
                  onChange={e => setTargetDate(e.target.value)}
                  className="w-full bg-navy-900 border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-all"
                  min={new Date().toISOString().split('T')[0]}
                />
                <button 
                  onClick={handleStartRoute}
                  disabled={!targetDate || isStartingRoute}
                  className="mt-6 w-full flex items-center justify-center gap-2 px-8 py-3.5 bg-accent hover:bg-accent/90 text-white font-medium rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-[0_0_20px_rgba(124,107,245,0.4)] hover:shadow-[0_0_30px_rgba(124,107,245,0.6)]"
                >
                  {isStartingRoute ? (
                    <LoaderCircle className="w-5 h-5 animate-spin" />
                  ) : (
                    "Start My Route"
                  )}
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    );
  }

  // Dashboard view
  if (!progressSummary || !progressSummary.selected_role) return null;

  const { selected_role, target_date, readiness_score, stage, next_topic, module_progress, graph_history } = progressSummary;

  // Format graph data safely
  const chartData = (graph_history || []).map((s, i) => ({
    name: `Snapshot ${i+1}`,
    score: s.readiness_score,
  }));

  // Prevent graph from rendering empty if no history
  const hasGraphData = chartData.length > 0;

  return (
    <div className="min-h-screen bg-background text-foreground pb-20 selection:bg-accent/30 selection:text-white">
      <header className="sticky top-0 z-20 border-b border-white/10 bg-background/90 backdrop-blur-xl px-4 sm:px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3 sm:gap-4">
          <span className="font-bold tracking-wider text-accent-soft uppercase text-xs sm:text-sm">RoleRoute</span>
          <div className="h-4 w-px bg-white/20"></div>
          <span className="text-xs sm:text-sm font-medium text-slate-300 truncate max-w-[120px] sm:max-w-none">
            {selected_role.name}
          </span>
        </div>
        <button 
          onClick={handleReset} 
          disabled={isResetting}
          className="flex items-center gap-2 text-xs sm:text-sm px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 hover:text-red-300 border border-red-500/20 transition-all disabled:opacity-50 font-medium"
        >
          {isResetting ? <LoaderCircle className="w-3.5 h-3.5 animate-spin" /> : null}
          Reset Demo
        </button>
      </header>

      <main className="mx-auto max-w-6xl px-4 sm:px-6 py-8 sm:py-12 grid gap-8 lg:gap-10 lg:grid-cols-12">
        {/* Left Column: Dashboard Overview */}
        <div className="lg:col-span-4 space-y-6 sm:space-y-8">
          <div className="p-6 sm:p-8 rounded-3xl border border-white/10 bg-white/5 relative overflow-hidden shadow-2xl">
            <div className="absolute top-0 right-0 p-8 bg-accent/20 blur-[60px] rounded-full w-32 h-32 -mr-10 -mt-10"></div>
            
            <div className="relative z-10">
              <h2 className="text-xs font-semibold tracking-wider text-slate-400 uppercase">Target Role</h2>
              <p className="text-2xl sm:text-3xl font-bold text-white mt-1">{selected_role.name}</p>
              <p className="text-sm font-medium text-slate-400 mt-2 bg-black/20 inline-block px-3 py-1 rounded-lg border border-white/5">
                Target: {target_date || "Not set"}
              </p>
              
              <div className="mt-10">
                <h2 className="text-xs font-semibold tracking-wider text-slate-400 uppercase">Readiness Score</h2>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-6xl font-black tracking-tighter text-accent-soft drop-shadow-[0_0_15px_rgba(157,180,255,0.3)]">
                    {readiness_score?.toFixed(0) || 0}
                  </span>
                  <span className="text-xl font-medium text-slate-500">/ 100</span>
                </div>
                <div className="mt-4 px-4 py-1.5 rounded-full bg-accent/10 border border-accent/20 text-accent-soft text-sm inline-flex font-medium">
                  Stage: {stage || "Unknown"}
                </div>
              </div>
            </div>
          </div>

          <div className="p-6 sm:p-8 rounded-3xl border border-white/10 bg-white/5 shadow-2xl">
            <h2 className="text-sm font-semibold text-white mb-6">Progress History</h2>
            <div className="h-[200px] w-full">
              {hasGraphData ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="name" hide />
                    <YAxis 
                      domain={[0, 100]} 
                      stroke="rgba(255,255,255,0.2)" 
                      fontSize={11} 
                      tickLine={false} 
                      axisLine={false} 
                      tick={{ fill: 'rgba(255,255,255,0.4)' }}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#07111f', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)' }}
                      itemStyle={{ color: '#9db4ff', fontWeight: 600 }}
                      labelStyle={{ color: 'rgba(255,255,255,0.5)', fontSize: '12px', marginBottom: '4px' }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="score" 
                      name="Score"
                      stroke="#7c6bf5" 
                      strokeWidth={3} 
                      dot={{ fill: '#07111f', stroke: '#7c6bf5', strokeWidth: 2, r: 4 }} 
                      activeDot={{ fill: '#7c6bf5', stroke: '#fff', strokeWidth: 2, r: 6 }} 
                      animationDuration={1000}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-slate-500">
                  No history recorded yet.
                </div>
              )}
            </div>
          </div>

          {next_topic && (
            <div className="p-6 sm:p-8 rounded-3xl border border-emerald-500/20 bg-gradient-to-b from-emerald-500/10 to-emerald-500/5 shadow-2xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 blur-[40px] rounded-full -mr-10 -mt-10 transition-opacity group-hover:opacity-100 opacity-50"></div>
              
              <div className="relative z-10">
                <h2 className="text-xs font-bold uppercase tracking-widest text-emerald-400">Up Next</h2>
                <p className="text-xl sm:text-2xl font-semibold text-emerald-50 mt-3 leading-tight">{next_topic.title}</p>
                
                <button 
                  onClick={() => handleCompleteTopic(next_topic.id)}
                  disabled={isCompletingTopic === next_topic.id}
                  className="mt-6 flex items-center justify-center gap-2.5 px-5 py-3.5 bg-emerald-500 hover:bg-emerald-400 text-emerald-950 rounded-xl text-sm font-bold transition-all w-full shadow-[0_0_20px_rgba(16,185,129,0.2)] hover:shadow-[0_0_25px_rgba(16,185,129,0.4)] disabled:opacity-70 disabled:cursor-not-allowed"
                >
                  {isCompletingTopic === next_topic.id ? (
                    <LoaderCircle className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <CheckCircle2 className="w-5 h-5" />
                      Mark as Completed
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Learning Path */}
        <div className="lg:col-span-8 space-y-6 sm:space-y-8">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <h2 className="text-xl sm:text-2xl font-bold text-white">Learning Path</h2>
          </div>
          
          <div className="space-y-6">
            {(module_progress || []).map((mod, i) => (
              <div key={mod.id} className="border border-white/5 rounded-3xl bg-white/[0.03] overflow-hidden shadow-xl ring-1 ring-white/5">
                <div className="p-5 sm:p-6 border-b border-white/5 bg-white/[0.02]">
                  <div className="flex items-start sm:items-center justify-between gap-4 flex-col sm:flex-row">
                    <div>
                      <span className="text-xs font-bold tracking-wider text-accent-soft uppercase mb-1 block">Module {i+1}</span>
                      <h3 className="font-semibold text-white text-lg sm:text-xl">
                        {mod.title}
                      </h3>
                    </div>
                    <div className="flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-lg border border-white/5">
                      <div className="w-full bg-white/10 rounded-full h-1.5 w-16 overflow-hidden">
                        <div 
                          className="bg-accent h-full rounded-full transition-all duration-500"
                          style={{ width: `${mod.total_count > 0 ? (mod.completed_count / mod.total_count) * 100 : 0}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold text-slate-300">
                        {mod.completed_count}/{mod.total_count}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-slate-400 mt-3 leading-relaxed">{mod.description}</p>
                </div>
                
                <div className="divide-y divide-white/5">
                  {(mod.topics || []).map(topic => {
                    const isCompleting = isCompletingTopic === topic.id;
                    return (
                      <div key={topic.id} className="p-5 sm:p-6 flex gap-4 sm:gap-5 hover:bg-white/[0.02] transition-colors group">
                        <div className="mt-1 flex-shrink-0">
                          {topic.completed ? (
                            <div className="bg-emerald-500/20 p-1 rounded-full">
                              <CheckCircle className="w-5 h-5 text-emerald-400" />
                            </div>
                          ) : (
                            <div className="p-1">
                              <Circle className="w-5 h-5 text-slate-600 group-hover:text-slate-500 transition-colors" />
                            </div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 sm:gap-4">
                            <h4 className={`text-base sm:text-lg font-semibold ${topic.completed ? 'text-slate-300' : 'text-slate-100'}`}>
                              {topic.title}
                            </h4>
                            <span className="text-xs font-medium text-slate-500 bg-black/20 px-2 py-1 rounded whitespace-nowrap self-start">
                              {topic.estimated_minutes} min
                            </span>
                          </div>
                          <p className="text-sm text-slate-400 mt-2 leading-relaxed">{topic.description}</p>
                          
                          <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                            <div className="flex flex-wrap gap-2">
                              {(topic.skill_tags || []).map(tag => (
                                <span key={tag} className="text-[10px] uppercase font-semibold tracking-wider px-2.5 py-1 rounded bg-white/5 text-slate-400 border border-white/10">
                                  {tag.replace('-', ' ')}
                                </span>
                              ))}
                            </div>
                            
                            {!topic.completed && (
                              <button 
                                onClick={() => handleCompleteTopic(topic.id)}
                                disabled={isCompletingTopic !== null}
                                className="self-start sm:self-auto flex items-center justify-center min-w-[100px] text-xs font-bold px-4 py-2 rounded-xl bg-accent/10 text-accent hover:bg-accent hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed border border-accent/20 hover:border-accent"
                              >
                                {isCompleting ? <LoaderCircle className="w-4 h-4 animate-spin" /> : "Complete"}
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
