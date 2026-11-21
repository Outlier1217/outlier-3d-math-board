
#!/usr/bin/env python3
from pathlib import Path

ROOT = Path.cwd()
if not (ROOT / "package.json").exists() or not (ROOT / "src").exists():
    raise SystemExit("Run from /workspaces/outlier-3d-math-board")

files = {
"src/lib/calculus.ts": r'''
export type FunctionId = "paraboloid" | "saddle" | "product" | "tilted" | "cubic";
export type CalculusFunction = {
  id: FunctionId; name: string; equation: string;
  evaluate: (x: number, y: number) => number;
  dx: (x: number, y: number) => number;
  dy: (x: number, y: number) => number;
};
export const CALCULUS_FUNCTIONS: CalculusFunction[] = [
  { id: "paraboloid", name: "Elliptic paraboloid", equation: "f(x, y) = x² + y²", evaluate: (x,y) => x*x+y*y, dx: x => 2*x, dy: (_x,y) => 2*y },
  { id: "saddle", name: "Hyperbolic paraboloid", equation: "f(x, y) = x² − y²", evaluate: (x,y) => x*x-y*y, dx: x => 2*x, dy: (_x,y) => -2*y },
  { id: "product", name: "Saddle surface", equation: "f(x, y) = xy", evaluate: (x,y) => x*y, dx: (_x,y) => y, dy: x => x },
  { id: "tilted", name: "Mixed quadratic surface", equation: "f(x, y) = x² + y² + xy", evaluate: (x,y) => x*x+y*y+x*y, dx: (x,y) => 2*x+y, dy: (x,y) => 2*y+x },
  { id: "cubic", name: "Cubic surface", equation: "f(x, y) = x³ + y³", evaluate: (x,y) => x**3+y**3, dx: x => 3*x*x, dy: (_x,y) => 3*y*y },
];
export function getCalculusFunction(id: FunctionId): CalculusFunction {
  return CALCULUS_FUNCTIONS.find(item => item.id === id) ?? CALCULUS_FUNCTIONS[0];
}
export function tangentPlaneValue(fn: CalculusFunction, a: number, b: number, x: number, y: number): number {
  return fn.evaluate(a,b) + fn.dx(a,b)*(x-a) + fn.dy(a,b)*(y-b);
}
export function formatNumber(value: number): string {
  const safe = Math.abs(value) < 1e-10 ? 0 : value;
  return Number(safe.toFixed(4)).toString();
}
''',
"src/components/calculus-scene.tsx": r'''
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
''',
"src/app/calculus/page.tsx": r'''
"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import CalculusScene from "@/components/calculus-scene";
import { CALCULUS_FUNCTIONS, formatNumber, getCalculusFunction, tangentPlaneValue, type FunctionId } from "@/lib/calculus";

const panel: React.CSSProperties={background:"#111c2e",border:"1px solid #26364d",borderRadius:12,padding:16};
const field: React.CSSProperties={width:"100%",accentColor:"#38bdf8",marginTop:8};

export default function CalculusPage() {
  const [functionId,setFunctionId]=useState<FunctionId>("paraboloid");
  const [a,setA]=useState(1),[b,setB]=useState(1);
  const [showSurface,setShowSurface]=useState(true),[showTangent,setShowTangent]=useState(true),[showGradient,setShowGradient]=useState(true);
  const fn=getCalculusFunction(functionId), value=fn.evaluate(a,b), fx=fn.dx(a,b), fy=fn.dy(a,b);
  const constant=value-fx*a-fy*b, gradientMagnitude=Math.hypot(fx,fy);
  const tangentEquation=`z = ${formatNumber(fx)}(x − ${formatNumber(a)}) + ${formatNumber(fy)}(y − ${formatNumber(b)}) + ${formatNumber(value)}`;
  const sample=useMemo(()=>tangentPlaneValue(fn,a,b,a+0.5,b+0.5),[fn,a,b]);
  return <main style={{minHeight:"100vh",background:"#080f1d",color:"#e2e8f0",fontFamily:"Inter,ui-sans-serif,system-ui,sans-serif"}}>
    <header style={{height:64,display:"flex",alignItems:"center",justifyContent:"space-between",padding:"0 24px",borderBottom:"1px solid #26364d",background:"#0d1728"}}>
      <div><div style={{fontSize:13,fontWeight:800,letterSpacing:1.4}}>OUTLIER <span style={{color:"#38bdf8"}}>CALCULUS</span></div><div style={{fontSize:10,color:"#94a3b8",letterSpacing:1.2}}>3D MATHEMATICS VISUALIZER</div></div>
      <Link href="/" style={{color:"#93c5fd",textDecoration:"none",fontSize:12,border:"1px solid #334155",borderRadius:8,padding:"8px 12px"}}>← Back to 3D Board</Link>
    </header>
    <div style={{padding:"22px 24px 12px"}}><div style={{color:"#38bdf8",fontSize:10,fontWeight:800,letterSpacing:1.5}}>CALCULUS / MULTIVARIABLE DIFFERENTIATION</div><h1 style={{fontSize:25,margin:"7px 0 5px",color:"#f8fafc"}}>Partial Derivatives & Tangent Plane</h1><p style={{margin:0,color:"#94a3b8",fontSize:12}}>Explore how a surface changes in the x and y directions at a movable point.</p></div>
    <div className="calculus-layout" style={{display:"grid",gridTemplateColumns:"minmax(0,1fr) 340px",gap:16,padding:"12px 24px 24px",alignItems:"start"}}>
      <section style={{...panel,padding:0,overflow:"hidden",minWidth:0}}>
        <div style={{height:"min(68vh,680px)",minHeight:420}}><CalculusScene functionId={functionId} a={a} b={b} showSurface={showSurface} showTangent={showTangent} showGradient={showGradient}/></div>
        <div style={{display:"flex",flexWrap:"wrap",gap:14,padding:"12px 16px",borderTop:"1px solid #26364d",color:"#94a3b8",fontSize:10}}>
          <span><span style={{color:"#38bdf8"}}>●</span> Function surface</span><span><span style={{color:"#f59e0b"}}>●</span> Tangent plane</span><span><span style={{color:"#f472b6"}}>●</span> x-direction slope</span><span><span style={{color:"#a78bfa"}}>●</span> y-direction slope</span><span>Drag to rotate · Scroll to zoom</span>
        </div>
      </section>
      <aside style={{display:"grid",gap:12}}>
        <section style={panel}><h2 style={{margin:"0 0 12px",fontSize:13,color:"#f8fafc"}}>Function</h2>
          <select value={functionId} onChange={e=>setFunctionId(e.target.value as FunctionId)} style={{width:"100%",background:"#0b1423",border:"1px solid #334155",borderRadius:8,color:"#e2e8f0",padding:10,fontSize:12}}>
            {CALCULUS_FUNCTIONS.map(item=><option key={item.id} value={item.id}>{item.name}</option>)}
          </select><div style={{marginTop:10,color:"#7dd3fc",fontSize:14,fontWeight:700}}>{fn.equation}</div>
        </section>
        <section style={panel}><h2 style={{margin:"0 0 12px",fontSize:13,color:"#f8fafc"}}>Move the point P(a, b)</h2>
          <label style={{display:"block",fontSize:11,color:"#cbd5e1"}}>a = {a.toFixed(2)}<input aria-label="Point x coordinate a" type="range" min="-2" max="2" step="0.05" value={a} onChange={e=>setA(Number(e.target.value))} style={field}/></label>
          <label style={{display:"block",fontSize:11,color:"#cbd5e1",marginTop:15}}>b = {b.toFixed(2)}<input aria-label="Point y coordinate b" type="range" min="-2" max="2" step="0.05" value={b} onChange={e=>setB(Number(e.target.value))} style={field}/></label>
          <button type="button" onClick={()=>{setA(1);setB(1)}} style={{marginTop:14,background:"#1e293b",border:"1px solid #334155",color:"#cbd5e1",padding:"7px 10px",borderRadius:7,cursor:"pointer",fontSize:11}}>Reset point</button>
        </section>
        <section style={panel}><h2 style={{margin:"0 0 10px",fontSize:13,color:"#f8fafc"}}>3D Display</h2>
          <label style={{display:"flex",alignItems:"center",gap:9,fontSize:11,color:"#cbd5e1",margin:"9px 0"}}><input type="checkbox" checked={showSurface} onChange={e=>setShowSurface(e.target.checked)}/>Function surface</label>
          <label style={{display:"flex",alignItems:"center",gap:9,fontSize:11,color:"#cbd5e1",margin:"9px 0"}}><input type="checkbox" checked={showTangent} onChange={e=>setShowTangent(e.target.checked)}/>Tangent plane</label>
          <label style={{display:"flex",alignItems:"center",gap:9,fontSize:11,color:"#cbd5e1",margin:"9px 0"}}><input type="checkbox" checked={showGradient} onChange={e=>setShowGradient(e.target.checked)}/>Gradient components</label>
        </section>
        <section style={{...panel,borderColor:"#24506a",background:"#0d2032"}}><h2 style={{margin:"0 0 10px",fontSize:13,color:"#7dd3fc"}}>Live Calculations</h2>
          <div style={{fontSize:11,color:"#94a3b8"}}>At P = ({formatNumber(a)}, {formatNumber(b)})</div>
          <div style={{marginTop:8,fontSize:12,lineHeight:1.9}}>
            <div>f(a, b) = <strong style={{color:"#f8fafc"}}>{formatNumber(value)}</strong></div>
            <div>∂f/∂x = fₓ(a, b) = <strong style={{color:"#f9a8d4"}}>{formatNumber(fx)}</strong></div>
            <div>∂f/∂y = fᵧ(a, b) = <strong style={{color:"#c4b5fd"}}>{formatNumber(fy)}</strong></div>
            <div>|∇f| = <strong style={{color:"#fde68a"}}>{formatNumber(gradientMagnitude)}</strong></div>
          </div>
          <div style={{borderTop:"1px solid #29445b",marginTop:10,paddingTop:10}}><div style={{color:"#7dd3fc",fontSize:11,fontWeight:700}}>Tangent plane equation</div><div style={{fontSize:11,lineHeight:1.7,marginTop:5,overflowWrap:"anywhere"}}>{tangentEquation}</div><div style={{color:"#94a3b8",fontSize:10,marginTop:7}}>Expanded form: z = {formatNumber(fx)}x + ({formatNumber(fy)})y + ({formatNumber(constant)})</div></div>
        </section>
        <section style={panel}><h2 style={{margin:"0 0 8px",fontSize:13,color:"#f8fafc"}}>How to read this</h2><p style={{margin:0,fontSize:11,lineHeight:1.7,color:"#94a3b8"}}>fₓ measures the instantaneous rate of change when x changes while y is held constant. fᵧ measures the rate when y changes while x is held constant. The tangent plane uses both slopes to approximate the surface near P.</p><div style={{marginTop:8,fontSize:10,color:"#64748b"}}>Plane check at (a + 0.5, b + 0.5): z = {formatNumber(sample)}</div></section>
      </aside>
    </div>
    <style jsx global>{`@media(max-width:900px){.calculus-layout{grid-template-columns:minmax(0,1fr)!important;padding-left:12px!important;padding-right:12px!important}}`}</style>
  </main>;
}
'''
}

for relative, content in files.items():
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.lstrip(), encoding="utf-8")
    print(f"Created: {relative}")

print("\nModule files created. Run ESLint, then pnpm build. Open /calculus.")
