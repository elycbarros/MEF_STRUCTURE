'use client';

import { useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Grid, Environment, Float, Html } from '@react-three/drei';
import * as THREE from 'three';
import { useMestreStore } from '@/lib/store-mestre';
import type { MestreElementType, SoilLayer } from '@/lib/mestre-types';

function FootingModel() {
  const { params } = useMestreStore();
  const A = params.A_m || 1.5;
  const B = params.B_m || 1.5;
  const H = params.h_m || 0.6;
  const ap = params.ap || 0.2;
  const bp = params.bp || 0.2;

  return (
    <group position={[0, -H/2, 0]}>
      {/* Base da Sapata */}
      <mesh castShadow receiveShadow>
        <boxGeometry args={[A, H, B]} />
        <meshStandardMaterial 
          color="#e5e5e5" 
          transparent 
          opacity={0.7} 
          roughness={0.3}
          metalness={0.1}
        />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(A, H, B)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.3} transparent />
        </lineSegments>
      </mesh>

      {/* Pescoço do Pilar (Stub) */}
      <mesh position={[0, H/2 + 0.5, 0]} castShadow>
        <boxGeometry args={[ap, 1.0, bp]} />
        <meshStandardMaterial color="#d1d1d1" roughness={0.5} />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(ap, 1.0, bp)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.2} transparent />
        </lineSegments>
      </mesh>

      {/* Label de Dimensão */}
      <Html position={[0, H/2 + 1.2, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          {A.toFixed(2)}m x {B.toFixed(2)}m x {H.toFixed(2)}m
        </div>
      </Html>
    </group>
  );
}

function PileModel() {
  const { params } = useMestreStore();
  const radius = (params.diameter || 0.40) / 2;
  const height = params.length || 12.0;
  const layers = params.layers || [];

  return (
    <group>
      {/* Plano de referência da superfície do terreno / cota 0 */}
      <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <circleGeometry args={[radius * 5.5, 64]} />
        <meshStandardMaterial color="#2f855a" transparent opacity={0.16} side={THREE.DoubleSide} />
      </mesh>
      <Html position={[radius * 3.2, 0.08, 0]} center>
        <div className="bg-emerald-600/90 text-white text-[9px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          cota 0 / terreno
        </div>
      </Html>

      {/* Corpo da estaca enterrado: topo na cota 0 e ponta em -L */}
      <mesh castShadow receiveShadow position={[0, -height / 2, 0]}>
        <cylinderGeometry args={[radius, radius, height, 32]} />
        <meshStandardMaterial 
          color="#e5e5e5" 
          transparent 
          opacity={0.7} 
          roughness={0.3}
          metalness={0.1}
        />
        {/* Wireframe edges */}
        <lineSegments>
          <edgesGeometry args={[new THREE.CylinderGeometry(radius, radius, height, 32)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.3} transparent />
        </lineSegments>
      </mesh>

      {/* Camadas de Solo (Representação visual) */}
      <group position={[0, 0, 0]}>
        {layers.map((layer: SoilLayer, i: number) => {
          const layerHeight = layer.thickness_m;
          const layerPos = -(layer.depth_m - layerHeight / 2);
          const color = layer.soil_type === 'areia' ? '#f0e68c' : 
                        layer.soil_type === 'argila' ? '#a52a2a' : 
                        layer.soil_type === 'silte' ? '#d2b48c' : '#808080';
          
          return (
            <mesh key={i} position={[0, layerPos, 0]} receiveShadow>
              <cylinderGeometry args={[radius * 4, radius * 4, layerHeight, 32]} />
              <meshStandardMaterial 
                color={color} 
                transparent 
                opacity={0.15} 
                side={THREE.DoubleSide}
              />
            </mesh>
          );
        })}
      </group>

      {/* Label de Dimensão */}
      <Html position={[0, -height - 0.5, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          Ø { (radius * 2 * 100).toFixed(0) }cm x {height.toFixed(1)}m
        </div>
      </Html>
    </group>
  );
}

function PileCapModel() {
  const { params } = useMestreStore();
  const spacing = params.dist_piles || 1.6;
  const pileRadius = (params.diam_pile || params.diameter || 0.4) / 2;
  const capHeight = (params.d_height || 0.65) * 1.15;
  const capLength = spacing + pileRadius * 4;
  const capWidth = Math.max(0.9, pileRadius * 5);
  const pileLength = Math.min(params.length || 4, 5);
  const ap = params.ap || 0.3;
  const bp = params.bp || 0.3;

  return (
    <group>
      <mesh position={[0, -0.02, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[capLength * 1.35, capWidth * 1.8]} />
        <meshStandardMaterial color="#2f855a" transparent opacity={0.13} side={THREE.DoubleSide} />
      </mesh>

      {/* Bloco semi-enterrado: topo próximo da cota 0 e base abaixo. */}
      <mesh castShadow receiveShadow position={[0, -capHeight / 2, 0]}>
        <boxGeometry args={[capLength, capHeight, capWidth]} />
        <meshStandardMaterial color="#dedede" transparent opacity={0.72} roughness={0.34} />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(capLength, capHeight, capWidth)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.35} transparent />
        </lineSegments>
      </mesh>

      {/* Pilar nasce acima do bloco. */}
      <mesh castShadow position={[0, 0.45, 0]}>
        <boxGeometry args={[ap, 0.9, bp]} />
        <meshStandardMaterial color="#cfcfcf" roughness={0.45} />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(ap, 0.9, bp)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.18} transparent />
        </lineSegments>
      </mesh>

      {/* Duas estacas enterradas sob o bloco. */}
      {[-spacing / 2, spacing / 2].map((x) => (
        <mesh key={x} castShadow receiveShadow position={[x, -capHeight - pileLength / 2, 0]}>
          <cylinderGeometry args={[pileRadius, pileRadius, pileLength, 32]} />
          <meshStandardMaterial color="#e5e5e5" transparent opacity={0.72} roughness={0.3} />
          <lineSegments>
            <edgesGeometry args={[new THREE.CylinderGeometry(pileRadius, pileRadius, pileLength, 32)]} />
            <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.25} transparent />
          </lineSegments>
        </mesh>
      ))}

      <Html position={[0, 1.15, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          Bloco 2 estacas · e = {spacing.toFixed(2)}m
        </div>
      </Html>
    </group>
  );
}

function BeamModel() {
  const { params } = useMestreStore();
  const meshRef = useRef<THREE.Mesh>(null);

  // Dimensões do backend (m)
  const L = params.L || 6.0;
  const b = params.b || 0.20;
  const h = params.h || 0.50;

  return (
    <group>
      {/* Concreto da Viga */}
      <mesh ref={meshRef} castShadow receiveShadow>
        <boxGeometry args={[L, h, b]} />
        <meshStandardMaterial 
          color="#e5e5e5" 
          transparent 
          opacity={0.6} 
          roughness={0.3}
          metalness={0.1}
        />
        
        {/* Wireframe edges para definição macOS style */}
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(L, h, b)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.3} transparent />
        </lineSegments>
      </mesh>

      {/* Armaduras Longitudinais (Cilindros simplificados) */}
      <group position={[0, 0, 0]}>
        {/* Barra Inferior Esq */}
        <mesh position={[0, -h/2 + 0.05, -b/2 + 0.05]} rotation={[0, 0, Math.PI/2]}>
          <cylinderGeometry args={[0.006, 0.006, L - 0.1]} />
          <meshStandardMaterial color="#FF9500" metalness={0.8} roughness={0.2} />
        </mesh>
        {/* Barra Inferior Dir */}
        <mesh position={[0, -h/2 + 0.05, b/2 - 0.05]} rotation={[0, 0, Math.PI/2]}>
          <cylinderGeometry args={[0.006, 0.006, L - 0.1]} />
          <meshStandardMaterial color="#FF9500" metalness={0.8} roughness={0.2} />
        </mesh>
        {/* Barra Superior Esq */}
        <mesh position={[0, h/2 - 0.05, -b/2 + 0.05]} rotation={[0, 0, Math.PI/2]}>
          <cylinderGeometry args={[0.004, 0.004, L - 0.1]} />
          <meshStandardMaterial color="#FF9500" metalness={0.8} roughness={0.2} />
        </mesh>
        {/* Barra Superior Dir */}
        <mesh position={[0, h/2 - 0.05, b/2 - 0.05]} rotation={[0, 0, Math.PI/2]}>
          <cylinderGeometry args={[0.004, 0.004, L - 0.1]} />
          <meshStandardMaterial color="#FF9500" metalness={0.8} roughness={0.2} />
        </mesh>
      </group>

      {/* Estribos (Anéis simplificados a cada 1m para demo) */}
      {[...Array(Math.floor(L))].map((_, i) => (
        <mesh key={i} position={[-(L/2) + i + 0.5, 0, 0]}>
          <boxGeometry args={[0.005, h - 0.04, b - 0.04]} />
          <meshStandardMaterial color="#FF9500" wireframe />
        </mesh>
      ))}

      {/* Label de Dimensão */}
      <Html position={[0, h/2 + 0.2, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          {L.toFixed(2)}m x {h.toFixed(2)}m x {b.toFixed(2)}m
        </div>
      </Html>
    </group>
  );
}

function ColumnModel() {
  const { params } = useMestreStore();
  const b = params.b || 0.4;
  const h = params.h || 0.4;
  const height = params.L_free || 3.0;

  return (
    <group position={[0, height / 2 - 1, 0]}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[b, height, h]} />
        <meshStandardMaterial color="#e5e5e5" transparent opacity={0.68} roughness={0.35} />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(b, height, h)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.35} transparent />
        </lineSegments>
      </mesh>

      {[-1, 1].flatMap((sx) =>
        [-1, 1].map((sz) => (
          <mesh key={`${sx}-${sz}`} position={[sx * (b / 2 - 0.05), 0, sz * (h / 2 - 0.05)]}>
            <cylinderGeometry args={[0.008, 0.008, height - 0.1, 16]} />
            <meshStandardMaterial color="#FF9500" metalness={0.8} roughness={0.2} />
          </mesh>
        ))
      )}

      <Html position={[0, height / 2 + 0.35, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          Pilar {b.toFixed(2)}m x {h.toFixed(2)}m
        </div>
      </Html>
    </group>
  );
}

function SlabModel() {
  const { params } = useMestreStore();
  const lx = params.Lx || params.L || 5.0;
  const ly = params.Ly || 4.0;
  const h = params.h || 0.16;

  return (
    <group>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[lx, h, ly]} />
        <meshStandardMaterial color="#e5e5e5" transparent opacity={0.6} roughness={0.3} />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(lx, h, ly)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.25} transparent />
        </lineSegments>
      </mesh>

      <gridHelper args={[Math.max(lx, ly), 10, '#007AFF', '#94a3b8']} position={[0, h / 2 + 0.01, 0]} />

      <Html position={[0, h / 2 + 0.45, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          Laje {lx.toFixed(1)}m x {ly.toFixed(1)}m
        </div>
      </Html>
    </group>
  );
}

function StairModel() {
  const { params } = useMestreStore();
  const run = params.L_horizontal || params.L || 4;
  const rise = params.H || 2.8;
  const width = params.width || 1.2;
  const steps = 8;

  return (
    <group rotation={[0, -0.35, 0]}>
      {Array.from({ length: steps }).map((_, i) => {
        const tread = run / steps;
        const stepRise = rise / steps;
        return (
          <mesh key={i} castShadow receiveShadow position={[-run / 2 + tread * i + tread / 2, stepRise * i + stepRise / 2, 0]}>
            <boxGeometry args={[tread, stepRise, width]} />
            <meshStandardMaterial color="#dedede" transparent opacity={0.72} roughness={0.34} />
            <lineSegments>
              <edgesGeometry args={[new THREE.BoxGeometry(tread, stepRise, width)]} />
              <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.24} transparent />
            </lineSegments>
          </mesh>
        );
      })}
      <Html position={[0, rise + 0.35, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          Escada · {run.toFixed(1)}m
        </div>
      </Html>
    </group>
  );
}

function RetainingWallModel() {
  const { params } = useMestreStore();
  const height = params.h_wall || params.h || 4;
  const base = params.b_base || 2.5;
  const thickness = 0.28;

  return (
    <group>
      <mesh castShadow receiveShadow position={[0, -0.12, 0]}>
        <boxGeometry args={[base, 0.24, 1.2]} />
        <meshStandardMaterial color="#d9d9d9" transparent opacity={0.72} roughness={0.35} />
      </mesh>
      <mesh castShadow receiveShadow position={[-base * 0.18, height / 2 - 0.05, 0]}>
        <boxGeometry args={[thickness, height, 1.2]} />
        <meshStandardMaterial color="#d9d9d9" transparent opacity={0.72} roughness={0.35} />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(thickness, height, 1.2)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.28} transparent />
        </lineSegments>
      </mesh>
      <mesh position={[base * 0.22, height / 2 - 0.1, 0]} receiveShadow>
        <boxGeometry args={[base * 0.45, height * 0.9, 1.15]} />
        <meshStandardMaterial color="#8b7355" transparent opacity={0.22} roughness={0.8} />
      </mesh>
      <Html position={[0, height + 0.35, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          Muro de arrimo · H = {height.toFixed(1)}m
        </div>
      </Html>
    </group>
  );
}

function ReservoirModel() {
  const { params } = useMestreStore();
  const length = params.length || 5;
  const width = params.width || 3;
  const depth = params.depth || 3;

  return (
    <group>
      <mesh castShadow receiveShadow position={[0, depth / 2, 0]}>
        <boxGeometry args={[length, depth, width]} />
        <meshStandardMaterial color="#d9e8ff" transparent opacity={0.28} roughness={0.18} />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(length, depth, width)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.55} transparent />
        </lineSegments>
      </mesh>
      <mesh position={[0, depth * 0.42, 0]}>
        <boxGeometry args={[length * 0.92, depth * 0.55, width * 0.92]} />
        <meshStandardMaterial color="#38bdf8" transparent opacity={0.22} roughness={0.1} />
      </mesh>
      <Html position={[0, depth + 0.4, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          Reservatório · {length.toFixed(1)}m x {width.toFixed(1)}m
        </div>
      </Html>
    </group>
  );
}

function CorbelModel() {
  const { params } = useMestreStore();
  const a = params.a_dist || 0.35;
  const d = params.d_eff || 0.55;

  return (
    <group>
      <mesh castShadow receiveShadow position={[-0.35, 0.6, 0]}>
        <boxGeometry args={[0.35, 1.8, 0.6]} />
        <meshStandardMaterial color="#d9d9d9" transparent opacity={0.72} roughness={0.35} />
      </mesh>
      <mesh castShadow receiveShadow position={[a / 2, 0.2, 0]}>
        <boxGeometry args={[a + 0.35, d, 0.6]} />
        <meshStandardMaterial color="#dedede" transparent opacity={0.72} roughness={0.35} />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(a + 0.35, d, 0.6)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.3} transparent />
        </lineSegments>
      </mesh>
      <Html position={[0.1, 1.65, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          Consolo curto
        </div>
      </Html>
    </group>
  );
}

function GerberToothModel() {
  return (
    <group>
      <mesh castShadow receiveShadow position={[-0.65, 0, 0]}>
        <boxGeometry args={[1.4, 0.45, 0.55]} />
        <meshStandardMaterial color="#dedede" transparent opacity={0.72} roughness={0.35} />
      </mesh>
      <mesh castShadow receiveShadow position={[0.25, -0.18, 0]}>
        <boxGeometry args={[0.7, 0.28, 0.55]} />
        <meshStandardMaterial color="#dedede" transparent opacity={0.72} roughness={0.35} />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(0.7, 0.28, 0.55)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.35} transparent />
        </lineSegments>
      </mesh>
      <Html position={[0, 0.65, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          Dente Gerber
        </div>
      </Html>
    </group>
  );
}

function DeepBeamModel() {
  const { params } = useMestreStore();
  const span = params.L || 4;
  const height = params.h || 3;

  return (
    <group>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[span, height, 0.42]} />
        <meshStandardMaterial color="#dedede" transparent opacity={0.72} roughness={0.35} />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(span, height, 0.42)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.3} transparent />
        </lineSegments>
      </mesh>
      <Html position={[0, height / 2 + 0.35, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
          Viga parede
        </div>
      </Html>
    </group>
  );
}

function GenericSpecialModel({ type }: { type: MestreElementType }) {
  return (
    <group>
      <mesh castShadow receiveShadow>
        <dodecahedronGeometry args={[0.9, 0]} />
        <meshStandardMaterial color="#d9d9d9" transparent opacity={0.7} roughness={0.4} />
        <lineSegments>
          <edgesGeometry args={[new THREE.DodecahedronGeometry(0.9, 0)]} />
          <lineBasicMaterial color="#007AFF" linewidth={1} opacity={0.35} transparent />
        </lineSegments>
      </mesh>
      <Html position={[0, 1.25, 0]} center>
        <div className="bg-primary/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm whitespace-nowrap capitalize">
          {type.replace('_', ' ')}
        </div>
      </Html>
    </group>
  );
}

export function Beam3DView() {
  const { selectedElementType } = useMestreStore();
  const model = selectedElementType === 'pile' ? (
    <PileModel />
  ) : selectedElementType === 'pile_cap' ? (
    <PileCapModel />
  ) : selectedElementType === 'footing' ? (
    <FootingModel />
  ) : selectedElementType === 'column' ? (
    <ColumnModel />
  ) : selectedElementType === 'slab' ? (
    <SlabModel />
  ) : selectedElementType === 'stair' || selectedElementType === 'helical_stairs' ? (
    <StairModel />
  ) : selectedElementType === 'concrete_wall' ? (
    <RetainingWallModel />
  ) : selectedElementType === 'retaining_wall' ? (
    <RetainingWallModel />
  ) : selectedElementType === 'reservoir' ? (
    <ReservoirModel />
  ) : selectedElementType === 'corbel' ? (
    <CorbelModel />
  ) : selectedElementType === 'gerber_tooth' ? (
    <GerberToothModel />
  ) : selectedElementType === 'deep_beam' ? (
    <DeepBeamModel />
  ) : selectedElementType === 'beam' ? (
    <BeamModel />
  ) : (
    <GenericSpecialModel type={selectedElementType} />
  );

  return (
    <div className="w-full h-full bg-[#f8f9fa] dark:bg-[#0a0a0a] rounded-2xl overflow-hidden relative border border-border/50">
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[5, 3, 5]} fov={40} />
        <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 1.75} />
        
        <ambientLight intensity={1.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={2} castShadow />
        <pointLight position={[-10, -10, -10]} intensity={1} />
        
        {selectedElementType === 'pile' || selectedElementType === 'pile_cap' ? (
          model
        ) : (
          <Float speed={1.5} rotationIntensity={0.1} floatIntensity={0.2}>
            {model}
          </Float>
        )}

        <Grid 
          renderOrder={-1} 
          position={[0, selectedElementType === 'pile' || selectedElementType === 'pile_cap' ? 0 : -1, 0]}
          infiniteGrid 
          cellSize={1} 
          sectionSize={5} 
          sectionThickness={1.5} 
          sectionColor="#007AFF" 
          fadeDistance={30} 
        />
        
        <Environment preset="city" />
      </Canvas>

      <div className="absolute bottom-4 left-4 flex flex-col gap-1">
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Viewport Mestre</span>
        <span className="text-xs font-medium text-primary">Modelo Geométrico 1:1</span>
      </div>
    </div>
  );
}
