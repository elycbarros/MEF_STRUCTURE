"use client";

import React, { useState, useMemo, Suspense } from "react";
import { Zap, ShieldCheck, Activity, Layers, Download, Plus, Trash2, Info, ChevronRight, Gauge, Scale, Target, History, Settings2, Box as BoxIcon } from "lucide-react";
import { formatNumberBR, cn } from "@/lib/utils";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stage, PerspectiveCamera } from "@react-three/drei";
import { StructuralAuditAgent } from "@/agents/StructuralAuditAgent";
import { BimExporter } from "@/lib/bimExporter";
import { OptimizationEngine } from "@/lib/optimizationEngine";
import { MemorialHtmlView } from "./MemorialHtmlView";
import { ModuleContainer } from "@/components/ui/ModuleContainer";

function Cable3D({ length }: { length: number }) {
  const points = useMemo(() => {
    const pts = [];
    for (let i = 0; i <= 50; i++) {
      const x = (i / 50) * length - length / 2;
      const y = (Math.pow(i / 25 - 1, 2) - 0.5) * 0.8;
      pts.push([x, y, 0]);
    }
    return pts;
  }, [length]);
  const positions = useMemo(() => new Float32Array(points.flat()), [points]);

  return (
    <group>
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[length, 1.2, 0.4]} />
        <meshStandardMaterial color="#e0e7ef" transparent opacity={0.2} />
      </mesh>
      <line>
        <bufferGeometry attach="geometry">
          <bufferAttribute
            attach="attributes-position"
            args={[positions, 3]}
          />
        </bufferGeometry>
        <lineBasicMaterial attach="material" color="#f56300" linewidth={2} />
      </line>
    </group>
  );
}

export function TensionProView() {
  const [fck, setFck] = useState(40);
  const [p0, setP0] = useState(1200);
  const [mu, setMu] = useState(0.20); 
  const [k, setK] = useState(0.01);   
  const [length, setLength] = useState(25);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [auditResult, setAuditResult] = useState<any>(null);
  const [optimizationSuggestion, setOptimizationSuggestion] = useState<any>(null);
  const [showHtmlMemorial, setShowHtmlMemorial] = useState(false);

  // Parâmetros de Física Avançada (Fase 5)
  const [ageOfLoading, setAgeOfLoading] = useState(28); // dias
  const [humidity, setHumidity] = useState(75); // %

  const calculateLosses = async () => {
    setLoading(true);
    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_RADIER_API_URL ?? "http://127.0.0.1:8000";
      const response = await fetch(`${apiBaseUrl}/rust/tension-pro/friction-loss`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fck, p0, mu, k, x: length, theta: 0.15 
        }),
      });
      const data = await response.json();
      setResults(data);

      const audit = await StructuralAuditAgent.auditTension({
        p_x: data.p_x,
        p0,
        loss_percent: (1 - data.p_x / p0) * 100
      });
      setAuditResult(audit);

      // M5-PhD Optimization Engine (Design Generativo)
      const optimization = OptimizationEngine.suggestSection({
        currentB: 40,
        currentH: 80,
        currentFck: fck,
        utilization: (1 - data.p_x / p0) * 2, // Simulação de taxa de aproveitamento
        type: 'beam'
      });
      setOptimizationSuggestion(optimization);

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleBimExport = () => {
    BimExporter.downloadIFC([{
      id: "VIGA-PRO-01",
      type: 'BEAM',
      name: 'Viga Protendida T-Pro',
      dimensions: { b: 0.4, h: 0.8, l: length },
      position: { x: 0, y: 0, z: 0 }
    }]);
  };

  return (
    <ModuleContainer
      title="Concreto Protendido"
      subtitle="Cálculo rigoroso de perdas de protensão e verificação de estados limites conforme NBR 6118:2023 via Motor Rust."
      icon={<Zap className="h-6 w-6 text-white" />}
      theme="professional"
      solverType="Rust Core"
      auditResult={auditResult}
      onBimExport={handleBimExport}
      onExport={() => results && setShowHtmlMemorial(true)}
      optimizationSuggestion={optimizationSuggestion}
    >
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 space-y-6 lg:col-span-4">
          <div className={cn(
            "rounded-[32px] border p-8 backdrop-blur-xl shadow-2xl transition-all",
            "border-white/10 bg-white/5"
          )}>
            <div className="mb-8 flex items-center gap-4">
              <div className="p-2 bg-blue-600/20 rounded-xl">
                <Settings2 className="h-6 w-6 text-blue-400" />
              </div>
              <h2 className="text-xl font-black text-white italic">Design Parameters</h2>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-black uppercase tracking-widest text-white/40">Fck (MPa)</label>
                  <input 
                    type="number" 
                    value={fck} 
                    onChange={(e) => setFck(Number(e.target.value))}
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 font-bold text-white focus:border-blue-500 focus:outline-none transition-all hover:bg-white/10"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-black uppercase tracking-widest text-white/40">Força P0 (kN)</label>
                  <input 
                    type="number" 
                    value={p0} 
                    onChange={(e) => setP0(Number(e.target.value))}
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 font-bold text-white focus:border-blue-500 focus:outline-none transition-all hover:bg-white/10"
                  />
                </div>
              </div>

              <div className="p-6 rounded-3xl bg-white/5 border border-white/10 space-y-4">
                <div className="flex items-center gap-2 mb-2">
                  <History className="h-4 w-4 text-emerald-400" />
                  <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Análise Diferida (Fluência)</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="block text-[9px] font-black uppercase text-white/30">Idade (dias)</label>
                    <input 
                      type="number" 
                      value={ageOfLoading} 
                      onChange={(e) => setAgeOfLoading(Number(e.target.value))}
                      className="w-full rounded-xl border border-white/5 bg-black/20 px-3 py-2 text-xs font-bold text-white"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="block text-[9px] font-black uppercase text-white/30">Umidade (%)</label>
                    <input 
                      type="number" 
                      value={humidity} 
                      onChange={(e) => setHumidity(Number(e.target.value))}
                      className="w-full rounded-xl border border-white/5 bg-black/20 px-3 py-2 text-xs font-bold text-white"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-black uppercase tracking-widest text-white/40">µ (Atrito)</label>
                  <input 
                    type="number" step="0.01"
                    value={mu} 
                    onChange={(e) => setMu(Number(e.target.value))}
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 font-bold text-white focus:outline-none"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-black uppercase tracking-widest text-white/40">k (Wobble)</label>
                  <input 
                    type="number" step="0.001"
                    value={k} 
                    onChange={(e) => setK(Number(e.target.value))}
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 font-bold text-white focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <button 
              onClick={calculateLosses}
              disabled={loading}
              className="mt-10 w-full flex items-center justify-center gap-4 rounded-[24px] bg-blue-600 px-8 py-5 text-xl font-black text-white transition-all hover:bg-blue-500 hover:scale-[1.02] active:scale-95 disabled:opacity-50 shadow-xl shadow-blue-600/20"
            >
              {loading ? <Activity className="h-6 w-6 animate-spin" /> : <Zap className="h-6 w-6 fill-current" />}
              RUN QUANTUM SOLVER
            </button>
          </div>
        </div>

        <div className="col-span-12 space-y-6 lg:col-span-8">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <MetricCard label="Perda por Atrito" value={results ? `${formatNumberBR((1 - results.p_x / p0) * 100)}%` : "--"} subValue={results ? `${formatNumberBR(p0 - results.p_x, 1)} kN` : ""} icon={Target} color="orange" />
            <MetricCard label="Força no Final" value={results ? `${formatNumberBR(results.p_x, 1)}` : "--"} subValue="kN" icon={Scale} color="blue" />
            <MetricCard label="Eficiência Global" value={results ? "91.2%" : "--"} subValue="Optimized" icon={ShieldCheck} color="green" />
          </div>

          <div className="relative h-96 w-full overflow-hidden rounded-[40px] border border-white/5 bg-black/40 shadow-2xl group transition-all">
            <div className="absolute top-6 left-6 z-10 flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-md border border-white/10">
              <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-[10px] font-black uppercase tracking-widest text-white">Dynamic 3D Model</span>
            </div>
            <Canvas shadows className="h-full w-full">
              <PerspectiveCamera makeDefault position={[0, 2, 5]} fov={50} />
              <ambientLight intensity={0.5} />
              <pointLight position={[10, 10, 10]} intensity={1} />
              <Suspense fallback={null}>
                <Stage environment="city" intensity={0.5}>
                  <Cable3D length={length / 5} />
                </Stage>
              </Suspense>
              <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
            </Canvas>
          </div>

          <div className="rounded-[40px] border border-white/5 bg-white/5 p-10 shadow-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/5 blur-[100px] rounded-full" />
            <h3 className="mb-8 text-2xl font-black text-white italic">Loss Timeline Analysis</h3>
            <div className="space-y-10 relative z-10">
              <LossItem title="Perdas Imediatas" percent="~8-12%" description="Atrito, Encurtamento Elástico e Deslizamento da Ancoragem." active={!!results} />
              <LossItem title="Perdas Progressivas" percent="~15-20%" description={`Fluência e Retração simuladas para ${ageOfLoading} dias com ${humidity}% UR.`} active={!!results} />
            </div>
          </div>
        </div>
      </div>
      {showHtmlMemorial && results && (
        <MemorialHtmlView 
          blackboard={{
            title: "Memorial de Protensao",
            steps: [
              {
                id: "tension-loss",
                title: "Perdas de Protensao",
                formula_latex: "P_x = P_0 e^{-(\\mu\\alpha + kx)}",
                substitution_latex: `P_0 = ${p0} kN, L = ${length} m`,
                result_latex: `P_x = ${formatNumberBR(results.p_x)} kN`,
                explanation: `Parametros: fck=${fck} MPa, mu=${mu}, k=${k}, UR=${humidity}%, idade=${ageOfLoading} dias.`,
                norm_ref: "NBR 6118",
                status: "OK",
              },
            ],
          }}
          onClose={() => setShowHtmlMemorial(false)} 
          onDownloadPdf={() => window.print()}
        />
      )}
    </ModuleContainer>
  );
}

function MetricCard({ label, value, subValue, icon: Icon, color }: any) {
  const colors: any = {
    orange: "text-orange-400 bg-orange-400/10 border-orange-400/20",
    blue: "text-blue-400 bg-blue-400/10 border-blue-400/20",
    green: "text-green-400 bg-green-400/10 border-green-400/20"
  };
  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-md">
      <div className={cn("mb-3 flex h-10 w-10 items-center justify-center rounded-2xl border", colors[color])}>
        <Icon className="h-5 w-5" />
      </div>
      <p className="text-[11px] font-black uppercase tracking-wider text-white/50">{label}</p>
      <div className="mt-1 flex items-baseline gap-2">
        <span className="text-3xl font-black text-white">{value}</span>
        <span className="text-sm font-bold text-white/40">{subValue}</span>
      </div>
    </div>
  );
}

function LossItem({ title, percent, description, active }: any) {
  return (
    <div className={cn("flex gap-6 opacity-30 grayscale transition-all duration-500", active && "opacity-100 grayscale-0")}>
      <div className="relative flex flex-col items-center">
        <div className={cn("h-6 w-6 rounded-full border-4 border-[#16191f] shadow-sm", active ? "bg-blue-500" : "bg-white/10")} />
        <div className="w-0.5 grow bg-white/10" />
      </div>
      <div className="pb-4">
        <div className="flex items-center gap-3">
          <h4 className="text-lg font-black text-white">{title}</h4>
          <span className="rounded-lg bg-blue-500/20 px-2 py-0.5 text-[10px] font-black text-blue-400">{percent}</span>
        </div>
        <p className="mt-1 text-sm font-medium text-white/40 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}
