"use client";

import React from 'react';
import { LayoutDashboard, FileText, Database, Settings, PieChart, Activity } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navItems = [
  { id: 'resumo', icon: LayoutDashboard, label: 'Resumo' },
  { id: 'designs', icon: FileText, label: 'Designs' },
  { id: 'analise', icon: Activity, label: 'Análise' },
  { id: 'relatorios', icon: PieChart, label: 'Relatórios' },
  { id: 'dados', icon: Database, label: 'Dados' },
  { id: 'configuracoes', icon: Settings, label: 'Configurações' },
];

interface SidebarProps {
  activeItem: string;
  onSelect: (id: string) => void;
}

export function Sidebar({ activeItem, onSelect }: SidebarProps) {
  return (
    <aside className="w-64 glass-sidebar h-screen flex flex-col p-6 fixed left-0 top-0">
      <div className="flex items-center gap-3 mb-10 px-2">
        <div className="w-8 h-8 bg-apple-blue rounded-lg flex items-center justify-center">
          <Database className="text-white w-5 h-5" />
        </div>
        <span className="font-bold text-xl tracking-tight text-apple-text uppercase">Structural Suite</span>
      </div>
      
      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const isActive = item.id === activeItem;
          return (
          <button
            key={item.label}
            type="button"
            onClick={() => onSelect(item.id)}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group",
              isActive
                ? "bg-apple-blue/10 text-apple-blue shadow-sm" 
                : "text-apple-muted hover:bg-black/5 hover:text-apple-text"
            )}
          >
            <item.icon className={cn("w-5 h-5", isActive ? "text-apple-blue" : "text-apple-muted group-hover:text-apple-text")} />
            <span className="font-medium text-sm">{item.label}</span>
          </button>
        );
        })}
      </nav>
      
      <div className="mt-auto pt-6 border-t border-black/5">
        <p className="text-[10px] text-apple-muted uppercase font-bold tracking-widest px-3 mb-2">Engenharia v2.6</p>
        <div className="px-3 py-2 bg-apple-green/10 text-apple-green text-[11px] font-bold rounded-lg flex items-center justify-center border border-apple-green/20">
          STATUS: OTIMIZADO
        </div>
      </div>
    </aside>
  );
}
