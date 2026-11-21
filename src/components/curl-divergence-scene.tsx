"use client";

import { useMemo } from "react";
import * as THREE from "three";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Line } from "@react-three/drei";
import {
  evaluateCustomField,
  vectorFields,
  type VectorFieldId,
} from "@/lib/curl-divergence";

type Props = {
  fieldId: VectorFieldId;
  point: [number, number, number];
  showField: boolean;
  showCurl: boolean;
  showPoint: boolean;
  coefficients: [number, number, number];
};

function Axes() {
  return (
    <>
      <gridHelper args={[8, 16, "#475569", "#263244"]} rotation={[Math.PI / 2, 0, 0]} />
      <Line points={[[-4, 0, 0], [4, 0, 0]]} color="#ef4444" lineWidth={1.5} />
      <Line points={[[0, -4, 0], [0, 4, 0]]} color="#22c55e" lineWidth={1.5} />
      <Line points={[[0, 0, -4], [0, 0, 4]]} color="#3b82f6" lineWidth={1.5} />
    </>
  );
}

function Arrow({
  origin,
  vector,
  color,
  scale = 1,
}: {
  origin: [number, number, number];
  vector: [number, number, number];
  color: string;
  scale?: number;
}) {
  const ox = origin[0], oy = origin[1], oz = origin[2];
  const vx = vector[0], vy = vector[1], vz = vector[2];
  const arrow = useMemo(() => {
    const direction = new THREE.Vector3(vx, vy, vz);
    const length = direction.length();
    if (length < 1e-8) return null;
    direction.normalize();
    return new THREE.ArrowHelper(direction, new THREE.Vector3(ox, oy, oz), Math.min(length * scale, 1.15), color, 0.13, 0.075);
  }, [ox, oy, oz, vx, vy, vz, color, scale]);

  if (!arrow) return null;
  return <primitive object={arrow} />;
}

function FieldArrows({ fieldId, coefficients }: { fieldId: VectorFieldId; coefficients: [number, number, number] }) {
  const a = coefficients[0];
  const b = coefficients[1];
  const c = coefficients[2];

  const arrows = useMemo(() => {
    const result: { origin: [number, number, number]; vector: [number, number, number] }[] = [];
    const field = vectorFields.find((item) => item.id === fieldId);
    for (let x = -2; x <= 2; x += 1) {
      for (let y = -2; y <= 2; y += 1) {
        for (let z = -2; z <= 2; z += 2) {
          const origin: [number, number, number] = [x, y, z];
          const vector = fieldId === "custom"
            ? evaluateCustomField(x, y, z, a, b, c)
            : field?.evaluate(x, y, z) ?? [0, 0, 0];
          result.push({ origin, vector });
        }
      }
    }
    return result;
  }, [fieldId, a, b, c]);

  return <>{arrows.map((item, index) => <Arrow key={index} origin={item.origin} vector={item.vector} color="#38bdf8" scale={0.34} />)}</>;
}

function CurlVector({ fieldId, point }: { fieldId: VectorFieldId; point: [number, number, number] }) {
  const curl = fieldId === "custom"
    ? [0, 0, 0]
    : vectorFields.find((item) => item.id === fieldId)?.curl(...point) ?? [0, 0, 0];
  return <Arrow origin={point} vector={curl as [number, number, number]} color="#fbbf24" scale={0.8} />;
}

function PointMarker({ point }: { point: [number, number, number] }) {
  return <mesh position={point}><sphereGeometry args={[0.075, 20, 20]} /><meshStandardMaterial color="#f472b6" emissive="#831843" emissiveIntensity={0.7} /></mesh>;
}

export default function CurlDivergenceScene({ fieldId, point, showField, showCurl, showPoint, coefficients }: Props) {
  return (
    <div className="h-[440px] w-full overflow-hidden rounded-xl border border-white/10 bg-[#080e19]">
      <Canvas camera={{ position: [7, 7, 7], fov: 45 }} gl={{ antialias: true }}>
        <color attach="background" args={["#080e19"]} />
        <ambientLight intensity={0.8} />
        <directionalLight position={[5, 8, 6]} intensity={1.2} />
        <Axes />
        {showField && <FieldArrows fieldId={fieldId} coefficients={coefficients} />}
        {showCurl && <CurlVector fieldId={fieldId} point={point} />}
        {showPoint && <PointMarker point={point} />}
        <OrbitControls makeDefault />
      </Canvas>
    </div>
  );
}
