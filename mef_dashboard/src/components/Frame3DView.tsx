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
}

interface Frame3DViewProps {
  nodes: Node[];
  members: Member[];
  onSelectMember?: (id: number) => void;
}

function BeamMember({ member, nodes, onSelect }: { member: Member, nodes: Node[], onSelect?: (id: number) => void }) {
  const n1 = nodes.find(n => n.node === member.Node1);
  const n2 = nodes.find(n => n.node === member.Node2);
  
  if (!n1 || !n2) return null;

  const p1 = new THREE.Vector3(n1.x, n1.y, n1.z);
  const p2 = new THREE.Vector3(n2.x, n2.y, n2.z);
  
  const length = p1.distanceTo(p2);
  const center = p1.clone().add(p2).multiplyScalar(0.5);
  
  // Calcular rotação para alinhar o cilindro/box com os pontos
  const direction = p2.clone().sub(p1).normalize();
  const quaternion = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction);

  const isColumn = member.Type === "Column" || Math.abs(direction.y) > 0.9;
  const color = isColumn ? "#34495e" : "#3498db";

  return (
    <mesh 
      position={center} 
      quaternion={quaternion} 
      onClick={(e) => {
        e.stopPropagation();
        onSelect?.(member.index);
      }}
    >
      <boxGeometry args={[member.b / 1000, length, member.d / 1000]} />
      <meshStandardMaterial color={color} metalness={0.6} roughness={0.4} />
      
      {/* Label para o membro */}
      <Html distanceFactor={15}>
        <div className="bg-black/60 text-white text-[8px] px-1 rounded backdrop-blur-sm pointer-events-none whitespace-nowrap">
          {isColumn ? "P" : "V"}{member.index}
        </div>
      </Html>
    </mesh>
  );
}

export default function Frame3DView({ nodes, members, onSelectMember }: Frame3DViewProps) {
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
    <div className="w-full h-[500px] bg-slate-900 rounded-2xl overflow-hidden relative group shadow-2xl border border-white/10">
      <div className="absolute top-4 left-4 z-10">
        <div className="bg-white/10 backdrop-blur-md p-3 rounded-xl border border-white/20">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-1">Modelo Analítico 3D</h3>
          <p className="text-[10px] text-white/60">Pórtico Espacial (StrucPy Engine)</p>
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

              return (
                <group key={m.index}>
                  <Line
                    points={[[n1.x, n1.y, n1.z], [n2.x, n2.y, n2.z]]}
                    color={hovered === m.index ? "#6366f1" : isPillar ? "#475569" : "#94a3b8"}
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
            
            {/* Apoios */}
            {nodes.filter(n => n.y === 0).map(n => (
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
        <div className="bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 text-[10px] text-white/80">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full bg-[#3498db]"></div>
            <span>Vigas (Beams)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#34495e]"></div>
            <span>Pilares (Columns)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
