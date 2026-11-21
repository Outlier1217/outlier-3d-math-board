from pathlib import Path

ROOT = Path.cwd()
FILES = {
"src/lib/double-integrals.ts": r'''
export type DoubleIntegralFunctionId = "sum" | "squares" | "product" | "wave";
export type DoubleIntegralFunction = {
  id: DoubleIntegralFunctionId; label: string; formula: string;
  value: (x: number, y: number) => number;
  exactIntegral: (xMax: number, yMax: number) => number;
};
export const doubleIntegralFunctions: DoubleIntegralFunction[] = [
  { id:"sum", label:"Linear surface", formula:"f(x, y) = x + y",
    value:(x,y)=>x+y, exactIntegral:(a,b)=>(a*a*b)/2+(a*b*b)/2 },
  { id:"squares", label:"Elliptic paraboloid", formula:"f(x, y) = x² + y²",
    value:(x,y)=>x*x+y*y, exactIntegral:(a,b)=>(a*a*a*b)/3+(a*b*b*b)/3 },
  { id:"product", label:"Product surface", formula:"f(x, y) = xy",
    value:(x,y)=>x*y, exactIntegral:(a,b)=>(a*a*b*b)/4 },
  { id:"wave", label:"Trigonometric surface", formula:"f(x, y) = sin(x) cos(y)",
    value:(x,y)=>Math.sin(x)*Math.cos(y), exactIntegral:(a,b)=>(1-Math.cos(a))*Math.sin(b) },
];
export function getDoubleIntegralFunction(id: DoubleIntegralFunctionId) {
  return doubleIntegralFunctions.find(fn=>fn.id===id) ?? doubleIntegralFunctions[0];
}
export function midpointIntegral(fn:(x:number,y:number)=>number,xMax:number,yMax:number,n:number) {
  const dx=xMax/n, dy=yMax/n; let total=0;
  for(let i=0;i<n;i++) for(let j=0;j<n;j++) total+=fn((i+.5)*dx,(j+.5)*dy)*dx*dy;
  return total;
}
export function formatIntegralNumber(value:number) {
  if(Math.abs(value)<0.00005) return "0";
  return Number(value.toFixed(4)).toString();
}
''',
"src/components/double-integral-scene.tsx": r'''
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
  const surface=useMemo(()=>buildSurface(fn.value,p.xMax,p.yMax),[p.functionId,p.xMax,p.yMax]);
  const columns=useMemo(()=>buildColumns(fn.value,p.xMax,p.yMax,p.divisions),[p.functionId,p.xMax,p.yMax,p.divisions]);
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
''',
"src/app/calculus/double-integrals/page.tsx": r'''
"use client";
import Link from "next/link";
import { useState } from "react";
import DoubleIntegralScene from "@/components/double-integral-scene";
import { doubleIntegralFunctions,formatIntegralNumber,getDoubleIntegralFunction,midpointIntegral,
  type DoubleIntegralFunctionId } from "@/lib/double-integrals";

const panel:React.CSSProperties={background:"#111e30",border:"1px solid #263b55",borderRadius:14,padding:17};
const field:React.CSSProperties={width:"100%",background:"#0b1525",color:"#e2e8f0",border:"1px solid #344861",borderRadius:8,padding:"10px 11px"};

export default function DoubleIntegralsPage() {
  const [functionId,setFunctionId]=useState<DoubleIntegralFunctionId>("sum");
  const [xMax,setXMax]=useState(2),[yMax,setYMax]=useState(2),[divisions,setDivisions]=useState(12);
  const [showSurface,setShowSurface]=useState(true),[showColumns,setShowColumns]=useState(true);
  const fn=getDoubleIntegralFunction(functionId);
  const exact=fn.exactIntegral(xMax,yMax);
  const estimate=midpointIntegral(fn.value,xMax,yMax,divisions);
  const area=(xMax/divisions)*(yMax/divisions), error=Math.abs(exact-estimate);
  const resultCards=[{label:"Exact integral",value:formatIntegralNumber(exact)},
    {label:"Midpoint estimate",value:formatIntegralNumber(estimate)},
    {label:"Absolute error",value:formatIntegralNumber(error)},
    {label:"Subrectangles",value:String(divisions*divisions)}];

  return <main className="calculus-page" style={{minHeight:"100vh",background:"#080f1d",color:"#e2e8f0",fontFamily:"Inter,ui-sans-serif,system-ui,sans-serif"}}>
    <header style={{minHeight:64,display:"flex",alignItems:"center",justifyContent:"space-between",gap:12,padding:"12px 24px",borderBottom:"1px solid #26364d",background:"#0d1728"}}>
      <div><div style={{fontSize:13,fontWeight:800,letterSpacing:1.4}}>OUTLIER <span style={{color:"#38bdf8"}}>CALCULUS</span></div><div style={{fontSize:10,color:"#94a3b8",letterSpacing:1.2}}>DOUBLE INTEGRALS & VOLUME</div></div>
      <Link href="/calculus" style={{color:"#93c5fd",textDecoration:"none",border:"1px solid #344861",borderRadius:8,padding:"10px 13px",fontSize:12}}>← Back to Calculus</Link>
    </header>
    <div style={{padding:"24px 24px 12px"}}>
      <div style={{color:"#38bdf8",fontSize:11,fontWeight:800,letterSpacing:1.5}}>CALCULUS / MULTIPLE INTEGRATION</div>
      <h1 style={{fontSize:26,fontWeight:600,margin:"12px 0 7px"}}>Double Integrals Visualizer</h1>
      <p style={{color:"#9fb2ca",fontSize:13,margin:0,lineHeight:1.7}}>Explore the volume under z = f(x,y), the rectangular integration region, and how Riemann columns approximate the double integral.</p>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"minmax(0,1fr) 350px",gap:16,padding:"12px 24px 28px",alignItems:"start"}}>
      <section style={{...panel,padding:0,overflow:"hidden",minWidth:0}}>
        <div style={{height:"min(66vh,660px)",minHeight:390}}>
          <DoubleIntegralScene functionId={functionId} xMax={xMax} yMax={yMax} divisions={divisions} showSurface={showSurface} showColumns={showColumns}/>
        </div>
        <div style={{display:"flex",flexWrap:"wrap",gap:14,padding:"12px 15px",borderTop:"1px solid #263b55",color:"#9fb2ca",fontSize:10}}>
          <span><span style={{color:"#22b8d5"}}>●</span> Surface z = f(x,y)</span><span><span style={{color:"#f59e0b"}}>●</span> Riemann columns</span><span>Drag to rotate · Scroll to zoom</span>
        </div>
      </section>
      <aside style={{display:"grid",gap:13}}>
        <section style={panel}>
          <label htmlFor="integrand" style={{display:"block",fontSize:12,marginBottom:9}}>Integrand / surface</label>
          <select id="integrand" value={functionId} onChange={e=>setFunctionId(e.target.value as DoubleIntegralFunctionId)} style={field}>
            {doubleIntegralFunctions.map(item=><option key={item.id} value={item.id}>{item.label}</option>)}
          </select>
          <div style={{color:"#7dd3fc",fontWeight:700,fontSize:14,marginTop:12}}>{fn.formula}</div>
        </section>
        <section style={panel}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:13}}>Integration region R</div>
          <label style={{display:"flex",justifyContent:"space-between",fontSize:11,marginBottom:7}}>x upper limit <strong>{formatIntegralNumber(xMax)}</strong></label>
          <input aria-label="X upper integration limit" type="range" min=".5" max="3" step=".1" value={xMax} onChange={e=>setXMax(Number(e.target.value))} style={{width:"100%",accentColor:"#38bdf8"}}/>
          <label style={{display:"flex",justifyContent:"space-between",fontSize:11,margin:"14px 0 7px"}}>y upper limit <strong>{formatIntegralNumber(yMax)}</strong></label>
          <input aria-label="Y upper integration limit" type="range" min=".5" max="3" step=".1" value={yMax} onChange={e=>setYMax(Number(e.target.value))} style={{width:"100%",accentColor:"#38bdf8"}}/>
          <div style={{color:"#94a3b8",fontSize:10,marginTop:10}}>R = [0, {formatIntegralNumber(xMax)}] × [0, {formatIntegralNumber(yMax)}]</div>
        </section>
        <section style={panel}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:10}}>Riemann subdivision</div>
          <div style={{display:"flex",justifyContent:"space-between",fontSize:11,marginBottom:7}}>n × n rectangles <strong>{divisions} × {divisions}</strong></div>
          <input aria-label="Riemann subdivisions" type="range" min="4" max="24" step="1" value={divisions} onChange={e=>setDivisions(Number(e.target.value))} style={{width:"100%",accentColor:"#f59e0b"}}/>
          <div style={{color:"#94a3b8",fontSize:10,marginTop:8}}>ΔA = Δx Δy = {formatIntegralNumber(area)}</div>
        </section>
        <section style={panel}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:11}}>3D Display</div>
          {[{label:"Function surface",checked:showSurface,setter:setShowSurface},{label:"Riemann columns",checked:showColumns,setter:setShowColumns}].map(item=>
            <label key={item.label} style={{display:"flex",alignItems:"center",gap:9,fontSize:11,margin:"9px 0",cursor:"pointer"}}>
              <input type="checkbox" checked={item.checked} onChange={e=>item.setter(e.target.checked)}/>{item.label}
            </label>)}
        </section>
        <section style={panel}>
          <div style={{color:"#7dd3fc",fontSize:12,fontWeight:800,marginBottom:12}}>LIVE RESULTS</div>
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:9}}>
            {resultCards.map(item=><div key={item.label} style={{background:"#0b1728",border:"1px solid #263b55",borderRadius:9,padding:10}}>
              <div style={{color:"#94a3b8",fontSize:10}}>{item.label}</div><div style={{color:"#e2e8f0",fontSize:15,fontWeight:700,marginTop:5}}>{item.value}</div>
            </div>)}
          </div>
        </section>
      </aside>
    </div>
    <div style={{padding:"0 24px 32px",display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(280px,1fr))",gap:14}}>
      <section style={panel}>
        <div style={{color:"#fbbf24",fontSize:12,fontWeight:800,marginBottom:10}}>1. INTEGRATION REGION</div>
        <div style={{fontSize:17,lineHeight:1.8}}>R = [0, {formatIntegralNumber(xMax)}] × [0, {formatIntegralNumber(yMax)}]</div>
        <div style={{color:"#a9bdd4",fontSize:12,lineHeight:1.8,marginTop:7}}>The base region is a rectangle in the xy-plane. Each small subrectangle has area ΔA = Δx Δy.</div>
      </section>
      <section style={panel}>
        <div style={{color:"#38bdf8",fontSize:12,fontWeight:800,marginBottom:10}}>2. DOUBLE INTEGRAL</div>
        <div style={{fontSize:17,lineHeight:1.8}}>∬R f(x,y) dA</div>
        <div style={{color:"#a9bdd4",fontSize:12,lineHeight:1.8,marginTop:7}}>For this rectangular region, the iterated form is:</div>
        <div style={{fontSize:15,marginTop:8}}>∫₀^{formatIntegralNumber(xMax)} ∫₀^{formatIntegralNumber(yMax)} f(x,y) dy dx</div>
      </section>
      <section style={{...panel,gridColumn:"1 / -1"}}>
        <div style={{color:"#34d399",fontSize:12,fontWeight:800,marginBottom:10}}>3. RIEMANN SUM APPROXIMATION</div>
        <div style={{fontSize:17,lineHeight:1.8}}>Σᵢ Σⱼ f(xᵢ*, yⱼ*) Δx Δy</div>
        <div style={{color:"#a9bdd4",fontSize:12,lineHeight:1.9,marginTop:7}}>Midpoint estimate = <strong style={{color:"#34d399"}}>{formatIntegralNumber(estimate)}</strong><br/>Exact integral = <strong style={{color:"#34d399"}}>{formatIntegralNumber(exact)}</strong><br/>Absolute error = {formatIntegralNumber(error)}</div>
      </section>
      <section style={{...panel,gridColumn:"1 / -1"}}>
        <div style={{color:"#7dd3fc",fontSize:12,fontWeight:800,marginBottom:10}}>STEP-BY-STEP METHOD</div>
        <ol style={{color:"#c5d4e6",fontSize:12,lineHeight:2,paddingLeft:20,margin:0}}>
          <li>Identify the rectangular region R and its x and y limits.</li>
          <li>Divide R into n × n small rectangles.</li>
          <li>Calculate Δx = xMax/n and Δy = yMax/n.</li>
          <li>Evaluate f at each rectangle's midpoint and multiply by Δx Δy.</li>
          <li>Add all contributions to get the midpoint Riemann approximation.</li>
          <li>As subdivisions become finer, the Riemann sum approaches the double integral.</li>
        </ol>
        <div style={{color:"#94a3b8",fontSize:11,lineHeight:1.7,marginTop:10}}>Note: the live estimate uses midpoint sampling; the exact value is calculated analytically for each built-in function.</div>
      </section>
    </div>
  </main>;
}
'''
}

if not (ROOT / "package.json").exists():
    raise SystemExit("Run this script from the project root (folder containing package.json).")
for relative_path, content in FILES.items():
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {relative_path}")
    path.write_text(content.lstrip("\n"), encoding="utf-8")
    print(f"Created: {relative_path}")
print("\nDouble Integrals module files created.")
print("Existing board and previous Calculus modules were not modified.")
print("Next: run ESLint on the three files, then pnpm build.")
