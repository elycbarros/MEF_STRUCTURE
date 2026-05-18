'use client';

import { useEffect, useMemo, useState } from 'react';
import { Activity, CheckCircle2, CircleAlert, Cpu, RefreshCw } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { BASE_URL, getMestreHealth, type MestreHealth } from '@/lib/api-mestre';
import { useMestreStore } from '@/lib/store-mestre';

type HealthState = 'checking' | 'online' | 'offline';

export function EngineStatusPanel() {
  const { calculationTrace, selectedElementType, isLoading, error } = useMestreStore();
  const [health, setHealth] = useState<MestreHealth | null>(null);
  const [status, setStatus] = useState<HealthState>('checking');
  const [lastCheckedAt, setLastCheckedAt] = useState<Date | null>(null);

  const checkHealth = useMemo(() => {
    return async () => {
      const controller = new AbortController();
      const timeout = window.setTimeout(() => controller.abort(), 3500);
      setStatus('checking');
      try {
        const data = await getMestreHealth(controller.signal);
        setHealth(data);
        setStatus('online');
      } catch {
        setHealth(null);
        setStatus('offline');
      } finally {
        window.clearTimeout(timeout);
        setLastCheckedAt(new Date());
      }
    };
  }, []);

  useEffect(() => {
    void checkHealth();
  }, [checkHealth]);

  const statusLabel = status === 'online' ? 'Engine Online' : status === 'offline' ? 'Engine Offline' : 'Verificando engine';
  const statusColor = status === 'online' ? 'text-emerald-600' : status === 'offline' ? 'text-red-600' : 'text-amber-600';
  const StatusIcon = status === 'online' ? CheckCircle2 : status === 'offline' ? CircleAlert : RefreshCw;
  const solver = calculationTrace?.solver_module || 'Aguardando cálculo';
  const blackboard = calculationTrace?.blackboard_builder || 'Memorial ainda não gerado';
  const checks = [
    calculationTrace?.classical_check ? 'clássico' : null,
    calculationTrace?.mef_check ? 'MEF' : null,
  ].filter(Boolean).join(' + ') || 'sem auditoria executada';

  return (
    <div className="bg-card/50 border border-border/60 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="bg-primary/10 w-10 h-10 rounded-lg flex items-center justify-center shrink-0">
            <StatusIcon className={`w-5 h-5 ${statusColor} ${status === 'checking' ? 'animate-spin' : ''}`} />
          </div>
          <div className="min-w-0">
            <h4 className={`text-sm font-bold ${statusColor}`}>{statusLabel}</h4>
            <p className="text-xs text-muted-foreground truncate">
              {health?.engine ?? 'Atlas Structural Engine'}{health?.version ? ` · v${health.version}` : ''}
            </p>
          </div>
        </div>
        <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0" onClick={() => void checkHealth()} disabled={status === 'checking'}>
          <RefreshCw className={`w-4 h-4 ${status === 'checking' ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-2 text-xs">
        <div className="flex items-start gap-2">
          <Cpu className="w-3.5 h-3.5 mt-0.5 text-muted-foreground shrink-0" />
          <div className="min-w-0">
            <div className="font-semibold text-foreground truncate">{solver}</div>
            <div className="text-muted-foreground truncate">{selectedElementType} · {checks}</div>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <Activity className="w-3.5 h-3.5 mt-0.5 text-muted-foreground shrink-0" />
          <div className="min-w-0">
            <div className="font-semibold text-foreground truncate">{blackboard}</div>
            <div className="text-muted-foreground truncate">
              {isLoading ? 'Cálculo em andamento' : error ? error : lastCheckedAt ? `Último check: ${lastCheckedAt.toLocaleTimeString()}` : BASE_URL}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
