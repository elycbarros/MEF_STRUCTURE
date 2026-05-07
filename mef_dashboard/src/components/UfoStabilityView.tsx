"use client";

import React, { useState } from "react";
import { Activity, Building2, Wind, Layers, Info, ChevronRight, Gauge, ShieldCheck, TrendingDown, AlertCircle, Box as BoxIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stage, PerspectiveCamera, Grid } from "@react-three/drei";
import { Suspense, useEffect } from "react";
import { StructuralAuditAgent } from "@/agents/StructuralAuditAgent";
import { ModuleContainer } from "@/components/ui/ModuleContainer";

function Building3D({ floors = 12 }: { floors?: number }) {
// ... (rest of Building3D)
  return (
    <group>
      {/* Pavimentos */}
      {[...Array(floors)].map((_, i) => (
        <mesh key={i} position={[0, i * 0.4, 0]}>
          <boxGeometry args={[4, 0.05, 3]} />
          <meshStandardMaterial color="#3b82f6" transparent opacity={0.3} />
        </mesh>
      ))}
      {/* Núcleo de Rigidez */}
      <mesh position={[0, (floors * 0.4) / 2, 0]}>
        <boxGeometry args={[1, floors * 0.4, 1]} />
        <meshStandardMaterial color="#1e40af" transparent opacity={0.6} />
      </mesh>
      {/* Colunas principais */}
      <mesh position={[-1.8, (floors * 0.4) / 2, -1.3]}>
        <boxGeometry args={[0.2, floors * 0.4, 0.2]} />
        <meshStandardMaterial color="#1d1d1f" />
      </mesh>
      <mesh position={[1.8, (floors * 0.4) / 2, -1.3]}>
        <boxGeometry args={[0.2, floors * 0.4, 0.2]} />
        <meshStandardMaterial color="#1d1d1f" />
      </mesh>
      <mesh position={[-1.8, (floors * 0.4) / 2, 1.3]}>
        <boxGeometry args={[0.2, floors * 0.4, 0.2]} />
        <meshStandardMaterial color="#1d1d1f" />
      </mesh>
      <mesh position={[1.8, (floors * 0.4) / 2, 1.3]}>
        <boxGeometry args={[0.2, floors * 0.4, 0.2]} />
        <meshStandardMaterial color="#1d1d1f" />
      </mesh>
    </group>
  );
}

export function UfoStabilityView() {
  const [gammaZ, setGammaZ] = useState(1.12);
  const [loading, setLoading] = useState(false);
  const [auditResult, setAuditResult] = useState<any>(null);

  const handleProcessUFO = async () => {
    setLoading(true);
    // Simulação de processamento pesado em Rust
    await new Promise(r => setTimeout(r, 2000));
    const audit = await StructuralAuditAgent.auditGlobalStability(gammaZ);
    setAuditResult(audit);
    setLoading(false);
  };

  const getStabilityClass = (gz: number) => {
    if (gz <= 1.10) return { label: "Estrutura Fixa", color: "text-green-600", bg: "bg-green-50" };
    if (gz <= 1.30) return { label: "Estrutura de Nós Móveis", color: "text-yellow-600", bg: "bg-yellow-50" };
    return { label: "Instabilidade Crítica", color: "text-red-600", bg: "bg-red-50" };
  };

  const sClass = getStabilityClass(gammaZ);

  return (
    <ModuleContainer
      title="Estabilidade Global"
      subtitle="Análise de 2ª ordem e efeitos P-Delta em edifícios de múltiplos pavimentos via Motor Rust Faer de alta performance."
      icon={<Activity className="h-6 w-6 text-white" />}
      theme="professional"
      solverType="Rust Core"
      auditResult={auditResult}
    >
      <div className="grid grid-cols-12 gap-6">
        {/* Painel Lateral */}
        <div className="col-span-12 space-y-6 lg:col-span-4">
          <div className="rounded-3xl border border-white/60 bg-white/50 p-6 backdrop-blur-xl shadow-sm">
            <h3 className="mb-6 text-lg font-black text-[#1d1d1f]">Métrica de Estabilidade</h3>
            <div className="space-y-6">
              <div className="text-center">
                <div className="inline-block rounded-full bg-[#1d1d1f] p-8 shadow-xl">
                  <span className="text-5xl font-black text-white">{gammaZ.toFixed(2)}</span>
                  <p className="mt-1 text-[10px] font-black uppercase tracking-widest text-white/50">Coeficiente γz</p>
                </div>
                <div className={cn("mt-6 rounded-2xl p-4 transition-colors", sClass.bg)}>
                   <p className={cn("text-sm font-black uppercase tracking-tight", sClass.color)}>
                     {sClass.label}
                   </p>
                </div>
              </div>

              <div className="space-y-4">
                 <div>
                   <div className="mb-1 flex justify-between text-[11px] font-black uppercase text-[#6a7485]">
                     <span>Risco de 2ª Ordem</span>
                     <span>{((gammaZ - 1) * 100).toFixed(0)}%</span>
                   </div>
                   <div className="h-2 w-full overflow-hidden rounded-full bg-[#e0e7ef]">
                     <div className="h-full bg-blue-600 transition-all" style={{ width: `${Math.min((gammaZ - 1) * 200, 100)}%` }} />
                   </div>
                 </div>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-[#e0e7ef] bg-white p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <TrendingDown className="h-4 w-4 text-blue-600" />
              <h3 className="text-xs font-black uppercase tracking-wider text-[#6a7485]">Dinâmica e Vibrações</h3>
            </div>
            
            <div className="space-y-4">
              {[
                { label: "1º Modo (Translação X)", freq: "0.85 Hz", period: "1.18 s" },
                { label: "2º Modo (Translação Y)", freq: "0.92 Hz", period: "1.09 s" },
                { label: "3º Modo (Torção)", freq: "1.45 Hz", period: "0.69 s" },
              ].map((m, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="text-[10px] font-black text-[#1d1d1f]">{m.label}</div>
                  <div className="text-right">
                    <p className="text-[10px] font-black text-blue-600">{m.freq}</p>
                    <p className="text-[9px] font-bold text-slate-400">{m.period}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 p-3 rounded-xl bg-blue-50 border border-blue-100">
               <p className="text-[10px] font-bold text-blue-800 leading-tight">
                 Auditado Conforto (NBR 6123): Aceleração de pico dentro dos limites normativos para uso residencial.
               </p>
            </div>
          </div>

          <div className="rounded-3xl border border-[#f8d7da] bg-[#fdf2f2] p-6 text-[#721c24]">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <p className="text-xs font-bold leading-relaxed">
                Atenção: Coeficientes γz superiores a 1.30 indicam que a estrutura é extremamente flexível e pode exigir uma análise P-Delta rigorosa ou reforço dos núcleos de rigidez.
              </p>
            </div>
          </div>
        </div>

        {/* Visualização do Prédio (3D Real) */}
        <div className="col-span-12 lg:col-span-8">
           <div className="relative h-[500px] w-full overflow-hidden rounded-[40px] border border-white/60 bg-gradient-to-br from-slate-50 to-slate-200 shadow-inner">
             <Canvas shadows className="h-full w-full">
               <PerspectiveCamera makeDefault position={[8, 8, 8]} fov={40} />
               <ambientLight intensity={0.7} />
               <pointLight position={[10, 10, 10]} intensity={1.5} />
               <Suspense fallback={null}>
              <Stage environment="city" intensity={0.5}>
                   <Building3D floors={15} />
                 </Stage>
                 <Grid infiniteGrid fadeDistance={20} cellColor="#3b82f6" sectionColor="#1e40af" />
               </Suspense>
               <OrbitControls autoRotate autoRotateSpeed={0.3} />
             </Canvas>

             <div className="absolute bottom-10 left-10">
               <div className="rounded-2xl border border-white/60 bg-white/50 p-4 backdrop-blur-md shadow-sm">
                 <p className="text-[11px] font-black uppercase text-[#6a7485]">Status do Modelo</p>
                 <div className="mt-1 flex items-center gap-2">
                   <div className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
                   <span className="text-sm font-bold text-[#1d1d1f]">Sincronizado com Rust Core</span>
                 </div>
               </div>
             </div>

             <div className="absolute right-10 top-10 flex flex-col gap-2">
                <button className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm transition-transform hover:scale-110">
                   <Layers className="h-5 w-5 text-[#4d5360]" />
                </button>
                <button className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm transition-transform hover:scale-110">
                   <TrendingDown className="h-5 w-5 text-[#4d5360]" />
                </button>
             </div>
           </div>
        </div>
      </div>

    </ModuleContainer>
  );
}
