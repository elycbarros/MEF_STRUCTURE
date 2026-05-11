'use client';

import { useMestreStore } from '@/lib/store-mestre';
import { cn } from '@/lib/utils';
import { 
  BrainCircuit,
  Activity,
  ChevronLeft,
  Menu
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { MestreElementType } from '@/lib/mestre-types';

import { MESTRE_MODULES, MESTRE_CATEGORIES } from '@/lib/mestre-modules';
import { EngineeringSettings } from './EngineeringSettings';

export function MestreSidebar() {
  const { selectedElementType, setSelectedElementType, sidebarCollapsed, setSidebarCollapsed } = useMestreStore();

  const sections = MESTRE_CATEGORIES.map(category => ({
    title: category,
    items: MESTRE_MODULES.filter(m => m.category === category)
  }));

  return (
    <aside className={cn(
      "h-screen bg-card border-r border-border/50 flex flex-col z-20 transition-all duration-500 ease-in-out relative",
      sidebarCollapsed ? "w-[80px]" : "w-[300px]"
    )}>
      <div className={cn(
        "p-6 border-b border-border/50 flex items-center transition-all",
        sidebarCollapsed ? "justify-center" : "justify-between"
      )}>
        {!sidebarCollapsed && (
          <h2 className="text-xs font-bold tracking-[0.2em] text-muted-foreground uppercase flex items-center gap-2">
            <BrainCircuit className="w-4 h-4 text-primary" />
            Atlas Mestre
          </h2>
        )}
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="h-8 w-8 text-muted-foreground hover:bg-primary/10 hover:text-primary transition-all"
        >
          {sidebarCollapsed ? <Menu className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-8 overflow-x-hidden">
        {sections.map((section) => (
          <div key={section.title} className="space-y-3">
            {!sidebarCollapsed && (
              <h3 className="px-3 text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 whitespace-nowrap">
                {section.title}
              </h3>
            )}
            <div className="space-y-1">
              {section.items.map((item) => {
                const isSelected = item.id ? selectedElementType === item.id : false;
                return (
                  <button
                    key={`${section.title}-${item.label}`}
                    onClick={() => item.id && setSelectedElementType(item.id as MestreElementType)}
                    title={sidebarCollapsed ? item.label : item.disabled ? 'Em breve' : undefined}
                    disabled={item.disabled}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300",
                      isSelected 
                        ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20 scale-[1.02]" 
                        : "text-muted-foreground hover:bg-muted hover:text-foreground",
                      item.disabled && "cursor-not-allowed opacity-45 hover:bg-transparent hover:text-muted-foreground",
                      sidebarCollapsed && "justify-center px-0"
                    )}
                  >
                    <item.icon className={cn("w-4 h-4 shrink-0", isSelected ? "text-white" : item.disabled ? "text-muted-foreground" : "text-primary")} />
                    {!sidebarCollapsed && (
                      <>
                        <span className="min-w-0 flex-1 truncate text-left">{item.label}</span>
                        {item.disabled && (
                          <span className="rounded-full border border-border/60 px-1.5 py-0.5 text-[8px] font-black uppercase tracking-widest text-muted-foreground">
                            breve
                          </span>
                        )}
                      </>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className={cn(
        "p-6 border-t border-border/50 bg-muted/20 transition-all",
        sidebarCollapsed ? "flex justify-center" : ""
      )}>
        <div className={cn("flex items-center gap-3", sidebarCollapsed ? "justify-center" : "")}>
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0">
            <Activity className="w-4 h-4" />
          </div>
          {!sidebarCollapsed && (
            <div className="truncate">
              <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-tight">Status</p>
              <p className="text-xs font-bold text-foreground flex items-center gap-1.5 truncate">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse shrink-0" />
                V6.2 Elite
              </p>
            </div>
          )}
        </div>
        
        {!sidebarCollapsed && (
          <div className="mt-4 pt-4 border-t border-border/30">
            <EngineeringSettings />
          </div>
        )}
      </div>
    </aside>
  );
}
