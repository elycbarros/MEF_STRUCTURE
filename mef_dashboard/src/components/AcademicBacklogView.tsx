"use client";

import React from "react";
import { AlertTriangle, ArrowRight, ClipboardCheck, Target } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AcademicTabId } from "@/hooks/useProjectState";

type BacklogStatus = "todo" | "doing" | "done";

interface BacklogItem {
  id: string;
  title: string;
  module: string;
  outcome: string;
  tab: AcademicTabId;
  systemType?: "radier" | "laje";
  priority: "Aula" | "Lista" | "Pesquisa";
  status: BacklogStatus;
}

interface AcademicBacklogViewProps {
  setActiveTab: (tab: AcademicTabId) => void;
  setSystemType: (type: "radier" | "laje") => void;
}

const statusConfig: Record<BacklogStatus, { label: string; className: string }> = {
  todo: { label: "A fazer", className: "border-slate-200 bg-slate-50 text-slate-600" },
  doing: { label: "Em aula", className: "border-blue-200 bg-blue-50 text-blue-700" },
  done: { label: "Concluido", className: "border-emerald-200 bg-emerald-50 text-emerald-700" },
};

export const academicBacklogSeed: BacklogItem[] = [
  {
    id: "radier-winkler",
    title: "Modelar radier em base elastica",
    module: "Radier",
    outcome: "Interpretar kv, recalque, pressao no solo e consistencia de Winkler.",
    tab: "geometria",
    systemType: "radier",
    priority: "Aula",
    status: "doing",
  },
  {
    id: "laje-isolada",
    title: "Resolver laje isolada academica",
    module: "Laje",
    outcome: "Comparar apoio discreto, carga distribuida, flecha e armadura minima.",
    tab: "geometria",
    systemType: "laje",
    priority: "Aula",
    status: "todo",
  },
  {
    id: "viga-blackboard",
    title: "Dimensionar viga no quadro negro",
    module: "Viga",
    outcome: "Percorrer momento, cortante, ELS, ancoragem e cobrimento no roteiro MESTRE.",
    tab: "vigas",
    priority: "Lista",
    status: "todo",
  },
  {
    id: "pilar-esbeltez",
    title: "Estudar pilar e efeitos de 2a ordem",
    module: "Pilar",
    outcome: "Ver esbeltez, excentricidade minima, taxa de armadura e decisao final.",
    tab: "pilares_isolados",
    priority: "Lista",
    status: "todo",
  },
  {
    id: "reservatorio-contencao",
    title: "Explorar reservatorios e elementos especiais",
    module: "Especiais",
    outcome: "Conectar empuxos, durabilidade e detalhamento em pecas hidraulicas.",
    tab: "especiais",
    priority: "Pesquisa",
    status: "todo",
  },
  {
    id: "radier-estaqueado",
    title: "Preparar pesquisa de radier estaqueado",
    module: "Pesquisa",
    outcome: "Separar solo, radier, estacas, contato e variaveis dominantes para modulo futuro.",
    tab: "geometria",
    systemType: "radier",
    priority: "Pesquisa",
    status: "todo",
  },
];

export function getAcademicBacklogProgress() {
  if (typeof window === "undefined") {
    return { doneCount: 0, total: academicBacklogSeed.length, progress: 0 };
  }

  try {
    const stored = window.localStorage.getItem("engine-mestre-backlog");
    const saved = stored ? (JSON.parse(stored) as Array<Pick<BacklogItem, "id" | "status">>) : [];
    const statusById = new Map(saved.map((item) => [item.id, item.status]));
    const items = academicBacklogSeed.map((item) => ({ ...item, status: statusById.get(item.id) ?? item.status }));
    const doneCount = items.filter((item) => item.status === "done").length;
    return { doneCount, total: items.length, progress: Math.round((doneCount / items.length) * 100) };
  } catch {
    return { doneCount: 0, total: academicBacklogSeed.length, progress: 0 };
  }
}

export function AcademicBacklogView({ setActiveTab, setSystemType }: AcademicBacklogViewProps) {
  const [backlog, setBacklog] = React.useState<BacklogItem[]>(() => {
    if (typeof window === "undefined") return academicBacklogSeed;
    const stored = window.localStorage.getItem("engine-mestre-backlog");
    if (!stored) return academicBacklogSeed;
    try {
      const saved = JSON.parse(stored) as Array<Pick<BacklogItem, "id" | "status">>;
      const statusById = new Map(saved.map((item) => [item.id, item.status]));
      return academicBacklogSeed.map((item) => ({ ...item, status: statusById.get(item.id) ?? item.status }));
    } catch {
      window.localStorage.removeItem("engine-mestre-backlog");
      return academicBacklogSeed;
    }
  });

  React.useEffect(() => {
    window.localStorage.setItem(
      "engine-mestre-backlog",
      JSON.stringify(backlog.map(({ id, status }) => ({ id, status })))
    );
  }, [backlog]);

  const cycleStatus = (id: string) => {
    const order: BacklogStatus[] = ["todo", "doing", "done"];
    setBacklog((items) =>
      items.map((item) => {
        if (item.id !== id) return item;
        const nextIndex = (order.indexOf(item.status) + 1) % order.length;
        return { ...item, status: order[nextIndex] };
      })
    );
  };

  const openBacklogItem = (item: BacklogItem) => {
    if (item.systemType) setSystemType(item.systemType);
    setActiveTab(item.tab);
  };

  const doneCount = backlog.filter((item) => item.status === "done").length;
  const activeItem = backlog.find((item) => item.status === "doing") ?? backlog.find((item) => item.status === "todo");
  const progress = Math.round((doneCount / backlog.length) * 100);

  return (
    <div className="space-y-6 py-4">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-600">Engine MESTRE</h3>
          <h2 className="mt-1 text-3xl font-black text-slate-900">Backlog Pedagogico</h2>
          <p className="mt-2 max-w-2xl text-sm font-semibold leading-relaxed text-slate-600">
            Roteiro de aula separado do painel inicial, com progresso, prioridade e acesso direto ao modulo de calculo.
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Progresso</p>
          <p className="mt-1 text-2xl font-black text-slate-950">{progress}%</p>
          <p className="text-xs font-bold text-slate-500">{doneCount}/{backlog.length} concluidos</p>
        </div>
      </div>

      <section className="grid gap-4 lg:grid-cols-[1fr_360px]">
        <div className="rounded-3xl border border-blue-100 bg-blue-50/60 p-5">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-white px-3 py-1 text-[10px] font-black uppercase tracking-widest text-blue-700">
            <ClipboardCheck className="h-3.5 w-3.5" />
            Fila de aprendizagem
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            {backlog.map((item) => {
              const status = statusConfig[item.status];
              return (
                <article key={item.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">{item.module} | {item.priority}</p>
                      <h4 className="mt-1 text-sm font-black text-slate-950">{item.title}</h4>
                    </div>
                    <button
                      type="button"
                      onClick={() => cycleStatus(item.id)}
                      className={cn("shrink-0 rounded-full border px-2 py-1 text-[10px] font-black", status.className)}
                    >
                      {status.label}
                    </button>
                  </div>
                  <p className="mt-3 min-h-10 text-xs font-semibold leading-relaxed text-slate-600">{item.outcome}</p>
                  <button
                    type="button"
                    onClick={() => openBacklogItem(item)}
                    className="mt-4 inline-flex items-center gap-2 text-[10px] font-black uppercase tracking-wider text-blue-700"
                  >
                    Abrir roteiro <ArrowRight className="h-3 w-3" />
                  </button>
                </article>
              );
            })}
          </div>
        </div>

        <aside className="space-y-4 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-950 text-white">
            <Target className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Proxima acao</p>
            <h3 className="mt-2 text-lg font-black text-slate-950">{activeItem?.title ?? "Trilha concluida"}</h3>
            <p className="mt-2 text-xs font-semibold leading-relaxed text-slate-600">
              {activeItem?.outcome ?? "Revise os relatorios gerados e compare os resultados entre os modulos."}
            </p>
          </div>
          <button
            type="button"
            disabled={!activeItem}
            onClick={() => activeItem && openBacklogItem(activeItem)}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-xs font-black text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Continuar aula <ArrowRight className="h-4 w-4" />
          </button>
          <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4">
            <div className="flex items-start gap-2">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-700" />
              <p className="text-[11px] font-bold leading-relaxed text-amber-800">
                Radier estaqueado fica como pesquisa orientada: o modelo fisico muda e nao deve ser tratado como variacao simples do radier liso.
              </p>
            </div>
          </div>
        </aside>
      </section>
    </div>
  );
}
