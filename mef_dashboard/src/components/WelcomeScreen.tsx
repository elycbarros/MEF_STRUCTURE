"use client";

import React from "react";
import { GraduationCap, Rocket, ArrowRight, BookOpen, Cpu, ShieldCheck, Zap, Layers } from "lucide-react";
import { cn } from "@/lib/utils";

interface WelcomeScreenProps {
  onSelectMode: (mode: "academic" | "professional") => void;
}

export default function WelcomeScreen({ onSelectMode }: WelcomeScreenProps) {
  return (
    <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Decorative Elements */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/5 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-500/5 blur-[120px] rounded-full" />
      </div>

      <div className="max-w-5xl w-full relative z-10">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 mb-4">
            <ShieldCheck className="w-4 h-4 text-indigo-600" />
            <span className="text-[10px] font-black uppercase tracking-widest text-indigo-600">MEF STRUCTURAL V6.0.0-PHD</span>
          </div>
          <h1 className="text-5xl font-black tracking-tight text-[#1a1c1e] mb-4 italic">
            Escolha seu <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-indigo-400">Engine</span>
          </h1>
          <p className="text-[#6a7485] font-medium max-w-xl mx-auto">
            Selecione o ambiente de trabalho ideal para seu projeto estrutural.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* MESTRE - Academic Mode */}
          <button 
            onClick={() => onSelectMode("academic")}
            className="group relative text-left p-8 rounded-[40px] border border-[#e0e7ef] bg-white shadow-xl hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
              <GraduationCap size={120} />
            </div>
            
            <div className="flex items-center gap-4 mb-6">
              <div className="p-4 bg-amber-50 rounded-2xl border border-amber-100 group-hover:bg-amber-100 transition-colors">
                <GraduationCap className="w-8 h-8 text-amber-600" />
              </div>
              <div>
                <h2 className="text-2xl font-black text-[#1a1c1e]">Engine MESTRE</h2>
                <p className="text-xs font-bold text-amber-600 uppercase tracking-widest">Modo Acadêmico</p>
              </div>
            </div>

            <p className="text-[#6a7485] text-sm leading-relaxed mb-8">
              Ideal para estudantes e professores. Foco em elementos isolados, 
              didática normativa e resolução passo-a-passo baseada em livros técnicos.
            </p>

            <ul className="space-y-3 mb-10">
              <li className="flex items-center gap-3 text-sm font-medium text-[#4a5568]">
                <BookOpen className="w-4 h-4 text-amber-500" />
                <span>Resolução didática (Livro-texto)</span>
              </li>
              <li className="flex items-center gap-3 text-sm font-medium text-[#4a5568]">
                <Layers className="w-4 h-4 text-amber-500" />
                <span>Elementos Isolados (Lajes/Blocos)</span>
              </li>
              <li className="flex items-center gap-3 text-sm font-medium text-[#4a5568]">
                <ShieldCheck className="w-4 h-4 text-amber-500" />
                <span>Verificações Normativas Simplificadas</span>
              </li>
            </ul>

            <div className="inline-flex items-center gap-2 text-amber-600 font-black text-sm group-hover:gap-4 transition-all">
              INICIAR APRENDIZADO <ArrowRight className="w-4 h-4" />
            </div>
          </button>

          {/* UFO - Professional Mode */}
          <button 
            onClick={() => onSelectMode("professional")}
            className="group relative text-left p-8 rounded-[40px] border border-indigo-600/10 bg-[#1a1c1e] shadow-2xl hover:shadow-indigo-500/20 transition-all duration-500 hover:-translate-y-2 overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity text-white">
              <Rocket size={120} />
            </div>

            <div className="flex items-center gap-4 mb-6">
              <div className="p-4 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 group-hover:bg-indigo-500/20 transition-colors">
                <Rocket className="w-8 h-8 text-indigo-400" />
              </div>
              <div>
                <h2 className="text-2xl font-black text-white">Engine UFO</h2>
                <p className="text-xs font-bold text-indigo-400 uppercase tracking-widest">Modo Profissional Elite</p>
              </div>
            </div>

            <p className="text-slate-400 text-sm leading-relaxed mb-8">
              Engine de alta performance para edifícios altos. Análise global 
              P-Delta, inteligência autônoma PhD e simulações distribuídas.
            </p>

            <ul className="space-y-3 mb-10">
              <li className="flex items-center gap-3 text-sm font-medium text-slate-300">
                <Cpu className="w-4 h-4 text-indigo-400" />
                <span>Agente Autônomo PhD (Auto-Design)</span>
              </li>
              <li className="flex items-center gap-3 text-sm font-medium text-slate-300">
                <Zap className="w-4 h-4 text-indigo-400" />
                <span>Análise Global 3D & Estabilidade P-Delta</span>
              </li>
              <li className="flex items-center gap-3 text-sm font-medium text-slate-300">
                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                <span>Diagnóstico de Auditoria Forense</span>
              </li>
            </ul>

            <div className="inline-flex items-center gap-2 text-indigo-400 font-black text-sm group-hover:gap-4 transition-all">
              INICIAR PROJETO ELITE <ArrowRight className="w-4 h-4" />
            </div>
          </button>
        </div>

        <div className="mt-12 text-center">
          <p className="text-[10px] font-bold text-[#8a9ab0] uppercase tracking-widest">
            Desenvolvido por Antigravity Deepmind & Elyc Barros • 2026
          </p>
        </div>
      </div>
    </div>
  );
}
