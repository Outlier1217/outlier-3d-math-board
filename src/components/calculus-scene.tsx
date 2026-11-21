"use client";
import { useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import { Grid, Line, OrbitControls, Text } from "@react-three/drei";
import * as THREE from "three";
import { getCalculusFunction, tangentPlaneValue, type FunctionId } from "@/lib/calculus";

type Props = { functionId: FunctionId; a: number; b: number; showSurface: boolean; showTangent: boolean; showGradient: boolean };

function Surface({ functionId, a, b, tangent = false }: { functionId: FunctionId; a: number; b: number; tangent?: boolean }) {
  const geometry = useMemo(() => {
    const fn = getCalculusFunction(functionId);
    const divisions = 64, min = -3, max = 3;
    const positions: number[] = [], indices: number[] = [];
    for (let row=0; row<=divisions; row++) {
      const y = min + (max-min)*row/divisions;
      for (let col=0; col<=divisions; col++) {
        const x = min + (max-min)*col/divisions;
        positions.push(x,y,tangent ? tangentPlaneValue(fn,a,b,x,y) : fn.evaluate(x,y));
      }
    }
    for (let row=0; row<divisions; row++) for (let col=0; col<divisions; col++) {
      const p=row*(divisions+1)+col, q=p+divisions+1;
      indices.push(p,q,p+1,q,q+1,p+1);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position",new THREE.Float32BufferAttribute(positions,3));
    geo.setIndex(indices); geo.computeVertexNormals();
    return geo;
  },[functionId,a,b,tangent]);
  return <mesh geometry={geometry}>
    {tangent
      ? <meshStandardMaterial color="#f59e0b" transparent opacity={0.48} side={THREE.DoubleSide} roughness={0.55} depthWrite={false}/>
      : <meshStandardMaterial color="#38bdf8" transparent opacity={0.78} side={THREE.DoubleSide} roughness={0.45}/>}
  </mesh>;
}

function Arrow({ origin, vector, color, label }: { origin: [number,number,number]; vector: [number,number,number]; color: string; label: string }) {
  const len=Math.hypot(...vector);
  if (len<1e-8) return null;
  const dir=new THREE.Vector3(...vector).normalize();
  const arrow=new THREE.ArrowHelper(dir,new THREE.Vector3(...origin),Math.min(1.8,Math.max(0.55,len*0.22)),color,0.22,0.13);
  return <group><primitive object={arrow}/><Text position={[origin[0]+dir.x*1.95,origin[1]+dir.y*1.95,origin[2]+dir.z*1.95+0.15]} fontSize={0.2} color={color} outlineWidth={0.02} outlineColor="#0f172a">{label}</Text></group>;
}

function Scene(p: Props) {
  const fn=getCalculusFunction(p.functionId), z=fn.evaluate(p.a,p.b), fx=fn.dx(p.a,p.b), fy=fn.dy(p.a,p.b);
  const point: [number,number,number]=[p.a,p.b,z];
  return <>
    <color attach="background" args={["#080f1d"]}/>
    <ambientLight intensity={1.1}/><directionalLight position={[5,7,10]} intensity={1.6}/>
    <Grid args={[12,12]} position={[0,0,-0.015]} rotation={[Math.PI/2,0,0]} cellSize={1} cellThickness={0.6} cellColor="#334155" sectionSize={3} sectionThickness={1} sectionColor="#64748b" fadeDistance={18} infiniteGrid/>
    <Line points={[[-3.5,0,0],[3.5,0,0]]} color="#f87171" lineWidth={2}/>
    <Line points={[[0,-3.5,0],[0,3.5,0]]} color="#4ade80" lineWidth={2}/>
    <Line points={[[0,0,-5],[0,0,8]]} color="#60a5fa" lineWidth={2}/>
    <Text position={[3.7,0,0]} fontSize={0.22} color="#fca5a5">X</Text>
    <Text position={[0,3.7,0]} fontSize={0.22} color="#86efac">Y</Text>
    <Text position={[0,0,8.2]} fontSize={0.22} color="#93c5fd">Z</Text>
    {p.showSurface && <Surface functionId={p.functionId} a={p.a} b={p.b}/>}
    {p.showTangent && <Surface functionId={p.functionId} a={p.a} b={p.b} tangent/>}
    <mesh position={point}><sphereGeometry args={[0.09,24,24]}/><meshStandardMaterial color="#f8fafc" emissive="#f8fafc" emissiveIntensity={0.35}/></mesh>
    <Line points={[[p.a,p.b,0],point]} color="#f8fafc" lineWidth={1.5} dashed/>
    <Text position={[p.a+0.18,p.b+0.18,z+0.25]} fontSize={0.22} color="#ffffff" outlineWidth={0.025} outlineColor="#0f172a">P(a, b, f(a,b))</Text>
    {p.showGradient && <>
      <Arrow origin={point} vector={[fx,0,0]} color="#f472b6" label={`fx = ${fx.toFixed(2)}`}/>
      <Arrow origin={point} vector={[0,fy,0]} color="#a78bfa" label={`fy = ${fy.toFixed(2)}`}/>
      <Arrow origin={point} vector={[fx,fy,0]} color="#facc15" label="∇f"/>
    </>}
    <OrbitControls makeDefault target={[0,0,0]} enableDamping dampingFactor={0.08} minDistance={4} maxDistance={24}/>
  </>;
}
export default function CalculusScene(props: Props) {
  return <Canvas camera={{position:[9,10,8],fov:43,near:0.1,far:100,up:[0,0,1]}} gl={{antialias:true,alpha:false}} dpr={[1,2]}><Scene {...props}/></Canvas>;
}
