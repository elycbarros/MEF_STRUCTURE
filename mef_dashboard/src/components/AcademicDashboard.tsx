"use client";

import React from "react";
import { Cpu } from "lucide-react";
import type { AcademicTabId } from "@/hooks/useProjectState";

interface AcademicDashboardProps {
  setActiveTab: (tab: AcademicTabId) => void;
  setSystemType: (type: "radier" | "laje") => void;
}

export function AcademicDashboard({ setActiveTab, setSystemType }: AcademicDashboardProps) {
  return (
    <div className="flex h-[400px] w-full flex-col items-center justify-center rounded-[48px] border border-dashed border-slate-200 bg-white/5">
      <div className="text-center">
        <Cpu className="mx-auto h-12 w-12 text-slate-900/10 mb-4 animate-pulse" />
        <h2 className="text-3xl font-black uppercase tracking-[0.3em] text-slate-900">Mestre Structural Lab</h2>
        <p className="mt-4 text-[10px] font-black uppercase tracking-[0.5em] text-slate-400">
          EM BREVE - REFATORANDO INTERFACE PEDAGÓGICA
        </p>
        <p className="mt-2 text-[9px] font-bold text-slate-500 uppercase tracking-widest">
          UTILIZE O MENU LATERAL PARA ACESSAR OS MÓDULOS ATIVOS
        </p>
      </div>
    </div>
  );
}
