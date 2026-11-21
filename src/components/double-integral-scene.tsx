"use client";
import { Canvas } from "@react-three/fiber";
import { Grid, OrbitControls, Text } from "@react-three/drei";
import { useMemo } from "react";
import * as THREE from "three";
import { getDoubleIntegralFunction, type DoubleIntegralFunctionId } from "@/lib/double-integrals";

type Props = {
  functionId: DoubleIntegralFunctionId; xMax:number; yMax:number; divisions:number;
  showSurface:boolean; showColumns:boolean;
};

function buildSurface(fn:(x:number,y:number)=>number,xMax:number,yMax:number) {
  const n=48, positions:number[]=[], indices:number[]=[];
  for(let j=0;j<=n;j++) for(let i=0;i<=n;i++) {
    const x=i/n*xMax, y=j/n*yMax; positions.push(x,y,fn(x,y));
  }
  for(let j=0;j<n;j++) for(let i=0;i<n;i++) {
    const p=j*(n+1)+i;
    indices.push(p,p+1,p+n+2,p,p+n+2,p+n+1);
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute("position",new THREE.Float32BufferAttribute(positions,3));
  g.setIndex(indices); g.computeVertexNormals(); return g;
}

function buildColumns(fn:(x:number,y:number)=>number,xMax:number,yMax:number,n:number) {
  const positions:number[]=[], indices:number[]=[]; let offset=0;
  const dx=xMax/n, dy=yMax/n;
  for(let i=0;i<n;i++) for(let j=0;j<n;j++) {
    const x0=i*dx,x1=x0+dx,y0=j*dy,y1=y0+dy;
    const h=fn((x0+x1)/2,(y0+y1)/2);
    if(h<=0) continue;
    const v=[[x0,y0,0],[x1,y0,0],[x1,y1,0],[x0,y1,0],
      [x0,y0,h],[x1,y0,h],[x1,y1,h],[x0,y1,h]];
    for(const p of v) positions.push(p[0],p[1],p[2]);
    const faces=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
      [1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]];
    for(const f of faces) indices.push(offset+f[0],offset+f[1],offset+f[2]);
    offset+=8;
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute("position",new THREE.Float32BufferAttribute(positions,3));
  g.setIndex(indices); g.computeVertexNormals(); return g;
}

function IntegralMeshes(p:Props) {
  const fn=getDoubleIntegralFunction(p.functionId);
  const surface=useMemo(()=>buildSurface(fn.value,p.xMax,p.yMax),[fn.value,p.xMax,p.yMax]);
  const columns=useMemo(()=>buildColumns(fn.value,p.xMax,p.yMax,p.divisions),[fn.value,p.xMax,p.yMax,p.divisions]);
  return <>
    {p.showSurface && <mesh geometry={surface}><meshStandardMaterial color="#22b8d5" roughness={.48} metalness={.05} side={THREE.DoubleSide}/></mesh>}
    {p.showColumns && <mesh geometry={columns}><meshStandardMaterial color="#f59e0b" roughness={.55} transparent opacity={.72} side={THREE.DoubleSide}/></mesh>}
  </>;
}

function SceneContent(p:Props) {
  const fn=getDoubleIntegralFunction(p.functionId);
  return <>
    <color attach="background" args={["#08111f"]}/>
    <ambientLight intensity={1.15}/>
    <directionalLight position={[5,-4,10]} intensity={2}/>
    <Grid position={[0,0,-.025]} args={[8,8]} cellSize={.5} cellThickness={.6} cellColor="#263b55"
      sectionSize={1} sectionThickness={1} sectionColor="#42617f" fadeDistance={18} infiniteGrid={false}/>
    <axesHelper args={[3.5]}/>
    <IntegralMeshes {...p}/>
    <Text position={[p.xMax/2,-.22,-.12]} fontSize={.13} color="#fb7185">x: 0 to {p.xMax.toFixed(1)}</Text>
    <Text position={[-.22,p.yMax/2,-.12]} fontSize={.13} color="#34d399" rotation={[0,0,Math.PI/2]}>y: 0 to {p.yMax.toFixed(1)}</Text>
    <Text position={[p.xMax+.15,p.yMax+.12,fn.value(p.xMax,p.yMax)+.2]} fontSize={.12} color="#e2e8f0">z = f(x,y)</Text>
    <OrbitControls makeDefault target={[p.xMax/2,p.yMax/2,.7]} minDistance={5} maxDistance={18}/>
  </>;
}
export default function DoubleIntegralScene(p:Props) {
  return <Canvas camera={{position:[8,-10,8],up:[0,0,1],fov:43,near:.1,far:100}} gl={{antialias:true}} dpr={[1,1.6]}>
    <SceneContent {...p}/>
  </Canvas>;
}
