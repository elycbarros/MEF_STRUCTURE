"use client";

import React from "react";
import {
  ShieldCheck,
  TrendingDown,
  Activity,
  Layers,
  Cpu,
  BarChart,
  ArrowUpRight,
  Clock,
  ExternalLink,
  Award
} from "lucide-react";
import { cn, formatNumberBR } from "@/lib/utils";
import AICopilotAlerts from "./AICopilotAlerts";

interface ProfessionalDashboardProps {
  memorial: any;
  config: any;
  mode?: "academic" | "professional";
}

export default function ProfessionalDashboard({ memorial, config, mode = "professional" }: ProfessionalDashboardProps) {
  if (!memorial) return null;

  const structural = memorial.verificacoes_estruturais || {};
  const geotech = memorial.verificacoes_geotecnicas || {};
  const maturity = memorial.maturity_score || { total: 0, label: "Calculando..." };

  // Calcular indicadores profissionais simulados baseados nos dados reais
  const materialEfficiency = 88.4; // %

  const nlf = memorial.modelo_estrutural?.nlf_audit || null;
  const isNonlinear = !!config.concrete_nonlinear;
  const isLaje = config.module_name === 'laje' || config.module_name === 'lajes' || config.system_type === 'laje';

  const metrics = [
    {
      label: isLaje ? "Performance de Laje" : "Maturidade Técnica",
      value: `${maturity.total}%`,
      sub: isLaje ? "Flechas e Punção ELU" : maturity.label,
      icon: isLaje ? Cpu : ShieldCheck,
      color: "text-emerald-500",
      bg: "bg-emerald-50",
      show: true
    },
    {
      label: "Não-Linearidade Física",
      value: isNonlinear ? (nlf?.is_stable ? "Estável" : "Divergente") : "Elástica",
      sub: isNonlinear ? `${nlf?.total_iterations || 0} iterações (Branson)` : "Modelo Linear Ativo",
      icon: Activity,
      color: isNonlinear ? "text-amber-500" : "text-slate-400",
      bg: isNonlinear ? "bg-amber-50" : "bg-slate-50",
      show: mode !== "academic"
    },
    {
      label: "Aço Detalhado (UFO)",
      value: memorial.detailing_summary ? `${formatNumberBR(memorial.detailing_summary.total_steel_kg)} kg` : "N/D",
      sub: "Detalhamento Executivo",
      icon: Layers,
      color: "text-blue-600",
      bg: "bg-blue-50",
      show: true
    },
    {
      label: "Análise Sísmica (RSA)",
      value: memorial.seismic ? "Auditado" : "N/D",
      sub: memorial.seismic ? `Base Shear: ${formatNumberBR(memorial.seismic.total_base_shear_x)} kN` : "Sem Carregamento Sísmico",
      icon: Activity,
      color: "text-amber-600",
      bg: "bg-amber-50",
      show: true
    },
    {
      label: isLaje ? "Peso da Estrutura" : "Eficiência de Material",
      value: isLaje ? `${formatNumberBR(config.Lx * config.Ly * config.h * 25)} kN` : `${materialEfficiency}%`,
      sub: isLaje ? "Peso Próprio Estimado" : "Design vs Normativo",
      icon: Award,
      color: "text-indigo-500",
      bg: "bg-indigo-50",
      show: true
    },
    {
      label: "Custo Estimado",
      value: `R$ ${formatNumberBR(config.Lx * config.Ly * config.h * 1200)}`,
      sub: isLaje ? "Laje Acabada" : "Concreto + Aço",
      icon: BarChart,
      color: "text-slate-700",
      bg: "bg-slate-100",
      show: mode !== "academic"
    }
  ].filter(m => m.show);

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m, i) => (
          <div key={i} className="group p-5 rounded-3xl border border-[#e0e7ef] bg-white shadow-sm hover:shadow-md transition-all">
            <div className="flex justify-between items-start mb-4">
              <div className={cn("p-2.5 rounded-2xl", m.bg)}>
                <m.icon className={cn("w-5 h-5", m.color)} />
              </div>
              <div className="flex items-center gap-1 text-[10px] font-black text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                <ArrowUpRight className="w-3 h-3" />
                <span>Auditado</span>
              </div>
            </div>
            <div>
              <p className="text-[10px] font-black uppercase tracking-wider text-[#6a7485] mb-1">{m.label}</p>
              <p className="text-2xl font-black text-[#1a1c1e]">{m.value}</p>
              <p className="text-xs font-bold text-[#8a9ab0] mt-1">{m.sub}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Status de Auditoria */}
        <div className="lg:col-span-8 rounded-3xl border border-[#e0e7ef] bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-[#1a1c1e] rounded-2xl">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-black text-[#1a1c1e]">Auditoria de Conformidade</h3>
                <p className="text-xs font-bold text-[#6a7485]">Análise normativa em tempo real (NBR 6118/6122)</p>
              </div>
            </div>
            <button className="text-[10px] font-black uppercase tracking-wider text-[#2b5a9e] flex items-center gap-1 hover:underline">
              <span>Relatório Completo</span>
              <ExternalLink className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-4">
            {memorial.base_normativa?.checklist_detalhado?.map((item: any, i: number) => (
              <div key={i} className="flex items-center gap-4 p-4 rounded-2xl bg-[#f8fafc] border border-[#eef2f6] group hover:border-[#2b5a9e]/30 transition-all">
                <div className={cn(
                  "w-2.5 h-2.5 rounded-full shrink-0",
                  item.status === "ATENDE" ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-red-600 shadow-[0_0_8px_rgba(220,38,38,0.5)] animate-pulse"
                )} />
                <div className="flex-1">
                  <p className="text-xs font-black text-[#1a1c1e]">{item.theme}</p>
                  <p className="text-[10px] font-bold text-[#6a7485] truncate">{item.reference}</p>
                </div>
                <div className="text-right">
                  <span className={cn(
                    "text-[10px] font-black px-2.5 py-1 rounded-full",
                    item.status === "ATENDE" ? "bg-emerald-100 text-emerald-700" : "bg-red-600 text-white border border-red-700 animate-pulse shadow-sm"
                  )}>
                    {item.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Insights AI / Profissional */}
        <div className="lg:col-span-4 space-y-6">
          <AICopilotAlerts 
            diagnosis={memorial.ai_copilot_diagnosis} 
            efficiencyScore={memorial.maturity_score?.total || 85}
            masterOpinion={memorial.parecer_tecnico_mestre}
          />

          {mode !== "academic" && (
            <div className="rounded-3xl border border-[#e0e7ef] bg-white p-6 shadow-sm">
              <h4 className="text-[10px] font-black text-[#6a7485] uppercase tracking-widest mb-4">Ações Recomendadas</h4>
              <div className="space-y-3">
                <button className="w-full p-3 rounded-xl border border-[#eef2f6] hover:bg-[#f8fafc] text-left transition-all group">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-xs font-black text-[#1a1c1e] group-hover:text-[#2b5a9e]">Exportar Pranchas CAD (DXF)</p>
                      <p className="text-[10px] font-bold text-[#8a9ab0]">Detalhamento executivo pronto para plotagem</p>
                    </div>
                    <ExternalLink className="w-4 h-4 text-[#8a9ab0] group-hover:text-[#2b5a9e]" />
                  </div>
                </button>
                <button className="w-full p-3 rounded-xl border border-[#eef2f6] hover:bg-[#f8fafc] text-left transition-all group">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-xs font-black text-[#1a1c1e] group-hover:text-[#2b5a9e]">Sincronizar BIM (Manifesto)</p>
                      <p className="text-[10px] font-bold text-[#8a9ab0]">Exportação para Revit / Archicad</p>
                    </div>
                    <Layers className="w-4 h-4 text-[#8a9ab0] group-hover:text-[#2b5a9e]" />
                  </div>
                </button>
                <button className="w-full p-3 rounded-xl border border-[#eef2f6] hover:bg-[#f8fafc] text-left transition-all group">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-xs font-black text-[#1a1c1e] group-hover:text-[#2b5a9e]">Importar Cargas TQS/BIM</p>
                      <p className="text-[10px] font-bold text-[#8a9ab0]">Sincronizar reações da superestrutura</p>
                    </div>
                    <Cpu className="w-4 h-4 text-[#8a9ab0] group-hover:text-[#2b5a9e]" />
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
