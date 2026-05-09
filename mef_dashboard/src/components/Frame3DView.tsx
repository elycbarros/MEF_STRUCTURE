"use client";

import React, { useRef, useMemo, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { 
  OrbitControls, 
  PerspectiveCamera, 
  Html,
  PresentationControls,
  Grid,
  Line,
  Text
} from "@react-three/drei";
import * as THREE from "three";

interface Node {
  node: number;
  x: number;
  y: number; // Altura no StrucPy
  z: number;
}

interface Member {
  index: number;
  Node1: number;
  Node2: number;
  b: number; // mm
  d: number; // mm
  Type: string;
  color?: string; // Color override
}

interface Load {
  nodeId: number;
  fx?: number;
  fy?: number;
  fz?: number;
}

interface Frame3DViewProps {
  nodes: Node[];
  members: Member[];
  onSelectMember?: (id: number) => void;
  loads?: Load[];
  reactions?: Load[];
  supportNodeIds?: number[];
}

function LoadArrow({ position, force, color = 0xff0000, label }: { position: [number, number, number], force: [number, number, number], color?: number | string, label?: string }) {
  const direction = new THREE.Vector3(...force).normalize();
  const length = 1.2; // Fixed length for better visibility
  if (force.every(v => v === 0)) return null;

  // Offset position so the arrow tip touches the node (pushing)
  const offsetPosition = new THREE.Vector3(...position).sub(direction.clone().multiplyScalar(length));

  return (
    <group position={offsetPosition.toArray()}>
      <arrowHelper 
        args={[direction, new THREE.Vector3(0, 0, 0), length, color, 0.2, 0.1]} 
      />
      {label && (
        <Text
          position={direction.clone().multiplyScalar(-0.3).toArray()}
          fontSize={0.25}
          color={color}
          anchorX="center"
          anchorY="middle"
          fontWeight="bold"
        >
          {label}
        </Text>
      )}
    </group>
  );
}

export default function Frame3DView({ nodes, members, onSelectMember, loads = [], reactions = [], supportNodeIds }: Frame3DViewProps) {
  const [hovered, setHovered] = useState<number | null>(null);
  const [showPillars, setShowPillars] = useState(true);
  const [showBeams, setShowBeams] = useState(true);
  const [showLabels, setShowLabels] = useState(true);

  // Centralizar o modelo
  const center = useMemo(() => {
    if (nodes.length === 0) return new THREE.Vector3(0, 0, 0);
    const sumX = nodes.reduce((acc, n) => acc + n.x, 0);
    const sumY = nodes.reduce((acc, n) => acc + n.y, 0);
    const sumZ = nodes.reduce((acc, n) => acc + n.z, 0);
    return new THREE.Vector3(sumX / nodes.length, sumY / nodes.length, sumZ / nodes.length);
  }, [nodes]);

  return (
    <div className="w-full h-full bg-slate-900 overflow-hidden relative group shadow-2xl">
      <div className="absolute top-4 left-4 z-10">
        <div className="bg-white/10 backdrop-blur-md p-3 rounded-xl border border-white/20">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-1">Modelo Analítico 3D</h3>
          <p className="text-[10px] text-slate-700">Pórtico Espacial (StrucPy Engine)</p>
        </div>
      </div>

      <div className="absolute top-4 right-4 z-20 flex flex-col gap-2 bg-white/80 backdrop-blur-md p-3 rounded-xl border border-black/10 shadow-sm">
        <label className="flex items-center gap-2 text-[10px] font-bold text-slate-800 cursor-pointer">
          <input type="checkbox" checked={showPillars} onChange={e => setShowPillars(e.target.checked)} className="accent-indigo-500" />
          PILARES
        </label>
        <label className="flex items-center gap-2 text-[10px] font-bold text-slate-800 cursor-pointer">
          <input type="checkbox" checked={showBeams} onChange={e => setShowBeams(e.target.checked)} className="accent-indigo-500" />
          VIGAS
        </label>
        <label className="flex items-center gap-2 text-[10px] font-bold text-slate-800 cursor-pointer">
          <input type="checkbox" checked={showLabels} onChange={e => setShowLabels(e.target.checked)} className="accent-indigo-500" />
          LABELS
        </label>
      </div>

      <Canvas shadows camera={{ position: [10, 10, 10], fov: 35 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[20, 20, 20]} intensity={1} />
        <spotLight position={[-20, 40, 20]} angle={0.15} penumbra={1} intensity={2} castShadow />
        
        <PresentationControls
          global
          speed={1}
          damping={0.25}
          snap
          rotation={[0, 0.3, 0]}
          polar={[-Math.PI / 3, Math.PI / 3]}
          azimuth={[-Math.PI / 1.4, Math.PI / 1.4]}
        >
          <group position={[-center.x, -center.y, -center.z]}>
            {members.map((m, i) => {
              const n1 = nodes.find(n => n.node === m.Node1);
              const n2 = nodes.find(n => n.node === m.Node2);
              if (!n1 || !n2) return null;
              
              const isPillar = m.Type === "Column";
              if (isPillar && !showPillars) return null;
              if (!isPillar && !showBeams) return null;

              const memberColor = m.color || (hovered === m.index ? "#6366f1" : isPillar ? "#475569" : "#94a3b8");

              return (
                <group key={m.index}>
                  <Line
                    points={[[n1.x, n1.y, n1.z], [n2.x, n2.y, n2.z]]}
                    color={memberColor}
                    lineWidth={hovered === m.index ? 5 : 2}
                    onPointerOver={() => setHovered(m.index)}
                    onPointerOut={() => setHovered(null)}
                    onClick={() => onSelectMember?.(m.index)}
                  />
                  {showLabels && (
                    <Text
                      position={[(n1.x + n2.x) / 2, (n1.y + n2.y) / 2 + 0.2, (n1.z + n2.z) / 2]}
                      fontSize={0.2}
                      color="#f1f5f9"
                      anchorX="center"
                      anchorY="middle"
                    >
                      {m.index}
                    </Text>
                  )}
                </group>
              );
            })}
            
            {/* Loads */}
            {loads.map((l, i) => {
              const node = nodes.find(n => n.node === l.nodeId);
              if (!node) return null;
              const val = Math.sqrt((l.fx||0)**2 + (l.fy||0)**2 + (l.fz||0)**2);
              return (
                <LoadArrow 
                  key={`load-${i}`} 
                  position={[node.x, node.y, node.z]} 
                  force={[l.fx || 0, l.fy || 0, l.fz || 0]} 
                  label={`${val.toFixed(1)} kN`}
                />
              );
            })}

            {/* Reactions */}
            {reactions.map((r, i) => {
              const node = nodes.find(n => n.node === r.nodeId);
              if (!node) return null;
              const val = Math.sqrt((r.fx||0)**2 + (r.fy||0)**2 + (r.fz||0)**2);
              return (
                <LoadArrow 
                  key={`reaction-${i}`} 
                  position={[node.x, node.y, node.z]} 
                  force={[r.fx || 0, r.fy || 0, r.fz || 0]} 
                  color="#10b981" // Emerald-500
                  label={`${val.toFixed(1)} kN`}
                />
              );
            })}

            {/* Node Labels */}
            {showLabels && nodes.map(n => (
              <Text
                key={`node-label-${n.node}`}
                position={[n.x, n.y + 0.25, n.z]}
                fontSize={0.15}
                color="#cbd5e1"
                anchorX="center"
                anchorY="middle"
                fontWeight="bold"
              >
                {n.node}
              </Text>
            ))}

            {/* Apoios */}
            {nodes.filter(n => supportNodeIds ? supportNodeIds.includes(n.node) : n.y === 0).map(n => (
              <mesh key={`sup-${n.node}`} position={[n.x, -0.1, n.z]}>
                <cylinderGeometry args={[0.3, 0.4, 0.2, 4]} />
                <meshStandardMaterial color="#e74c3c" />
              </mesh>
            ))}
          </group>
        </PresentationControls>

        <Grid
          infiniteGrid
          fadeDistance={50}
          fadeStrength={5}
          cellSize={1}
          sectionSize={5}
          sectionColor="#334155"
          cellColor="#1e293b"
        />
        
        <OrbitControls makeDefault enableDamping dampingFactor={0.05} />
      </Canvas>

      <div className="absolute bottom-4 right-4 flex flex-col gap-2">
        <div className="bg-white/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-200 text-[10px] text-slate-900/80">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
            <span>Tração (Tension)</span>
          </div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full bg-rose-500"></div>
            <span>Compressão (Compression)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
            <span>Reação de Apoio</span>
          </div>
        </div>
      </div>
    </div>
  );
}
