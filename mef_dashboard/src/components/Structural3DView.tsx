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
import { Binary, Box, Maximize2, RotateCcw } from "lucide-react";

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
      
      // Cores baseadas no valor - Escala Aero-Space (Deep Blue to Gold)
      const t = Math.abs(node.w) / maxW;
      const color = new THREE.Color();
      if (t < 0.5) {
        color.setHSL(0.6, 0.8, 0.3 + t * 0.4); // Blue tones
      } else {
        color.setHSL(0.1 + (0.5-t)*0.1, 0.9, 0.5); // Gold/Amber tones
      }
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
        roughness={0.2} 
        metalness={0.8} 
        envMapIntensity={0.5}
        transparent
        opacity={0.9}
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
        <boxGeometry args={[0.3, 4, 0.3]} />
        <meshStandardMaterial 
          color={hovered ? "#60a5fa" : "#1e293b"} 
          metalness={1} 
          roughness={0.1} 
          emissive={hovered ? "#1d4ed8" : "#000000"}
          emissiveIntensity={0.5}
        />
      </mesh>
      
      {reaction !== undefined && Math.abs(reaction) > 0.1 && (
        <group position={[0, 0.5, 0]}>
          <mesh position={[0, reaction * 0.005, 0]}>
             <cylinderGeometry args={[0.04, 0.04, Math.abs(reaction) * 0.01, 12]} />
             <meshStandardMaterial color={reaction > 0 ? "#f43f5e" : "#3b82f6"} emissive={reaction > 0 ? "#f43f5e" : "#3b82f6"} emissiveIntensity={1} />
          </mesh>
          {(hovered || Math.abs(reaction) > 1000) && (
            <Html distanceFactor={10} zIndexRange={[100, 0]}>
              <div className="bg-slate-100/90 text-slate-900 text-[10px] px-3 py-1.5 rounded-xl whitespace-nowrap shadow-2xl backdrop-blur-xl border border-slate-200 font-black animate-in zoom-in duration-300">
                <div className="flex items-center gap-2">
                   <span className="opacity-40 font-mono">{id}</span>
                   <span className="text-blue-600">{reaction.toFixed(1)} <span className="text-[8px] opacity-60">kN</span></span>
                </div>
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
    <div className="w-full h-[650px] bg-slate-50 rounded-[3rem] overflow-hidden border border-slate-200 relative group shadow-2xl">
      {/* HUD - Technical Controls */}
      <div className="absolute top-8 left-8 z-10 flex flex-col gap-4">
        <div className="bg-white/80 backdrop-blur-xl p-6 rounded-[2rem] border border-slate-200 shadow-2xl space-y-4">
          <div className="flex items-center gap-3">
             <div className="p-2 bg-blue-500/10 rounded-xl border border-blue-500/20">
                <Box className="w-4 h-4 text-blue-600" />
             </div>
             <div>
                <h3 className="text-xs font-black text-slate-900 tracking-widest uppercase">Digital Twin MEF</h3>
                <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Global Stability Engine</p>
             </div>
          </div>
          
          <div className="h-px bg-white/5" />

          <div className="flex gap-3">
             <button 
               onClick={() => setAutoRotate(!autoRotate)}
               className={cn(
                 "flex items-center gap-2 px-4 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all border",
                 autoRotate 
                  ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-600/20" 
                  : "bg-white/5 border-slate-200 text-slate-600 hover:text-slate-900"
               )}
             >
               <RotateCcw className={cn("w-3 h-3", autoRotate && "animate-spin-slow")} />
               Auto-Rotate
             </button>
             <button className="p-2 bg-white/5 border border-slate-200 rounded-xl text-slate-600 hover:text-slate-900 transition-colors">
                <Maximize2 className="w-4 h-4" />
             </button>
          </div>
        </div>
      </div>

      {/* 3D Canvas */}
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

        <ContactShadows resolution={1024} scale={Lx * 2} blur={2} opacity={0.6} far={10} color="#000000" />
        <Environment preset="city" />
        <Grid 
          infiniteGrid 
          fadeDistance={50} 
          fadeStrength={5} 
          cellSize={1} 
          sectionSize={5} 
          sectionColor="#cbd5e1" 
          cellColor="#e2e8f0" 
        />
        
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

      {/* Metrics Overlay */}
      <div className="absolute bottom-8 right-8 flex flex-col gap-3 items-end">
        <div className="bg-white/60 backdrop-blur-xl p-5 rounded-[2rem] border border-slate-200 shadow-2xl space-y-3">
          <div className="flex items-center gap-3">
             <Binary className="w-3 h-3 text-slate-500" />
             <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Análise de Deformação</p>
          </div>
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-4 text-[11px] font-black text-slate-900">
               <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div>
               <span className="opacity-60 uppercase tracking-widest text-[9px]">MIN:</span> {Math.min(...nodes.map(n => n.w)).toFixed(2)} mm
            </div>
            <div className="flex items-center gap-4 text-[11px] font-black text-slate-900">
               <div className="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]"></div>
               <span className="opacity-60 uppercase tracking-widest text-[9px]">MAX:</span> {Math.max(...nodes.map(n => n.w)).toFixed(2)} mm
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
