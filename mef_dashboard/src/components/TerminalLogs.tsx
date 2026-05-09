"use client";

import React, { useEffect, useRef } from "react";
import { Terminal, Cpu, Database, Activity, TerminalSquare } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

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
    <AnimatePresence>
      {isVisible && (
        <motion.div 
          initial={{ y: 20, opacity: 0, scale: 0.95 }}
          animate={{ y: 0, opacity: 1, scale: 1 }}
          exit={{ y: 20, opacity: 0, scale: 0.95 }}
          className={cn(
            "fixed bottom-8 right-8 z-50 w-[450px] overflow-hidden",
            "bg-slate-100/80 backdrop-blur-xl rounded-[2rem] border border-slate-200 shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white/5">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
              <div className="flex flex-col">
                <span className="text-[10px] font-black text-slate-900 uppercase tracking-[0.3em] leading-none">Console de Análise</span>
                <span className="text-[8px] font-medium text-slate-500 uppercase tracking-widest mt-1">MEF Engine Node-01</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-white/5" />
                <div className="w-1.5 h-1.5 rounded-full bg-white/5" />
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500/20" />
              </div>
              <TerminalSquare className="w-4 h-4 text-slate-500" />
            </div>
          </div>
          
          {/* Content */}
          <div 
            ref={scrollRef}
            className="h-56 overflow-y-auto p-6 font-mono text-[10px] space-y-2.5 scrollbar-thin scrollbar-thumb-white/5 relative"
          >
            {/* Scanline Effect Overlay */}
            <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(255,0,0,0.02),rgba(0,255,0,0.01),rgba(0,0,255,0.02))] bg-[length:100%_2px,3px_100%] z-10" />

            {logs.map((log, i) => (
              <motion.div 
                key={i} 
                initial={{ x: -10, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                className="flex gap-3 leading-relaxed group"
              >
                <span className="text-blue-500/40 shrink-0 font-bold tracking-tighter">[{log.timestamp}]</span>
                <span className={cn(
                  "flex-1 tracking-tight",
                  log.type === "info" && "text-slate-300",
                  log.type === "success" && "text-emerald-600 font-bold drop-shadow-[0_0_5px_rgba(52,211,153,0.3)]",
                  log.type === "error" && "text-red-600 font-black uppercase tracking-widest",
                  log.type === "warning" && "text-amber-600"
                )}>
                  <span className="opacity-40 mr-1.5">›</span>
                  {log.message}
                </span>
              </motion.div>
            ))}
            {logs.length === 0 && (
              <div className="text-slate-600 italic animate-pulse">Aguardando sinais do motor estrutural...</div>
            )}
          </div>

          {/* Footer Metrics */}
          <div className="px-6 py-4 bg-white/[0.02] border-t border-slate-200 grid grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-[8px] font-black uppercase tracking-widest text-slate-500">
                <span>CPU Load</span>
                <span className="text-blue-600">42%</span>
              </div>
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: "42%" }}
                  className="h-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" 
                />
              </div>
            </div>
            
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-[8px] font-black uppercase tracking-widest text-slate-500">
                <span>Memory</span>
                <span className="text-emerald-600">128MB</span>
              </div>
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: "24%" }}
                  className="h-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" 
                />
              </div>
            </div>

            <div className="flex flex-col justify-center items-end">
              <div className="flex items-center gap-2 text-[10px] font-mono text-blue-600 font-black">
                <Activity className="w-3 h-3 animate-pulse" />
                LIVE
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
