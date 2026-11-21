"use client";

import { Canvas } from "@react-three/fiber";
import { Grid, Line, OrbitControls, Text } from "@react-three/drei";
import { useMemo } from "react";
import * as THREE from "three";
import { getGradientFunction, type GradientFunctionId } from "@/lib/gradient";

type Props = {
  functionId: GradientFunctionId;
  a: number;
  b: number;
  directionAngle: number;
  showGradient: boolean;
  showDirection: boolean;
  showSurface: boolean;
};

function Surface({ functionId, showSurface }: { functionId: GradientFunctionId; showSurface: boolean }) {
  const geometry = useMemo(() => {
    const fn = getGradientFunction(functionId);
    const divisions = 64;
    const size = 6;
    const positions: number[] = [];
    const indices: number[] = [];
    for (let iy = 0; iy <= divisions; iy += 1) {
      const y = -size/2 + (iy/divisions)*size;
      for (let ix = 0; ix <= divisions; ix += 1) {
        const x = -size/2 + (ix/divisions)*size;
        positions.push(x, y, fn.value(x, y));
      }
    }
    for (let iy = 0; iy < divisions; iy += 1) {
      for (let ix = 0; ix < divisions; ix += 1) {
        const p = iy*(divisions+1)+ix;
        indices.push(p, p+1, p+divisions+2, p, p+divisions+2, p+divisions+1);
      }
    }
    const result = new THREE.BufferGeometry();
    result.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    result.setIndex(indices);
    result.computeVertexNormals();
    return result;
  }, [functionId]);

  if (!showSurface) return null;
  return <mesh geometry={geometry}>
    <meshStandardMaterial color="#22b8d5" roughness={0.5} metalness={0.06} side={THREE.DoubleSide} />
  </mesh>;
}

function VectorArrow({ origin, vector, color, length }: {
  origin: [number, number, number];
  vector: THREE.Vector3;
  color: string;
  length: number;
}) {
  const ox = origin[0];
  const oy = origin[1];
  const oz = origin[2];
  const vx = vector.x;
  const vy = vector.y;
  const vz = vector.z;

  const arrow = useMemo(() => new THREE.ArrowHelper(
    new THREE.Vector3(vx, vy, vz).normalize(),
    new THREE.Vector3(ox, oy, oz),
    length,
    color,
    0.24,
    0.14
  ), [ox, oy, oz, vx, vy, vz, color, length]);

  return <primitive object={arrow} />;
}

function SceneContent(props: Props) {
  const fn = getGradientFunction(props.functionId);
  const z = fn.value(props.a, props.b);
  const gx = fn.dx(props.a, props.b);
  const gy = fn.dy(props.a, props.b);
  const origin: [number, number, number] = [props.a, props.b, z];
  const gradient = new THREE.Vector3(gx, gy, 0);
  const direction = new THREE.Vector3(
    Math.cos(props.directionAngle*Math.PI/180),
    Math.sin(props.directionAngle*Math.PI/180), 0
  );
  const gradientMagnitude = gradient.length();

  return <>
    <color attach="background" args={["#08111f"]} />
    <ambientLight intensity={1.1} />
    <directionalLight position={[5, -4, 9]} intensity={2} />
    <Grid position={[0,0,-0.04]} args={[8,8]} cellSize={1} cellThickness={0.65}
      cellColor="#263b55" sectionSize={2} sectionThickness={1.1}
      sectionColor="#42617f" fadeDistance={18} infiniteGrid={false} />
    <axesHelper args={[3.5]} />
    <Surface functionId={props.functionId} showSurface={props.showSurface} />
    <mesh position={origin}>
      <sphereGeometry args={[0.075,20,20]} />
      <meshBasicMaterial color="#f8fafc" />
    </mesh>
    <Line points={[origin,[props.a,props.b,0]]} color="#f8fafc" lineWidth={1.5} dashed dashSize={0.09} gapSize={0.06} />
    <Text position={[props.a+0.16,props.b+0.12,z+0.2]} fontSize={0.14} color="#f8fafc" anchorX="left">P(a,b)</Text>
    {props.showGradient && gradientMagnitude > 0.0001 && <VectorArrow origin={origin} vector={gradient}
      color="#fbbf24" length={Math.min(2.15,0.65+Math.log1p(gradientMagnitude)*0.55)} />}
    {props.showDirection && <VectorArrow origin={origin} vector={direction} color="#fb7185" length={1.55} />}
    <Line points={[[0,0,0],[3.6,0,0]]} color="#fb7185" lineWidth={1.5} />
    <Line points={[[0,0,0],[0,3.6,0]]} color="#34d399" lineWidth={1.5} />
    <Line points={[[0,0,0],[0,0,3.6]]} color="#60a5fa" lineWidth={1.5} />
    <Text position={[3.72,0,0]} fontSize={0.17} color="#fb7185">x</Text>
    <Text position={[0,3.72,0]} fontSize={0.17} color="#34d399">y</Text>
    <Text position={[0,0,3.72]} fontSize={0.17} color="#60a5fa">z</Text>
    <OrbitControls makeDefault target={[0,0,0.5]} minDistance={5} maxDistance={17} />
  </>;
}

export default function GradientScene(props: Props) {
  return <Canvas camera={{ position:[8,-10,8], up:[0,0,1], fov:43, near:0.1, far:100 }}
    gl={{ antialias:true }} dpr={[1,1.75]}>
    <SceneContent {...props} />
  </Canvas>;
}
