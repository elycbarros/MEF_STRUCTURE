"use client";

import React, { useState } from "react";
import { Download, Printer, FileText, CheckCircle2, AlertTriangle, XCircle, Info, ExternalLink, TrendingUp, Wind } from "lucide-react";
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

interface ReportViewProps {
   results: any;
   frameResults?: any;
   stabilityResults?: any;
   windResults?: any;
   projectMeta: any;

   apiBaseUrl: string;
}

function SanityBadge({ label, ok, msg_ok, msg_fail }: { label: string, ok: boolean, msg_ok: string, msg_fail: string }) {
   return (
      <div className={`p-4 rounded-xl border flex flex-col gap-2 ${ok ? 'bg-[#ecfdf5] border-[#a7f3d0] text-[#065f46]' : 'bg-[#fef2f2] border-[#fecaca] text-[#991b1b]'}`}>
         <div className="flex items-center gap-2">
            {ok ? <CheckCircle2 className="h-5 w-5" /> : <AlertTriangle className="h-5 w-5" />}
            <span className="font-bold text-sm uppercase">{label}</span>
         </div>
         <span className="text-xs font-semibold">{ok ? msg_ok : msg_fail}</span>
      </div>
   );
}

export function ReportView({ results, frameResults, stabilityResults, windResults, projectMeta, apiBaseUrl }: ReportViewProps) {

   const [exporting, setExporting] = useState(false);

   const downloadPdf = async () => {
      setExporting(true);
      try {
         const response = await fetch(`${apiBaseUrl}/export/pdf`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
               results: results,
               project_meta: projectMeta,
               wind_results: windResults,
               stability_results: stabilityResults,
            }),
         });

         if (!response.ok) throw new Error("Falha ao gerar PDF");

         const blob = await response.blob();
         const url = window.URL.createObjectURL(blob);
         const a = document.createElement("a");
         a.href = url;
         a.download = `Relatorio_Estrutural_${projectMeta.obra.replace(/\s+/g, "_")}.pdf`;
         document.body.appendChild(a);
         a.click();
         window.URL.revokeObjectURL(url);
      } catch (error) {
         console.error(error);
         alert("Erro ao baixar o PDF. Verifique se o backend está rodando.");
      } finally {
         setExporting(false);
      }
   };

   if (!results) {
      return (
         <div className="flex flex-col items-center justify-center py-20 text-apple-muted">
            <FileText className="h-16 w-16 opacity-20" />
            <p className="mt-4 font-medium">Execute uma análise para visualizar o relatório.</p>
         </div>
      );
   }

   const isLaje = results.master?.system_type === "laje";
   const memorial = results.memorial || {};
   const deterministic = results.deterministic || {};
   const executiveDecision = results.executive_decision || {};
   const geotech = memorial.verificacoes_geotecnicas || {};
   const structural = memorial.verificacoes_estruturais || {};
   const service = memorial.verificacoes_de_servico || {};
   const flexure = structural.flexao || {};
   const punching = structural.puncao || {};

   return (
      <div className="space-y-8 pb-20">
         {/* Header Ações */}
         <div className="flex flex-wrap items-center justify-between gap-4 no-print">
            <div>
               <h2 className="text-2xl font-black text-apple-text">Relatório Técnico</h2>
               <p className="text-sm font-medium text-apple-muted">
                  {isLaje
                     ? "Documento gerado automaticamente com base no modelo MEF (Lajes Lab Pro)."
                     : "Documento gerado automaticamente com base no modelo MEF-Winkler."}
               </p>
            </div>
            <div className="flex items-center gap-3">
               <button
                  onClick={() => window.print()}
                  className="inline-flex items-center gap-2 rounded-xl border border-black/10 bg-white px-4 py-2 text-sm font-bold text-apple-text hover:bg-apple-bg transition"
               >
                  <Printer className="h-4 w-4" />
                  Imprimir
               </button>
               <button
                  onClick={downloadPdf}
                  disabled={exporting}
                  className="inline-flex items-center gap-2 rounded-xl bg-apple-blue px-4 py-2 text-sm font-bold text-white shadow-apple hover:opacity-90 transition disabled:opacity-50"
               >
                  <Download className={`h-4 w-4 ${exporting ? "animate-bounce" : ""}`} />
                  {exporting ? "Gerando..." : "Baixar PDF Profissional"}
               </button>
            </div>
         </div>

         {/* Preview do Documento */}
         <div className="bg-white rounded-apple border border-black/5 shadow-sm p-8 sm:p-12 print:shadow-none print:border-none print:p-0">

            {/* Cabeçalho do Memorial */}
            <div className="flex justify-between items-start border-b border-apple-bg pb-6 mb-8">
               <div>
                  <h1 className="text-2xl font-black tracking-tight text-apple-text">
                     {isLaje ? "MEMORIAL DE CÁLCULO: LAJES ELEVADAS" : "MEMORIAL DE CÁLCULO ESTRUTURAL"}
                  </h1>
                  <p className="text-sm font-bold text-apple-blue uppercase tracking-widest mt-1">
                     {isLaje ? "LAJES PRO ENGINE | STRUCTURAL SUITE" : "RADIER PRO ENGINE | STRUCTURAL SUITE"}
                  </p>
               </div>
               <div className="text-right text-[11px] font-bold text-apple-muted space-y-1">
                  <p>REVISÃO: {projectMeta.revisao}</p>
                  <p>EMISSÃO: {projectMeta.emissao}</p>
                  <p>PÁGINA: 1 de 1</p>
               </div>
            </div>

            {/* Estabilidade Global e Conforto */}
            {stabilityResults && (
               <section className="rounded-3xl border border-black/5 bg-white p-8 shadow-sm break-inside-avoid">
                  <div className="flex items-center justify-between mb-8">
                     <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-apple-blue/10 rounded-2xl flex items-center justify-center">
                           <TrendingUp className="text-apple-blue h-6 w-6" />
                        </div>
                        <div>
                           <h3 className="text-xl font-black text-apple-text">Estabilidade Global e Conforto</h3>
                           <p className="text-sm font-medium text-apple-muted">Análise de 2ª Ordem e Acelerações (NBR 6118)</p>
                        </div>
                     </div>
                     <div className="flex flex-col items-end">
                        <span className={`px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${stabilityResults.is_stable ? 'bg-apple-success/10 text-apple-success' : 'bg-apple-error/10 text-apple-error'}`}>
                           {stabilityResults.is_stable ? 'ESTRUTURA ESTÁVEL' : 'INSTABILIDADE DETECTADA'}
                        </span>
                     </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                     <div className="p-5 rounded-2xl bg-apple-bg border border-black/5">
                        <p className="text-[10px] font-black uppercase tracking-widest text-apple-muted mb-1">Parâmetro γz</p>
                        <p className="text-3xl font-black text-apple-text">{formatNumberBR(stabilityResults.gamma_z, 3)}</p>
                        <p className="text-[11px] font-bold mt-2 text-apple-muted">Limite normativo: 1.10 (1ª ordem) / 1.30 (estabilidade)</p>
                     </div>
                     <div className="p-5 rounded-2xl bg-apple-bg border border-black/5">
                        <p className="text-[10px] font-black uppercase tracking-widest text-apple-muted mb-1">Amplificação P-Δ</p>
                        <p className="text-3xl font-black text-apple-text">{formatNumberBR(stabilityResults.p_delta_factor)}</p>
                        <p className="text-[11px] font-bold mt-2 text-apple-muted">Fator de majoração de esforços de 2ª ordem</p>
                     </div>
                     <div className="p-5 rounded-2xl bg-apple-bg border border-black/5">
                        <p className="text-[10px] font-black uppercase tracking-widest text-apple-muted mb-1">Aceleração de Pico</p>
                        <p className="text-3xl font-black text-apple-text">{formatNumberBR(stabilityResults.peak_acceleration_ms2 * 100)} <span className="text-sm font-bold text-apple-muted">cm/s²</span></p>
                        <p className="text-[11px] font-bold mt-2 text-apple-muted">Status: {stabilityResults.comfort_status}</p>
                     </div>
                     <div className="p-5 rounded-2xl bg-apple-bg border border-black/5">
                        <p className="text-[10px] font-black uppercase tracking-widest text-apple-muted mb-1">Não-Linearidade</p>
                        <p className="text-sm font-bold text-apple-text mt-2">Fisica: Ativa (0.4/0.8)</p>
                        <p className="text-sm font-bold text-apple-text">Geométrica: P-Delta</p>
                     </div>
                  </div>

                  <div className="mt-8 p-4 rounded-2xl bg-apple-blue/5 border border-apple-blue/10">
                     <p className="text-xs font-semibold text-apple-blue leading-relaxed">
                        <strong>Nota Técnica:</strong> A análise de estabilidade global utiliza o coeficiente Gama-Z como indicador de sensibilidade aos efeitos de segunda ordem.
                        Para edifícios acima de 40 pavimentos, recomenda-se a análise P-Delta iterativa e a verificação de conforto humano para ventos com período de retorno de 1 ano.
                     </p>
                  </div>
               </section>
            )}

            {/* Ações de Vento */}
            {windResults && (
               <section className="rounded-3xl border border-black/5 bg-white p-8 shadow-sm break-inside-avoid">
                  <div className="flex items-center justify-between mb-8">
                     <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center">
                           <Wind className="text-blue-500 h-6 w-6" />
                        </div>
                        <div>
                           <h3 className="text-xl font-black text-apple-text">Ações de Vento (NBR 6123)</h3>
                           <p className="text-sm font-medium text-apple-muted">Premissas e Esforços de Projeto</p>
                        </div>
                     </div>
                     <div className="flex flex-col items-end">
                        <span className="px-4 py-1 bg-blue-50 text-blue-600 rounded-full text-[10px] font-black uppercase tracking-wider border border-blue-100">
                           Carga Horizontal Ativa
                        </span>
                     </div>
                  </div>

                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                     <div className="p-5 rounded-2xl bg-apple-bg border border-black/5">
                        <p className="text-[10px] font-black uppercase tracking-widest text-apple-muted mb-1">Velocidade V₀</p>
                        <p className="text-2xl font-black text-apple-text">{windResults.config?.v0} <span className="text-sm font-bold text-apple-muted">m/s</span></p>
                        <p className="text-[11px] font-bold mt-2 text-apple-muted">S1=1.0 | S3=1.0</p>
                     </div>
                     <div className="p-5 rounded-2xl bg-apple-bg border border-black/5">
                        <p className="text-[10px] font-black uppercase tracking-widest text-apple-muted mb-1">Coef. Arrasto Cf</p>
                        <p className="text-2xl font-black text-apple-text">{formatNumberBR(windResults.geometry?.cf)}</p>
                        <p className="text-[11px] font-bold mt-2 text-apple-muted">Planta Retangular</p>
                     </div>
                     <div className="p-5 rounded-2xl bg-apple-bg border border-black/5">
                        <p className="text-[10px] font-black uppercase tracking-widest text-apple-muted mb-1">Força Total</p>
                        <p className="text-2xl font-black text-apple-text">{formatNumberBR(windResults.summary?.total_force_kN, 1)} <span className="text-sm font-bold text-apple-muted">kN</span></p>
                        <p className="text-[11px] font-bold mt-2 text-apple-muted">Resultante de base</p>
                     </div>
                     <div className="p-5 rounded-2xl bg-apple-bg border border-black/5">
                        <p className="text-[10px] font-black uppercase tracking-widest text-apple-muted mb-1">Momento Base</p>
                        <p className="text-2xl font-black text-apple-text">{formatNumberBR(windResults.summary?.base_moment_kNm, 0)} <span className="text-sm font-bold text-apple-muted">kNm</span></p>
                        <p className="text-[11px] font-bold mt-2 text-apple-muted">Tombamento total</p>
                     </div>
                  </div>

                  <div className="overflow-hidden rounded-2xl border border-black/5">
                     <table className="w-full text-xs text-left">
                        <thead className="bg-apple-bg/50 font-black text-apple-muted uppercase text-[9px] tracking-widest">
                           <tr>
                              <th className="px-6 py-3 border-b border-black/5">Z (m)</th>
                              <th className="px-6 py-3 border-b border-black/5">Vk (m/s)</th>
                              <th className="px-6 py-3 border-b border-black/5">Pressão q (Pa)</th>
                              <th className="px-6 py-3 border-b border-black/5 text-right">Força Nível (kN)</th>
                           </tr>
                        </thead>
                        <tbody className="divide-y divide-black/5">
                           {windResults.profile?.filter((_: any, i: number) => i % (Math.ceil(windResults.profile.length / 10)) === 0 || i === windResults.profile.length - 1).map((level: any, i: number) => (
                              <tr key={i} className="hover:bg-apple-blue/5 transition-colors">
                                 <td className="px-6 py-3 font-black text-apple-text">{formatNumberBR(level.z, 1)}</td>
                                 <td className="px-6 py-3 font-bold text-apple-muted">{formatNumberBR(level.vk_m_s)}</td>
                                 <td className="px-6 py-3 font-bold text-apple-muted">{formatNumberBR(level.q_Pa, 0)}</td>
                                 <td className="px-6 py-3 text-right font-black text-blue-600">{formatNumberBR(level.f_total_kN)}</td>
                              </tr>
                           ))}
                        </tbody>
                     </table>
                  </div>
               </section>
            )}


            {/* Info Obra */}
            <div className="grid grid-cols-2 gap-8 mb-10 text-sm">
               <div>
                  <h4 className="text-[10px] font-black text-apple-muted uppercase tracking-widest mb-2">Dados da Obra</h4>
                  <p className="font-bold">{projectMeta.obra}</p>
                  <p className="text-apple-muted">{projectMeta.local}</p>
               </div>
               <div className="text-right">
                  <h4 className="text-[10px] font-black text-apple-muted uppercase tracking-widest mb-2">Responsável Técnico</h4>
                  <p className="font-bold">{projectMeta.responsavel}</p>
                  <p className="text-apple-muted">{projectMeta.registro}</p>
               </div>
            </div>

            {/* Seção 1: Resumo Executivo */}
            <section className="mb-12">
               <div className="flex items-center gap-2 mb-4">
                  <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">01</span>
                  <h2 className="text-lg font-black text-apple-text">RESUMO EXECUTIVO</h2>
               </div>
               <ExecutiveDecisionCard decision={executiveDecision} />
            </section>

            {/* Seção 1.5: Sanity Checks Rápidos */}
            {results.sanity_checks && (
               <section className="mb-12">
                  <div className="flex items-center gap-2 mb-4">
                     <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">01.5</span>
                     <h2 className="text-lg font-black text-apple-text uppercase">Sanity Checks (Diagnóstico Rápido)</h2>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                     {isLaje ? (
                        <>
                           <SanityBadge label="Flechas" ok={results.sanity_checks.recalque_ok} msg_ok="Dentro do Limite Normativo" msg_fail="Excede Limite Normativo" />
                           <SanityBadge label="Punção" ok={results.sanity_checks.puncao_ok} msg_ok="Tensões Seguras / Não Aplicável" msg_fail="Risco de Punção" />
                           <SanityBadge label="Fissuração" ok={results.reinforcement_summary?.serviceability?.wk_x_ok && results.reinforcement_summary?.serviceability?.wk_y_ok} msg_ok="Dentro do Limite Normativo" msg_fail="Excede Limite Normativo" />
                        </>
                     ) : (
                        <>
                           <SanityBadge label="Pressão do Solo" ok={results.sanity_checks.pressao_solo_ok} msg_ok="Dentro do Limite Admissível" msg_fail="Excede Limite Admissível" />
                           <SanityBadge label="Recalques" ok={results.sanity_checks.recalque_ok} msg_ok="Conforme NBR (Wmax < 50mm)" msg_fail="Excede Limites NBR" />
                           <SanityBadge label="Punção" ok={results.sanity_checks.puncao_ok} msg_ok="Tensões Seguras / Não Aplicável" msg_fail="Risco de Punção / Reforço Requerido" />
                        </>
                     )}
                  </div>
               </section>
            )}

            {/* Seção 2: Dados de Entrada */}
            <section className="mb-12">
               <div className="flex items-center gap-2 mb-4">
                  <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">02</span>
                  <h2 className="text-lg font-black text-apple-text">DADOS DE ENTRADA</h2>
               </div>
               <div className="grid grid-cols-3 gap-6">
                  <ReportMetric label="Geometria" value={`${results.master?.Lx}m x ${results.master?.Ly}m`} sub={`Área: ${formatNumberBR(results.master?.area_m2, 1)} m²`} />
                  <ReportMetric label="Espessura" value={`${results.master?.h} m`} sub={`Vol: ${formatNumberBR(results.master?.volume_m3, 1)} m³`} />
                  {!isLaje && <ReportMetric label="Solo (kv)" value={`${formatNumberBR(results.master?.kv / 1000, 0)}`} unit="kN/m³" />}
                  {isLaje && <ReportMetric label="Sistema" value="Laje Elevada" sub="Apoios Discretos" />}
               </div>
            </section>

            {/* Seção 2.1: Consumo de Materiais */}
            <section className="mb-12">
               <div className="flex items-center gap-2 mb-4">
                  <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">02.1</span>
                  <h2 className="text-lg font-black text-apple-text uppercase">Consumo de Materiais (Estimativo)</h2>
               </div>
               <div className="grid grid-cols-4 gap-4">
                  <ReportMetric
                     label="Concreto"
                     value={formatNumberBR(flexure.metrics?.concrete_volume_m3, 1)}
                     unit="m³"
                     sub="Volume total"
                  />
                  <ReportMetric
                     label="Aço Total"
                     value={formatNumberBR(flexure.metrics?.total_steel_kg, 0)}
                     unit="kg"
                     sub="+10% perdas"
                  />
                  <ReportMetric
                     label="Taxa/Volume"
                     value={formatNumberBR(flexure.metrics?.steel_density_kg_m3, 1)}
                     unit="kg/m³"
                     sub="Média global"
                  />
                  <ReportMetric
                     label="Taxa/Área"
                     value={formatNumberBR(flexure.metrics?.steel_density_kg_m2, 1)}
                     unit="kg/m²"
                     sub="Média global"
                  />
               </div>
            </section>

            {/* Seção 3: Reações de Apoio (Apenas Lajes) */}
            {isLaje && results.memorial?.acoes_e_combinacoes?.reacoes_apoio && (
               <section className="mb-12">
                  <div className="flex items-center gap-2 mb-4">
                     <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">03</span>
                     <h2 className="text-lg font-black text-apple-text uppercase tracking-tight">Reações de Apoio (Nodal)</h2>
                  </div>
                  <div className="overflow-hidden rounded-apple-inner border border-black/5">
                     <table className="w-full text-xs text-left">
                        <thead className="bg-apple-bg/50 font-black text-apple-muted uppercase text-[9px] tracking-widest">
                           <tr>
                              <th className="px-4 py-3">Pilar / Apoio</th>
                              <th className="px-4 py-3 text-center">Posição (X, Y) [m]</th>
                              <th className="px-4 py-3 text-right">Reação Vertical (kN)</th>
                           </tr>
                        </thead>
                        <tbody className="divide-y divide-black/5">
                           {results.memorial?.acoes_e_combinacoes?.reacoes_apoio?.map((p: any) => (
                              <tr key={p.id} className="hover:bg-apple-blue/5 transition-colors">
                                 <td className="px-4 py-3 font-bold text-apple-text">{p.id}</td>
                                 <td className="px-4 py-3 text-center text-apple-muted font-mono tracking-tighter">
                                    {formatNumberBR(p.x)}m , {formatNumberBR(p.y)}m
                                 </td>
                                 <td className="px-4 py-3 text-right font-mono font-bold text-apple-blue">
                                    {formatNumberBR(p.reaction_kN)}
                                 </td>
                              </tr>
                           ))}
                           <tr className="bg-apple-bg/30 font-black border-t-2 border-black/5">
                              <td colSpan={2} className="px-4 py-3 text-right uppercase text-[9px] tracking-widest">Somatório das Reações</td>
                              <td className="px-4 py-3 text-right font-mono text-apple-text text-sm">
                                 {formatNumberBR(results.memorial?.acoes_e_combinacoes?.carga_pilares_kN)} kN
                              </td>
                           </tr>
                        </tbody>
                     </table>
                  </div>
                  <p className="mt-3 text-[10px] text-apple-muted italic leading-relaxed">
                     * As reações são calculadas nos nós restringidos por penalidade rígida (10^14 N/m).
                     Diferenças residuais inferiores a 0.1% são aceitáveis devido à discretização da malha MEF.
                  </p>
               </section>
            )}

            {/* Seção 3: Resultados Geotécnicos */}
            {!isLaje && (
               <section className="mb-12">
                  <div className="flex items-center gap-2 mb-4">
                     <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">03</span>
                     <h2 className="text-lg font-black text-apple-text">VERIFICAÇÕES GEOTÉCNICAS</h2>
                  </div>
                  <div className="overflow-hidden rounded-apple-inner border border-black/5">
                     <table className="w-full text-sm text-left">
                        <thead className="bg-apple-bg/50 font-bold text-apple-muted">
                           <tr>
                              <th className="px-4 py-3">Parâmetro</th>
                              <th className="px-4 py-3">Valor Calculado</th>
                              <th className="px-4 py-3">Limite Admissível</th>
                              <th className="px-4 py-3">Status</th>
                           </tr>
                        </thead>
                        <tbody className="divide-y divide-black/5">
                           <tr>
                              <td className="px-4 py-3 font-medium">Pressão Máxima</td>
                              <td className="px-4 py-3">{formatNumberBR(geotech.pressao_max_modelo_kPa)} kPa</td>
                              <td className="px-4 py-3">{formatNumberBR(geotech.tensao_admissivel_kPa)} kPa</td>
                              <td className="px-4 py-3"><StatusLabel ok={geotech.atende_pressao_max_modelo} /></td>
                           </tr>
                           <tr>
                              <td className="px-4 py-3 font-medium">Recalque Máximo</td>
                              <td className="px-4 py-3">{formatNumberBR(service.w_max_mm)} mm</td>
                              <td className="px-4 py-3">25.00 mm</td>
                              <td className="px-4 py-3"><StatusLabel ok={service.w_max_mm < 25} /></td>
                           </tr>
                        </tbody>
                     </table>
                  </div>
               </section>
            )}

            {/* Seção 4: Armaduras Principais */}
            <section className="mb-12">
               <div className="flex items-center gap-2 mb-4">
                  <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">04</span>
                  <h2 className="text-lg font-black text-apple-text">DETALHAMENTO DE ARMADURAS</h2>
               </div>
               <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-apple-inner bg-apple-bg/30 border border-black/5">
                     <h4 className="text-[10px] font-black text-apple-muted uppercase mb-3">Face Superior (Negativo)</h4>
                     <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                           <span className="font-medium">Asx:</span>
                           <span className="font-bold text-apple-blue">{formatNumberBR(flexure.Asx_top_adot_max_cm2_m)} cm²/m</span>
                        </div>
                        <div className="flex justify-between text-sm">
                           <span className="font-medium">Asy:</span>
                           <span className="font-bold text-apple-blue">{formatNumberBR(flexure.Asy_top_adot_max_cm2_m)} cm²/m</span>
                        </div>
                        <p className="text-[10px] text-apple-muted mt-2 italic">* Sugestão: {flexure.sugestao_x_sup}</p>
                     </div>
                  </div>
                  <div className="p-4 rounded-apple-inner bg-apple-bg/30 border border-black/5">
                     <h4 className="text-[10px] font-black text-apple-muted uppercase mb-3">Face Inferior (Positivo)</h4>
                     <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                           <span className="font-medium">Asx:</span>
                           <span className="font-bold text-apple-blue">{formatNumberBR(flexure.Asx_bottom_adot_max_cm2_m)} cm²/m</span>
                        </div>
                        <div className="flex justify-between text-sm">
                           <span className="font-medium">Asy:</span>
                           <span className="font-bold text-apple-blue">{formatNumberBR(flexure.Asy_bottom_adot_max_cm2_m)} cm²/m</span>
                        </div>
                        <p className="text-[10px] text-apple-muted mt-2 italic">* Sugestão: {flexure.sugestao_x_inf}</p>
                     </div>
                  </div>
               </div>
            </section>

            {/* Seção 5: Verificação de Punção */}
            <section className="mb-12">
               <div className="flex items-center gap-2 mb-4">
                  <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">05</span>
                  <h2 className="text-lg font-black text-apple-text">VERIFICAÇÃO DE PUNÇÃO (NBR 6118)</h2>
               </div>
               {punching.status === 'nao_aplicavel_sem_pilares' ? (
                  <div className="p-4 rounded-apple-inner bg-apple-bg/30 border border-black/5 text-sm text-apple-muted italic">
                     Não aplicável para carregamento uniforme sem pilares/cargas concentradas.
                  </div>
               ) : (
                  <div className="overflow-hidden rounded-apple-inner border border-black/5">
                     <table className="w-full text-sm text-left">
                        <thead className="bg-apple-bg/50 font-bold text-apple-muted">
                           <tr>
                              <th className="px-4 py-3">Pilar Crítico</th>
                              <th className="px-4 py-3">Tensão de Projeto (τsd)</th>
                              <th className="px-4 py-3">Resistência (τrd1)</th>
                              <th className="px-4 py-3">Ratio (η)</th>
                              <th className="px-4 py-3">Status</th>
                           </tr>
                        </thead>
                        <tbody className="divide-y divide-black/5">
                           <tr>
                              <td className="px-4 py-3 font-medium">{punching.critical_local || 'N/D'}</td>
                              <td className="px-4 py-3">{formatNumberBR(punching.tau_sd)} MPa</td>
                              <td className="px-4 py-3">{formatNumberBR(punching.tau_rd1)} MPa</td>
                              <td className="px-4 py-3 font-bold">{formatNumberBR(punching.ratio_max)}</td>
                              <td className="px-4 py-3"><StatusLabel ok={punching.atende} /></td>
                           </tr>
                        </tbody>
                     </table>
                  </div>
               )}
            </section>

            {/* Seção 6: Comparativo Metodológico */}
            {!isLaje && (
               <section className="mb-12">
                  <div className="flex items-center gap-2 mb-4">
                     <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">06</span>
                     <h2 className="text-lg font-black text-apple-text">COMPARATIVO METODOLÓGICO (MEF vs ANALÍTICO)</h2>
                  </div>
                  <div className="grid grid-cols-2 gap-8">
                     <div>
                        <h4 className="text-[10px] font-black text-apple-muted uppercase mb-3">Pressões de Contato (kPa)</h4>
                        <div className="space-y-2 text-sm">
                           <div className="flex justify-between border-b border-apple-bg pb-1">
                              <span>MEF (Winkler):</span>
                              <span className="font-bold">{formatNumberBR(geotech.pressao_max_modelo_kPa)}</span>
                           </div>
                           <div className="flex justify-between border-b border-apple-bg pb-1">
                              <span>Analítico (Rígido):</span>
                              <span className="font-bold">{formatNumberBR(memorial.comparativo_metodologias?.analytical?.q_max_kPa)}</span>
                           </div>
                           <div className="flex justify-between text-apple-muted text-[11px]">
                              <span>Divergência:</span>
                              <span>{formatNumberBR(Math.abs((memorial.comparativo_metodologias?.divergence_metrics?.q_max_diff_pct || 0) * 100), 1)}%</span>
                           </div>
                        </div>
                     </div>
                     <div className="p-4 rounded-apple-inner bg-apple-blue/5 border border-apple-blue/10">
                        <p className="text-[11px] text-apple-muted leading-relaxed">
                           <Info className="inline-block h-3 w-3 mr-1 mb-0.5" />
                           A divergência entre modelos indica o grau de rigidez relativa da placa. Valores MEF superiores ao analítico sugerem concentrações de tensão sob os apoios.
                        </p>
                     </div>
                  </div>
               </section>
            )}

            {/* Seção 7: Checklist Normativo Detalhado */}
            <section className="mb-12 page-break-before">
               <div className="flex items-center gap-2 mb-4">
                  <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">07</span>
                  <h2 className="text-lg font-black text-apple-text">CHECKLIST DE CONFORMIDADE NORMATIVA</h2>
               </div>
               <div className="space-y-3">
                  {memorial.base_normativa?.checklist_detalhado?.map((item: any, idx: number) => (
                     <div key={idx} className="flex items-center justify-between p-3 rounded-xl border border-black/5 bg-apple-bg/10">
                        <div className="flex items-center gap-3">
                           {item.status === 'ATENDE' ? (
                              <CheckCircle2 className="h-5 w-5 text-apple-green" />
                           ) : (
                              <AlertTriangle className="h-5 w-5 text-apple-red" />
                           )}
                           <div>
                              <p className="text-sm font-bold text-apple-text">{item.theme}</p>
                              <p className="text-[10px] text-apple-muted font-medium">{item.reference}</p>
                           </div>
                        </div>
                        <div className="text-right">
                           <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${item.status === 'ATENDE' ? 'bg-apple-green/10 text-apple-green' : 'bg-apple-red/10 text-apple-red'}`}>
                              {item.status}
                           </span>
                        </div>
                     </div>
                  ))}
               </div>
            </section>

            {/* Seção 8: Memória de Cálculo e Formulações */}
            <section className="mb-12 page-break-before">
               <div className="flex items-center gap-2 mb-6">
                  <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">08</span>
                  <h2 className="text-lg font-black text-apple-text tracking-tight">MEMÓRIA DE CÁLCULO E FORMULAÇÕES</h2>
               </div>

               <div className="space-y-8">
                  {/* Materiais e Ações */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                     <div className="p-4 rounded-apple-inner bg-apple-bg/20 border border-black/5">
                        <h4 className="text-[10px] font-black text-apple-muted uppercase mb-3">Majoração de Ações (ELU)</h4>
                        <div className="font-serif italic text-sm space-y-1">
                           <p>F<sub>d</sub> = F<sub>k</sub> · γ<sub>f</sub></p>
                           <p>γ<sub>f</sub> = 1.40 (Combinação Normal)</p>
                        </div>
                     </div>
                     <div className="p-4 rounded-apple-inner bg-apple-bg/20 border border-black/5">
                        <h4 className="text-[10px] font-black text-apple-muted uppercase mb-3">Resistência do Concreto</h4>
                        <div className="font-serif italic text-sm space-y-1">
                           <p>f<sub>cd</sub> = f<sub>ck</sub> / γ<sub>c</sub></p>
                           <p>γ<sub>c</sub> = 1.40</p>
                        </div>
                     </div>
                     <div className="p-4 rounded-apple-inner bg-apple-bg/20 border border-black/5">
                        <h4 className="text-[10px] font-black text-apple-muted uppercase mb-3">Resistência do Aço</h4>
                        <div className="font-serif italic text-sm space-y-1">
                           <p>f<sub>yd</sub> = f<sub>yk</sub> / γ<sub>s</sub></p>
                           <p>γ<sub>s</sub> = 1.15</p>
                        </div>
                     </div>
                  </div>

                  {/* Flexão e Punção */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                     <div className="p-6 rounded-apple-inner bg-white border border-black/5 shadow-sm">
                        <h4 className="text-xs font-black text-apple-text uppercase mb-6 border-b border-black/5 pb-2">Dimensionamento à Flexão</h4>
                        <div className="space-y-6 font-serif italic text-apple-text/90">
                           <div className="flex items-center gap-4">
                              <span className="text-base">d = h - c - ϕ/2</span>
                              <span className="text-[10px] font-sans not-italic text-apple-muted">(Altura útil da seção)</span>
                           </div>

                           <div className="flex items-center gap-3">
                              <span className="text-lg">A<sub>s</sub> = </span>
                              <div className="flex flex-col items-center">
                                 <span className="px-2 border-b border-black/40">M<sub>sd</sub></span>
                                 <span className="px-2">0.8 · d · f<sub>yd</sub></span>
                              </div>
                           </div>

                           <div className="not-italic font-sans text-[10px] text-apple-muted space-y-1 pt-4 border-t border-black/5">
                              <p>• Aplicação do critério de Wood-Armer para momentos M<sub>x</sub>, M<sub>y</sub> e M<sub>xy</sub>.</p>
                              <p>• Taxa mínima de armadura ρ<sub>min</sub> conforme Tabela 17.3 da NBR 6118.</p>
                           </div>
                        </div>
                     </div>

                     <div className="p-6 rounded-apple-inner bg-white border border-black/5 shadow-sm">
                        <h4 className="text-xs font-black text-apple-text uppercase mb-6 border-b border-black/5 pb-2">Verificação de Punção (ELU)</h4>
                        <div className="space-y-6 font-serif italic text-apple-text/90">
                           <div className="flex items-center gap-3">
                              <span className="text-lg">τ<sub>sd</sub> = </span>
                              <div className="flex flex-col items-center">
                                 <span className="px-2 border-b border-black/40">F<sub>sd</sub> · β</span>
                                 <span className="px-2">u · d</span>
                              </div>
                           </div>

                           <div className="flex items-center gap-3">
                              <span className="text-lg">τ<sub>rd1</sub> = </span>
                              <span className="text-base">0.12 · k · (100 · ρ · f<sub>ck</sub>)<sup>1/3</sup></span>
                           </div>

                           <div className="not-italic font-sans text-[10px] text-apple-muted space-y-1 pt-4 border-t border-black/5">
                              <p>• Perímetro crítico <strong>u</strong> a uma distância de 2d da face do pilar.</p>
                              <p>• Fator <strong>β</strong> considera a excentricidade de carga (momentos fletores).</p>
                           </div>
                        </div>
                     </div>
                  </div>

                  {/* Solo */}
                  {!isLaje && (
                     <div className="p-6 rounded-apple-inner bg-apple-bg/10 border border-black/5">
                        <h4 className="text-xs font-black text-apple-text uppercase mb-4 text-center">Interação Solo-Estrutura (Winkler)</h4>
                        <div className="flex flex-col items-center justify-center space-y-4">
                           <p className="font-serif italic text-2xl text-apple-blue">σ(x,y) = k<sub>v</sub> · w(x,y)</p>
                           <div className="max-w-md text-center text-[10px] text-apple-muted leading-relaxed">
                              <p>A solução numérica é obtida via Método dos Elementos Finitos (MEF) utilizando elementos de placa de Mindlin-Reissner, garantindo a compatibilidade de deformações entre o radier e o solo elástico.</p>
                           </div>
                        </div>
                     </div>
                  )}
               </div>
            </section>

            {/* Seção 9: Trilha de Auditoria Numérica */}
            <section className="mb-12 page-break-before">
               <div className="flex items-center gap-2 mb-6">
                  <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">09</span>
                  <h2 className="text-lg font-black text-apple-text tracking-tight uppercase">Trilha de Auditoria Numérica</h2>
               </div>

               {memorial.trilha_auditoria_numérica ? (
                  <div className="space-y-6">
                     <PedagogicalStepsView blackboard={memorial.trilha_auditoria_numérica} />
                     <div className="p-6 rounded-2xl bg-red-600/5 border border-red-600/20 italic">
                        <p className="text-xs font-black text-red-700 mb-2 uppercase tracking-tighter">Parecer de Auditoria Forense:</p>
                        <p className="text-sm font-bold text-apple-text leading-relaxed">"{memorial.parecer_tecnico_mestre}"</p>
                     </div>
                  </div>
               ) : (
                  <>
                     <p className="text-[11px] text-apple-muted mb-6 italic">Valores reais do projeto substituídos nas formulações normativas — rastreabilidade completa para auditoria técnica.</p>
                     <div className="space-y-6">
                        {(() => {
                           const L_x = memorial.dados_da_obra?.dimensoes_m?.Lx ?? results.master?.Lx ?? 0;
                           const L_y = memorial.dados_da_obra?.dimensoes_m?.Ly ?? results.master?.Ly ?? 0;
                           const n_x = memorial.dados_da_obra?.malha?.nx ?? results.master?.nx ?? 0;
                           const n_y = memorial.dados_da_obra?.malha?.ny ?? results.master?.ny ?? 0;
                           const area = memorial.dados_da_obra?.area_radier_m2 ?? (L_x * L_y);
                           const elements = (n_x > 0 && n_y > 0) ? (n_x - 1) * (n_y - 1) : 0;
                           const nodes = n_x * n_y;
                           return (
                              <div className="p-5 rounded-apple-inner bg-apple-bg/5 border border-black/5">
                                 <h4 className="text-[10px] font-black text-apple-muted uppercase mb-4">Passo 01: Geometria e Matriz do Modelo (MEF)</h4>
                                 <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm font-serif italic">
                                    <div className="space-y-2">
                                       <p>L<sub>x</sub> = <span className="font-bold text-apple-text">{formatNumberBR(L_x)} m</span></p>
                                       <p>L<sub>y</sub> = <span className="font-bold text-apple-text">{formatNumberBR(L_y)} m</span></p>
                                       <p>Área (A) = <span className="font-bold text-apple-text">{formatNumberBR(area)} m²</span></p>
                                    </div>
                                    <div className="space-y-2">
                                       <p>Malha = <span className="font-bold text-apple-text">{n_x} × {n_y} nós</span> ({nodes} nós totais)</p>
                                       <p>Elementos Finitos = <span className="font-bold text-apple-text">{elements} elementos</span></p>
                                       <p className="text-[10px] font-sans not-italic text-apple-muted pt-1">Formulação: Placa Mindlin-Reissner (3 GL/nó)</p>
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
                              <div className="p-5 rounded-apple-inner bg-apple-bg/5 border border-black/5">
                                 <h4 className="text-[10px] font-black text-apple-muted uppercase mb-4">
                                    {isLaje ? "Passo 02: Parâmetros dos Materiais" : "Passo 02: Parâmetros dos Materiais e Solo"}
                                 </h4>
                                 <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-sm font-serif italic mb-6">
                                    <div className="space-y-2">
                                       <p>f<sub>ck</sub> = <span className="font-bold text-apple-text">{formatNumberBR(fck, 0)} MPa</span></p>
                                       <p>E<sub>cs</sub> = <span className="font-bold text-apple-text">{formatNumberBR(E_GPa, 1)} GPa</span></p>
                                       <p>ν = <span className="font-bold text-apple-text">{formatNumberBR(nu)}</span></p>
                                    </div>
                                    <div className="space-y-2">
                                       <p>Espessura (h) = <span className="font-bold text-apple-text">{formatNumberBR(h_m * 100, 1)} cm</span></p>
                                       {!isLaje && (
                                          <>
                                             <p>Módulo de Mola (k<sub>v</sub>) = <span className="font-bold text-apple-text">{formatNumberBR(kv_MN_m3, 1)} MN/m³</span></p>
                                             <p>Tensão Adm. (σ<sub>adm</sub>) = <span className="font-bold text-apple-text">{formatNumberBR(sigma_adm, 1)} kPa</span></p>
                                          </>
                                       )}
                                    </div>
                                 </div>
                                 <div className="border-t border-black/5 pt-4 text-sm font-serif italic flex items-center gap-2">
                                    <span className="whitespace-nowrap">Rigidez à Flexão (D) = </span>
                                    <div className="flex flex-col items-center">
                                       <span className="border-b border-black px-2">E<sub>cs</sub> · h³</span>
                                       <span className="px-2">12 · (1 − ν²)</span>
                                    </div>
                                    <span> = <span className="font-bold text-apple-blue">{formatNumberBR(D_MNm)} MN·m</span></span>
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
                              <div className="p-5 rounded-apple-inner bg-apple-bg/5 border border-black/5">
                                 <h4 className="text-[10px] font-black text-apple-muted uppercase mb-4">Passo 03: Carregamentos e Equilíbrio Global (Solver)</h4>
                                 <div className="space-y-4 font-serif italic text-sm">
                                    <p>Carga Distribuída (q) = <span className="font-bold">{formatNumberBR(q_kPa)} kPa</span></p>
                                    <p>Σ Cargas Concentradas (Pilares) = <span className="font-bold">{formatNumberBR(P_kN)} kN</span></p>
                                    <p>Carga Total Vertical (F<sub>ext</sub>) = <span className="font-bold">{formatNumberBR(F_total)} kN</span></p>

                                    <div className="bg-white/50 p-3 rounded mt-4 text-xs">
                                       <p className="font-sans not-italic font-bold mb-1">Resolução do Sistema: [K] {`{U}`} = {`{F}`}</p>
                                       <div className="flex items-center gap-2">
                                          <span>Resíduo Numérico = {residual.toExponential(3)}</span>
                                          <span className={`px-2 py-0.5 rounded text-[9px] font-black ${atendeEquilibrio ? 'bg-apple-green/10 text-apple-green' : 'bg-apple-red/10 text-apple-red'}`}>
                                             {atendeEquilibrio ? 'CONVERGIU' : 'DIVERGIU'}
                                          </span>
                                       </div>
                                    </div>
                                 </div>
                              </div>
                           );
                        })()}

                        {/* Passo 04: Reações do Solo e Verificação Geotécnica */}
                        {!isLaje && ((() => {
                           const qmax = geotech.pressao_max_modelo_kPa;
                           const qmed = geotech.pressao_media_kPa;
                           const sigma = geotech.tensao_admissivel_kPa;
                           return (
                              <div className="p-5 rounded-apple-inner bg-apple-bg/5 border border-black/5">
                                 <h4 className="text-[10px] font-black text-apple-muted uppercase mb-4">Passo 04: Reações do Solo e Verificação Geotécnica</h4>
                                 <div className="space-y-4 font-serif italic text-sm">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                       <div className="space-y-3">
                                          <p>σ<sub>méd</sub> = Σ F<sub>ext</sub> / A = <span className="font-bold">{formatNumberBR(qmed) ?? 'N/D'} kPa</span></p>
                                          <p>σ<sub>máx</sub> = max(k<sub>v</sub> · w) = <span className="font-bold">{formatNumberBR(qmax) ?? 'N/D'} kPa</span></p>
                                       </div>
                                       <div className="space-y-3">
                                          <p>σ<sub>adm</sub> = <span className="font-bold">{formatNumberBR(sigma) ?? 'N/D'} kPa</span></p>
                                          <div className="flex items-center gap-2 pt-2 border-t border-black/10">
                                             <span className="not-italic font-sans font-black text-[10px]">VERIFICAÇÃO:</span>
                                             <span className="font-bold text-xs">{formatNumberBR(qmax)} ≤ {formatNumberBR(sigma)}</span>
                                             <span className={`ml-2 px-2 py-0.5 rounded text-[9px] font-black ${geotech.atende_pressao_max_modelo ? 'bg-apple-green/10 text-apple-green' : 'bg-apple-red/10 text-apple-red'}`}>
                                                {geotech.atende_pressao_max_modelo ? 'OK' : 'FALHA'}
                                             </span>
                                          </div>
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
                              <div className="p-5 rounded-apple-inner bg-apple-bg/5 border border-black/5">
                                 <h4 className="text-[10px] font-black text-apple-muted uppercase mb-4">Passo 05: Esforços Internos Analíticos (Momentos)</h4>
                                 <div className="space-y-4 font-serif italic text-sm">
                                    <p>
                                       M<sub>x</sub> = −D · (∂²w/∂x² + ν·∂²w/∂y²) = <span className="font-bold">{isNearZero ? '≈ 0.00' : (mx?.toFixed(2) ?? 'N/D')} kNm/m</span>
                                    </p>
                                    <p>
                                       M<sub>y</sub> = −D · (∂²w/∂y² + ν·∂²w/∂x²) = <span className="font-bold">{isNearZero ? '≈ 0.00' : (my?.toFixed(2) ?? 'N/D')} kNm/m</span>
                                    </p>
                                    {isNearZero && (
                                       <div className="bg-apple-blue/5 p-3 mt-4 rounded border border-apple-blue/10">
                                          <p className="text-apple-blue text-xs font-sans not-italic">
                                             <strong>Flexão Teórica Nula:</strong> O modelo está submetido apenas a cargas uniformes e apresenta recalque rígido (curvatura plana).
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
                              <div className="p-5 rounded-apple-inner bg-apple-bg/5 border border-black/5">
                                 <h4 className="text-[10px] font-black text-apple-muted uppercase mb-4">Passo 06: Dimensionamento à Flexão Crítico (ELU)</h4>
                                 <div className="space-y-4 font-serif italic text-sm">
                                    <p>
                                       M<sub>k,máx</sub> = max(|M<sub>x</sub>|, |M<sub>y</sub>|) = <span className="font-bold">{isNearZero ? '≈ 0.0000' : (mk?.toFixed(4) ?? 'N/D')} kNm/m</span>
                                    </p>
                                    <p>
                                       M<sub>sd</sub> = M<sub>k,máx</sub> · γ<sub>f</sub> = <span className="font-bold">{isNearZero ? '≈ 0.0000' : (msd?.toFixed(4) ?? 'N/D')} kNm/m</span>
                                    </p>

                                    <div className="flex items-center gap-3 py-2">
                                       <span>A<sub>s,calc</sub> = </span>
                                       <div className="flex flex-col items-center">
                                          <span className="px-3 border-b border-black">M<sub>sd</sub></span>
                                          <span className="px-3">0.8 · d · f<sub>yd</sub></span>
                                       </div>
                                       <span> = </span>
                                       <span className="font-bold text-lg text-apple-blue">{isNearZero ? '≈ 0.0000' : (as_calc?.toFixed(4) ?? 'N/D')} cm²/m</span>
                                    </div>

                                    <div className="bg-white/50 p-4 rounded mt-4 text-[11px] not-italic font-sans space-y-2">
                                       <div className="flex justify-between items-center border-b border-black/10 pb-2">
                                          <span>A<sub>s,mínima</sub> (Normativa por face):</span>
                                          <strong>{formatNumberBR(as_min)} cm²/m</strong>
                                       </div>
                                       <div className="flex justify-between items-center pt-1">
                                          <span>A<sub>s,adotada</sub> (Máxima na seção crítica):</span>
                                          <strong className="text-apple-blue text-sm">{formatNumberBR(as_adopted)} cm²/m</strong>
                                       </div>
                                    </div>
                                 </div>
                              </div>
                           );
                        })()}

                        {/* Passo 07: Verificação de Punção (Se aplicável) */}
                        {punching.status !== 'nao_aplicavel_sem_pilares' && (
                           <div className="p-5 rounded-apple-inner bg-apple-bg/5 border border-black/5">
                              <h4 className="text-[10px] font-black text-apple-muted uppercase mb-4">Passo 07: Verificação de Punção no Pilar Crítico (ELU)</h4>
                              <div className="space-y-4 font-serif italic text-sm">
                                 <p>F<sub>sd</sub> = F<sub>k</sub> · γ<sub>f</sub> = <span className="font-bold">{formatNumberBR(punching.Ved_kN, 1) ?? 'N/D'} kN</span></p>
                                 <p>Perímetro (u₁) = <span className="font-bold">{formatNumberBR(punching.u) ?? 'N/D'} m</span></p>

                                 <p className="pt-2">τ<sub>sd</sub> = (F<sub>sd</sub> · β) / (u₁ · d) = <span className="font-bold">{formatNumberBR(punching.tau_sd, 3) ?? 'N/D'} MPa</span></p>
                                 <p>τ<sub>Rd1</sub> = 0.12 · k · (100 · ρ · f<sub>ck</sub>)<sup>1/3</sup> = <span className="font-bold">{formatNumberBR(punching.tau_rd1, 3) ?? 'N/D'} MPa</span></p>

                                 <div className="flex items-center gap-2 pt-4 border-t border-black/10">
                                    <span className="not-italic font-sans font-black text-[10px]">VERIFICAÇÃO CORTANTE:</span>
                                    <span className="font-bold text-xs">{formatNumberBR(punching.tau_sd, 3)} ≤ {formatNumberBR(punching.tau_rd1, 3)}</span>
                                    <span className={`ml-4 px-2 py-0.5 rounded text-[9px] font-black ${punching.atende ? 'bg-apple-green/10 text-apple-green' : 'bg-apple-red/10 text-apple-red'}`}>
                                       {punching.atende ? 'OK' : 'FALHA (REQUER ARMADURA)'}
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
                           const wk_ok = service.wk_x_ok && service.wk_y_ok;
                           return (
                              <div className="p-5 rounded-apple-inner bg-apple-bg/5 border border-black/5">
                                 <h4 className="text-[10px] font-black text-apple-muted uppercase mb-4">Passo 08: Estados Limites de Serviço (ELS)</h4>

                                 <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-sm font-serif italic">
                                    <div className="space-y-4">
                                       <h5 className="text-[10px] font-sans font-bold not-italic border-b border-black/10 pb-1">Recalques e Deformações</h5>
                                       <div className="space-y-2">
                                          <p>w<sub>máx</sub> = <span className="font-bold text-apple-text">{formatNumberBR(wmax)} mm</span> <span className="text-[10px] font-sans not-italic text-apple-muted">(Lim: 50mm)</span></p>
                                          <p>Δw (Diferencial) = <span className="font-bold text-apple-text">{formatNumberBR(wdiff)} mm</span> <span className="text-[10px] font-sans not-italic text-apple-muted">(Lim: 25mm)</span></p>
                                       </div>
                                    </div>

                                    <div className="space-y-4">
                                       <h5 className="text-[10px] font-sans font-bold not-italic border-b border-black/10 pb-1">Fissuração (w<sub>k</sub>)</h5>
                                       <div className="space-y-2">
                                          <p>w<sub>k,x</sub> = <span className="font-bold text-apple-text">{formatNumberBR(wk_x)} mm</span></p>
                                          <p>w<sub>k,y</sub> = <span className="font-bold text-apple-text">{formatNumberBR(wk_y)} mm</span></p>
                                          <p>w<sub>limite</sub> = <span className="font-bold text-apple-text">{formatNumberBR(wk_limit)} mm</span></p>
                                          <div className="pt-1">
                                             <span className={`px-2 py-0.5 rounded text-[9px] font-sans font-black ${wk_ok ? 'bg-apple-green/10 text-apple-green' : 'bg-apple-red/10 text-apple-red'}`}>
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
                      <div className="mt-16 pt-12 border-t border-apple-bg/5 page-break-before">
                         <ISETheoryView />
                      </div>
                  </>
               )}
            </section>

            {/* Seção 10: Visualização 3D (Apenas Lajes ou se houver malha) */}
            {
               (isLaje || results.mesh) && (
                  <section className="mb-12 page-break-before">
                     <div className="flex items-center gap-2 mb-6">
                        <span className="bg-apple-blue text-white text-[10px] font-black px-1.5 py-0.5 rounded">10</span>
                        <h2 className="text-lg font-black text-apple-text tracking-tight uppercase">Visualização Estrutural 3D</h2>
                     </div>
                     <p className="text-[11px] text-apple-muted mb-6 italic">Modelo tridimensional da laje com amplificação dos deslocamentos para análise de rigidez e comportamento estrutural.</p>
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

            {/* Seção 11: Mapa de Pressões no Solo */}
            {
               !isLaje && (
                  <section className="mb-12 page-break-before">
                     <div className="flex items-center gap-2 mb-6">
                        <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">11</span>
                        <h2 className="text-lg font-black text-apple-text tracking-tight uppercase">Mapa de Pressões de Contato Solo-Radier</h2>
                     </div>
                     <p className="text-[11px] text-apple-muted mb-6 italic">Distribuição estimada de pressões de contato com indicação de posição dos pilares. Gradiente verde (baixa pressão) → vermelho (pressão máxima).</p>
                     <SoilPressureMap
                        Lx={results.master?.Lx ?? 10}
                        Ly={results.master?.Ly ?? 10}
                        qmax={geotech.pressao_max_modelo_kPa ?? 0}
                        qmed={geotech.pressao_media_kPa ?? 0}
                        sigma_adm={geotech.tensao_admissivel_kPa ?? 200}
                        pillars={(results.memorial?.acoes_e_combinacoes?.pilares_considerados ?? []).map((p: any) => ({
                           id: p.id ?? 'P',
                           x: p.x ?? 0,
                           y: p.y ?? 0,
                           p_kN: p.p_kN ?? 0,
                        }))}
                     />

                     {/* Faixas regionais de armadura */}
                     {results.regional_reinforcement?.zones && (
                        <div className="mt-6">
                           <h4 className="text-[10px] font-black text-apple-muted uppercase tracking-wide mb-3">Armadura por Faixas Regionais (cm²/m)</h4>
                           <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                              {Object.entries(results.regional_reinforcement.zones as Record<string, any>).map(([zone, data]: [string, any]) => (
                                 <div key={zone} className="p-3 rounded-apple-inner bg-apple-bg/20 border border-black/5">
                                    <p className="text-[10px] font-black text-apple-muted uppercase mb-2">{zone.replace(/_/g, ' ')}</p>
                                    <div className="space-y-1 text-xs">
                                       <div className="flex justify-between">
                                          <span>Asx:</span><span className="font-bold text-apple-blue">{formatNumberBR(data.Asx_cm2_m)} cm²/m</span>
                                       </div>
                                       <div className="flex justify-between">
                                          <span>Asy:</span><span className="font-bold text-apple-blue">{formatNumberBR(data.Asy_cm2_m)} cm²/m</span>
                                       </div>
                                       <p className="text-[10px] text-apple-muted mt-1 italic">{data.sugestao_x}</p>
                                    </div>
                                 </div>
                              ))}
                           </div>
                           {results.regional_reinforcement.requer_reforco_local && (
                              <div className="mt-3 flex items-center gap-2 p-3 rounded-xl bg-yellow-50 border border-yellow-200 text-xs text-yellow-700 font-medium">
                                 <AlertTriangle className="h-4 w-4 shrink-0" />
                                 <span>Reforço local recomendado nas faixas sobre pilares (pico &gt; 1.5× pano central).</span>
                              </div>
                           )}
                           <p className="text-[10px] text-apple-muted mt-2 italic">{results.regional_reinforcement.nota}</p>
                        </div>
                     )}
                  </section>
               )
            }

            {/* Seção 12: Comparador de Soluções */}
            {
               !isLaje && (
                  <section className="mb-12">
                     <div className="flex items-center gap-2 mb-6">
                        <span className="bg-apple-text text-white text-[10px] font-black px-1.5 py-0.5 rounded">12</span>
                        <h2 className="text-lg font-black text-apple-text tracking-tight uppercase">Comparador de Soluções de Fundação</h2>
                     </div>
                     <p className="text-[11px] text-apple-muted mb-4 italic">Avaliação qualitativa orientativa das soluções disponíveis. Somente o Radier Liso está implementado e calculado neste módulo.</p>
                     {results.solution_comparison?.solutions ? (
                        <SolutionComparator
                           solutions={results.solution_comparison.solutions}
                           nota={results.solution_comparison.nota}
                        />
                     ) : (
                        <p className="text-[11px] text-apple-muted italic">Execute a análise para visualizar o comparativo.</p>
                     )}
                  </section>
               )
            }

            {/* Seção 13: Checklist de Concreto Massa */}
            {
               results.thermal_checklist?.applicable && !isLaje && (
                  <section className="mb-12">
                     <div className="flex items-center gap-2 mb-6">
                        <span className="bg-orange-500 text-white text-[10px] font-black px-1.5 py-0.5 rounded">13</span>
                        <h2 className="text-lg font-black text-apple-text tracking-tight uppercase">Checklist de Concreto Massa</h2>
                        <span className="ml-2 text-[10px] font-black px-2 py-0.5 rounded-full bg-orange-100 text-orange-600 border border-orange-200">
                           h = {formatNumberBR(results.thermal_checklist.h_adopted_m)} m ≥ {formatNumberBR(results.thermal_checklist.threshold_m)} m
                        </span>
                     </div>
                     <p className="text-[11px] text-apple-muted mb-4">{results.thermal_checklist.nota}</p>
                     <div className="space-y-2">
                        {results.thermal_checklist.items?.map((item: any) => (
                           <div key={item.id} className="flex items-center justify-between p-3 rounded-xl border border-orange-100 bg-orange-50/40">
                              <div className="flex items-center gap-3">
                                 <AlertTriangle className={`h-4 w-4 shrink-0 ${item.priority === 'alta' ? 'text-orange-500' : 'text-yellow-500'}`} />
                                 <p className="text-sm font-medium text-apple-text">{item.description}</p>
                              </div>
                              <span className={`text-[10px] font-black px-2 py-0.5 rounded-full shrink-0 ${item.priority === 'alta'
                                 ? 'bg-orange-100 text-orange-600 border border-orange-200'
                                 : 'bg-yellow-100 text-yellow-700 border border-yellow-200'
                                 }`}>
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
                        <span className="bg-indigo-600 text-white text-[10px] font-black px-1.5 py-0.5 rounded">10</span>
                        <h2 className="text-lg font-black text-apple-text tracking-tight uppercase">Dimensionamento do Pórtico 3D (StrucPy)</h2>
                     </div>

                     <div className="space-y-10">
                        {/* Pilares */}
                        <div>
                           <h3 className="text-xs font-black text-apple-muted uppercase tracking-widest mb-4 flex items-center gap-2">
                              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                              Dimensionamento de Pilares
                           </h3>
                           <div className="overflow-hidden rounded-apple-inner border border-black/5">
                              <table className="w-full text-[11px] text-left">
                                 <thead className="bg-apple-bg/50 font-black text-apple-muted uppercase text-[9px] tracking-widest">
                                    <tr>
                                       <th className="px-4 py-3">Pilar</th>
                                       <th className="px-4 py-3">Seção (cm)</th>
                                       <th className="px-4 py-3 text-right">Nd (kN)</th>
                                       <th className="px-4 py-3 text-right">As (cm²)</th>
                                       <th className="px-4 py-3 text-right">Taxa (%)</th>
                                    </tr>
                                 </thead>
                                 <tbody className="divide-y divide-black/5">
                                    {frameResults.design_results?.pillars?.map((p: any) => (
                                       <tr key={p.id} className="hover:bg-indigo-50/30 transition-colors">
                                          <td className="px-4 py-3 font-bold text-apple-text">{p.id}</td>
                                          <td className="px-4 py-3 font-mono">{(p.b * 100).toFixed(0)}x{(p.h * 100).toFixed(0)}</td>
                                          <td className="px-4 py-3 text-right font-mono text-apple-blue">{formatNumberBR(p.Nd, 1)}</td>
                                          <td className="px-4 py-3 text-right font-bold text-indigo-600">{formatNumberBR(p.As)}</td>
                                          <td className="px-4 py-3 text-right font-mono text-apple-muted">{formatNumberBR(((p.As / (p.b * p.h * 10000)) * 100))}%</td>
                                       </tr>
                                    ))}
                                 </tbody>
                              </table>
                           </div>
                        </div>

                        {/* Vigas */}
                        <div>
                           <h3 className="text-xs font-black text-apple-muted uppercase tracking-widest mb-4 flex items-center gap-2">
                              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                              Dimensionamento de Vigas
                           </h3>
                           <div className="overflow-hidden rounded-apple-inner border border-black/5">
                              <table className="w-full text-[11px] text-left">
                                 <thead className="bg-apple-bg/50 font-black text-apple-muted uppercase text-[9px] tracking-widest">
                                    <tr>
                                       <th className="px-4 py-3">Viga</th>
                                       <th className="px-4 py-3">Seção (cm)</th>
                                       <th className="px-4 py-3 text-right">Mk (kNm)</th>
                                       <th className="px-4 py-3 text-right">As Inf (cm²)</th>
                                       <th className="px-4 py-3 text-right">As Sup (cm²)</th>
                                    </tr>
                                 </thead>
                                 <tbody className="divide-y divide-black/5">
                                    {frameResults.design_results?.beams?.map((b: any) => (
                                       <tr key={b.id} className="hover:bg-indigo-50/30 transition-colors">
                                          <td className="px-4 py-3 font-bold text-apple-text">{b.id}</td>
                                          <td className="px-4 py-3 font-mono">{(b.b * 100).toFixed(0)}x{(b.h * 100).toFixed(0)}</td>
                                          <td className="px-4 py-3 text-right font-mono text-apple-blue">{formatNumberBR(b.max_moment, 1)}</td>
                                          <td className="px-4 py-3 text-right font-bold text-indigo-600">{formatNumberBR(b.As_bottom)}</td>
                                          <td className="px-4 py-3 text-right font-bold text-apple-muted">{formatNumberBR(b.As_top)}</td>
                                       </tr>
                                    ))}
                                 </tbody>
                              </table>
                           </div>
                        </div>

                        <div className="bg-indigo-50/50 p-4 rounded-xl border border-indigo-100 flex items-start gap-3">
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
                  <section className="mt-12 pt-12 border-t border-black/10 break-before-page">
                     <div className="flex items-center gap-2 mb-8">
                        <span className="bg-apple-blue text-white text-[10px] font-black px-1.5 py-0.5 rounded">M4</span>
                        <h2 className="text-lg font-black text-apple-text tracking-tight uppercase">Memorial Técnico Padronizado</h2>
                     </div>
                     <div className="prose prose-sm max-w-none prose-headings:font-black prose-headings:text-apple-text prose-p:text-apple-muted prose-strong:text-apple-text">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                           {results.memorial_markdown || memorial.standard_markdown}
                        </ReactMarkdown>
                     </div>
                  </section>
               )
            }

            {/* Rodapé do Memorial */}
            <div className="mt-20 pt-8 border-t border-apple-bg flex justify-between items-end opacity-50 text-[9px] font-bold uppercase tracking-widest">
               <div>MEF STRUCTURAL SUITE - Structural Intelligence | Audit v24.4.1</div>
               <div>Desenvolvido por VibeDoCode</div>
            </div>

         </div >
      </div >
   );
}

function ReportMetric({ label, value, unit, sub }: { label: string; value: string; unit?: string; sub?: string }) {
   return (
      <div className="border-l-2 border-apple-blue/20 pl-4">
         <p className="text-[10px] font-black text-apple-muted uppercase tracking-wider">{label}</p>
         <p className="mt-1 text-xl font-black text-apple-text">
            {value} <span className="text-sm font-medium">{unit}</span>
         </p>
         {sub && <p className="mt-1 text-[11px] font-medium text-apple-muted">{sub}</p>}
      </div>
   );
}

function StatusLabel({ ok }: { ok: boolean | null }) {
   if (ok === null) return <span className="text-apple-muted">N/D</span>;
   return (
      <span className={`font-bold ${ok ? "text-apple-green" : "text-apple-red"}`}>
         {ok ? "ATENDE" : "NÃO ATENDE"}
      </span>
   );
}
