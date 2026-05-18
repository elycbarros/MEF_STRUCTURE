'use client';

import React, { useRef, useEffect } from 'react';
import { useMestreStore } from '@/lib/store-mestre';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BrainCircuit } from 'lucide-react';

type RenderFiber = {
  x: number;
  y: number;
  area: number;
  stress: number;
  strain: number;
  type: string;
};

export function FiberMeshView() {
  const { fullResults } = useMestreStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const fiberResults = fullResults?.fiber_results;
  const fibers = fiberResults?.fibers || [];
  const b_m = fullResults?.b_m || 0.4;
  const h_m = fullResults?.h_m || 0.4;

  useEffect(() => {
    if (!canvasRef.current || !fibers.length) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const padding = 40;
    const width = canvas.width - 2 * padding;
    const height = canvas.height - 2 * padding;

    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Scale
    const scale = Math.min(width / b_m, height / h_m);
    const offsetX = (canvas.width - b_m * scale) / 2;
    const offsetY = (canvas.height - h_m * scale) / 2;
    const defaultArea = (b_m * h_m) / Math.max(fibers.length, 1);

    const normalizeFiber = (fiber: any): RenderFiber => {
      if (Array.isArray(fiber)) {
        const [x, y, area, stress, strain, type] = fiber;
        return {
          x: Number(x) || 0,
          y: Number(y) || 0,
          area: Number(area) || defaultArea,
          stress: Number(stress) || 0,
          strain: Number(strain) || 0,
          type: type || 'concrete',
        };
      }

      return {
        x: Number(fiber?.x) || 0,
        y: Number(fiber?.y) || 0,
        area: Number(fiber?.area ?? fiber?.area_m2) || defaultArea,
        stress: Number(fiber?.sig_MPa ?? fiber?.stress ?? fiber?.stress_MPa) || 0,
        strain: Number(fiber?.eps ?? fiber?.strain) || 0,
        type: fiber?.type || 'concrete',
      };
    };

    const normalizedFibers: RenderFiber[] = fibers.map(normalizeFiber);

    // Draw Concrete Fibers
    normalizedFibers.forEach(({ x: fx, y: fy, area: fa, stress, type }) => {
      if (type === 'concrete') {
        const side = Math.sqrt(fa) * scale;
        const px = fx * scale + offsetX + (b_m * scale) / 2 - side / 2;
        const py = -fy * scale + offsetY + (h_m * scale) / 2 - side / 2;

        // Color mapping for stress (MPa)
        // Assume max stress is fcd (approx 20-40 MPa)
        const intensity = Math.min(Math.abs(stress) / 30, 1.0);
        ctx.fillStyle = `rgba(37, 99, 235, ${0.1 + intensity * 0.9})`;
        ctx.fillRect(px, py, side, side);
        
        // Border for high stress
        if (intensity > 0.8) {
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
          ctx.strokeRect(px, py, side, side);
        }
      }
    });

    // Draw Steel Bars
    normalizedFibers.forEach(({ x: fx, y: fy, area: fa, stress, type }) => {
      if (type === 'steel') {
        const px = fx * scale + offsetX + (b_m * scale) / 2;
        const py = -fy * scale + offsetY + (h_m * scale) / 2;
        
        const r = Math.sqrt(fa / Math.PI) * scale * 2; // Scale up for visibility
        ctx.beginPath();
        ctx.arc(px, py, Math.max(r, 4), 0, 2 * Math.PI);
        ctx.fillStyle = stress < 0 ? '#ef4444' : '#10b981'; // Tension vs Compression
        ctx.fill();
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    });

    // Draw Section Border
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 2;
    ctx.strokeRect(offsetX, offsetY, b_m * scale, h_m * scale);

  }, [fibers, b_m, h_m]);

  if (!fibers.length) return null;

  return (
    <Card className="overflow-hidden border-border/50 bg-card/50 backdrop-blur-sm">
      <CardHeader className="p-4 pb-0">
        <CardTitle className="text-xs font-black uppercase tracking-widest flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-primary" />
          Distribuição de Tensões (Fiber Model)
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 flex flex-col items-center">
        <canvas 
          ref={canvasRef} 
          width={300} 
          height={300} 
          className="bg-muted/20 rounded-xl"
        />
        <div className="mt-4 grid grid-cols-2 gap-4 w-full text-[10px] font-bold uppercase tracking-tight">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-600 rounded" />
            <span className="text-muted-foreground">Concreto (Compressão)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full" />
            <span className="text-muted-foreground">Aço (Tração)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
