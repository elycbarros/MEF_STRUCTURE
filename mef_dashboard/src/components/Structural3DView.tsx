"use client";

import React, { useRef, useMemo, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import {
  OrbitControls, 
  PerspectiveCamera, 
  Text, 
  Html,
  Float,
  PresentationControls,
  Stage,
  Grid,
  Environment,
  ContactShadows
} from "@react-three/drei";
import * as THREE from "three";
import { cn } from "@/lib/utils";

interface Node {
  x: number;
  y: number;
  w: number; // deslocamento ou valor para mapa de calor
  reaction?: number;
}

interface Structural3DViewProps {
  Lx: number;
  Ly: number;
  h: number;
  nodes: Node[];
  elements: number[][];
  pillars: Array<{ id: string; x: number; y: number; bx: number; by: number; reaction_kN?: number }>;
  viewMode: "displacements" | "moments" | "reactions";
}

function SlabMesh({ Lx, Ly, h, nodes, elements, viewMode }: any) {
  const meshRef = useRef<THREE.Mesh>(null);

  // Criar geometria customizada da laje
  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(nodes.length * 3);
    const colors = new Float32Array(nodes.length * 3);
    
    const maxW = Math.max(...nodes.map((n: any) => Math.abs(n.w)), 1e-9);
    
    nodes.forEach((node: any, i: number) => {
      positions[i * 3] = node.x - Lx / 2;
      positions[i * 3 + 1] = -node.w * 50; // Escala exagerada para visualização
      positions[i * 3 + 2] = node.y - Ly / 2;
      
      // Cores baseadas no valor - Escala Turbo/Viridis-like
      const t = Math.abs(node.w) / maxW;
      const color = new THREE.Color().setHSL(0.7 * (1 - t), 0.8, 0.5);
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    });

    const indices: number[] = [];
    elements.forEach((el: number[]) => {
      indices.push(el[0], el[1], el[2]);
      indices.push(el[0], el[2], el[3]);
    });

    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geo.setIndex(indices);
    geo.computeVertexNormals();
    return geo;
  }, [nodes, elements, Lx, Ly]);

  return (
    <mesh geometry={geometry} ref={meshRef} castShadow receiveShadow>
      <meshStandardMaterial 
        vertexColors 
        side={THREE.DoubleSide} 
        roughness={0.1} 
        metalness={0.1} 
        envMapIntensity={1}
      />
    </mesh>
  );
}

function Pillar({ x, y, Lx, Ly, h, id, reaction }: any) {
  const [hovered, setHovered] = useState(false);

  return (
    <group position={[x - Lx / 2, 0, y - Ly / 2]}>
      <mesh 
        position={[0, -2, 0]} 
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        castShadow
      >
        <boxGeometry args={[0.4, 4, 0.4]} />
        <meshStandardMaterial color={hovered ? "#3b82f6" : "#2d3436"} metalness={0.9} roughness={0.1} />
      </mesh>
      
      {reaction !== undefined && Math.abs(reaction) > 0.1 && (
        <group position={[0, 0.5, 0]}>
          <mesh position={[0, reaction * 0.005, 0]}>
             <cylinderGeometry args={[0.05, 0.05, Math.abs(reaction) * 0.01, 8]} />
             <meshStandardMaterial color={reaction > 0 ? "#ff2d55" : "#007aff"} emissive={reaction > 0 ? "#ff2d55" : "#007aff"} emissiveIntensity={0.5} />
          </mesh>
          {(hovered || Math.abs(reaction) > 1000) && (
            <Html distanceFactor={10} zIndexRange={[100, 0]}>
              <div className="bg-slate-900/90 text-white text-[9px] px-2 py-1 rounded-lg whitespace-nowrap shadow-2xl backdrop-blur-md border border-white/20 font-black animate-in zoom-in duration-200">
                <span className="opacity-60 mr-2">{id}</span>
                {reaction.toFixed(1)} kN
              </div>
            </Html>
          )}
        </group>
      )}
    </group>
  );
}

export default function Structural3DView({ Lx, Ly, h, nodes, elements, pillars, viewMode }: Structural3DViewProps) {
  const [autoRotate, setAutoRotate] = useState(true);

  return (
    <div className="w-full h-[600px] bg-[#0a0a0a] rounded-3xl overflow-hidden border border-white/5 relative group shadow-2xl">
      <div className="absolute top-6 left-6 z-10 flex flex-col gap-2">
        <div className="bg-black/40 backdrop-blur-xl p-4 rounded-2xl border border-white/10 shadow-2xl">
          <h3 className="text-sm font-black text-white italic tracking-tight mb-1">DIGITAL TWIN MEF</h3>
          <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest">Visualização Paramétrica (50x scale)</p>
          
          <div className="flex gap-2 mt-4">
             <button 
               onClick={() => setAutoRotate(!autoRotate)}
               className={cn(
                 "px-3 py-1 rounded-full text-[9px] font-black uppercase transition-all",
                 autoRotate ? "bg-indigo-600 text-white" : "bg-white/10 text-white/60"
               )}
             >
               Auto-Rotate
             </button>
          </div>
        </div>
      </div>

      <Canvas shadows dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[Lx, Lx * 0.8, Lx]} fov={35} />
        
        <Stage intensity={0.5} environment="city" adjustCamera={false}>
          <group scale={1}>
            <SlabMesh Lx={Lx} Ly={Ly} h={h} nodes={nodes} elements={elements} viewMode={viewMode} />
            {pillars.map((p) => (
              <Pillar key={p.id} {...p} Lx={Lx} Ly={Ly} h={h} reaction={p.reaction_kN} />
            ))}
          </group>
        </Stage>

        <ContactShadows resolution={1024} scale={Lx * 2} blur={2} opacity={0.4} far={10} color="#000000" />
        <Environment preset="city" />
        
        <OrbitControls 
          makeDefault 
          autoRotate={autoRotate}
          autoRotateSpeed={0.5}
          enableDamping 
          dampingFactor={0.05} 
          minDistance={5} 
          maxDistance={150} 
        />
      </Canvas>

      <div className="absolute bottom-6 right-6 flex flex-col gap-2 items-end">
        <div className="flex flex-col gap-1 bg-black/40 backdrop-blur-xl p-3 rounded-2xl border border-white/10 shadow-2xl">
          <div className="flex items-center gap-2 text-[10px] font-black text-white/80">
             <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]"></div>
             Min: {Math.min(...nodes.map(n => n.w)).toFixed(2)} mm
          </div>
          <div className="flex items-center gap-2 text-[10px] font-black text-white/80">
             <div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]"></div>
             Max: {Math.max(...nodes.map(n => n.w)).toFixed(2)} mm
          </div>
        </div>
      </div>
    </div>
  );
}
