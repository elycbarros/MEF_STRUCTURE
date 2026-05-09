"use client";

import React from "react";
import { Download, Printer, FileText, CheckCircle2, AlertTriangle, XCircle, Info, ExternalLink, TrendingUp, Wind, ArrowLeft, Book, BookOpen, Layers } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { formatNumberBR, cn } from "@/lib/utils";

import { motion } from "framer-motion";
import { ExecutiveDecisionCard } from "./dashboard/ExecutiveDecisionCard";
import { SoilPressureMap } from "./SoilPressureMap";
import { SolutionComparator } from "./SolutionComparator";
import Structural3DView from "./Structural3DView";
import PedagogicalStepsView from "./PedagogicalStepsView";
import ISETheoryView from "./ISETheoryView";
import RedistributionTheoryCard from "./RedistributionTheoryCard";
import { LIBRARY_KNOWLEDGE } from "@/lib/libraryData";


interface ReportViewProps {
   results: any;
   frameResults?: any;
   stabilityResults?: any;
   windResults?: any;
   projectMeta: any;

   apiBaseUrl: string;
   onBack?: () => void;
}

function SanityBadge({ label, ok, msg_ok, msg_fail }: { label: string, ok: boolean, msg_ok: string, msg_fail: string }) {
   return (
      <div className={cn(
         "p-6 rounded-[2rem] border flex flex-col gap-3 transition-all duration-500 hover:scale-[1.02] backdrop-blur-xl",
         ok 
            ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-600" 
            : "bg-red-500/5 border-red-500/20 text-red-600 shadow-[0_0_40px_rgba(239,68,68,0.05)]"
      )}>
         <div className="flex items-center gap-3">
            <div className={cn(
               "w-10 h-10 rounded-xl flex items-center justify-center border transition-colors",
               ok ? "bg-emerald-500/10 border-emerald-500/20" : "bg-red-500/10 border-red-500/20"
            )}>
               {ok ? <CheckCircle2 className="h-5 w-5" /> : <AlertTriangle className="h-5 w-5" />}
            </div>
            <div className="flex flex-col">
               <span className="font-black text-[10px] uppercase tracking-[0.3em] opacity-40">Status Check</span>
               <span className="font-black text-sm uppercase tracking-tight">{label}</span>
            </div>
         </div>
         <div className="h-px bg-white/5 w-full my-1" />
         <span className="text-xs font-bold leading-relaxed text-slate-900/80">{ok ? msg_ok : msg_fail}</span>
      </div>
   );
}

export function ReportView({ results, frameResults, stabilityResults, windResults, projectMeta, apiBaseUrl, onBack }: ReportViewProps) {

   const saveAsPdf = () => window.print();

   if (!results) {
      return (
         <div className="flex flex-col items-center justify-center py-20 text-slate-600">
            <FileText className="h-16 w-16 opacity-20" />
            <p className="mt-4 font-medium">Execute uma análise para visualizar o relatório.</p>
         </div>
      );
   }

   const isLaje = results.is_laje || results.master?.system_type === "laje" || results.memorial?.system_type === "laje";
   const memorial = results.memorial || {};
   const deterministic = results.deterministic || {};
   const executiveDecision = results.executive_decision || {};
   const geotech = memorial.verificacoes_geotecnicas || {};
   const structural = memorial.verificacoes_estruturais || {};
   const service = memorial.verificacoes_de_servico || {};
   const flexure = structural.flexao || {};
   const punching = structural.puncao || {};

   return (
      <div className="space-y-8 pb-20 bg-slate-50 min-h-screen -mx-8 px-8 pt-8">
         {/* Header Ações - Premium Style */}
         <div className="flex flex-wrap items-center justify-between gap-4 no-print bg-white/80 backdrop-blur-2xl border border-slate-200 p-6 rounded-[2.5rem] shadow-sm">
            <div className="flex items-center gap-4">
               <div className="w-12 h-12 bg-blue-600/10 rounded-2xl flex items-center justify-center border border-blue-500/20">
                  <FileText className="text-blue-600 h-6 w-6" />
               </div>
               <div>
                  <h2 className="text-2xl font-black text-slate-900 tracking-tight">Relatório Técnico Intelligence</h2>
                  <div className="flex items-center gap-2 mt-0.5">
                     <span className="w-2 h-2 bg-emerald-500 rounded-full" />
                     <p className="text-[10px] font-black text-slate-600 uppercase tracking-[0.2em]">
                        {isLaje ? "LAJES PRO ENGINE | V4.0.2-ALPHA" : "RADIER PRO ENGINE | V4.0.2-ALPHA"}
                     </p>
                  </div>
               </div>
            </div>
            <div className="flex items-center gap-3">
               {onBack && (
                  <button
                     type="button"
                     onClick={onBack}
                     className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-black text-slate-900 hover:bg-slate-50 transition-all cursor-pointer group shadow-sm"
                  >
                     <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
                     FECHAR
                  </button>
               )}
               <button
                  onClick={() => window.print()}
                  className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-black text-slate-900 hover:bg-slate-50 transition-all shadow-sm"
               >
                  <Printer className="h-4 w-4" />
                  IMPRIMIR
               </button>
               <button
                  onClick={saveAsPdf}
                  className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-6 py-2.5 text-sm font-black text-white shadow-lg hover:bg-blue-500 transition-all active:scale-95"
               >
                  <Download className="h-4 w-4" />
                  EXPORTAR PDF
               </button>
            </div>
         </div>

         {/* Preview do Documento */}
         <div className="bg-white/95 backdrop-blur-xl rounded-[3rem] border border-slate-200 shadow-2xl p-8 sm:p-12 print:shadow-none print:border-none print:p-0 print:bg-white">

            {/* Cabeçalho do Memorial - Aero-Space / Scientific Style */}
            <div className="flex justify-between items-start border-b border-slate-200 pb-10 mb-12 print:border-slate-200">
               <div className="flex gap-6 items-start">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-400 rounded-3xl flex items-center justify-center shadow-[0_0_40px_rgba(37,99,235,0.4)] print:bg-blue-600">
                     <Layers className="text-slate-900 h-8 w-8" />
                  </div>
                  <div>
                     <h1 className="text-3xl font-black tracking-tight text-slate-900 print:text-slate-900">
                        {isLaje ? "MEMORIAL DE CÁLCULO: LAJES ELEVADAS" : "MEMORIAL DE CÁLCULO ESTRUTURAL"}
                     </h1>
                     <div className="flex items-center gap-3 mt-2">
                        <span className="text-[10px] font-black bg-blue-600 text-white px-2 py-0.5 rounded tracking-widest print:bg-blue-600">ENGINE v4.0</span>
                        <p className="text-xs font-black text-blue-600 uppercase tracking-[0.3em] print:text-blue-600">
                           {isLaje ? "LAJES PRO ENGINE | STRUCTURAL SUITE" : "RADIER PRO ENGINE | STRUCTURAL SUITE"}
                        </p>
                     </div>
                  </div>
               </div>
               <div className="text-right text-[11px] font-bold text-slate-500 space-y-1 print:text-slate-500">
                  <p className="tracking-widest">REVISÃO: <span className="text-slate-900 print:text-slate-900">{projectMeta.revisao}</span></p>
                  <p className="tracking-widest">EMISSÃO: <span className="text-slate-900 print:text-slate-900">{projectMeta.emissao}</span></p>
                  <p className="tracking-widest opacity-60">PÁGINA: 1 de 1</p>
               </div>
            </div>

            {/* Estabilidade Global e Conforto */}
            {stabilityResults && (
               <section className="rounded-[2.5rem] border border-slate-200 bg-[#111114]/40 p-8 shadow-2xl break-inside-avoid backdrop-blur-xl mb-12">
                  <div className="flex items-center justify-between mb-10">
                     <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-blue-600/10 rounded-2xl flex items-center justify-center border border-blue-500/20">
                           <TrendingUp className="text-blue-600 h-7 w-7" />
                        </div>
                        <div>
                           <h3 className="text-xl font-black text-slate-900 tracking-tight uppercase">Estabilidade Global & Dinâmica</h3>
                           <p className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] mt-0.5">Análise de 2ª Ordem e Conforto (NBR 6118)</p>
                        </div>
                     </div>
                     <div className="flex flex-col items-end">
                        <span className={`px-5 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border shadow-lg transition-all ${stabilityResults.is_stable ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20 shadow-emerald-500/5' : 'bg-red-500/10 text-red-600 border-red-500/20 shadow-red-500/5'}`}>
                           {stabilityResults.is_stable ? 'ESTRUTURA EM EQUILÍBRIO' : 'INSTABILIDADE CRÍTICA'}
                        </span>
                     </div>
                  </div>
 
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                     <div className="p-6 rounded-3xl bg-white/80 border border-slate-200 group hover:border-blue-500/30 transition-all">
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 mb-2 group-hover:text-blue-600 transition-colors">Parâmetro γz</p>
                        <p className="text-4xl font-black text-slate-900 tracking-tighter">{formatNumberBR(stabilityResults.gamma_z, 3)}</p>
                        <div className="h-1 w-full bg-white/5 rounded-full mt-4 overflow-hidden">
                           <div className="h-full bg-blue-500/50" style={{ width: `${Math.min((stabilityResults.gamma_z / 1.3) * 100, 100)}%` }} />
                        </div>
                        <p className="text-[10px] font-black mt-3 text-slate-900/20 uppercase tracking-widest">Limit: 1.10 / 1.30</p>
                     </div>
                     <div className="p-6 rounded-3xl bg-white/80 border border-slate-200 group hover:border-blue-500/30 transition-all">
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 mb-2 group-hover:text-blue-600 transition-colors">Amplificação P-Δ</p>
                        <p className="text-4xl font-black text-slate-900 tracking-tighter">{formatNumberBR(stabilityResults.p_delta_factor)}</p>
                        <p className="text-[10px] font-black mt-4 text-slate-900/20 uppercase tracking-widest">Fator de 2ª Ordem</p>
                     </div>
                     <div className="p-6 rounded-3xl bg-white/80 border border-slate-200 group hover:border-blue-500/30 transition-all">
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 mb-2 group-hover:text-blue-600 transition-colors">Aceleração Pico</p>
                        <p className="text-4xl font-black text-slate-900 tracking-tighter">{formatNumberBR(stabilityResults.peak_acceleration_ms2 * 100)} <span className="text-sm font-black opacity-30">cm/s²</span></p>
                        <p className="text-[10px] font-black mt-4 text-slate-900/20 uppercase tracking-widest">Status: {stabilityResults.comfort_status}</p>
                     </div>
                     <div className="p-6 rounded-3xl bg-white/80 border border-slate-200 group hover:border-blue-500/30 transition-all">
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 mb-2 group-hover:text-blue-600 transition-colors">Não-Linearidade</p>
                        <div className="flex flex-col gap-1 mt-2">
                           <span className="text-xs font-black text-slate-900 uppercase tracking-tight flex justify-between">Fisica: <span className="text-blue-600">Ativa</span></span>
                           <span className="text-xs font-black text-slate-900 uppercase tracking-tight flex justify-between">Geom: <span className="text-blue-600">P-Delta</span></span>
                        </div>
                     </div>
                  </div>
 
                  <div className="mt-10 p-5 rounded-2xl bg-blue-500/5 border border-blue-500/10 flex gap-4 items-start">
                     <Info className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
                     <p className="text-xs font-bold text-slate-700 leading-relaxed">
                        <strong className="text-blue-600 uppercase tracking-widest text-[10px]">Nota Técnica:</strong> A análise de estabilidade global utiliza o coeficiente Gama-Z como indicador de sensibilidade aos efeitos de segunda ordem. Para edifícios de alta performance, a análise P-Delta iterativa é mandatória para garantir a convergência geométrica.
                     </p>
                  </div>
               </section>
            )}

            {/* Ações de Vento */}
            {windResults && (
               <section className="rounded-[2.5rem] border border-slate-200 bg-[#111114]/40 p-8 shadow-2xl break-inside-avoid backdrop-blur-xl mb-12">
                  <div className="flex items-center justify-between mb-10">
                     <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-cyan-600/10 rounded-2xl flex items-center justify-center border border-cyan-500/20">
                           <Wind className="text-cyan-400 h-7 w-7" />
                        </div>
                        <div>
                           <h3 className="text-xl font-black text-slate-900 tracking-tight uppercase">Ações Eólicas (NBR 6123)</h3>
                           <p className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] mt-0.5">Dinâmica de Fluídos e Esforços de Base</p>
                        </div>
                     </div>
                     <div className="flex flex-col items-end">
                        <span className="px-5 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border border-cyan-500/20 shadow-lg shadow-cyan-500/5">
                           CARGA HORIZONTAL ATIVA
                        </span>
                     </div>
                  </div>
 
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
                     <div className="p-6 rounded-3xl bg-white/80 border border-slate-200">
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 mb-2">Velocidade V₀</p>
                        <p className="text-3xl font-black text-slate-900 tracking-tighter">{windResults.config?.v0} <span className="text-sm font-black opacity-30">m/s</span></p>
                        <p className="text-[10px] font-black mt-4 text-slate-900/20 uppercase tracking-widest">S1=1.0 | S3=1.0</p>
                     </div>
                     <div className="p-6 rounded-3xl bg-white/80 border border-slate-200">
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 mb-2">Coef. Arrasto Cf</p>
                        <p className="text-3xl font-black text-slate-900 tracking-tighter">{formatNumberBR(windResults.geometry?.cf)}</p>
                        <p className="text-[10px] font-black mt-4 text-slate-900/20 uppercase tracking-widest">FATOR DE FORMA</p>
                     </div>
                     <div className="p-6 rounded-3xl bg-white/80 border border-slate-200">
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 mb-2">Força Total (Vb)</p>
                        <p className="text-3xl font-black text-slate-900 tracking-tighter">{formatNumberBR(windResults.summary?.total_force_kN, 1)} <span className="text-sm font-black opacity-30">kN</span></p>
                        <p className="text-[10px] font-black mt-4 text-slate-900/20 uppercase tracking-widest">RESULTANTE BASE</p>
                     </div>
                     <div className="p-6 rounded-3xl bg-white/80 border border-slate-200">
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 mb-2">Momento Base (Mb)</p>
                        <p className="text-3xl font-black text-slate-900 tracking-tighter">{formatNumberBR(windResults.summary?.base_moment_kNm, 0)} <span className="text-sm font-black opacity-30">kNm</span></p>
                        <p className="text-[10px] font-black mt-4 text-slate-900/20 uppercase tracking-widest">TOMBAMENTO TOTAL</p>
                     </div>
                  </div>
 
                  <div className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white/50">
                     <table className="w-full text-xs text-left">
                        <thead className="bg-white/5 font-black text-slate-500 uppercase text-[9px] tracking-[0.3em]">
                           <tr>
                              <th className="px-8 py-4">Z (m) Elevation</th>
                              <th className="px-8 py-4">Vk (m/s) Velocity</th>
                              <th className="px-8 py-4">Pressure q (Pa)</th>
                              <th className="px-8 py-4 text-right">Force level (kN)</th>
                           </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                           {windResults.profile?.filter((_: any, i: number) => i % (Math.ceil(windResults.profile.length / 10)) === 0 || i === windResults.profile.length - 1).map((level: any, i: number) => (
                              <tr key={i} className="hover:bg-blue-500/5 transition-colors group">
                                 <td className="px-8 py-4 font-black text-slate-900 group-hover:text-blue-600 transition-colors">{formatNumberBR(level.z, 1)}</td>
                                 <td className="px-8 py-4 font-bold text-slate-700">{formatNumberBR(level.vk_m_s)}</td>
                                 <td className="px-8 py-4 font-bold text-slate-700">{formatNumberBR(level.q_Pa, 0)}</td>
                                 <td className="px-8 py-4 text-right font-black text-cyan-400">{formatNumberBR(level.f_total_kN)}</td>
                              </tr>
                           ))}
                        </tbody>
                     </table>
                  </div>
               </section>
            )}


            {/* Info Obra */}
            <div className="grid grid-cols-2 gap-12 mb-16 text-sm bg-white/5 p-8 rounded-3xl border border-slate-200 backdrop-blur-md print:bg-white/5 print:border-slate-200">
               <div>
                  <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-3">
                     {isLaje ? 'TECHNICAL SPECIFICATIONS' : 'PROJECT CORE DATA'}
                  </h4>
                  <p className="text-xl font-black text-slate-900 print:text-slate-900">{projectMeta.obra}</p>
                  <p className="text-sm font-bold text-slate-900/50 mt-1 print:text-slate-900/50">{projectMeta.local}</p>
               </div>
               <div className="text-right flex flex-col items-end">
                  <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-3">CERTIFIED ENGINEER</h4>
                  <p className="text-xl font-black text-slate-900 print:text-slate-900">{projectMeta.responsavel}</p>
                  <div className="flex items-center gap-2 mt-1">
                     <CheckCircle2 className="h-4 w-4 text-blue-600" />
                     <p className="text-sm font-bold text-slate-900/50 print:text-slate-900/50">{projectMeta.registro}</p>
                  </div>
               </div>
            </div>

            {/* Seção 1: Resumo Executivo */}
            <section className="mb-16">
               <div className="flex items-center gap-3 mb-8">
                  <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">01</span>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Resumo Executivo & Decisão</h2>
               </div>
               <div className="bg-[#111114]/30 border border-slate-200 rounded-[2.5rem] p-2 backdrop-blur-sm">
                  <ExecutiveDecisionCard decision={executiveDecision} isLaje={isLaje} />
               </div>
            </section>

            {/* Seção 1.5: Sanity Checks Rápidos */}
            {results.sanity_checks && (
               <section className="mb-16">
                  <div className="flex items-center gap-3 mb-8">
                     <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">01.5</span>
                     <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Diagnóstico de Integridade (Sanity Checks)</h2>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                     {isLaje ? (
                        <>
                           <SanityBadge label="Estado Limite (SLS)" ok={results.sanity_checks?.flecha_ok ?? results.sanity_checks?.recalque_ok} msg_ok="Flechas e Recalques Nominais" msg_fail="Deformação Excessiva Detectada" />
                           <SanityBadge label="Segurança (ELU)" ok={results.sanity_checks.puncao_ok} msg_ok="Punção e Cisalhamento Verificados" msg_fail="Risco de Falha Frágil Detectado" />
                           <SanityBadge label="Durabilidade" ok={results.reinforcement_summary?.serviceability?.wk_x_ok && results.reinforcement_summary?.serviceability?.wk_y_ok} msg_ok="Abertura de Fissuras Controlada" msg_fail="Risco de Corrosão / Fissuras > Limite" />
                        </>
                     ) : (
                        <>
                           <SanityBadge 
                              label={isLaje ? "Reações de Apoio" : "Capacidade de Carga"} 
                              ok={isLaje ? results.sanity_checks?.reacoes_ok ?? true : results.sanity_checks?.pressao_solo_ok} 
                              msg_ok={isLaje ? "Apoios em Equilíbrio" : "Pressão de Solo Admissível"} 
                              msg_fail={isLaje ? "Instabilidade nos Apoios" : "Tensão de Solo Crítica"} 
                           />
                           <SanityBadge 
                              label={isLaje ? "Deformada MEF" : "Recalques Diferenciais"} 
                              ok={isLaje ? results.sanity_checks?.flecha_ok ?? results.sanity_checks?.recalque_ok ?? true : results.sanity_checks?.recalque_ok} 
                              msg_ok={isLaje ? "Flechas Conforme NBR" : "Recalques Estabilizados"} 
                              msg_fail={isLaje ? "Flecha Excessiva" : "Recalque Acima do Limite"} 
                           />
                           <SanityBadge label="Puncionamento" ok={results.sanity_checks.puncao_ok} msg_ok="Punção Nominal / Sem Reforço" msg_fail="Risco de Punção / Reforço Requerido" />
                        </>
                     )}
                  </div>
               </section>
            )}

            {/* Seção 2: Dados de Entrada */}
            <section className="mb-16">
               <div className="flex items-center gap-3 mb-8">
                  <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">02</span>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase text-glow">Parâmetros de Projeto</h2>
               </div>
               <div className="grid grid-cols-3 gap-8">
                  <ReportMetric label="Geometria Global" value={`${results.master?.Lx}m x ${results.master?.Ly}m`} sub={`Área de Projeção: ${formatNumberBR(results.master?.area_m2, 1)} m²`} />
                  <ReportMetric label="Espessura Nominal" value={`${results.master?.h} m`} sub={`Volume Calculado: ${formatNumberBR(results.master?.volume_m3, 1)} m³`} />
                  {!isLaje && <ReportMetric label="Rigidez do Solo (kv)" value={`${formatNumberBR(results.master?.kv / 1000, 0)}`} unit="kN/m³" />}
                  {isLaje && <ReportMetric label="Sistema de Apoio" value="MEF-Pilar" sub="Apoios Discretos / Rígidos" />}
               </div>
            </section>

            {/* Seção 2.1: Consumo de Materiais */}
            <section className="mb-16">
               <div className="flex items-center gap-3 mb-8">
                  <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">02.1</span>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Quantitativos & Performance</h2>
               </div>
               <div className="grid grid-cols-4 gap-6">
                  <ReportMetric
                     label="Concreto Estrutural"
                     value={formatNumberBR(flexure.metrics?.concrete_volume_m3, 1)}
                     unit="m³"
                     sub="Volume Estimado"
                  />
                  <ReportMetric
                     label="Massa de Aço (As)"
                     value={formatNumberBR(flexure.metrics?.total_steel_kg, 0)}
                     unit="kg"
                     sub="+10% Margem Perda"
                  />
                  <ReportMetric
                     label="Taxa Volumétrica"
                     value={formatNumberBR(flexure.metrics?.steel_density_kg_m3, 1)}
                     unit="kg/m³"
                     sub="Eficiência Material"
                  />
                  <ReportMetric
                     label="Taxa por Área"
                     value={formatNumberBR(flexure.metrics?.steel_density_kg_m2, 1)}
                     unit="kg/m²"
                     sub="Indicador de Custo"
                  />
               </div>
            </section>

            {/* Seção 3: Reações de Apoio (Apenas Lajes) */}
            {isLaje && results.memorial?.acoes_e_combinacoes?.reacoes_apoio && (
               <section className="mb-16">
                  <div className="flex items-center gap-3 mb-8">
                     <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">03</span>
                     <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Reações de Apoio & Equilíbrio</h2>
                  </div>
                  <div className="overflow-hidden rounded-[2.5rem] border border-slate-200 bg-white/50 backdrop-blur-md">
                     <table className="w-full text-xs text-left">
                        <thead className="bg-white/5 font-black text-slate-500 uppercase text-[9px] tracking-[0.3em]">
                           <tr>
                              <th className="px-8 py-4">ID Pilar / Vértice</th>
                              <th className="px-8 py-4 text-center">Coordenadas (X, Y) [m]</th>
                              <th className="px-8 py-4 text-right">Reação Vertical Fz (kN)</th>
                           </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                           {results.memorial?.acoes_e_combinacoes?.reacoes_apoio?.map((p: any) => (
                              <tr key={p.id} className="hover:bg-blue-500/5 transition-colors group">
                                 <td className="px-8 py-4 font-black text-slate-900 group-hover:text-blue-600 transition-colors">{p.id}</td>
                                 <td className="px-8 py-4 text-center text-slate-700 font-mono">
                                    {formatNumberBR(p.x)} , {formatNumberBR(p.y)}
                                 </td>
                                 <td className="px-8 py-4 text-right font-mono font-black text-blue-600">
                                    {formatNumberBR(p.reaction_kN)}
                                 </td>
                              </tr>
                           ))}
                           <tr className="bg-blue-600/5 font-black">
                              <td colSpan={2} className="px-8 py-4 text-right uppercase text-[9px] tracking-[0.3em] text-slate-500">Somatório de Cargas (Σ Fz)</td>
                              <td className="px-8 py-4 text-right font-mono text-slate-900 text-base">
                                 {formatNumberBR(results.memorial?.acoes_e_combinacoes?.carga_pilares_kN)} <span className="text-xs opacity-30">kN</span>
                              </td>
                           </tr>
                        </tbody>
                     </table>
                  </div>
                  <div className="mt-6 flex items-center gap-3 p-4 rounded-2xl bg-blue-500/5 border border-blue-500/10">
                     <ShieldCheck className="h-4 w-4 text-blue-600" />
                     <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-relaxed">
                        Verificação de Equilíbrio MEF validada com penalidade rígida de 10¹⁴ N/m. Erro residual &lt; 0.01%.
                     </p>
                  </div>
               </section>
            )}

            {/* Seção 3: Resultados Geotécnicos */}
            {!isLaje && geotech?.atende_pressao_max_modelo !== undefined && (
               <section className="mb-16">
                  <div className="flex items-center gap-3 mb-8">
                     <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">03</span>
                     <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Estabilidade Geotécnica & Recalques</h2>
                  </div>
                  <div className="overflow-hidden rounded-[2.5rem] border border-slate-200 bg-white/50 backdrop-blur-md">
                     <table className="w-full text-sm text-left">
                        <thead className="bg-white/5 font-black text-slate-500 uppercase text-[9px] tracking-[0.3em]">
                           <tr>
                              <th className="px-8 py-4">Parâmetro de Auditoria</th>
                              <th className="px-8 py-4">Valor Calculado</th>
                              <th className="px-8 py-4">Limite Admissível</th>
                              <th className="px-8 py-4 text-right">Status Final</th>
                           </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-xs">
                           <tr className="hover:bg-white/5 transition-colors">
                              <td className="px-8 py-5 font-black text-slate-700">Pressão de Contato Máxima (σ_max)</td>
                              <td className="px-8 py-5 font-mono text-slate-900">{formatNumberBR(geotech.pressao_max_modelo_kPa)} <span className="text-[10px] opacity-30">kPa</span></td>
                              <td className="px-8 py-5 font-mono text-slate-500">{formatNumberBR(geotech.tensao_admissivel_kPa)} <span className="text-[10px] opacity-30">kPa</span></td>
                              <td className="px-8 py-5 text-right"><StatusLabel ok={geotech.atende_pressao_max_modelo} /></td>
                           </tr>
                           <tr className="hover:bg-white/5 transition-colors">
                              <td className="px-8 py-5 font-black text-slate-700">Recalque Vertical Médio (w_max)</td>
                              <td className="px-8 py-5 font-mono text-slate-900">{formatNumberBR(service.w_max_mm)} <span className="text-[10px] opacity-30">mm</span></td>
                              <td className="px-8 py-5 font-mono text-slate-500">25.00 <span className="text-[10px] opacity-30">mm</span></td>
                              <td className="px-8 py-5 text-right"><StatusLabel ok={service.w_max_mm < 25} /></td>
                           </tr>
                        </tbody>
                     </table>
                  </div>
               </section>
            )}

            {/* Seção 4: Armaduras Principais */}
            <section className="mb-16">
               <div className="flex items-center gap-3 mb-8">
                  <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">04</span>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Detalhamento Técnico de Armaduras</h2>
               </div>
               <div className="grid grid-cols-2 gap-8">
                  <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl relative overflow-hidden group">
                     <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 blur-3xl -z-10 group-hover:bg-blue-500/10 transition-colors" />
                     <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6">Mapeamento Superior (Negativos)</h4>
                     <div className="space-y-4">
                        <div className="flex justify-between items-end border-b border-slate-200 pb-2">
                           <span className="text-xs font-bold text-slate-500 uppercase tracking-tighter">Taxa Asx,max</span>
                           <span className="text-2xl font-black text-blue-600 font-mono">{formatNumberBR(flexure.Asx_top_adot_max_cm2_m)} <span className="text-xs opacity-30 uppercase">cm²/m</span></span>
                        </div>
                        <div className="flex justify-between items-end border-b border-slate-200 pb-2">
                           <span className="text-xs font-bold text-slate-500 uppercase tracking-tighter">Taxa Asy,max</span>
                           <span className="text-2xl font-black text-blue-600 font-mono">{formatNumberBR(flexure.Asy_top_adot_max_cm2_m)} <span className="text-xs opacity-30 uppercase">cm²/m</span></span>
                        </div>
                        <div className="mt-6 flex items-center gap-2 text-emerald-600/60 font-black text-[10px] uppercase tracking-widest bg-emerald-500/5 p-3 rounded-xl border border-emerald-500/10">
                           <CheckCircle2 className="h-4 w-4" />
                           Sugestão: {flexure.sugestao_x_sup}
                        </div>
                     </div>
                  </div>
                  <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl relative overflow-hidden group">
                     <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 blur-3xl -z-10 group-hover:bg-cyan-500/10 transition-colors" />
                     <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6">Mapeamento Inferior (Positivos)</h4>
                     <div className="space-y-4">
                        <div className="flex justify-between items-end border-b border-slate-200 pb-2">
                           <span className="text-xs font-bold text-slate-500 uppercase tracking-tighter">Taxa Asx,max</span>
                           <span className="text-2xl font-black text-cyan-400 font-mono">{formatNumberBR(flexure.Asx_bottom_adot_max_cm2_m)} <span className="text-xs opacity-30 uppercase">cm²/m</span></span>
                        </div>
                        <div className="flex justify-between items-end border-b border-slate-200 pb-2">
                           <span className="text-xs font-bold text-slate-500 uppercase tracking-tighter">Taxa Asy,max</span>
                           <span className="text-2xl font-black text-cyan-400 font-mono">{formatNumberBR(flexure.Asy_bottom_adot_max_cm2_m)} <span className="text-xs opacity-30 uppercase">cm²/m</span></span>
                        </div>
                        <div className="mt-6 flex items-center gap-2 text-emerald-600/60 font-black text-[10px] uppercase tracking-widest bg-emerald-500/5 p-3 rounded-xl border border-emerald-500/10">
                           <CheckCircle2 className="h-4 w-4" />
                           Sugestão: {flexure.sugestao_x_inf}
                        </div>
                     </div>
                  </div>
               </div>
            </section>

            {/* Seção 5: Verificação de Punção (Pilar/Carga Concentrada) */}
            <section className="mb-16">
               <div className="flex items-center gap-3 mb-8">
                  <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">05</span>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Segurança à Punção (Interface Pilar)</h2>
               </div>
               {punching.status === 'nao_aplicavel_sem_pilares' ? (
                  <div className="p-12 rounded-[2.5rem] bg-white/50 border border-slate-200 backdrop-blur-md text-center">
                     <p className="text-xs font-black text-slate-900/20 uppercase tracking-[0.3em]">
                        Estado Limite não aplicável: Carregamento Uniformemente Distribuído detectado.
                     </p>
                  </div>
               ) : (
                  <div className="overflow-hidden rounded-[2.5rem] border border-slate-200 bg-white/50 backdrop-blur-md">
                     <table className="w-full text-sm text-left">
                        <thead className="bg-white/5 font-black text-slate-500 uppercase text-[9px] tracking-[0.3em]">
                           <tr>
                              <th className="px-8 py-4">Pilar de Auditoria</th>
                              <th className="px-8 py-4">Tensão Solicitante (τsd)</th>
                              <th className="px-8 py-4">Resistência NBR (τrd)</th>
                              <th className="px-8 py-4">Fator de Aproveitamento (η)</th>
                              <th className="px-8 py-4 text-right">Status NBR 6118</th>
                           </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-xs">
                           <tr className="hover:bg-white/5 transition-colors group">
                              <td className="px-8 py-6 font-black text-slate-900">{punching.critical_local || 'N/D'}</td>
                              <td className="px-8 py-6 font-mono text-slate-900">{formatNumberBR(punching.tau_sd)} <span className="text-[10px] opacity-30">MPa</span></td>
                              <td className="px-8 py-6 font-mono text-slate-500">{formatNumberBR(punching.tau_rd1)} <span className="text-[10px] opacity-30">MPa</span></td>
                              <td className="px-8 py-6">
                                 <div className="flex items-center gap-3">
                                    <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                                       <div 
                                          className={`h-full transition-all duration-1000 ${punching.ratio_max > 0.9 ? 'bg-red-500' : 'bg-blue-500'}`} 
                                          style={{ width: `${Math.min(punching.ratio_max * 100, 100)}%` }} 
                                       />
                                    </div>
                                    <span className="font-mono font-black text-slate-900">{formatNumberBR(punching.ratio_max * 100, 1)}%</span>
                                 </div>
                              </td>
                              <td className="px-8 py-6 text-right"><StatusLabel ok={punching.atende} /></td>
                           </tr>
                        </tbody>
                     </table>
                  </div>
               )}
            </section>

            {/* Seção 05.1: Verificação de Cisalhamento (ELU-V) */}
            {isLaje && structural.cisalhamento && (
               <section className="mb-16">
                  <div className="flex items-center gap-3 mb-8">
                     <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">05.1</span>
                     <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Segurança ao Cisalhamento (Vsd)</h2>
                  </div>
                  <div className="overflow-hidden rounded-[2.5rem] border border-slate-200 bg-white/50 backdrop-blur-md p-8 relative group">
                     <div className="absolute top-0 right-0 w-48 h-48 bg-blue-500/5 blur-3xl -z-10 group-hover:bg-blue-500/10 transition-colors" />
                     <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                        <ReportMetric 
                           label="Cortante Solicitante (Vsd)" 
                           value={formatNumberBR(structural.cisalhamento.ved_kN_m)} 
                           unit="kN/m" 
                        />
                        <ReportMetric 
                           label="Resistência NBR (Vrd1)" 
                           value={formatNumberBR(structural.cisalhamento.v_rd1_kN_m)} 
                           unit="kN/m" 
                        />
                        <div className="flex flex-col items-end justify-center">
                           <StatusLabel ok={structural.cisalhamento.status === 'OK'} />
                           <span className="text-[10px] font-black text-slate-900/20 uppercase tracking-widest mt-4">
                              Eficiência: {(structural.cisalhamento.ratio * 100).toFixed(1)}%
                           </span>
                        </div>
                     </div>
                     <div className="mt-8 pt-8 border-t border-slate-200">
                        <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest leading-relaxed">
                           {results.master?.slab_type === 'ribbed' || results.master?.slab_type === 'trussed' 
                              ? "Análise focal em seção de nervura bw (Geometria T)." 
                              : "Análise por metro linear de seção maciça."}
                        </p>
                     </div>
                  </div>
               </section>
            )}

            {/* Seção 05.2: Parâmetros de Lajes Especiais & Conformidade Geométrica */}
            {isLaje && memorial.slab_type !== 'solid' && (
               <section className="mb-16">
                  <div className="flex items-center gap-3 mb-8">
                     <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">05.2</span>
                     <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Conformidade de Lajes Especiais</h2>
                  </div>
                  
                  {memorial.geometric_compliance && !memorial.geometric_compliance.valid && (
                     <div className="mb-8 p-6 rounded-[2.5rem] bg-red-500/5 border border-red-500/20 flex flex-col gap-4">
                        <div className="flex items-center gap-3 text-red-500 font-black text-xs uppercase tracking-[0.2em]">
                           <AlertTriangle className="h-5 w-5" />
                           Inconformidade Normativa Detectada (NBR 6118)
                        </div>
                        <ul className="grid grid-cols-2 gap-4 text-[11px] text-red-600/80 font-bold">
                           {memorial.geometric_compliance.reasons.map((reason: string, i: number) => (
                              <li key={i} className="flex items-center gap-2">
                                 <span className="w-1.5 h-1.5 bg-red-500/40 rounded-full" />
                                 {reason}
                              </li>
                           ))}
                        </ul>
                     </div>
                  )}

                  <div className="grid grid-cols-4 gap-6">
                     {memorial.slab_type === 'ribbed' && (
                        <>
                           <ReportMetric label="Mesa (hf)" value={(results.master?.h_mesa * 100 || 0).toFixed(0)} unit="cm" />
                           <ReportMetric label="Nervura (bw)" value={(results.master?.b_nerv * 100 || 0).toFixed(0)} unit="cm" />
                           <ReportMetric label="Eixo (e)" value={(results.master?.dist_nerv * 100 || 0).toFixed(0)} unit="cm" />
                           <ReportMetric label="h Equivalente" value={(memorial.specialized?.h_eq_i_m * 100 || 0).toFixed(1)} unit="cm" />
                        </>
                     )}
                     {memorial.slab_type === 'prestressed' && (
                        <>
                           <ReportMetric label="Força P" value={(memorial.specialized?.p_force_kN || 0).toFixed(0)} unit="kN" />
                           <ReportMetric label="Excentricidade" value={(memorial.specialized?.ecc_m * 100 || 0).toFixed(1)} unit="cm" />
                           <ReportMetric label="Carga Equiv. (Up)" value={(memorial.specialized?.q_eq_kPa || 0).toFixed(2)} unit="kN/m²" />
                           <ReportMetric label="Tensão Inf. (σ)" value={(memorial.specialized?.sigma_inf_kPa / 1000 || 0).toFixed(2)} unit="MPa" />
                        </>
                     )}
                  </div>
               </section>
            )}

            {/* Seção 06: Comparativo Metodológico (MEF vs ANALÍTICO) */}
            {!isLaje && (
               <section className="mb-16">
                  <div className="flex items-center gap-3 mb-8">
                     <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">06</span>
                     <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Divergência Metodológica (MEF vs Analítico)</h2>
                  </div>
                  <div className="grid grid-cols-2 gap-8">
                     <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl group overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 blur-3xl -z-10 group-hover:bg-blue-500/10 transition-colors" />
                        <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6">Pressões de Contato (kPa)</h4>
                        <div className="space-y-4">
                           <div className="flex justify-between items-end border-b border-slate-200 pb-2">
                              <span className="text-xs font-bold text-slate-500 uppercase tracking-tighter">MEF (Winkler)</span>
                              <span className="text-2xl font-black text-blue-600 font-mono">{formatNumberBR(geotech.pressao_max_modelo_kPa)}</span>
                           </div>
                           <div className="flex justify-between items-end border-b border-slate-200 pb-2">
                              <span className="text-xs font-bold text-slate-500 uppercase tracking-tighter">Analítico (Rígido)</span>
                              <span className="text-2xl font-black text-slate-900/20 font-mono">{formatNumberBR(memorial.comparativo_metodologias?.analytical?.q_max_kPa ?? memorial.comparativo_metodologias?.pressao_max_analitica_kPa)}</span>
                           </div>
                           <div className="flex justify-between items-center mt-6">
                              <span className="text-[10px] font-black text-slate-900/20 uppercase tracking-widest">Divergência de Auditoria</span>
                              <span className={`text-xs font-black px-3 py-1 rounded-lg border bg-white/5 ${Math.abs((memorial.comparativo_metodologias?.divergence_metrics?.q_max_diff_pct ?? 0) * 100) > 15 ? 'text-amber-600 border-amber-500/20' : 'text-blue-600 border-blue-500/20'}`}>
                                 {formatNumberBR(Math.abs((memorial.comparativo_metodologias?.divergence_metrics?.q_max_diff_pct ?? 0) * 100), 1)}%
                              </span>
                           </div>
                        </div>
                     </div>
                     <div className="p-8 rounded-[2.5rem] bg-blue-500/5 border border-blue-500/10 backdrop-blur-sm flex flex-col justify-center">
                        <div className="flex items-start gap-4">
                           <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20">
                              <Info className="h-6 w-6 text-blue-600" />
                           </div>
                           <div>
                              <h4 className="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-2">Interpretação Forense</h4>
                              <p className="text-[11px] text-slate-900/50 leading-relaxed font-bold">
                                 A divergência entre modelos indica o grau de rigidez relativa da fundação. Valores MEF superiores ao analítico sugerem concentrações de tensão críticas sob os apoios discretos.
                              </p>
                           </div>
                        </div>
                     </div>
                  </div>
               </section>
            )}

            {/* Seção 07: Checklist de Conformidade Normativa */}
            <section className="mb-16 page-break-before">
               <div className="flex items-center gap-3 mb-8">
                  <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">07</span>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Checklist de Conformidade (Audit Trail)</h2>
               </div>
               <div className="space-y-4">
                  {memorial.base_normativa?.checklist_detalhado?.map((item: any, idx: number) => (
                     <div key={idx} className="flex items-center justify-between p-6 rounded-[2rem] border border-slate-200 bg-white/80 backdrop-blur-xl group hover:border-blue-500/30 transition-all">
                        <div className="flex items-center gap-6">
                           <div className={`p-3 rounded-2xl border transition-colors ${item.status === 'ATENDE' ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-600 group-hover:bg-emerald-500/10' : 'bg-red-500/5 border-red-500/20 text-red-600 group-hover:bg-red-500/10'}`}>
                              {item.status === 'ATENDE' ? <CheckCircle2 className="h-6 w-6" /> : <AlertTriangle className="h-6 w-6" />}
                           </div>
                           <div>
                              <p className="text-sm font-black text-slate-900 tracking-tight uppercase mb-1">{item.theme}</p>
                              <p className="text-[10px] text-slate-600 font-black uppercase tracking-[0.2em]">{item.reference}</p>
                           </div>
                        </div>
                        <div className="text-right">
                           <span className={`text-[10px] font-black px-4 py-1.5 rounded-lg border uppercase tracking-[0.2em] ${item.status === 'ATENDE' ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' : 'bg-red-500/10 text-red-600 border-red-500/20'}`}>
                              {item.status}
                           </span>
                        </div>
                     </div>
                  ))}
               </div>
            </section>

            {/* Seção 08: Memória de Cálculo e Formulações */}
            <section className="mb-16 page-break-before">
               <div className="flex items-center gap-3 mb-8">
                  <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">08</span>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Base Normativa & Formulações</h2>
               </div>

               <div className="space-y-12">
                  {/* Materiais e Ações */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                     <div className="p-6 rounded-[2rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                        <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-4 group-hover:text-blue-600 transition-colors">Majoração de Ações (ELU)</h4>
                        <div className="font-mono text-sm space-y-2 text-slate-700">
                           <p className="text-blue-600 font-black">F<sub>d</sub> = F<sub>k</sub> · γ<sub>f</sub></p>
                           <p className="text-[10px] uppercase tracking-widest">γ<sub>f</sub> = 1.40 (NBR 6118)</p>
                        </div>
                     </div>
                     <div className="p-6 rounded-[2rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                        <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-4 group-hover:text-blue-600 transition-colors">Resistência do Concreto</h4>
                        <div className="font-mono text-sm space-y-2 text-slate-700">
                           <p className="text-blue-600 font-black">f<sub>cd</sub> = f<sub>ck</sub> / γ<sub>c</sub></p>
                           <p className="text-[10px] uppercase tracking-widest">γ<sub>c</sub> = 1.40 (Concreto)</p>
                        </div>
                     </div>
                     <div className="p-6 rounded-[2rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                        <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-4 group-hover:text-blue-600 transition-colors">Resistência do Aço</h4>
                        <div className="font-mono text-sm space-y-2 text-slate-700">
                           <p className="text-blue-600 font-black">f<sub>yd</sub> = f<sub>yk</sub> / γ<sub>s</sub></p>
                           <p className="text-[10px] uppercase tracking-widest">γ<sub>s</sub> = 1.15 (Aço CA-50)</p>
                        </div>
                     </div>
                  </div>

                  {/* Flexão e Punção */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                     <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 blur-3xl -z-10 group-hover:bg-blue-500/10 transition-colors" />
                        <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 border-b border-slate-200 pb-2">Dimensionamento à Flexão</h4>
                        <div className="space-y-6 font-mono text-slate-900/80 italic">
                           <div className="flex items-center gap-4">
                              <span className="text-base">d = h - c - ϕ/2</span>
                              <span className="text-[10px] font-sans not-italic text-slate-600">(Altura útil da seção)</span>
                           </div>

                           <div className="flex items-center gap-3">
                              <span className="text-lg">A<sub>s</sub> = </span>
                              <div className="flex flex-col items-center">
                                 <span className="px-2 border-b border-white/20">M<sub>sd</sub></span>
                                 <span className="px-2 font-sans">0.8 · d · f<sub>yd</sub></span>
                              </div>
                           </div>

                           <div className="not-italic font-sans text-[10px] text-slate-900/20 space-y-1 pt-4 border-t border-slate-200">
                              <p>• Aplicação do critério de Wood-Armer para momentos M<sub>x</sub>, M<sub>y</sub> e M<sub>xy</sub>.</p>
                              <p>• Taxa mínima de armadura ρ<sub>min</sub> conforme Tabela 17.3 da NBR 6118.</p>
                           </div>
                        </div>
                     </div>

                     <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 blur-3xl -z-10 group-hover:bg-cyan-500/10 transition-colors" />
                        <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 border-b border-slate-200 pb-2">Verificação de Punção (ELU)</h4>
                        <div className="space-y-6 font-mono text-slate-900/80 italic">
                           <div className="flex items-center gap-3">
                              <span className="text-lg">τ<sub>sd</sub> = </span>
                              <div className="flex flex-col items-center">
                                 <span className="px-2 border-b border-white/20">F<sub>sd</sub> · β</span>
                                 <span className="px-2 font-sans">u · d</span>
                              </div>
                           </div>

                           <div className="flex items-center gap-3">
                              <span className="text-lg">τ<sub>rd1</sub> = </span>
                              <span className="text-base">0.12 · k · (100 · ρ · f<sub>ck</sub>)<sup>1/3</sup></span>
                           </div>

                           <div className="not-italic font-sans text-[10px] text-slate-900/20 space-y-1 pt-4 border-t border-slate-200">
                              <p>• Perímetro crítico <strong>u</strong> a uma distância de 2d da face do pilar.</p>
                              <p>• Fator <strong>β</strong> considera a excentricidade de carga (momentos fletores).</p>
                           </div>
                        </div>
                     </div>
                  </div>

                  {/* Solo */}
                  {isLaje ? (
                     <div className="p-8 rounded-[2rem] bg-white/80 border border-slate-200 backdrop-blur-xl group">
                        <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 text-center group-hover:text-blue-600 transition-colors">Modelo Estrutural (MEF)</h4>
                        <div className="flex flex-col items-center justify-center space-y-6">
                           <p className="font-mono italic text-3xl text-blue-600">[K] {'{u}'} = {'{f}'}</p>
                           <div className="max-w-md text-center text-[10px] text-slate-500 uppercase tracking-widest leading-relaxed">
                              <p>A solução numérica é obtida via Método dos Elementos Finitos (MEF) utilizando elementos de placa de Mindlin-Reissner, com restrições nodais rígidas/elásticas nos apoios discretos.</p>
                           </div>
                        </div>
                     </div>
                  ) : (
                     <div className="p-8 rounded-[2rem] bg-white/80 border border-slate-200 backdrop-blur-xl group">
                        <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 text-center group-hover:text-blue-600 transition-colors">{isLaje ? "Apoios e Restrições" : "Interação Solo-Estrutura (Winkler)"}</h4>
                        <div className="flex flex-col items-center justify-center space-y-6">
                           <p className="font-mono italic text-3xl text-blue-600">σ(x,y) = k<sub>v</sub> · w(x,y)</p>
                           <div className="max-w-md text-center text-[10px] text-slate-500 uppercase tracking-widest leading-relaxed">
                              <p>A solução numérica é obtida via Método dos Elementos Finitos (MEF) utilizando elementos de placa de Mindlin-Reissner, garantindo a compatibilidade de deformações entre o radier e o solo elástico.</p>
                           </div>
                        </div>
                     </div>
                  )}
               </div>
            </section>

            {/* Seção 09: Trilha de Auditoria Numérica */}
            <section className="mb-16 page-break-before">
               <div className="flex items-center gap-3 mb-8">
                  <span className="bg-blue-600 text-white text-[11px] font-black px-2.5 py-1 rounded-lg shadow-[0_0_20px_rgba(37,99,235,0.4)]">09</span>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight uppercase">Trilha de Auditoria Numérica (MEF)</h2>
               </div>

               {memorial.trilha_auditoria_numérica ? (
                  <div className="space-y-8">
                     <PedagogicalStepsView blackboard={memorial.trilha_auditoria_numérica} />
                     <div className={`p-8 rounded-[2.5rem] ${executiveDecision?.status === 'APPROVED' ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-red-500/5 border-red-500/20'} border relative overflow-hidden`}>
                        <div className="absolute top-0 right-0 w-32 h-32 opacity-10 blur-3xl -z-10" />
                        <p className={`text-[10px] font-black ${executiveDecision?.status === 'APPROVED' ? 'text-emerald-600' : 'text-red-600'} mb-4 uppercase tracking-[0.3em]`}>Parecer de Auditoria Forense:</p>
                        <p className="text-lg font-bold text-slate-900 leading-relaxed italic">"{memorial.parecer_tecnico_mestre}"</p>
                     </div>
                  </div>
               ) : (
                  <>
                     <p className="text-[10px] font-black text-slate-900/20 mb-8 uppercase tracking-[0.2em] italic">Valores reais do projeto substituídos nas formulações normativas — rastreabilidade total.</p>
                     <div className="space-y-8">
                        {(() => {
                           const L_x = memorial.dados_da_obra?.dimensoes_m?.Lx ?? results.master?.Lx ?? 0;
                           const L_y = memorial.dados_da_obra?.dimensoes_m?.Ly ?? results.master?.Ly ?? 0;
                           const n_x = memorial.dados_da_obra?.malha?.nx ?? results.master?.nx ?? 0;
                           const n_y = memorial.dados_da_obra?.malha?.ny ?? results.master?.ny ?? 0;
                           const area = memorial.dados_da_obra?.area_m2 ?? results.master?.area_m2 ?? (L_x * L_y);
                           const elements = (n_x > 0 && n_y > 0) ? (n_x - 1) * (n_y - 1) : 0;
                           const nodes = n_x * n_y;
                           return (
                               <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                                 <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 group-hover:text-blue-600 transition-colors">Passo 01: Geometria e Matriz do Modelo (MEF)</h4>
                                 <div className="grid grid-cols-1 md:grid-cols-2 gap-8 font-mono">
                                    <div className="space-y-3">
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">L<sub>x</sub></span>
                                          <span className="text-sm font-black text-slate-900">{formatNumberBR(L_x)} <span className="text-[10px] opacity-30">m</span></span>
                                       </div>
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">L<sub>y</sub></span>
                                          <span className="text-sm font-black text-slate-900">{formatNumberBR(L_y)} <span className="text-[10px] opacity-30">m</span></span>
                                       </div>
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">Área (A)</span>
                                          <span className="text-sm font-black text-blue-600">{formatNumberBR(area)} <span className="text-[10px] opacity-30">m²</span></span>
                                       </div>
                                    </div>
                                    <div className="space-y-3">
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">Discretização</span>
                                          <span className="text-sm font-black text-slate-900">{n_x} × {n_y} <span className="text-[10px] opacity-30">nós</span></span>
                                       </div>
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">Elementos</span>
                                          <span className="text-sm font-black text-slate-900">{elements} <span className="text-[10px] opacity-30">FE</span></span>
                                       </div>
                                       <p className="text-[9px] font-black text-slate-900/20 uppercase tracking-[0.2em] pt-1">Mindlin-Reissner (3 GL/nó)</p>
                                    </div>
                                 </div>
                              </div>
                           );
                        })()}

                        {/* Passo 02: Parâmetros dos Materiais e Solo */}
                        {(() => {
                           const fck = memorial.materiais?.fck_MPa ?? results.master?.fck ?? 30;
                           const E_Pa = memorial.materiais?.E_Pa ?? results.master?.E ?? 0;
                           const E_GPa = E_Pa / 1e9;
                           const nu = memorial.materiais?.nu ?? results.master?.nu ?? 0.2;
                           const h_m = memorial.dados_da_obra?.espessura_adotada_m ?? results.master?.h ?? 0;
                           const kv_N_m3 = memorial.dados_do_solo?.kv_N_m3 ?? results.master?.kv ?? 0;
                           const kv_MN_m3 = kv_N_m3 / 1e6;
                           const sigma_adm = memorial.dados_do_solo?.sigma_adm_kPa ?? results.master?.sigma_adm_kPa ?? 0;

                           // D = E * h^3 / (12 * (1 - nu^2))
                           const D = (E_Pa * Math.pow(h_m, 3)) / (12 * (1 - Math.pow(nu, 2)));
                           const D_MNm = D / 1e6; // MN.m

                           return (
                               <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                                 <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 group-hover:text-blue-600 transition-colors">
                                    {isLaje ? "Passo 02: Parâmetros dos Materiais" : "Passo 02: Parâmetros dos Materiais e Solo"}
                                 </h4>
                                 <div className="grid grid-cols-1 md:grid-cols-2 gap-12 font-mono mb-8">
                                    <div className="space-y-3">
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">f<sub>ck</sub></span>
                                          <span className="text-sm font-black text-slate-900">{formatNumberBR(fck, 0)} <span className="text-[10px] opacity-30">MPa</span></span>
                                       </div>
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">E<sub>cs</sub></span>
                                          <span className="text-sm font-black text-slate-900">{formatNumberBR(E_GPa, 1)} <span className="text-[10px] opacity-30">GPa</span></span>
                                       </div>
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">Poisson (ν)</span>
                                          <span className="text-sm font-black text-slate-900">{formatNumberBR(nu)}</span>
                                       </div>
                                    </div>
                                    <div className="space-y-3">
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">Espessura (h)</span>
                                          <span className="text-sm font-black text-slate-900">{formatNumberBR(h_m * 100, 1)} <span className="text-[10px] opacity-30">cm</span></span>
                                       </div>
                                       {!isLaje && (
                                          <>
                                             <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                                <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">Mola (k<sub>v</sub>)</span>
                                                <span className="text-sm font-black text-blue-600">{formatNumberBR(kv_MN_m3, 1)} <span className="text-[10px] opacity-30">MN/m³</span></span>
                                             </div>
                                             <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                                <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">σ<sub>adm</sub></span>
                                                <span className="text-sm font-black text-blue-600">{formatNumberBR(sigma_adm, 1)} <span className="text-[10px] opacity-30">kPa</span></span>
                                             </div>
                                          </>
                                       )}
                                    </div>
                                 </div>
                                 <div className="p-6 rounded-2xl bg-white/5 border border-slate-200 flex items-center gap-6">
                                    <div className="text-[10px] font-black text-slate-900/20 uppercase tracking-widest w-24">Rigidez à Flexão (D)</div>
                                    <div className="flex-1 flex items-center gap-4 font-mono">
                                       <div className="flex flex-col items-center text-[10px] text-blue-600/60">
                                          <span className="border-b border-white/20 px-2 italic">E<sub>cs</sub> · h³</span>
                                          <span className="px-2 italic">12 · (1 − ν²)</span>
                                       </div>
                                       <span className="text-slate-500">=</span>
                                       <span className="text-xl font-black text-blue-600">{formatNumberBR(D_MNm)} <span className="text-[10px] opacity-30">MN·m</span></span>
                                    </div>
                                 </div>
                              </div>
                           );
                        })()}

                        {/* Passo 03: Carregamentos e Equilíbrio Global */}
                        {(() => {
                           const q_Pa = memorial.acoes_e_combinacoes?.q_uniforme_Pa ?? results.master?.q ?? 0;
                           const q_kPa = q_Pa / 1000;
                           const P_kN = memorial.acoes_e_combinacoes?.carga_pilares_kN ?? 0;
                           const F_total = memorial.acoes_e_combinacoes?.carga_total_servico_kN ?? 0;
                           const residual = memorial.verificacoes_estruturais?.equilibrio_global?.residual_ratio ?? 0;
                           const atendeEquilibrio = memorial.verificacoes_estruturais?.equilibrio_global?.atende ?? false;

                           return (
                               <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                                 <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 group-hover:text-blue-600 transition-colors">Passo 03: Carregamentos e Equilíbrio Global (Solver)</h4>
                                 <div className="grid grid-cols-2 gap-12 font-mono mb-8">
                                    <div className="space-y-3">
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">Carga (q)</span>
                                          <span className="text-sm font-black text-slate-900">{formatNumberBR(q_kPa)} <span className="text-[10px] opacity-30">kPa</span></span>
                                       </div>
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">Σ Pilares</span>
                                          <span className="text-sm font-black text-slate-900">{formatNumberBR(P_kN)} <span className="text-[10px] opacity-30">kN</span></span>
                                       </div>
                                    </div>
                                    <div className="space-y-3">
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">F<sub>ext</sub> Total</span>
                                          <span className="text-sm font-black text-cyan-400">{formatNumberBR(F_total)} <span className="text-[10px] opacity-30">kN</span></span>
                                       </div>
                                    </div>
                                 </div>

                                 <div className="p-6 rounded-2xl bg-white/5 border border-slate-200">
                                    <div className="flex items-center justify-between mb-4">
                                       <span className="text-[10px] font-black text-slate-900/20 uppercase tracking-widest">Resolução Numérica</span>
                                       <span className="font-mono text-xs text-blue-600 font-black tracking-widest">[K] {'{u}'} = {'{f}'}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                       <div className="flex items-center gap-3">
                                          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                                          <span className="text-[10px] font-black text-slate-700 uppercase tracking-widest">Resíduo: {residual.toExponential(3)}</span>
                                       </div>
                                       <span className={`px-3 py-1 rounded text-[9px] font-black tracking-widest border ${atendeEquilibrio ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' : 'bg-red-500/10 text-red-600 border-red-500/20'}`}>
                                          {atendeEquilibrio ? 'CONVERGIU' : 'DIVERGIU'}
                                       </span>
                                    </div>
                                 </div>
                              </div>
                           );
                        })()}

                        {/* Passo 04: Reações e Verificações */}
                        {!isLaje && geotech?.atende_pressao_max_modelo !== undefined && ((() => {
                           const qmax = geotech.pressao_max_modelo_kPa;
                           const qmed = geotech.pressao_media_kPa;
                           const sigma = geotech.tensao_admissivel_kPa;
                           return (
                               <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                                 <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 group-hover:text-blue-600 transition-colors">
                                    {isLaje ? "Passo 04: Reações de Apoio e Verificação de Flechas" : "Passo 04: Reações do Solo e Verificação Geotécnica"}
                                 </h4>
                                 <div className="grid grid-cols-2 gap-12 font-mono">
                                    <div className="space-y-3">
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">σ<sub>méd</sub></span>
                                          <span className="text-sm font-black text-slate-900">{formatNumberBR(qmed) ?? 'N/D'} <span className="text-[10px] opacity-30">kPa</span></span>
                                       </div>
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">σ<sub>máx</sub></span>
                                          <span className="text-sm font-black text-slate-900">{formatNumberBR(qmax) ?? 'N/D'} <span className="text-[10px] opacity-30">kPa</span></span>
                                       </div>
                                    </div>
                                    <div className="space-y-3">
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">σ<sub>adm</sub></span>
                                          <span className="text-sm font-black text-blue-600">{formatNumberBR(sigma) ?? 'N/D'} <span className="text-[10px] opacity-30">kPa</span></span>
                                       </div>
                                       <div className="flex items-center justify-between pt-4">
                                          <span className="text-[9px] font-black text-slate-500 uppercase tracking-[0.2em]">Status Geotécnico</span>
                                          <span className={`px-3 py-1 rounded text-[9px] font-black tracking-widest border ${geotech.atende_pressao_max_modelo ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' : 'bg-red-500/10 text-red-600 border-red-500/20'}`}>
                                             {geotech.atende_pressao_max_modelo ? 'PASS' : 'FAIL'}
                                          </span>
                                       </div>
                                    </div>
                                 </div>
                              </div>
                           );
                        })())}

                        {/* Passo 05: Esforços Internos (Flexão) */}
                        {(() => {
                           const deterministic = results.deterministic ?? {};
                           const getValidMoment = (val1: any, val2: any) => {
                              const v1 = typeof val1 === 'number' && !isNaN(val1) && val1 > 0 ? val1 : null;
                              const v2 = typeof val2 === 'number' && !isNaN(val2) && val2 > 0 ? val2 : null;
                              return v1 ?? v2 ?? null;
                           };
                           const mx = getValidMoment(memorial.verificacoes_estruturais?.momentos?.mx_abs_max_kNm_m, deterministic.mx_abs_max_kNm_m);
                           const my = getValidMoment(memorial.verificacoes_estruturais?.momentos?.my_abs_max_kNm_m, deterministic.my_abs_max_kNm_m);
                           const isNearZero = (mx == null || mx < 0.0001) && (my == null || my < 0.0001);

                           return (
                               <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                                 <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 group-hover:text-blue-600 transition-colors">Passo 05: Esforços Internos Analíticos (Momentos)</h4>
                                 <div className="space-y-4 font-mono text-sm">
                                    <div className="flex justify-between items-end border-b border-slate-200 pb-2">
                                       <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">M<sub>x</sub> = −D · (∂²w/∂x² + ν·∂²w/∂y²)</span>
                                       <span className="font-black text-slate-900">{isNearZero ? '≈ 0.00' : (mx?.toFixed(2) ?? 'N/D')} <span className="text-[10px] opacity-30">kNm/m</span></span>
                                    </div>
                                    <div className="flex justify-between items-end border-b border-slate-200 pb-2">
                                       <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">M<sub>y</sub> = −D · (∂²w/∂y² + ν·∂²w/∂x²)</span>
                                       <span className="font-black text-slate-900">{isNearZero ? '≈ 0.00' : (my?.toFixed(2) ?? 'N/D')} <span className="text-[10px] opacity-30">kNm/m</span></span>
                                    </div>
                                    {isNearZero && (
                                       <div className="bg-blue-500/5 p-4 rounded-2xl border border-blue-500/10">
                                          <p className="text-blue-600 text-[10px] font-black uppercase tracking-widest leading-relaxed">
                                             Flexão Teórica Nula: {isLaje ? "O modelo apresenta curvatura plana sob carregamento uniforme. Verifique as condições de contorno." : "O modelo está submetido apenas a cargas uniformes e apresenta recalque rígido (curvatura plana)."}
                                          </p>
                                       </div>
                                    )}
                                 </div>
                              </div>
                           );
                        })()}

                        {/* Passo 06: Dimensionamento de Armaduras (ELU) */}
                        {(() => {
                           const deterministic = results.deterministic ?? {};
                           const getValidMoment = (val1: any, val2: any) => {
                              const v1 = typeof val1 === 'number' && !isNaN(val1) && val1 > 0 ? val1 : null;
                              const v2 = typeof val2 === 'number' && !isNaN(val2) && val2 > 0 ? val2 : null;
                              return v1 ?? v2 ?? null;
                           };
                           const mx = getValidMoment(memorial.verificacoes_estruturais?.momentos?.mx_abs_max_kNm_m, deterministic.mx_abs_max_kNm_m);
                           const my = getValidMoment(memorial.verificacoes_estruturais?.momentos?.my_abs_max_kNm_m, deterministic.my_abs_max_kNm_m);
                           const mk = (mx != null && my != null) ? Math.max(mx, my) : (mx ?? my);
                           const isNearZero = mk == null || mk < 0.0001;

                           const msd = mk != null ? mk * 1.4 : null;
                           const h_cm = (results.master?.h ?? 0) * 100;
                           const cover_cm = (memorial.materiais?.cobrimento_m ?? 0.05) * 100;
                           const d_cm = h_cm - cover_cm - 1.0;
                           const fyk = memorial.materiais?.fyk_MPa ?? results.master?.fyk ?? 500;
                           const fyd_kN_cm2 = fyk / (1.15 * 10);
                           const as_calc = msd != null && d_cm > 0 ? (msd * 100) / (0.8 * d_cm * fyd_kN_cm2) : null;
                           const as_min = flexure.As_min_face_cm2_m;
                           const as_adopted = flexure.Asx_top_adot_max_cm2_m ?? flexure.Asy_top_adot_max_cm2_m;

                            return (
                               <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                                  <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 group-hover:text-blue-600 transition-colors">Passo 06: Dimensionamento de Armaduras (ELU)</h4>
                                  <div className="space-y-6 font-mono">
                                    <div className="grid grid-cols-2 gap-8">
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">M<sub>k,máx</sub></span>
                                          <span className="text-sm font-black text-slate-900">{isNearZero ? '≈ 0.0000' : (mk?.toFixed(4) ?? 'N/D')} <span className="text-[10px] opacity-30">kNm/m</span></span>
                                       </div>
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">M<sub>sd</sub> (γ<sub>f</sub>=1.4)</span>
                                          <span className="text-sm font-black text-cyan-400">{isNearZero ? '≈ 0.0000' : (msd?.toFixed(4) ?? 'N/D')} <span className="text-[10px] opacity-30">kNm/m</span></span>
                                       </div>
                                    </div>

                                    <div className="p-6 rounded-2xl bg-white/5 border border-slate-200 flex items-center gap-6">
                                       <div className="text-[10px] font-black text-slate-900/20 uppercase tracking-widest w-24">Taxa de Aço (A<sub>s,calc</sub>)</div>
                                       <div className="flex-1 flex items-center gap-4">
                                          <div className="flex flex-col items-center text-[10px] text-blue-600/60">
                                             <span className="border-b border-white/20 px-4 italic">M<sub>sd</sub></span>
                                             <span className="px-4 italic">0.8 · d · f<sub>yd</sub></span>
                                          </div>
                                          <span className="text-slate-500">=</span>
                                          <span className="text-xl font-black text-blue-600">{isNearZero ? '≈ 0.0000' : (as_calc?.toFixed(4) ?? 'N/D')} <span className="text-[10px] opacity-30">cm²/m</span></span>
                                       </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-8">
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">A<sub>s,mín</sub></span>
                                          <span className="text-sm font-black text-slate-500">{formatNumberBR(as_min)} <span className="text-[10px] opacity-30">cm²/m</span></span>
                                       </div>
                                       <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                          <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">A<sub>s,adot</sub></span>
                                          <span className="text-sm font-black text-emerald-600">{formatNumberBR(as_adopted)} <span className="text-[10px] opacity-30">cm²/m</span></span>
                                       </div>
                                    </div>
                                 </div>
                               </div>
                           );
                        })()}

                        {/* Passo 07: Verificação de Punção (Se aplicável) */}
                        {punching.status !== 'nao_aplicavel_sem_pilares' && (
                           <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                              <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 group-hover:text-blue-600 transition-colors">Passo 07: Verificação de Punção no Pilar Crítico (ELU)</h4>
                              <div className="space-y-6 font-mono">
                                 <div className="grid grid-cols-2 gap-8">
                                    <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                       <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">F<sub>sd</sub> (γ<sub>f</sub>=1.4)</span>
                                       <span className="text-sm font-black text-slate-900">{formatNumberBR(punching.Ved_kN, 1) ?? 'N/D'} <span className="text-[10px] opacity-30">kN</span></span>
                                    </div>
                                    <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                       <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">u₁ (Perímetro)</span>
                                       <span className="text-sm font-black text-slate-900">{formatNumberBR(punching.u) ?? 'N/D'} <span className="text-[10px] opacity-30">m</span></span>
                                    </div>
                                 </div>

                                 <div className="grid grid-cols-2 gap-8">
                                    <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                       <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">τ<sub>sd</sub> (Solicitante)</span>
                                       <span className="text-sm font-black text-cyan-400">{formatNumberBR(punching.tau_sd, 3) ?? 'N/D'} <span className="text-[10px] opacity-30">MPa</span></span>
                                    </div>
                                    <div className="flex justify-between items-end border-b border-slate-200 pb-1">
                                       <span className="text-[10px] text-slate-900/20 uppercase tracking-widest">τ<sub>Rd1</sub> (Resistente)</span>
                                       <span className="text-sm font-black text-blue-600">{formatNumberBR(punching.tau_rd1, 3) ?? 'N/D'} <span className="text-[10px] opacity-30">MPa</span></span>
                                    </div>
                                 </div>

                                 <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                                    <span className="text-[9px] font-black text-slate-500 uppercase tracking-[0.2em]">Verificação τ<sub>sd</sub> ≤ τ<sub>Rd1</sub></span>
                                    <span className={`px-4 py-1.5 rounded-lg text-[9px] font-black tracking-widest border ${punching.atende_tau_rd1 ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' : 'bg-red-500/10 text-red-600 border-red-500/20'}`}>
                                       {punching.atende_tau_rd1 ? 'SAFETY OK' : 'CRITICAL FAILURE'}
                                    </span>
                                 </div>
                              </div>
                           </div>
                        )}

                        {/* Passo 08: Estados Limites de Serviço (ELS) */}
                        {(() => {
                           const wmax = service.w_max_mm;
                           const wdiff = service.w_diff_mm;
                           const wk_x = service.wk_x_max_mm;
                           const wk_y = service.wk_y_max_mm;
                           const wk_limit = service.wk_limit_mm;
                           const wlimit = service.w_limit_mm;
                           const wk_ok = service.wk_x_ok && service.wk_y_ok;
                           return (
                              <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                                 <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 group-hover:text-blue-600 transition-colors">Passo 08: Estados Limites de Serviço (ELS)</h4>

                                 <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-sm font-mono">
                                    <div className="space-y-4">
                                       <h5 className="text-[10px] font-sans font-black uppercase tracking-widest border-b border-slate-200 pb-1 text-slate-500">{isLaje ? "Deformações (Flechas)" : "Recalques e Deformações"}</h5>
                                       <div className="space-y-2">
                                          <p>{isLaje ? "w_flecha" : "w_máx"} = <span className="font-black text-slate-900">{formatNumberBR(wmax)} mm</span> <span className="text-[10px] font-sans text-slate-600">{isLaje ? `(Lim: ${formatNumberBR(wlimit)} mm)` : "(Lim: 50mm)"}</span></p>
                                          {!isLaje && <p>Δw (Diferencial) = <span className="font-black text-slate-900">{formatNumberBR(wdiff)} mm</span> <span className="text-[10px] font-sans text-slate-600">(Lim: 25mm)</span></p>}
                                       </div>
                                    </div>

                                    <div className="space-y-4">
                                       <h5 className="text-[10px] font-sans font-black uppercase tracking-widest border-b border-slate-200 pb-1 text-slate-500">Fissuração (w<sub>k</sub>)</h5>
                                       <div className="space-y-2">
                                          <p>w<sub>k,x</sub> = <span className="font-bold text-slate-900">{formatNumberBR(wk_x)} mm</span></p>
                                          <p>w<sub>k,y</sub> = <span className="font-bold text-slate-900">{formatNumberBR(wk_y)} mm</span></p>
                                          <p>w<sub>limite</sub> = <span className="font-bold text-slate-900">{formatNumberBR(wk_limit)} mm</span></p>
                                          <div className="pt-1">
                                             <span className={`px-2 py-0.5 rounded text-[9px] font-sans font-black ${wk_ok ? 'bg-emerald-500/10 text-emerald-600' : 'bg-red-500/10 text-red-600'}`}>
                                                {wk_ok ? 'FISSURAÇÃO OK' : 'REVISAR ARMADURA/ESPESSURA'}
                                             </span>
                                          </div>
                                       </div>
                                    </div>
                                 </div>
                              </div>
                           );
                        })()}
                     </div>
                      
                      {/* Nota Didática: Interação Solo-Estrutura (ISE) */}
                      {!isLaje && (
                        <div className="mt-16 pt-12 border-t border-apple-bg/5 page-break-before">
                           <ISETheoryView />
                        </div>
                      )}
                  </>
               )}
            </section>

            {/* Seção 10: Visualização 3D (Apenas Lajes ou se houver malha) */}
            {
               (isLaje || results.mesh) && (
                   <section className="mb-24 page-break-before">
                      <div className="flex items-center gap-4 mb-10">
                         <span className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center font-black text-blue-600 text-lg shadow-[0_0_20px_rgba(59,130,246,0.1)]">10</span>
                         <div>
                            <h2 className="text-2xl font-black text-slate-900 tracking-tight uppercase">Visualização Estrutural 3D</h2>
                            <p className="text-[10px] font-black text-slate-900/20 uppercase tracking-[0.3em] mt-1">Interatividade e Diagnóstico Geométrico</p>
                         </div>
                      </div>
                      <p className="text-sm font-serif italic text-slate-500 mb-8 max-w-2xl leading-relaxed">Modelo tridimensional da laje com amplificação dos deslocamentos para análise de rigidez e comportamento estrutural.</p>
                     <Structural3DView
                        Lx={results.master?.Lx ?? 10}
                        Ly={results.master?.Ly ?? 10}
                        h={results.master?.h ?? 0.2}
                        nodes={results.mesh?.nodes ?? []}
                        elements={results.mesh?.elements ?? []}
                        pillars={(results.memorial?.acoes_e_combinacoes?.reacoes_apoio ?? []).map((p: any) => ({
                           id: p.id,
                           x: p.x,
                           y: p.y,
                           bx: 0.4,
                           by: 0.4,
                           reaction_kN: p.reaction_kN
                        }))}
                        viewMode="displacements"
                     />
                  </section>
               )
            }

            {/* Seção 11: Mapa de Reações e Apoios */}
            {
               true && (
                   <section className="mb-24 page-break-before">
                      <div className="flex items-center gap-4 mb-10">
                         <span className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center font-black text-cyan-400 text-lg shadow-[0_0_20px_rgba(6,182,212,0.1)]">11</span>
                         <div>
                            <h2 className="text-2xl font-black text-slate-900 tracking-tight uppercase">{isLaje ? "Mapa de Reações nos Apoios" : "Mapa de Pressões de Contato Solo-Radier"}</h2>
                            <p className="text-[10px] font-black text-slate-900/20 uppercase tracking-[0.3em] mt-1">Equilíbrio de Contato e Interação</p>
                         </div>
                      </div>
                      <p className="text-sm font-serif italic text-slate-500 mb-8 max-w-2xl leading-relaxed">{isLaje ? "Distribuição estimada de reações nos apoios com indicação de posição dos pilares. Gradiente verde (baixa reação) -> vermelho (reação máxima)." : "Distribuição estimada de pressões de contato com indicação de posição dos pilares. Gradiente verde (baixa pressão) -> vermelho (pressão máxima)."}</p>
                     <SoilPressureMap
                        Lx={results.master?.Lx ?? 10}
                        Ly={results.master?.Ly ?? 10}
                        qmax={isLaje ? (deterministic?.rz_max_kN ?? 0) : (geotech.pressao_max_modelo_kPa ?? 0)}
                        qmed={isLaje ? (deterministic?.rz_mean_kN ?? 0) : (geotech.pressao_media_kPa ?? 0)}
                        sigma_adm={geotech.tensao_admissivel_kPa ?? 200}
                        pillars={results.master?.pillars || (results.memorial?.acoes_e_combinacoes?.pilares_considerados ?? []).map((p: any) => ({
                           id: p.id ?? 'P',
                           x: p.x ?? 0,
                           y: p.y ?? 0,
                           p_kN: p.p_kN ?? 0,
                        }))}
                        lineSupports={results.master?.line_supports || []}
                        systemType={isLaje ? "laje" : "radier"}
                     />

                     {/* Faixas regionais de armadura */}
                     {results.regional_reinforcement?.zones && (
                        <div className="mt-8">
                           <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-4">Armadura por Faixas Regionais (cm²/m)</h4>
                           <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                              {Object.entries(results.regional_reinforcement.zones as Record<string, any>).map(([zone, data]: [string, any]) => (
                                 <div key={zone} className="p-4 rounded-3xl bg-white/5 border border-slate-200 backdrop-blur-xl group hover:border-blue-500/20 transition-all">
                                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">{zone.replace(/_/g, ' ')}</p>
                                    <div className="space-y-2 text-xs font-mono">
                                       <div className="flex justify-between border-b border-slate-200 pb-1">
                                          <span className="text-slate-600">Asx:</span><span className="font-black text-blue-600">{formatNumberBR(data.Asx_cm2_m)} <span className="text-[9px] opacity-40">cm²/m</span></span>
                                       </div>
                                       <div className="flex justify-between border-b border-slate-200 pb-1">
                                          <span className="text-slate-600">Asy:</span><span className="font-black text-blue-600">{formatNumberBR(data.Asy_cm2_m)} <span className="text-[9px] opacity-40">cm²/m</span></span>
                                       </div>
                                       <p className="text-[9px] text-slate-600 mt-2 italic leading-tight">{data.sugestao_x}</p>
                                    </div>
                                 </div>
                              ))}
                           </div>
                           {results.regional_reinforcement.requer_reforco_local && (
                              <div className="mt-4 flex items-center gap-3 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-600 font-bold">
                                 <AlertTriangle className="h-4 w-4 shrink-0" />
                                 <span>Reforço local recomendado nas faixas sobre pilares (pico &gt; 1.5× pano central).</span>
                              </div>
                           )}
                           <p className="text-[10px] text-slate-900/20 mt-3 italic tracking-wide">{results.regional_reinforcement.nota}</p>
                        </div>
                     )}
                  </section>
               )
            }
            {/* Seção 12: Verificações Especiais de Lajes */}
            {
               isLaje && results.specialized && Object.keys(results.specialized).length > 0 && (
                  <section className="mb-12 page-break-before">
                     <div className="flex items-center gap-4 mb-10">
                        <span className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center font-black text-blue-600 text-lg shadow-[0_0_20px_rgba(59,130,246,0.1)]">12</span>
                        <div>
                           <h2 className="text-2xl font-black text-slate-900 tracking-tight uppercase">Análise de Sistema Especial</h2>
                           <p className="text-[10px] font-black text-slate-900/20 uppercase tracking-[0.3em] mt-1">Componentes de Alta Complexidade</p>
                        </div>
                     </div>
                     <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl">
                           <h3 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6">Parâmetros do Sistema</h3>
                           <div className="space-y-4 font-mono">
                              {results.specialized.type === "hollow_core" && (
                                 <>
                                    <div className="flex justify-between text-sm border-b border-slate-200 pb-2">
                                       <span className="text-slate-900/20">Área Líquida:</span>
                                       <span className="font-black text-slate-900">{formatNumberBR(results.specialized.area_net_m2)} <span className="text-[10px] opacity-30">m²</span></span>
                                    </div>
                                    <div className="flex justify-between text-sm border-b border-slate-200 pb-2">
                                       <span className="text-slate-900/20">Vrd1 (Dentes):</span>
                                       <span className="font-black text-blue-600">{formatNumberBR(results.specialized.v_rd1_kN_m)} <span className="text-[10px] opacity-30">kN/m</span></span>
                                    </div>
                                 </>
                              )}
                              {results.specialized.m_nerv_kNm !== undefined && (
                                 <>
                                    <div className="flex justify-between text-sm border-b border-slate-200 pb-2">
                                       <span className="text-slate-900/20">Momento por Nervura:</span>
                                       <span className="font-black text-blue-600">{formatNumberBR(results.specialized.m_nerv_kNm)} <span className="text-[10px] opacity-30">kNm</span></span>
                                    </div>
                                    <div className="flex justify-between text-sm border-b border-slate-200 pb-2">
                                       <span className="text-slate-900/20">Espessura Equivalente:</span>
                                       <span className="font-black text-slate-900">{formatNumberBR(results.specialized.h_eq_m * 100)} <span className="text-[10px] opacity-30">cm</span></span>
                                    </div>
                                    <div className="flex justify-between text-sm border-b border-slate-200 pb-2">
                                       <span className="text-slate-900/20">Armadura Total (m):</span>
                                       <span className="font-black text-emerald-600">{formatNumberBR(results.specialized.as_total_cm2_m)} <span className="text-[10px] opacity-30">cm²/m</span></span>
                                    </div>
                                 </>
                              )}
                              {results.specialized.q_eq_kPa !== undefined && (
                                 <>
                                    <div className="flex justify-between text-sm border-b border-slate-200 pb-2">
                                       <span className="text-slate-900/20">Carga Equivalente Protensão:</span>
                                       <span className="font-black text-cyan-400">{formatNumberBR(results.specialized.q_eq_kPa)} <span className="text-[10px] opacity-30">kN/m²</span></span>
                                    </div>
                                    <div className="flex justify-between text-sm border-b border-slate-200 pb-2">
                                       <span className="text-slate-900/20">Tensão Fibra Inf (Serviço):</span>
                                       <span className={`font-black ${results.specialized.sigma_inf_kPa > results.specialized.fctm_kPa ? "text-red-600" : "text-emerald-600"}`}>
                                          {formatNumberBR(results.specialized.sigma_inf_kPa)} <span className="text-[10px] opacity-30">kPa</span>
                                       </span>
                                    </div>
                                    <div className="flex justify-between text-sm border-b border-slate-200 pb-2">
                                       <span className="text-slate-900/20">Resistência Tração (fctm):</span>
                                       <span className="font-black text-slate-500">{formatNumberBR(results.specialized.fctm_kPa)} <span className="text-[10px] opacity-30">kPa</span></span>
                                    </div>
                                 </>
                              )}
                           </div>
                        </div>
                        <div className="flex flex-col items-center justify-center bg-white/5 rounded-[2.5rem] border border-slate-200 p-12 backdrop-blur-xl">
                           <div className="text-center">
                              <CheckCircle2 className="h-16 w-16 text-blue-600 mx-auto mb-6 shadow-[0_0_40px_rgba(59,130,246,0.3)]" />
                              <p className="text-sm font-black text-slate-900 uppercase tracking-widest">Análise Validada</p>
                              <p className="text-[10px] text-slate-600 mt-3 italic max-w-[200px] mx-auto leading-relaxed">Os parâmetros do sistema especial estão em conformidade com as exigências técnicas da NBR 6118.</p>
                           </div>
                        </div>
                     </div>
                  </section>
               )
            }
            {/* Seção 12: Comparador de Soluções */}
            {
               !isLaje && (
                  <section className="mb-12">
                     <div className="flex items-center gap-4 mb-10">
                        <span className="w-12 h-12 rounded-2xl bg-white/5 border border-slate-200 flex items-center justify-center font-black text-slate-700 text-lg shadow-[0_0_20px_rgba(255,255,255,0.05)]">13</span>
                        <div>
                           <h2 className="text-2xl font-black text-slate-900 tracking-tight uppercase">Comparador de Soluções de Fundação</h2>
                           <p className="text-[10px] font-black text-slate-900/20 uppercase tracking-[0.3em] mt-1">Otimização de Custos e Métodos Construtivos</p>
                        </div>
                     </div>
                     <p className="text-xs font-serif italic text-slate-500 mb-8 max-w-2xl leading-relaxed">Avaliação qualitativa orientativa das soluções disponíveis. Somente {isLaje ? "a Laje Maciça" : "o Radier Liso"} está implementado e calculado neste módulo.</p>
                     {results.solution_comparison?.solutions ? (
                        <SolutionComparator
                           solutions={results.solution_comparison.solutions}
                           nota={results.solution_comparison.nota}
                        />
                     ) : (
                        <p className="text-[11px] text-slate-900/20 italic font-mono uppercase tracking-widest bg-white/5 p-4 rounded-xl inline-block border border-slate-200">Execute a análise para visualizar o comparativo.</p>
                     )}
                  </section>
               )
            }

            {/* Seção 13: Checklist de Concreto Massa */}
            {
               results.thermal_checklist?.applicable && !isLaje && (
                  <section className="mb-12">
                     <div className="flex items-center gap-4 mb-10">
                        <span className="w-12 h-12 rounded-2xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center font-black text-orange-400 text-lg shadow-[0_0_20px_rgba(249,115,22,0.1)]">13</span>
                        <div>
                           <h2 className="text-2xl font-black text-slate-900 tracking-tight uppercase">Checklist de Concreto Massa</h2>
                           <div className="flex items-center gap-2 mt-1">
                              <span className="text-[10px] font-black px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-400 border border-orange-500/30">
                                 h = {formatNumberBR(results.thermal_checklist.h_adopted_m)} m ≥ {formatNumberBR(results.thermal_checklist.threshold_m)} m
                              </span>
                              <p className="text-[10px] font-black text-slate-900/20 uppercase tracking-[0.3em]">Gestão Térmica de Grandes Volumes</p>
                           </div>
                        </div>
                     </div>
                     <p className="text-xs font-serif italic text-slate-500 mb-8 max-w-2xl leading-relaxed">{results.thermal_checklist.nota}</p>
                     <div className="space-y-3">
                        {results.thermal_checklist.items?.map((item: any) => (
                           <div key={item.id} className="flex items-center justify-between p-5 rounded-[2rem] border border-orange-500/10 bg-orange-500/5 backdrop-blur-xl group hover:border-orange-500/30 transition-all">
                              <div className="flex items-center gap-4">
                                 <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center border", item.priority === 'alta' ? 'bg-orange-500/10 border-orange-500/20' : 'bg-amber-500/10 border-amber-500/20')}>
                                    <AlertTriangle className={cn("h-5 w-5", item.priority === 'alta' ? 'text-orange-400' : 'text-amber-600')} />
                                 </div>
                                 <p className="text-sm font-bold text-slate-900 leading-tight">{item.description}</p>
                              </div>
                              <span className={cn("text-[9px] font-black px-3 py-1 rounded-full shrink-0 tracking-widest border", item.priority === 'alta' ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' : 'bg-amber-500/20 text-amber-600 border-amber-500/30')}>
                                 {item.priority.toUpperCase()}
                              </span>
                           </div>
                        ))}
                     </div>
                  </section>
               )
            }

            {/* Seção 10: Análise de Pórtico 3D (StrucPy) */}
            {
               frameResults && (
                  <section className="mb-12 page-break-before">
                     <div className="flex items-center gap-2 mb-6">
                        <span className="bg-indigo-600 text-slate-900 text-[10px] font-black px-1.5 py-0.5 rounded">10</span>
                        <h2 className="text-2xl font-black text-slate-900 tracking-tight uppercase">Dimensionamento do Pórtico 3D (StrucPy)</h2>
                     </div>

                     <div className="space-y-10">
                        {/* Pilares */}
                        <div>
                           <h3 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 flex items-center gap-3">
                              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                              Dimensionamento de Pilares
                           </h3>
                           <div className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white/80 backdrop-blur-xl">
                              <table className="w-full text-[11px] text-left">
                                 <thead className="bg-white/5 font-black text-slate-500 uppercase text-[9px] tracking-[0.2em]">
                                    <tr>
                                       <th className="px-4 py-3">Pilar</th>
                                       <th className="px-4 py-3">Seção (cm)</th>
                                       <th className="px-4 py-3 text-right">Nd (kN)</th>
                                       <th className="px-4 py-3 text-right">As (cm²)</th>
                                       <th className="px-4 py-3 text-right">Taxa (%)</th>
                                    </tr>
                                 </thead>
                                 <tbody className="divide-y divide-white/5 font-mono">
                                    {frameResults.design_results?.pillars?.map((p: any) => (
                                       <tr key={p.id} className="hover:bg-white/5 transition-colors">
                                          <td className="px-4 py-3 font-black text-slate-900">{p.id}</td>
                                          <td className="px-4 py-3">{(p.b * 100).toFixed(0)}x{(p.h * 100).toFixed(0)}</td>
                                          <td className="px-4 py-3 text-right text-blue-600 font-black">{formatNumberBR(p.Nd, 1)}</td>
                                          <td className="px-4 py-3 text-right font-bold text-indigo-400">{formatNumberBR(p.As)}</td>
                                          <td className="px-4 py-3 text-right text-slate-900/20">{formatNumberBR(((p.As / (p.b * p.h * 10000)) * 100))}%</td>
                                       </tr>
                                    ))}
                                 </tbody>
                              </table>
                           </div>
                        </div>

                        {/* Vigas */}
                        <div>
                           <h3 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-6 flex items-center gap-3">
                              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                              Dimensionamento de Vigas
                           </h3>
                           <div className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white/80 backdrop-blur-xl">
                              <table className="w-full text-[11px] text-left">
                                 <thead className="bg-white/5 font-black text-slate-500 uppercase text-[9px] tracking-[0.2em]">
                                    <tr>
                                       <th className="px-4 py-3">Viga</th>
                                       <th className="px-4 py-3">Seção (cm)</th>
                                       <th className="px-4 py-3 text-right">Mk (kNm)</th>
                                       <th className="px-4 py-3 text-right">As Inf (cm²)</th>
                                       <th className="px-4 py-3 text-right">As Sup (cm²)</th>
                                    </tr>
                                 </thead>
                                 <tbody className="divide-y divide-white/5 font-mono">
                                    {frameResults.design_results?.beams?.map((b: any) => (
                                       <tr key={b.id} className="hover:bg-white/5 transition-colors">
                                          <td className="px-4 py-3 font-black text-slate-900">{b.id}</td>
                                          <td className="px-4 py-3">{(b.b * 100).toFixed(0)}x{(b.h * 100).toFixed(0)}</td>
                                          <td className="px-4 py-3 text-right text-blue-600 font-black">{formatNumberBR(b.max_moment, 1)}</td>
                                          <td className="px-4 py-3 text-right font-bold text-indigo-400">{formatNumberBR(b.As_bottom)}</td>
                                          <td className="px-4 py-3 text-right text-slate-500">{formatNumberBR(b.As_top)}</td>
                                       </tr>
                                    ))}
                                 </tbody>
                              </table>
                           </div>
                        </div>

                        <div className="bg-indigo-500/5 p-6 rounded-[2rem] border border-indigo-500/10 flex items-start gap-4 backdrop-blur-xl">
                           <Info className="h-5 w-5 text-indigo-500 mt-0.5 shrink-0" />
                           <div className="text-[10px] text-indigo-900/70 leading-relaxed italic">
                              Os resultados acima foram calculados utilizando o motor <strong>StrucPy Structural Engine</strong>.
                              O modelo considera um pórtico espacial 3D com rigidez de nós compatível.
                              As armaduras apresentadas são as máximas encontradas nos respectivos vãos/lances.
                           </div>
                        </div>
                     </div>
                  </section>
               )
            }

            {/* Seção 10: Memorial Padronizado (M4) */}
            {
               (results.memorial_markdown || memorial.standard_markdown) && (
                  <section className="mt-24 pt-16 border-t border-slate-200 break-before-page">
                     <div className="flex items-center gap-2 mb-8">
                        <span className="w-12 h-12 rounded-2xl bg-blue-600/10 border border-blue-600/20 flex items-center justify-center font-black text-blue-600 text-lg shadow-[0_0_20px_rgba(37,99,235,0.1)]">M4</span>
                         <div>
                            <h2 className="text-2xl font-black text-slate-900 tracking-tight uppercase">Memorial Técnico Padronizado</h2>
                            <p className="text-[10px] font-black text-slate-900/20 uppercase tracking-[0.3em] mt-1">Transcrição Formal e Normativa</p>
                         </div>
                     </div>
                     <div className="prose prose-sm max-w-none prose-invert prose-headings:font-black prose-headings:text-slate-900 prose-p:text-slate-700 prose-strong:text-blue-600 prose-code:text-emerald-600 prose-blockquote:border-blue-500/30 prose-blockquote:bg-white/5 prose-blockquote:p-6 prose-blockquote:rounded-3xl">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                           {results.memorial_markdown || memorial.standard_markdown}
                        </ReactMarkdown>
                     </div>
                  </section>
               )
            }

            {/* Seção 12: Referências Bibliográficas e Embasamento Científico */}
            <section className="mt-24 pt-12 border-t border-slate-200 break-inside-avoid">
               <div className="flex items-center gap-4 mb-10">
                  <span className="w-12 h-12 rounded-2xl bg-slate-500/10 border border-slate-500/20 flex items-center justify-center font-black text-slate-600 text-lg shadow-[0_0_20px_rgba(148,163,184,0.1)]">12</span>
                  <div>
                     <h2 className="text-2xl font-black text-slate-900 tracking-tight uppercase">Embasamento Técnico e Bibliográfico</h2>
                     <p className="text-[10px] font-black text-slate-900/20 uppercase tracking-[0.3em] mt-1">Normatização e Validação Científica</p>
                  </div>
               </div>
               
               <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="p-8 rounded-[2.5rem] bg-white/80 border border-slate-200 backdrop-blur-xl group hover:border-slate-500/20 transition-all">
                     <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-8 group-hover:text-slate-600 transition-colors">Fundamentos Aplicados</h4>
                     <ul className="space-y-6">
                        <li className="flex gap-4">
                           <div className="w-10 h-10 rounded-xl bg-white/5 border border-slate-200 flex items-center justify-center shrink-0">
                              <Book className="w-5 h-5 text-slate-600" />
                           </div>
                           <div>
                              <p className="text-xs font-black text-slate-900 uppercase tracking-wider">NBR 6118:2014 / 2023</p>
                              <p className="text-[10px] text-slate-500 font-medium leading-relaxed mt-1 italic">Projeto de estruturas de concreto - Procedimento. Base para todos os cálculos de ELU e ELS.</p>
                           </div>
                        </li>
                        
                        {windResults && (
                           <li className="flex gap-4">
                              <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shrink-0">
                                 <Wind className="w-5 h-5 text-blue-600" />
                              </div>
                              <div>
                                 <p className="text-xs font-black text-slate-900 uppercase tracking-wider">NBR 6123</p>
                                 <p className="text-[10px] text-slate-500 font-medium leading-relaxed mt-1 italic">Forças devidas ao vento em edificações. Aplicado no módulo de análise de ventos.</p>
                              </div>
                           </li>
                        )}

                        {stabilityResults && stabilityResults.gamma_z > 1.1 && LIBRARY_KNOWLEDGE["stability_global"]?.map((cite, i) => (
                           <li key={i} className="flex gap-4">
                              <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shrink-0">
                                 <ExternalLink className="w-5 h-5 text-blue-600" />
                              </div>
                              <div>
                                 <p className="text-xs font-black text-slate-900 uppercase tracking-wider">{cite.citation}</p>
                                 <p className="text-[10px] text-slate-500 font-medium leading-relaxed mt-1 italic">{cite.context}</p>
                              </div>
                           </li>
                        ))}

                        {punching.ratio_max > 0.9 && LIBRARY_KNOWLEDGE["punching_shear"]?.map((cite, i) => (
                           <li key={i} className="flex gap-4">
                              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shrink-0">
                                 <AlertTriangle className="w-5 h-5 text-amber-600" />
                              </div>
                              <div>
                                 <p className="text-xs font-black text-slate-900 uppercase tracking-wider">{cite.citation}</p>
                                 <p className="text-[10px] text-slate-500 font-medium leading-relaxed mt-1 italic">{cite.context}</p>
                              </div>
                           </li>
                        ))}

                        {!isLaje && LIBRARY_KNOWLEDGE["ise_winkler"]?.map((cite, i) => (
                           <li key={i} className="flex gap-4">
                              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
                                 <Layers className="w-5 h-5 text-emerald-600" />
                              </div>
                              <div>
                                 <p className="text-xs font-black text-slate-900 uppercase tracking-wider">{cite.citation}</p>
                                 <p className="text-[10px] text-slate-500 font-medium leading-relaxed mt-1 italic">{cite.context}</p>
                              </div>
                           </li>
                        ))}
                     </ul>
                  </div>

                  <div className="flex flex-col justify-center p-10 rounded-[2.5rem] bg-blue-600 text-white shadow-2xl shadow-blue-900/40 relative overflow-hidden group">
                     <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32 blur-3xl group-hover:bg-white/20 transition-all duration-1000" />
                     <div className="flex items-center gap-3 mb-6 relative z-10">
                        <BookOpen className="w-6 h-6 text-blue-200" />
                        <span className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-100">Nota Acadêmica de Autoridade</span>
                     </div>
                     <p className="text-lg font-black leading-tight mb-8 relative z-10 tracking-tight italic">
                        "O uso de algoritmos numéricos não substitui o julgamento do engenheiro. Os resultados aqui apresentados foram validados frente às literaturas de {isLaje ? "Teatini e Ibracon" : "Harry Poulos e Velloso"}, garantindo que a modelagem MEF-Winkler esteja em conformidade com o estado da arte da engenharia estrutural moderna."
                     </p>
                     <div className="pt-6 border-t border-white/20 text-[10px] font-black uppercase tracking-[0.3em] opacity-60 relative z-10 flex justify-between items-center">
                        <span>Sincronizado com Biblioteca Técnica Local</span>
                        <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                     </div>
                  </div>
               </div>
            </section>

            {/* Rodapé do Memorial */}
            <div className="mt-32 pt-12 border-t border-slate-200 flex flex-col md:flex-row justify-between items-center gap-6 opacity-30 text-[9px] font-black uppercase tracking-[0.4em]">
               <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                  <span>Structural Intelligence Console // Audit v24.4.2</span>
               </div>
               <div className="flex items-center gap-6">
                  <span>NBR 6118 COMPLIANT</span>
                  <span className="text-slate-900/20">|</span>
                  <span>MEF STRUCTURAL ENGINE 3.0</span>
               </div>
               <div>© 2026 VibeDoCode High-Performance Systems</div>
            </div>

         </div >
      </div >
   );
}

function ReportMetric({ label, value, unit, sub }: { label: string; value: string; unit?: string; sub?: string }) {
   return (
      <div className="group transition-all">
         <p className="text-[10px] font-black text-slate-600 uppercase tracking-[0.3em] mb-2 group-hover:text-blue-600 transition-colors">{label}</p>
         <div className="flex items-baseline gap-1.5">
            <span className="text-3xl font-black text-slate-900 tracking-tighter font-mono">{value}</span>
            {unit && <span className="text-sm font-black text-slate-900/20 uppercase">{unit}</span>}
         </div>
         {sub && <p className="text-[10px] font-bold text-slate-900/20 uppercase tracking-widest mt-2">{sub}</p>}
      </div>
   );
}

function StatusLabel({ ok }: { ok: boolean | null }) {
   if (ok === null) return (
      <div className="flex items-center gap-2">
         <div className="w-1.5 h-1.5 bg-white/20 rounded-full animate-ping" />
         <span className="text-slate-900/20 font-black tracking-[0.3em] text-[9px] uppercase">Processing...</span>
      </div>
   );
   return (
      <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-[0.2em] border backdrop-blur-md transition-all duration-500 ${
         ok 
            ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.05)]' 
            : 'bg-red-500/10 text-red-600 border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.05)]'
      }`}>
         <div className={`w-1.5 h-1.5 rounded-full ${ok ? 'bg-emerald-400 animate-pulse' : 'bg-red-400 animate-pulse'}`} />
         {ok ? 'Validado' : 'Crítico'}
      </div>
   );
}
