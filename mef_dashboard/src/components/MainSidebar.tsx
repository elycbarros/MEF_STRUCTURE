"use client";

import React from "react";
import { LucideIcon, Activity, Settings } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

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
      "col-span-12 rounded-[2.5rem] border p-1.5 transition-all duration-700 overflow-hidden relative group",
      "border-slate-200 bg-slate-100/60 backdrop-blur-xl shadow-2xl shadow-blue-900/5"
    )}>
      {/* Glossy Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
      
      <nav className="flex flex-row items-center gap-1.5 overflow-x-auto pb-1.5 scrollbar-hide px-3 relative z-10">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "group relative flex shrink-0 items-center gap-3 rounded-2xl px-5 py-3 text-left transition-all duration-500",
                isActive
                  ? "bg-blue-600 text-white shadow-[0_0_20px_rgba(37,99,235,0.4)]"
                  : "text-slate-600 hover:bg-white/5 hover:text-slate-900"
              )}
            >
              {isActive && (
                <motion.div 
                  layoutId="activeTab"
                  className="absolute inset-0 bg-blue-600 rounded-2xl -z-10"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
              
              <div className={cn(
                "flex h-7 w-7 items-center justify-center rounded-lg transition-all duration-500 group-hover:scale-110 group-hover:rotate-6",
                isActive ? "bg-white/20" : "bg-white/5"
              )}>
                <Icon className={cn("h-3.5 w-3.5", isActive ? "text-slate-900" : "text-slate-600 group-hover:text-blue-600")} />
              </div>
              
              <span className="text-[11px] font-black uppercase tracking-widest whitespace-nowrap">
                {tab.label}
              </span>

              {isActive && (
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-1 bg-white/40 rounded-full blur-sm" />
              )}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
