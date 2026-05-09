"use client";

import React from "react";
import { Cpu } from "lucide-react";

interface ProfessionalDashboardProps {
  memorial: any;
  config: any;
  mode?: "academic" | "professional";
}

export default function ProfessionalDashboard({ memorial, config, mode = "professional" }: ProfessionalDashboardProps) {
  return (
    <div className="mt-8 flex h-[600px] w-full flex-col items-center justify-center rounded-[48px] border border-slate-200 bg-[#0f172a] shadow-2xl relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-transparent" />
      <div className="relative text-center">
        <div className="absolute -inset-10 animate-pulse rounded-full bg-blue-500/10 blur-3xl" />
        <Cpu className="mx-auto h-16 w-16 text-blue-500/20 mb-8" />
        <h2 className="relative text-5xl font-black uppercase tracking-[0.2em] text-white/10 italic">
          EM BREVE
        </h2>
        <p className="mt-4 text-[10px] font-black uppercase tracking-[0.5em] text-blue-500/40">
          STRUCTURAL PRO CORE ACTIVE - INTERFACE EM REFATORAÇÃO
        </p>
      </div>
    </div>
  );
}
