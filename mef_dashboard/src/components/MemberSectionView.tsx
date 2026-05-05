import React from 'react';

interface MemberSectionViewProps {
  b: number; // cm
  h: number; // cm
  as_top?: number; // cm2
  as_bottom?: number; // cm2
  type: 'beam' | 'pillar';
  title?: string;
}

import { formatNumberBR } from '@/lib/utils';

export default function MemberSectionView({ b, h, as_top = 0, as_bottom = 0, type, title }: MemberSectionViewProps) {
  // Escala para o SVG (ajustar para caber em 200x200)
  const scale = 150 / Math.max(b, h);
  const width = b * scale;
  const height = h * scale;
  const offsetX = (200 - width) / 2;
  const offsetY = (200 - height) / 2;

  // Cálculo simplificado de número de barras (assumindo Ø10 = 0.785 cm2)
  const num_top = Math.max(2, Math.ceil(as_top / 0.8));
  const num_bottom = Math.max(2, Math.ceil(as_bottom / 0.8));

  return (
    <div className="flex flex-col items-center p-4 bg-white rounded-2xl border border-black/5 shadow-sm">
      {title && <h5 className="text-[10px] font-bold text-apple-text uppercase mb-4">{title}</h5>}
      
      <svg width="200" height="200" viewBox="0 0 200 200" className="drop-shadow-sm">
        {/* Seção de Concreto */}
        <rect 
          x={offsetX} y={offsetY} width={width} height={height} 
          fill="#f1f5f9" stroke="#94a3b8" strokeWidth="2"
        />
        
        {/* Estribo (Offset de 3cm) */}
        <rect 
          x={offsetX + 3 * scale} y={offsetY + 3 * scale} 
          width={width - 6 * scale} height={height - 6 * scale} 
          fill="none" stroke="#64748b" strokeWidth="1" strokeDasharray="2,2"
        />

        {/* Barras Superiores */}
        {[...Array(num_top)].map((_, i) => (
          <circle 
            key={`top-${i}`}
            cx={offsetX + 5 * scale + (i * (width - 10 * scale) / (num_top - 1))}
            cy={offsetY + 5 * scale}
            r="3" fill="#1e293b"
          />
        ))}

        {/* Barras Inferiores */}
        {[...Array(num_bottom)].map((_, i) => (
          <circle 
            key={`bot-${i}`}
            cx={offsetX + 5 * scale + (i * (width - 10 * scale) / (num_bottom - 1))}
            cy={offsetY + height - 5 * scale}
            r="3" fill="#1e293b"
          />
        ))}

        {/* Dimensões */}
        <text x={offsetX + width / 2} y={offsetY - 5} textAnchor="middle" fontSize="10" fill="#64748b">{formatNumberBR(b, 0)} cm</text>
        <text x={offsetX - 5} y={offsetY + height / 2} textAnchor="end" fontSize="10" fill="#64748b" transform={`rotate(-90, ${offsetX - 5}, ${offsetY + height / 2})`}>{formatNumberBR(h, 0)} cm</text>
      </svg>

      <div className="mt-4 grid grid-cols-2 gap-4 w-full">
        <div className="text-center">
          <p className="text-[8px] text-apple-muted uppercase">As Superior</p>
          <p className="text-xs font-bold">{formatNumberBR(as_top)} cm²</p>
        </div>
        <div className="text-center">
          <p className="text-[8px] text-apple-muted uppercase">As Inferior</p>
          <p className="text-xs font-bold">{formatNumberBR(as_bottom)} cm²</p>
        </div>
      </div>
    </div>
  );
}
