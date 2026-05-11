import type { TechnicalDiagramData } from '@/lib/mestre-types';

function label(value: unknown, fallback = '-') {
  if (typeof value === 'number') return value.toFixed(value >= 10 ? 0 : 2);
  if (typeof value === 'string') return value;
  return fallback;
}

export function TechnicalDiagram({ data }: { data: TechnicalDiagramData }) {
  const kind = data.kind;
  const v = data.values ?? {};

  return (
    <div className="w-full bg-white dark:bg-zinc-950 rounded-2xl border border-border/50 p-5 shadow-sm overflow-hidden">
      <div className="mb-4 flex items-center justify-between">
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/70">
          Diagrama técnico gerado
        </span>
        <span className="text-[10px] font-bold uppercase text-primary">{data.title}</span>
      </div>
      <svg viewBox="0 0 760 430" className="w-full h-auto text-zinc-900 dark:text-zinc-100">
        <defs>
          <pattern id={`soil-${kind}`} width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="16" stroke="currentColor" strokeOpacity="0.18" strokeWidth="4" />
          </pattern>
          <marker id={`arrow-${kind}`} markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="currentColor" />
          </marker>
        </defs>

        {kind === 'footing' ? (
          <g>
            <rect x="110" y="210" width="540" height="95" fill={`url(#soil-${kind})`} opacity="0.55" />
            <line x1="90" y1="210" x2="670" y2="210" stroke="currentColor" strokeWidth="2" />
            <text x="115" y="197" fontSize="16" fontWeight="700">NIVEL DO TERRENO (NT)</text>
            <rect x="235" y="245" width="290" height="72" fill="none" stroke="currentColor" strokeWidth="3" />
            <rect x="356" y="145" width="58" height="172" fill="none" stroke="currentColor" strokeWidth="3" />
            <rect x="345" y="185" width="80" height="62" fill="none" stroke="currentColor" strokeWidth="3" />
            <path d="M255 278 H505 M255 296 H505 M360 150 V315 M410 150 V315" stroke="currentColor" strokeWidth="2" fill="none" />
            <line x1="235" y1="330" x2="525" y2="330" stroke="currentColor" strokeWidth="4" />
            {Array.from({ length: 7 }).map((_, i) => (
              <line key={i} x1={260 + i * 42} y1="390" x2={260 + i * 42} y2="340" stroke="currentColor" strokeWidth="3" markerEnd={`url(#arrow-${kind})`} />
            ))}
            <line x1="235" y1="350" x2="525" y2="350" stroke="currentColor" strokeWidth="1" />
            <text x="365" y="374" textAnchor="middle" fontSize="16" fontWeight="700">PRESSAO DE CONTATO σ = {label(v.sigma)} kPa</text>
            <text x="548" y="260" fontSize="16" fontWeight="700">SAPATA {label(v.A)} x {label(v.B)} x {label(v.h)} m</text>
            <text x="445" y="152" fontSize="16" fontWeight="700">PILAR / PESCOCO</text>
            <text x="380" y="415" textAnchor="middle" fontSize="20" fontWeight="800">VISTA EM CORTE - SAPATA ISOLADA</text>
          </g>
        ) : kind === 'slab' ? (
          <g>
            <rect x="140" y="115" width="480" height="220" fill="none" stroke="currentColor" strokeWidth="3" />
            <path d="M140 225 C250 270 500 270 620 225" fill="none" stroke="#007AFF" strokeWidth="4" />
            <line x1="140" y1="350" x2="620" y2="350" stroke="currentColor" strokeWidth="2" />
            <text x="380" y="375" textAnchor="middle" fontSize="16" fontWeight="700">Lx = {label(v.Lx)} m / Ly = {label(v.Ly)} m / h = {label(v.h)} m</text>
            <text x="380" y="70" textAnchor="middle" fontSize="20" fontWeight="800">PLACA MEF MINDLIN-REISSNER</text>
          </g>
        ) : kind === 'retaining_wall' ? (
          <g>
            <rect x="120" y="310" width="430" height="45" fill="none" stroke="currentColor" strokeWidth="3" />
            <rect x="245" y="95" width="52" height="260" fill="none" stroke="currentColor" strokeWidth="3" />
            <path d="M300 110 L590 355 H300 Z" fill={`url(#soil-${kind})`} opacity="0.5" stroke="currentColor" strokeWidth="2" />
            <line x1="555" y1="175" x2="330" y2="175" stroke="currentColor" strokeWidth="3" markerEnd={`url(#arrow-${kind})`} />
            <line x1="530" y1="245" x2="330" y2="245" stroke="currentColor" strokeWidth="3" markerEnd={`url(#arrow-${kind})`} />
            <text x="370" y="75" fontSize="18" fontWeight="800">MURO DE ARRIMO H = {label(v.h)} m</text>
          </g>
        ) : kind === 'frame' ? (
          <g>
            <path d="M 200 300 V 150 H 560 V 300" fill="none" stroke="currentColor" strokeWidth="4" />
            <line x1="180" y1="300" x2="220" y2="300" stroke="currentColor" strokeWidth="3" />
            <line x1="540" y1="300" x2="580" y2="300" stroke="currentColor" strokeWidth="3" />
            {/* Hachuras de apoio */}
            <path d="M190 310 L210 300 M200 310 L220 300 M180 310 L200 300" stroke="currentColor" strokeWidth="1" opacity="0.5" />
            <path d="M550 310 L570 300 M560 310 L580 300 M540 310 L560 300" stroke="currentColor" strokeWidth="1" opacity="0.5" />
            
            <path d="M 200 150 L 560 150" stroke="#007AFF" strokeWidth="2" strokeDasharray="4 4" opacity="0.6" />
            <circle cx="200" cy="150" r="6" fill="#007AFF" />
            <circle cx="560" cy="150" r="6" fill="#007AFF" />
            
            <text x="380" y="80" textAnchor="middle" fontSize="22" fontWeight="900" fill="#007AFF">MODELO MATRICIAL 3D</text>
            <text x="380" y="365" textAnchor="middle" fontSize="14" fontWeight="700" opacity="0.7">MÉTODO DA RIGIDEZ DIRETA — ATLAS ENGINE</text>
          </g>
        ) : kind === 'stair' ? (
          <g>
            {Array.from({ length: 8 }).map((_, i) => (
              <path key={i} d={`M ${140 + i * 55} ${315 - i * 25} h55 v${25 * (i + 1)} h-55 Z`} fill="none" stroke="currentColor" strokeWidth="2" />
            ))}
            <line x1="120" y1="335" x2="610" y2="110" stroke="#007AFF" strokeWidth="4" />
            <text x="375" y="380" textAnchor="middle" fontSize="18" fontWeight="800">ESCADA - L = {label(v.L)} m / α = {label(v.alpha)}°</text>
          </g>
        ) : (
          <g>
            <rect x="190" y="120" width="380" height="170" fill="none" stroke="currentColor" strokeWidth="3" />
            <path d="M210 285 C290 210 410 210 550 135" fill="none" stroke="#007AFF" strokeWidth="4" strokeDasharray="8 6" />
            <circle cx="250" cy="250" r="8" fill="currentColor" />
            <circle cx="520" cy="155" r="8" fill="currentColor" />
            <text x="380" y="345" textAnchor="middle" fontSize="18" fontWeight="800">{data.title.toUpperCase()}</text>
          </g>
        )}
      </svg>
    </div>
  );
}
