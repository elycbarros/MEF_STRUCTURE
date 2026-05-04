"use client";

import React from "react";
import { LucideIcon } from "lucide-react";

interface Tab {
  id: string;
  label: string;
  icon: LucideIcon;
}

interface MainSidebarProps {
  tabs: Tab[];
  activeTab: string;
  setActiveTab: (id: any) => void;
  theme?: "academic" | "professional";
}

export function MainSidebar({ tabs, activeTab, setActiveTab, theme = "academic" }: MainSidebarProps) {
  const isProfessional = theme === "professional";

  return (
    <aside className={cn(
      "col-span-12 rounded-[40px] border p-5 transition-all duration-700 lg:col-span-3",
      isProfessional 
        ? "border-white/5 bg-[#16191f]/80 backdrop-blur-2xl shadow-blue-900/5" 
        : "border-slate-200 bg-white/70 shadow-slate-200/50"
    )}>
      <div className="mb-6 px-4">
        <p className={cn(
          "text-[10px] font-black uppercase tracking-[0.3em]",
          isProfessional ? "text-blue-400/60" : "text-slate-400"
        )}>
          Navegação Lab
        </p>
      </div>

      <nav className="space-y-3">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "group flex w-full items-center gap-4 rounded-2xl px-5 py-4 text-left text-sm font-black transition-all",
                isActive
                  ? (isProfessional 
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30" 
                      : "bg-[#1d1d1f] text-white shadow-xl shadow-black/10")
                  : (isProfessional 
                      ? "text-white/40 hover:bg-white/5 hover:text-white" 
                      : "text-slate-500 hover:bg-slate-50 hover:text-slate-900")
              )}
            >
              <div className={cn(
                "flex h-8 w-8 items-center justify-center rounded-xl transition-transform group-hover:scale-110",
                isActive 
                  ? (isProfessional ? "bg-white/20" : "bg-white/10")
                  : (isProfessional ? "bg-white/5" : "bg-slate-100")
              )}>
                <Icon className={cn("h-4 w-4", isActive ? "text-white" : (isProfessional ? "text-white/40" : "text-slate-500"))} />
              </div>
              {tab.label}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
