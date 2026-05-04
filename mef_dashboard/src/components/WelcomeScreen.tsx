"use client";

import React from "react";
import { GraduationCap, Rocket, ArrowRight, BookOpen, Cpu, ShieldCheck, Zap, Layers } from "lucide-react";
import { cn } from "@/lib/utils";

interface WelcomeScreenProps {
  onSelectMode: (mode: "academic" | "professional") => void;
}

export default function WelcomeScreen({ onSelectMode }: WelcomeScreenProps) {
  return (
    <div className="min-h-screen bg-[#f8f9fa] flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Decorativo - Gradientes Suaves */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[50%] h-[50%] bg-blue-500/5 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute -bottom-[10%] -right-[10%] w-[50%] h-[50%] bg-indigo-500/5 blur-[120px] rounded-full animate-pulse" />
      </div>

      <div className="max-w-6xl w-full relative z-10">
        <div className="text-center mb-16 space-y-4">
          <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-white border border-slate-200 shadow-sm mb-4">
            <div className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-900">MEF Structural Platform V6.0</span>
          </div>
          <h1 className="text-6xl font-black tracking-tighter text-slate-900 leading-tight">
            Selecione seu <span className="text-blue-600">Ambiente</span> de Trabalho
          </h1>
          <p className="text-lg font-medium text-slate-500 max-w-2xl mx-auto">
            Integração absoluta entre o rigor acadêmico e a performance profissional de engenharia forense.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-10">
          {/* MESTRE - Lab Acadêmico */}
          <button 
            onClick={() => onSelectMode("academic")}
            className="group relative text-left p-10 rounded-[48px] border border-slate-200 bg-white shadow-xl hover:shadow-2xl transition-all duration-700 hover:-translate-y-3 overflow-hidden"
          >
            <div className="absolute -right-10 -top-10 p-8 opacity-[0.03] group-hover:opacity-[0.08] transition-all group-hover:scale-110">
              <GraduationCap size={240} />
            </div>
            
            <div className="flex flex-col gap-8">
              <div className="flex items-center gap-5">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 shadow-inner group-hover:bg-blue-600 group-hover:text-white transition-all">
                  <GraduationCap className="h-8 w-8" />
                </div>
                <div>
                  <h2 className="text-3xl font-black text-slate-900 tracking-tight">MESTRE LAB</h2>
                  <p className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-600">Scientific Engine</p>
                </div>
              </div>

              <p className="text-slate-500 font-bold leading-relaxed text-lg">
                Foco pedagógico em elementos isolados, dimensionamento assistido e conformidade normativa rigorosa (NBR 6118).
              </p>

              <div className="space-y-4">
                {[
                  { icon: BookOpen, text: "Resolução Passo-a-Passo" },
                  { icon: Layers, text: "Vigas, Lajes e Pilares Isolados" },
                  { icon: ShieldCheck, text: "Memoriais de Cálculo Didáticos" }
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-4 text-sm font-black text-slate-700">
                    <div className="h-2 w-2 rounded-full bg-blue-600" />
                    {item.text}
                  </div>
                ))}
              </div>

              <div className="pt-4 flex items-center gap-3 text-slate-900 font-black text-sm uppercase tracking-widest group-hover:gap-6 transition-all">
                Iniciar Aprendizado <ArrowRight className="h-5 w-5" />
              </div>
            </div>
          </button>

          {/* UFO - Engenharia Forense */}
          <button 
            onClick={() => onSelectMode("professional")}
            className="group relative text-left p-10 rounded-[48px] border border-white/5 bg-[#16191f] shadow-2xl hover:shadow-blue-600/20 transition-all duration-700 hover:-translate-y-3 overflow-hidden text-white"
          >
            <div className="absolute -right-10 -top-10 p-8 opacity-[0.05] group-hover:opacity-[0.1] transition-all group-hover:scale-110">
              <Rocket size={240} />
            </div>

            <div className="flex flex-col gap-8">
              <div className="flex items-center gap-5">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/40 group-hover:scale-110 transition-all">
                  <Rocket className="h-8 w-8" />
                </div>
                <div>
                  <h2 className="text-3xl font-black tracking-tight">UFO CORE</h2>
                  <p className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-400">Professional Engine</p>
                </div>
              </div>

              <p className="text-white/60 font-bold leading-relaxed text-lg">
                Análise global de edifícios altos, estabilidade P-Delta e auditoria autônoma Ph.D. para projetos de alta complexidade.
              </p>

              <div className="space-y-4">
                {[
                  { icon: Cpu, text: "Engine Rust de Alta Performance" },
                  { icon: Zap, text: "Simulação Global 3D & P-Delta" },
                  { icon: ShieldCheck, text: "Auditoria Forense Automatizada" }
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-4 text-sm font-black text-white/80">
                    <div className="h-2 w-2 rounded-full bg-blue-500 shadow-glow shadow-blue-500/50" />
                    {item.text}
                  </div>
                ))}
              </div>

              <div className="pt-4 flex items-center gap-3 text-blue-400 font-black text-sm uppercase tracking-widest group-hover:gap-6 transition-all">
                Iniciar Projeto Profissional <ArrowRight className="h-5 w-5" />
              </div>
            </div>
          </button>
        </div>

        <div className="mt-20 text-center opacity-30">
          <p className="text-[10px] font-black uppercase tracking-[0.4em] text-slate-500">
            Engineered with Precision by Deepmind & Elyc Barros • 2026
          </p>
        </div>
      </div>
    </div>
  );
}
