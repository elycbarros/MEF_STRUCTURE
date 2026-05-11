import Link from "next/link";
import { LayoutDashboard, Box, Settings, FolderOpen, HelpCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const menuItems = [
  { icon: LayoutDashboard, label: "Mestre", href: "/mestre" },
  { icon: FolderOpen, label: "Projetos", href: "/projects" },
  { icon: Box, label: "Modelos", href: "/models" },
  { icon: Settings, label: "Configurações", href: "/settings" },
];

export default function Sidebar() {
  return (
    <aside className="w-[260px] h-screen macos-vibrancy border-r flex flex-col transition-all duration-300">
      <div className="p-6">
        <h2 className="text-xl font-bold tracking-tight flex items-center gap-2">
          <div className="w-6 h-6 bg-macos-blue rounded-md flex items-center justify-center text-white text-xs">A</div>
          Atlas Engine
        </h2>
      </div>
      <nav className="flex-1 px-4 space-y-1">
        {menuItems.map((item) => (
          <Link
            key={item.label}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              "hover:bg-macos-blue/10 hover:text-macos-blue text-muted-foreground"
            )}
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="p-4 border-t border-border/50">
        <button className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-sm font-medium text-muted-foreground hover:bg-macos-blue/10 hover:text-macos-blue transition-colors">
          <HelpCircle className="w-4 h-4" />
          Ajuda & Suporte
        </button>
      </div>
    </aside>
  );
}
