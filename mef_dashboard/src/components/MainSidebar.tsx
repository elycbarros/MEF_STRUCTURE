"use client";

import React from "react";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

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
      "col-span-12 rounded-[30px] border p-2 transition-all duration-700",
      isProfessional 
        ? "border-white/5 bg-[#16191f]/80 backdrop-blur-2xl shadow-blue-900/5" 
        : "border-slate-200 bg-white/70 shadow-slate-200/50"
    )}>
      <nav className="flex flex-row items-center gap-2 overflow-x-auto pb-2 scrollbar-hide px-2">
        <div className="hidden lg:flex items-center px-4 border-r border-white/5 mr-2">
           <p className={cn(
            "text-[9px] font-black uppercase tracking-[0.3em] whitespace-nowrap",
            isProfessional ? "text-blue-400/60" : "text-slate-400"
          )}>
            Módulos
          </p>
        </div>

        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "group flex shrink-0 items-center gap-3 rounded-2xl px-4 py-3 text-left text-xs font-black transition-all",
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
                "flex h-6 w-6 items-center justify-center rounded-lg transition-transform group-hover:scale-110",
                isActive 
                  ? (isProfessional ? "bg-white/20" : "bg-white/10")
                  : (isProfessional ? "bg-white/5" : "bg-slate-100")
              )}>
                <Icon className={cn("h-3 w-3", isActive ? "text-white" : (isProfessional ? "text-white/40" : "text-slate-500"))} />
              </div>
              <span className="whitespace-nowrap">{tab.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
