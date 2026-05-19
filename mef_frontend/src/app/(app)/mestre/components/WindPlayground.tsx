'use client';

import { useCallback } from 'react';
import { Wind, Calculator, Gauge, Shield, Box, Brain, Activity } from 'lucide-react';

import { calculateWind } from '@/lib/api-mestre';
import { type MestreParams } from '@/lib/mestre-types';
import { useMestreStore } from '@/lib/store-mestre';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';


import { MestreDiagram } from './MestreDiagram';

export function WindPlayground() {
  const { 
    params, 
    updateParams, 
    setIsLoading, 
    setError, 
    applyMestreResponse,
    fullResults,
    isLoading,
    error 
  } = useMestreStore();

  const handleCalculate = useCallback(async (currentParams: MestreParams) => {
    setIsLoading(true);
    try {
      const data = await calculateWind(currentParams);
      if (data.success) {
        applyMestreResponse(data);
      } else {
        setError("Falha no cálculo de vento.");
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Erro de conexão com o motor NBR 6123.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [applyMestreResponse, setIsLoading, setError]);

  const updateNumber = (key: keyof MestreParams, value: string) => {
    const parsed = Number(value);
    if (!Number.isNaN(parsed)) updateParams({ [key]: parsed });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Wind className="w-5 h-5 text-primary" />
          Vento (NBR 6123)
        </h3>
        <Button variant="outline" className="h-11 px-4 border-primary/20 hover:bg-primary/5 text-primary">
          <Brain className="w-4 h-4" />
        </Button>
      </div>

      <div className="space-y-4">
        {/* Velocidade e Topografia */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Gauge className="w-3 h-3" />
            Velocidade e Fatores
          </h4>

          <div className="space-y-3">
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">Velocidade Básica V0 (m/s)</Label>
              <Input 
                type="number" 
                value={params.v0 ?? 30} 
                onChange={(e) => updateNumber('v0', e.target.value)} 
                className="h-9 bg-background/50 font-mono font-bold text-primary" 
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Fator S1 (Topográfico)</Label>
                <Select value={params.s1 !== undefined ? (params.s1 === 1 ? "1.0" : params.s1.toString()) : "1.0"} onValueChange={(value) => updateNumber('s1', value)}>
                  <SelectTrigger className="h-9 bg-background/50 text-[11px] truncate">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1.0">Plano/Ondulado (1.0)</SelectItem>
                    <SelectItem value="0.9">Vale Protegido (0.9)</SelectItem>
                    <SelectItem value="1.1">Talude/Morro (1.1)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Fator S3 (Estatístico)</Label>
                <Select value={params.s3 !== undefined ? (params.s3 === 1 ? "1.0" : params.s3.toString()) : "1.0"} onValueChange={(value) => updateNumber('s3', value)}>
                  <SelectTrigger className="h-9 bg-background/50 text-[11px] truncate">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1.1">Gp 1: Hospitais (1.10)</SelectItem>
                    <SelectItem value="1.0">Gp 2: Residencial (1.00)</SelectItem>
                    <SelectItem value="0.95">Gp 3: Industrial (0.95)</SelectItem>
                    <SelectItem value="0.88">Gp 4: Temporário (0.88)</SelectItem>
                    <SelectItem value="0.83">Gp 5: Baixo Risco (0.83)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </div>

        {/* Geometria e Rugosidade */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Box className="w-3 h-3" />
            Rugosidade e Geometria
          </h4>

          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Altura Total (m)</Label>
                <Input type="number" value={params.height ?? 15} onChange={(e) => updateNumber('height', e.target.value)} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Largura Exposta (m)</Label>
                <Input type="number" value={params.width_x ?? 10} onChange={(e) => updateNumber('width_x', e.target.value)} className="h-9 bg-background/50" />
              </div>
            </div>

            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Categoria de Rugosidade</Label>
              <Select value={(params.categoria ?? 2).toString()} onValueChange={(value) => updateNumber('categoria', value)}>
                <SelectTrigger className="h-9 bg-background/50">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Cat I (Mar, campos planos)</SelectItem>
                  <SelectItem value="2">Cat II (Campos com obstáculos)</SelectItem>
                  <SelectItem value="3">Cat III (Vilotas, subúrbios)</SelectItem>
                  <SelectItem value="4">Cat IV (Cidades densas)</SelectItem>
                  <SelectItem value="5">Cat V (Centros metropolitanos)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Efeitos Dinâmicos */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <div className="flex items-center justify-between">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
              <Activity className="w-3 h-3" />
              Análise Dinâmica
            </h4>
            <input 
              type="checkbox"
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
              checked={params.is_dynamic ?? false} 
              onChange={(e) => updateParams({ is_dynamic: e.target.checked })} 
            />
          </div>

          {params.is_dynamic && (
            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Freq. f1 (Hz)</Label>
                <Input type="number" step="0.1" value={params.f1 ?? 0.5} onChange={(e) => updateNumber('f1', e.target.value)} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Zeta (Amort.)</Label>
                <Input type="number" step="0.01" value={params.zeta ?? 0.01} onChange={(e) => updateNumber('zeta', e.target.value)} className="h-9 bg-background/50" />
              </div>
            </div>
          )}
        </div>
      </div>

      <Button onClick={() => handleCalculate(params)} className="w-full macos-button h-12 gap-2" disabled={isLoading}>
        <Calculator className="w-4 h-4" />
        {isLoading ? 'Analisando Ventos...' : 'Calcular Forças'}
      </Button>
      {fullResults?.profile && (
        <MestreDiagram
          title="Perfil de Pressão Dinâmica (q)"
          unit="Pa"
          color="#3b82f6"
          fillColor="rgba(59, 130, 246, 0.1)"
          totalLength={params.height || 30}
          points={fullResults.profile.map((p: any) => ({ x: p.z, y: p.q_Pa }))} // eslint-disable-line @typescript-eslint/no-explicit-any
        />
      )}

      {fullResults?.profile && (
        <WindTowerDiagram
          profile={fullResults.profile}
          height={params.height || 15}
          widthX={params.width_x || 10}
          summary={fullResults.summary}
        />
      )}

      {error && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive">
          <Shield className="w-4 h-4 mt-0.5 shrink-0" />
          <p className="text-xs font-medium leading-relaxed">{error}</p>
        </div>
      )}
    </div>
  );
}

function WindTowerDiagram({
  profile,
  height,
  widthX,
  summary
}: {
  profile: any[]; // eslint-disable-line @typescript-eslint/no-explicit-any
  height: number;
  widthX: number;
  summary: any; // eslint-disable-line @typescript-eslint/no-explicit-any
}) {
  if (!profile || profile.length === 0) return null;

  const svgW = 360;
  const svgH = 460;
  
  const padBottom = 50;
  const padTop = 40;
  const padLeft = 130;
  const towerW = 50; 
  const towerH = svgH - padTop - padBottom; // 370px

  const maxQ = Math.max(...profile.map(p => p.q_Pa), 1);

  // Mapping functions
  const yForZ = (z: number) => svgH - padBottom - (z / height) * towerH;
  const xForQ = (q: number) => padLeft - (q / maxQ) * 75; // 75px max width for curve

  // Building coordinates
  const bLeft = padLeft;
  const bRight = padLeft + towerW;
  const bBase = svgH - padBottom;
  const bTop = padTop;

  // Build pressure profile points sorted by height
  const sortedProfile = [...profile].sort((a, b) => a.z - b.z);
  
  const curvePoints = sortedProfile.map(p => `${xForQ(p.q_Pa).toFixed(1)},${yForZ(p.z).toFixed(1)}`);
  
  // Polygon points to close area against the tower face (bLeft)
  const polygonPoints = [
    `${bLeft},${yForZ(0).toFixed(1)}`,
    ...curvePoints,
    `${bLeft},${yForZ(height).toFixed(1)}`
  ].join(' ');

  const strokePoints = curvePoints.join(' ');

  const fmt = (v: number) => v.toLocaleString('pt-BR', { maximumFractionDigits: 1 });

  // Generate building floor lines (typically every 3m)
  const floorInterval = height <= 15 ? 3 : height <= 30 ? 3 : height <= 60 ? 6 : 10;
  const floors = [];
  for (let z = floorInterval; z < height; z += floorInterval) {
    floors.push(z);
  }
  if (floors.length === 0 || floors[floors.length - 1] !== height) {
    floors.push(height);
  }

  // Qualitative deformed shape points
  // u(z) = delta_max * (z/height)^3
  const deltaMax = 12; // max displacement in pixels
  const deformedPoints = sortedProfile.map(p => {
    const dx = deltaMax * Math.pow(p.z / height, 3);
    return `${(bLeft + dx).toFixed(1)},${yForZ(p.z).toFixed(1)}`;
  });
  const deformedRightPoints = sortedProfile.map(p => {
    const dx = deltaMax * Math.pow(p.z / height, 3);
    return `${(bRight + dx).toFixed(1)},${yForZ(p.z).toFixed(1)}`;
  });

  return (
    <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
          <Wind className="w-3.5 h-3.5 text-primary" />
          Ação Física & Deformada Qualitativa da Torre
        </h4>
        <div className="text-[9px] font-black uppercase tracking-widest text-primary bg-primary/5 px-2 py-0.5 rounded-md border border-primary/10">
          Rajada Dinâmica (G) = {fmt(summary?.g_dynamic ?? 1.0)}
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-6 items-center justify-center bg-background/20 rounded-xl p-3 border border-border/30">
        <div className="relative w-full max-w-[280px]">
          <svg viewBox={`0 0 ${svgW} ${svgH}`} className="w-full h-auto overflow-visible select-none">
            <defs>
              <linearGradient id="windGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.03" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.18" />
              </linearGradient>
              <marker id="arrowhead-wind" markerWidth="6" markerHeight="6" refX="6" refY="3" orient="auto">
                <path d="M0,0 L6,3 L0,6 Z" fill="#3b82f6" />
              </marker>
            </defs>

            {/* Ground line */}
            <line x1={20} y1={bBase} x2={svgW - 25} y2={bBase} stroke="currentColor" className="text-border" strokeWidth="2" />
            {Array.from({ length: 18 }).map((_, i) => {
              const lx = 20 + i * 16;
              return (
                <line
                  key={`hatch-${i}`}
                  x1={lx} y1={bBase} x2={lx - 5} y2={bBase + 5}
                  stroke="currentColor" className="text-muted-foreground/15" strokeWidth="1"
                />
              );
            })}
            <text x={20} y={bBase + 15} fontSize="8" fontWeight="bold" fill="currentColor" className="text-muted-foreground/50 uppercase tracking-wider">TERRENO</text>

            {/* Pressure Profile Area Fill */}
            <polygon points={polygonPoints} fill="url(#windGrad)" />
            {/* Pressure Profile Line */}
            <polyline points={strokePoints} fill="none" stroke="#3b82f6" strokeWidth="1.8" strokeLinecap="round" />

            {/* Concentrated load arrows at slab levels */}
            {floors.map((fz, i) => {
              const y = yForZ(fz);
              const closest = sortedProfile.reduce((prev, curr) => 
                Math.abs(curr.z - fz) < Math.abs(prev.z - fz) ? curr : prev
              );
              const px = xForQ(closest.q_Pa);
              
              return (
                <g key={`arrow-${i}`}>
                  <line 
                    x1={px} y1={y} x2={bLeft - 3} y2={y} 
                    stroke="#3b82f6" strokeWidth="1.5" 
                    markerEnd="url(#arrowhead-wind)" 
                  />
                  {i % 2 === 0 && (
                    <text 
                      x={px - 6} y={y + 3} 
                      textAnchor="end" fontSize="7.5" fontWeight="bold" 
                      fill="currentColor" className="text-blue-500/80 font-mono"
                    >
                      {fmt(closest.q_Pa)} Pa
                    </text>
                  )}
                </g>
              );
            })}

            {/* Undeformed original tower (Ghost/dashed) */}
            <rect 
              x={bLeft} y={bTop} width={towerW} height={towerH} 
              fill="none" stroke="currentColor" className="text-muted-foreground/20" strokeWidth="1.2" strokeDasharray="3 3" 
            />

            {/* Deformed Tower representation under wind action */}
            {/* Left face column */}
            <polyline points={deformedPoints.join(' ')} fill="none" stroke="currentColor" className="text-foreground" strokeWidth="2.2" strokeLinecap="round" />
            {/* Right face column */}
            <polyline points={deformedRightPoints.join(' ')} fill="none" stroke="currentColor" className="text-foreground" strokeWidth="2.2" strokeLinecap="round" />
            {/* Tower Roof top cap */}
            <line 
              x1={bLeft + deltaMax} y1={bTop} 
              x2={bRight + deltaMax} y2={bTop} 
              stroke="currentColor" className="text-foreground" strokeWidth="2.2" 
            />

            {/* Floors slabs in deformed state */}
            {floors.map((fz, i) => {
              const y = yForZ(fz);
              const dx = deltaMax * Math.pow(fz / height, 3);
              return (
                <g key={`deformed-slab-${i}`}>
                  <line 
                    x1={bLeft + dx} y1={y} 
                    x2={bRight + dx} y2={y} 
                    stroke="currentColor" className="text-foreground/50" strokeWidth="1.5" 
                  />
                  {/* Height label on the right */}
                  <text 
                    x={bRight + dx + 8} y={y + 3} 
                    fontSize="8.5" fontWeight="semibold" 
                    fill="currentColor" className="text-muted-foreground"
                  >
                    z = {fz} m
                  </text>
                </g>
              );
            })}

            {/* Title / Height tag */}
            <g transform={`translate(${bLeft + towerW/2 + deltaMax}, ${bTop - 12})`}>
              <text textAnchor="middle" fontSize="9.5" fontWeight="black" fill="currentColor" className="text-primary">
                {height}m (TOPO)
              </text>
            </g>

            {/* Wind text label at bottom left */}
            <g transform="translate(30, 230)">
              <text x={0} y={0} fontSize="9" fontWeight="black" fill="#3b82f6" className="tracking-widest">VENTO</text>
              <path d="M -5 8 L 25 8 M 20 4 L 25 8 L 20 12" stroke="#3b82f6" strokeWidth="1.5" fill="none" />
            </g>
          </svg>
        </div>

        {/* Dynamic Summary Cards */}
        <div className="flex flex-col gap-3 justify-center w-full sm:w-auto shrink-0">
          <div className="bg-background/80 p-2.5 rounded-xl border border-border/50 min-w-[130px]">
            <span className="block text-[8px] font-black uppercase text-muted-foreground tracking-widest leading-none mb-1">Força Total (Vd)</span>
            <span className="text-base font-black text-primary font-mono">
              {fmt(summary?.total_force_kN ?? 0)} <span className="text-[10px] font-bold">kN</span>
            </span>
          </div>

          <div className="bg-background/80 p-2.5 rounded-xl border border-border/50 min-w-[130px]">
            <span className="block text-[8px] font-black uppercase text-muted-foreground tracking-widest leading-none mb-1">Momento na Base</span>
            <span className="text-base font-black text-rose-500 font-mono">
              {fmt(summary?.base_moment_kNm ?? 0)} <span className="text-[10px] font-bold">kNm</span>
            </span>
          </div>

          <div className="bg-background/80 p-2.5 rounded-xl border border-border/50 min-w-[130px]">
            <span className="block text-[8px] font-black uppercase text-muted-foreground tracking-widest leading-none mb-1">Velocidade Máxima (Vk)</span>
            <span className="text-base font-black text-emerald-600 font-mono">
              {fmt(summary?.max_vk ?? 0)} <span className="text-[10px] font-bold">m/s</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

