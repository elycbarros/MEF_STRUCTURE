'use client';

import Link from "next/link";
import { Rocket, ChevronRight, GraduationCap } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

export default function SelectionPage() {
  return (
    <div className="min-h-screen bg-[#F5F5F7] dark:bg-[#000000] flex flex-col items-center justify-center p-6 selection-screen">
      
      {/* Background Decor */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px] animate-pulse" />
      </div>

      <div className="relative z-10 w-full max-w-4xl space-y-12">
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold tracking-widest uppercase mb-4 border border-primary/20">
            Atlas Engine v6.2
          </div>
          <h1 className="text-5xl md:text-6xl font-black tracking-tighter text-foreground drop-shadow-sm">
            Escolha seu <span className="text-primary">Ambiente</span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-xl mx-auto font-medium">
            Selecione a plataforma de análise estrutural ideal para sua necessidade atual.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Mestre Option */}
          <Link href="/mestre" className="group">
            <Card className="h-full border-none shadow-2xl bg-white/80 dark:bg-[#1C1C1E]/80 backdrop-blur-xl hover:scale-[1.02] transition-all duration-500 overflow-hidden group-hover:ring-2 ring-primary/50 cursor-pointer">
              <CardContent className="p-8 flex flex-col h-full">
                <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center mb-6 shadow-lg shadow-primary/30 group-hover:rotate-3 transition-transform duration-500">
                  <GraduationCap className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold mb-3">Atlas Mestre</h3>
                <p className="text-muted-foreground leading-relaxed mb-8 flex-1">
                  Ambiente pedagógico de alta fidelidade para estudo e dimensionamento de elementos isolados. 
                  Memoriais passo-a-passo e roteiros didáticos.
                </p>
                <div className="flex items-center text-primary font-bold gap-2 group-hover:gap-4 transition-all">
                  Entrar no Laboratório <ChevronRight className="w-4 h-4" />
                </div>
              </CardContent>
            </Card>
          </Link>

          {/* Professional Option */}
          <Link href="/projects" className="group">
            <Card className="h-full border-none shadow-2xl bg-white/80 dark:bg-[#1C1C1E]/80 backdrop-blur-xl hover:scale-[1.02] transition-all duration-500 overflow-hidden group-hover:ring-2 ring-blue-500/50 cursor-pointer">
              <CardContent className="p-8 flex flex-col h-full">
                <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center mb-6 shadow-lg shadow-blue-500/30 group-hover:-rotate-3 transition-transform duration-500">
                  <Rocket className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold mb-3">Atlas UFO (Pro)</h3>
                <p className="text-muted-foreground leading-relaxed mb-8 flex-1">
                  Análise global de edifícios complexos, integração solo-estrutura e dimensionamento profissional. 
                  Gestão de projetos e detalhamentos executivos.
                </p>
                <div className="flex items-center text-blue-600 font-bold gap-2 group-hover:gap-4 transition-all">
                  Iniciar Projeto Global <ChevronRight className="w-4 h-4" />
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>

        <div className="text-center">
          <p className="text-xs text-muted-foreground/60 font-medium tracking-widest uppercase">
            PhD Structural Engineering Lab • Powered by Rust Engine
          </p>
        </div>
      </div>
    </div>
  );
}
