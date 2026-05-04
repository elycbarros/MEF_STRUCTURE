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
}

export function MainSidebar({ tabs, activeTab, setActiveTab }: MainSidebarProps) {
  return (
    <aside className="col-span-12 rounded-3xl border border-white/60 bg-white/70 p-3 shadow-[0_10px_28px_rgba(0,0,0,0.05)] lg:col-span-3">
      <nav className="space-y-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm font-bold transition ${
                isActive
                  ? "bg-[#1d1d1f] text-white shadow-[0_10px_20px_rgba(0,0,0,0.20)]"
                  : "bg-white/70 text-[#4d5360] hover:bg-white"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
