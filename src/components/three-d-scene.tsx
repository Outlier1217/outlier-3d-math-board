"use client";

import { Canvas } from "@react-three/fiber";
import { Grid, Line, OrbitControls, Text } from "@react-three/drei";
import { Suspense } from "react";
import * as THREE from "three";
import { useSceneStore, type Octant } from "@/store/scene-store";


function Axis({
  end,
  color,
  label,
}: {
  end: [number, number, number];
  color: string;
  label: string;
}) {
  const direction = new THREE.Vector3(...end).normalize();
  const quaternion = new THREE.Quaternion().setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    direction
  );

  const labelPosition: [number, number, number] = [
    end[0] + Math.sign(end[0]) * 0.35,
    end[1] + Math.sign(end[1]) * 0.35,
    end[2] + Math.sign(end[2]) * 0.35,
  ];

  return (
    <group>
      <Line points={[[0, 0, 0], end]} color={color} lineWidth={2} />

      <mesh position={end} quaternion={quaternion}>
        <coneGeometry args={[0.09, 0.24, 16]} />
        <meshBasicMaterial color={color} />
      </mesh>

      <Text
        position={labelPosition}
        fontSize={0.32}
        color={color}
        anchorX="center"
        anchorY="middle"
      >
        {label}
      </Text>
    </group>
  );
}

function PointA() {
  const pointA = useSceneStore((state) => state.pointA);
  const point: [number, number, number] = [
    pointA.x,
    pointA.y,
    pointA.z,
  ];

  const projectionXY: [number, number, number] = [
    pointA.x,
    pointA.y,
    0,
  ];

  const projectionX: [number, number, number] = [
    pointA.x,
    0,
    0,
  ];

  const projectionY: [number, number, number] = [
    0,
    pointA.y,
    0,
  ];

  return (
    <group>
      <mesh position={point}>
        <sphereGeometry args={[0.09, 24, 24]} />
        <meshStandardMaterial
          color="#facc15"
          emissive="#8a5b00"
          emissiveIntensity={0.5}
        />
      </mesh>

      <Text
        position={[pointA.x + 0.25, pointA.y + 0.15, pointA.z + 0.25]}
        fontSize={0.28}
        color="#facc15"
        anchorX="left"
        anchorY="middle"
        outlineWidth={0.015}
        outlineColor="#111827"
      >
        {`A (${pointA.x}, ${pointA.y}, ${pointA.z})`}
      </Text>

      {/* Position vector OA */}
      <Line
        points={[[0, 0, 0], point]}
        color="#facc15"
        lineWidth={2.5}
      />

      {/* Projection lines */}
      <Line
        points={[
          point,
          projectionXY,
          projectionX,
          [0, 0, 0],
        ]}
        color="#60a5fa"
        lineWidth={1}
        dashed
        dashSize={0.12}
        gapSize={0.08}
        transparent
        opacity={0.65}
      />

      <Line
        points={[
          projectionXY,
          projectionY,
        ]}
        color="#60a5fa"
        lineWidth={1}
        dashed
        dashSize={0.12}
        gapSize={0.08}
        transparent
        opacity={0.65}
      />
    </group>
  );
}

function OctantHighlight({ octant }: { octant: Octant }) {
  const bounds: Record<Octant, [number, number, number]> = {
    1: [1, 1, 1],
    2: [-1, 1, 1],
    3: [-1, -1, 1],
    4: [1, -1, 1],
    5: [1, 1, -1],
    6: [-1, 1, -1],
    7: [-1, -1, -1],
    8: [1, -1, -1],
  };

  const signs = bounds[octant];
  const size = 5.5;

  return (
    <mesh
      position={[
        (signs[0] * size) / 2,
        (signs[1] * size) / 2,
        (signs[2] * size) / 2,
      ]}
    >
      <boxGeometry args={[size, size, size]} />
      <meshBasicMaterial
        color="#a78bfa"
        transparent
        opacity={0.09}
        side={THREE.DoubleSide}
        depthWrite={false}
      />
    </mesh>
  );
}

function Scene() {
  const selectedOctant = useSceneStore(
    (state) => state.selectedOctant
  );

  return (
    <>
      <ambientLight intensity={1.4} />
      <directionalLight position={[5, 8, 10]} intensity={2} />

      <Grid
        args={[20, 20]}
        position={[0, 0, -0.01]}
        rotation={[Math.PI / 2, 0, 0]}
        cellSize={1}
        cellThickness={0.7}
        cellColor="#405675"
        sectionSize={5}
        sectionThickness={1.2}
        sectionColor="#6684a8"
        fadeDistance={25}
        fadeStrength={1}
        infiniteGrid
      />

            {/* Selected Octant Highlight */}
      {selectedOctant !== null && (
        <OctantHighlight octant={selectedOctant} />
      )}

      {/* Positive and negative X axes */}
      <Axis end={[6, 0, 0]} color="#f87171" label="+X" />
      <Axis end={[-6, 0, 0]} color="#f87171" label="-X" />

      {/* Positive and negative Y axes */}
      <Axis end={[0, 6, 0]} color="#4ade80" label="+Y" />
      <Axis end={[0, -6, 0]} color="#4ade80" label="-Y" />

      {/* Positive and negative Z axes */}
      <Axis end={[0, 0, 6]} color="#60a5fa" label="+Z" />
      <Axis end={[0, 0, -6]} color="#60a5fa" label="-Z" />

      {/* Origin */}
      <mesh>
        <sphereGeometry args={[0.055, 16, 16]} />
        <meshBasicMaterial color="#ffffff" />
      </mesh>

      <Text
        position={[0.15, -0.2, -0.2]}
        fontSize={0.28}
        color="#e2e8f0"
        anchorX="left"
        anchorY="middle"
      >
        O
      </Text>

      <PointA />

      <OrbitControls
        makeDefault
        target={[0, 0, 0]}
        enableDamping
        dampingFactor={0.08}
        minDistance={3}
        maxDistance={30}
      />
    </>
  );
}

export default function ThreeDScene() {
  return (
    <Canvas
      className="three-d-canvas"
      camera={{
        position: [9, 10, 8],
        fov: 42,
        near: 0.1,
        far: 100,
        up: [0, 0, 1],
      }}
      gl={{ antialias: true, alpha: true }}
      dpr={[1, 2]}
    >
      <Suspense fallback={null}>
        <Scene />
      </Suspense>
    </Canvas>
  );
}
