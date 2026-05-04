"use client";

import React, { useEffect, useRef } from "react";
import { Terminal, Cpu, CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface Log {
  message: string;
  type: "info" | "success" | "error" | "warning";
  timestamp: string;
}

interface TerminalLogsProps {
  logs: Log[];
  isVisible: boolean;
}

export default function TerminalLogs({ logs, isVisible }: TerminalLogsProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  if (!isVisible && logs.length === 0) return null;

  return (
    <div className={cn(
      "fixed bottom-6 left-6 z-50 w-[400px] bg-[#1a1c1e] rounded-2xl border border-white/10 shadow-2xl overflow-hidden transition-all duration-500",
      isVisible ? "translate-y-0 opacity-100" : "translate-y-12 opacity-0 pointer-events-none"
    )}>
      <div className="flex items-center justify-between px-4 py-2 border-b border-white/5 bg-white/5">
        <div className="flex items-center gap-2">
          <Terminal className="w-3 h-3 text-indigo-400" />
          <span className="text-[10px] font-black text-white/40 uppercase tracking-widest">Engine Monitor</span>
        </div>
        <div className="flex gap-1">
          <div className="w-2 h-2 rounded-full bg-red-500/50" />
          <div className="w-2 h-2 rounded-full bg-amber-500/50" />
          <div className="w-2 h-2 rounded-full bg-emerald-500/50" />
        </div>
      </div>
      
      <div 
        ref={scrollRef}
        className="h-40 overflow-y-auto p-4 font-mono text-[10px] space-y-1.5 scrollbar-thin scrollbar-thumb-white/10"
      >
        {logs.map((log, i) => (
          <div key={i} className="flex gap-2 animate-in fade-in slide-in-from-left-2 duration-300">
            <span className="text-white/20">[{log.timestamp}]</span>
            <span className={cn(
              "flex-1",
              log.type === "info" && "text-white/80",
              log.type === "success" && "text-emerald-400",
              log.type === "error" && "text-red-400 font-bold",
              log.type === "warning" && "text-amber-400"
            )}>
              {log.message}
            </span>
          </div>
        ))}
        {logs.length === 0 && (
          <div className="text-white/20 italic">Aguardando processos...</div>
        )}
      </div>

      <div className="px-4 py-2 bg-white/[0.02] flex items-center gap-3">
        <Cpu className="w-3 h-3 text-indigo-400 animate-pulse" />
        <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
          <div className="h-full bg-indigo-500 w-[60%] animate-pulse" />
        </div>
      </div>
    </div>
  );
}
