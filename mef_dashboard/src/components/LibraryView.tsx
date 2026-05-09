"use client";

import React, { useState } from "react";
import { 
  Book, 
  Library, 
  Globe, 
  ShieldCheck, 
  Search, 
  ChevronRight, 
  BookOpen, 
  FileText,
  ExternalLink,
  Layers,
  Zap
} from "lucide-react";
import { cn } from "@/lib/utils";

interface BookReference {
  title: string;
  author: string;
  description: string;
  category: "foundations" | "concrete" | "tall" | "normative";
  isLocal?: boolean;
}

const REFERENCES: BookReference[] = [
  // Foundations & ISE
  {
    title: "Interação Solo-Estrutura (ISE)",
    author: "Diversos",
    description: "Conceitos sobre como a deformabilidade do solo influencia os esforços na superestrutura. Essencial para prédios altos e análises de recalque.",
    category: "foundations",
    isLocal: true
  },
  {
    title: "Engenharia de Fundações: Passo a Passo",
    author: "Dickran Berberian",
    description: "Guia prático da UnB sobre projeto e execução, cobrindo desde investigação (SPT) até soluções práticas de campo.",
    category: "foundations",
    isLocal: true
  },
  {
    title: "Fundações: Teoria e Prática",
    author: "Falconi / ABMS",
    description: "A 'bíblia' das fundações no Brasil, cobrindo mecânica dos solos, sistemas complexos e perícias.",
    category: "foundations",
    isLocal: true
  },
  {
    title: "Fundações (Volume I)",
    author: "Velloso e Lopes",
    description: "Obra clássica brasileira focada em geotecnia, investigação e fundações profundas.",
    category: "foundations",
    isLocal: true
  },
  {
    title: "Patologia das Fundações",
    author: "Diversos",
    description: "Foco em perícia e forense: diagnóstico de trincas, recalques diferenciais e técnicas de recuperação.",
    category: "foundations",
    isLocal: true
  },
  // Concrete
  {
    title: "Estruturas de Concreto Vol 1",
    author: "IBRACON-ABECE",
    description: "Referência nacional absoluta para o projeto de estruturas de concreto, detalhando normas e segurança.",
    category: "concrete",
    isLocal: true
  },
  {
    title: "Estruturas de Concreto Armado",
    author: "João Carlos Teatini",
    description: "Foco didático no dimensionamento de seções e elementos (vigas, lajes, pilares) para prática profissional.",
    category: "concrete",
    isLocal: true
  },
  // Tall Buildings
  {
    title: "Tall Building Foundation Design",
    author: "Harry G. Poulos",
    description: "A autoridade máxima mundial em fundações para arranha-céus e análise de grupos de estacas.",
    category: "tall",
    isLocal: true
  },
  {
    title: "Dynamics of Structures",
    author: "Anil K. Chopra",
    description: "Base teórica para análise sísmica e resposta dinâmica de estruturas complexas.",
    category: "tall",
    isLocal: true
  },
  {
    title: "Wind Effects on Structures",
    author: "Simiu & Scanlan",
    description: "Essencial para o cálculo de ações de vento e conforto dinâmico em edifícios altos.",
    category: "tall",
    isLocal: true
  },
  // Normative
  {
    title: "NBR 6118",
    author: "ABNT",
    description: "Projeto de estruturas de concreto - Procedimento.",
    category: "normative"
  },
  {
    title: "NBR 6123",
    author: "ABNT",
    description: "Forças devidas ao vento em edificações.",
    category: "normative"
  }
];

export default function LibraryView() {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState<string>("all");

  const filteredReferences = REFERENCES.filter(ref => {
    const matchesSearch = ref.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         ref.author.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = activeFilter === "all" || ref.category === activeFilter;
    return matchesSearch && matchesFilter;
  });

  const categories = [
    { id: "all", label: "Tudo", icon: Library },
    { id: "foundations", label: "Fundações & ISE", icon: ShieldCheck },
    { id: "concrete", label: "Concreto Estrutural", icon: Layers },
    { id: "tall", label: "Edifícios Altos", icon: Globe },
    { id: "normative", label: "Normas", icon: FileText }
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-12">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-blue-600">
            <Library className="w-5 h-5" />
            <span className="text-[10px] font-black uppercase tracking-[0.2em]">Conhecimento Técnico</span>
          </div>
          <h2 className="text-4xl font-black text-slate-900 tracking-tight">Biblioteca Técnica</h2>
          <p className="text-sm font-medium text-slate-500">Fundamentos científicos que alimentam os motores de cálculo do MEF STRUCTURAL.</p>
        </div>

        {/* Search Bar */}
        <div className="relative group min-w-[300px]">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600 group-focus-within:text-blue-600 transition-colors" />
          <input 
            type="text"
            placeholder="Pesquisar livros, autores ou normas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-11 pr-4 py-3.5 bg-white border border-slate-200 rounded-2xl text-sm font-bold focus:ring-4 focus:ring-blue-50 focus:border-blue-500 transition-all outline-none"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setActiveFilter(cat.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-black transition-all",
              activeFilter === cat.id 
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" 
                : "bg-white text-slate-500 border border-slate-200 hover:bg-slate-50"
            )}
          >
            <cat.icon className="w-3.5 h-3.5" />
            {cat.label}
          </button>
        ))}
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredReferences.map((ref, idx) => (
          <div 
            key={idx}
            className="group relative flex flex-col p-6 rounded-[32px] bg-white border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-500 overflow-hidden"
          >
            {/* Category Badge */}
            <div className="flex items-center justify-between mb-4">
              <span className={cn(
                "px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-wider",
                ref.category === "foundations" && "bg-amber-50 text-amber-600",
                ref.category === "concrete" && "bg-emerald-50 text-emerald-600",
                ref.category === "tall" && "bg-blue-50 text-blue-600",
                ref.category === "normative" && "bg-slate-100 text-slate-600"
              )}>
                {categories.find(c => c.id === ref.category)?.label}
              </span>
              {ref.isLocal && (
                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-slate-900 text-slate-900 rounded-full text-[8px] font-black">
                  <Zap className="w-2.5 h-2.5 fill-current" /> LOCAL
                </div>
              )}
            </div>

            <div className="flex-1 space-y-3">
              <h3 className="text-lg font-black text-slate-900 leading-tight group-hover:text-blue-600 transition-colors">
                {ref.title}
              </h3>
              <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">{ref.author}</p>
              <p className="text-xs text-slate-500 leading-relaxed font-medium">
                {ref.description}
              </p>
            </div>

            <div className="mt-6 pt-6 border-t border-slate-100 flex items-center justify-between">
              <button className="flex items-center gap-2 text-[10px] font-black text-blue-600 hover:gap-3 transition-all uppercase tracking-widest">
                Consultar Detalhes <ChevronRight className="w-3 h-3" />
              </button>
              <div className="p-2 rounded-xl bg-slate-50 text-slate-600 group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">
                <BookOpen className="w-4 h-4" />
              </div>
            </div>

            {/* Decorative background icon */}
            <div className="absolute -right-4 -bottom-4 opacity-[0.03] rotate-12 group-hover:scale-110 transition-transform duration-700 pointer-events-none">
              <BookOpen className="w-24 h-24" />
            </div>
          </div>
        ))}
      </div>

      {filteredReferences.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
          <div className="p-6 rounded-full bg-slate-50">
            <Search className="w-10 h-10 text-slate-200" />
          </div>
          <div>
            <h4 className="font-black text-slate-900">Nenhum resultado encontrado</h4>
            <p className="text-sm text-slate-500">Tente ajustar seus filtros ou pesquisar por outro termo.</p>
          </div>
        </div>
      )}
    </div>
  );
}
