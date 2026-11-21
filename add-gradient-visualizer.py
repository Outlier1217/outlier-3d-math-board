from pathlib import Path

ROOT = Path.cwd()

FILES = {
    "src/lib/gradient.ts": r'''
export type GradientFunctionId = "paraboloid" | "saddle" | "mixed" | "wave" | "ridge";

export type GradientFunction = {
  id: GradientFunctionId;
  label: string;
  formula: string;
  value: (x: number, y: number) => number;
  dx: (x: number, y: number) => number;
  dy: (x: number, y: number) => number;
};

export const gradientFunctions: GradientFunction[] = [
  { id: "paraboloid", label: "Elliptic paraboloid", formula: "f(x, y) = x² + y²",
    value: (x, y) => x*x + y*y, dx: (x) => 2*x, dy: (_x, y) => 2*y },
  { id: "saddle", label: "Saddle surface", formula: "f(x, y) = xy",
    value: (x, y) => x*y, dx: (_x, y) => y, dy: (x) => x },
  { id: "mixed", label: "Mixed quadratic", formula: "f(x, y) = x² + y² + xy",
    value: (x, y) => x*x + y*y + x*y, dx: (x, y) => 2*x+y, dy: (x, y) => 2*y+x },
  { id: "wave", label: "Trigonometric surface", formula: "f(x, y) = sin(x) cos(y)",
    value: (x, y) => Math.sin(x)*Math.cos(y),
    dx: (x, y) => Math.cos(x)*Math.cos(y), dy: (x, y) => -Math.sin(x)*Math.sin(y) },
  { id: "ridge", label: "Hyperbolic paraboloid", formula: "f(x, y) = x² − y²",
    value: (x, y) => x*x-y*y, dx: (x) => 2*x, dy: (_x, y) => -2*y },
];

export function getGradientFunction(id: GradientFunctionId): GradientFunction {
  return gradientFunctions.find((item) => item.id === id) ?? gradientFunctions[0];
}

export function formatGradientNumber(value: number): string {
  if (Math.abs(value) < 0.00005) return "0";
  return Number(value.toFixed(4)).toString();
}
''',
    "src/components/gradient-scene.tsx": r'''
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
  origin: [number, number, number]; vector: THREE.Vector3; color: string; length: number;
}) {
  const arrow = useMemo(() => new THREE.ArrowHelper(
    vector.clone().normalize(), new THREE.Vector3(...origin), length, color, 0.24, 0.14
  ), [origin[0], origin[1], origin[2], vector.x, vector.y, vector.z, color, length]);
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
''',
    "src/app/calculus/gradient/page.tsx": r'''
"use client";

import Link from "next/link";
import { useState } from "react";
import GradientScene from "@/components/gradient-scene";
import {
  formatGradientNumber, getGradientFunction, gradientFunctions,
  type GradientFunctionId,
} from "@/lib/gradient";

const panel: React.CSSProperties = {
  background:"#111e30", border:"1px solid #263b55", borderRadius:14, padding:17,
};
const fieldStyle: React.CSSProperties = {
  width:"100%", background:"#0b1525", color:"#e2e8f0",
  border:"1px solid #344861", borderRadius:8, padding:"10px 11px",
};

export default function GradientVisualizerPage() {
  const [functionId,setFunctionId] = useState<GradientFunctionId>("paraboloid");
  const [a,setA] = useState(1);
  const [b,setB] = useState(1);
  const [directionAngle,setDirectionAngle] = useState(35);
  const [showSurface,setShowSurface] = useState(true);
  const [showGradient,setShowGradient] = useState(true);
  const [showDirection,setShowDirection] = useState(true);

  const fn = getGradientFunction(functionId);
  const value = fn.value(a,b);
  const gx = fn.dx(a,b);
  const gy = fn.dy(a,b);
  const magnitude = Math.hypot(gx,gy);
  const radians = directionAngle*Math.PI/180;
  const ux = Math.cos(radians);
  const uy = Math.sin(radians);
  const directionalDerivative = gx*ux + gy*uy;
  const angleText = `${formatGradientNumber(directionAngle)}°`;
  const calculation = `${formatGradientNumber(gx)} × ${formatGradientNumber(ux)} + ${formatGradientNumber(gy)} × ${formatGradientNumber(uy)}`;
  const gradientDirection = magnitude < 0.000001
    ? "Gradient is zero at this point, so no unique steepest-ascent direction exists."
    : `∇f points in the direction (${formatGradientNumber(gx/magnitude)}, ${formatGradientNumber(gy/magnitude)}).`;

  return <main className="calculus-page" style={{minHeight:"100vh",background:"#080f1d",color:"#e2e8f0",fontFamily:"Inter,ui-sans-serif,system-ui,sans-serif"}}>
    <header style={{minHeight:64,display:"flex",alignItems:"center",justifyContent:"space-between",gap:12,padding:"12px 24px",borderBottom:"1px solid #26364d",background:"#0d1728"}}>
      <div><div style={{fontSize:13,fontWeight:800,letterSpacing:1.4}}>OUTLIER <span style={{color:"#38bdf8"}}>CALCULUS</span></div><div style={{fontSize:10,color:"#94a3b8",letterSpacing:1.2}}>GRADIENT & DIRECTIONAL DERIVATIVES</div></div>
      <Link href="/calculus" style={{color:"#93c5fd",textDecoration:"none",border:"1px solid #344861",borderRadius:8,padding:"10px 13px",fontSize:12}}>← Back to Calculus</Link>
    </header>

    <div style={{padding:"24px 24px 12px"}}>
      <div style={{color:"#38bdf8",fontSize:11,fontWeight:800,letterSpacing:1.5}}>CALCULUS / VECTOR DIFFERENTIATION</div>
      <h1 style={{fontSize:26,fontWeight:600,margin:"12px 0 7px"}}>Gradient & Directional Derivatives</h1>
      <p style={{color:"#9fb2ca",fontSize:13,margin:0,lineHeight:1.7}}>See how the gradient points toward the steepest increase, and how the directional derivative measures the slope in a chosen direction.</p>
    </div>

    <div className="gradient-layout" style={{display:"grid",gridTemplateColumns:"minmax(0,1fr) 350px",gap:16,padding:"12px 24px 28px",alignItems:"start"}}>
      <section style={{...panel,padding:0,overflow:"hidden",minWidth:0}}>
        <div style={{height:"min(66vh,660px)",minHeight:390}}>
          <GradientScene functionId={functionId} a={a} b={b} directionAngle={directionAngle} showGradient={showGradient} showDirection={showDirection} showSurface={showSurface}/>
        </div>
        <div style={{display:"flex",flexWrap:"wrap",gap:14,padding:"12px 15px",borderTop:"1px solid #263b55",color:"#9fb2ca",fontSize:10}}>
          <span><span style={{color:"#22b8d5"}}>●</span> Function surface</span>
          <span><span style={{color:"#fbbf24"}}>●</span> Gradient ∇f</span>
          <span><span style={{color:"#fb7185"}}>●</span> Direction u</span>
          <span>Drag to rotate · Scroll to zoom</span>
        </div>
      </section>

      <aside style={{display:"grid",gap:13}}>
        <section style={panel}>
          <label htmlFor="gradient-function" style={{display:"block",fontSize:12,marginBottom:9}}>Function</label>
          <select id="gradient-function" value={functionId} onChange={(e)=>setFunctionId(e.target.value as GradientFunctionId)} style={fieldStyle}>
            {gradientFunctions.map((item)=><option key={item.id} value={item.id}>{item.label}</option>)}
          </select>
          <div style={{color:"#7dd3fc",fontWeight:700,fontSize:14,marginTop:12}}>{fn.formula}</div>
        </section>

        <section style={panel}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:13}}>Point P(a, b)</div>
          <label style={{display:"flex",justifyContent:"space-between",fontSize:11,marginBottom:7}}>a <strong>{formatGradientNumber(a)}</strong></label>
          <input aria-label="Point coordinate a" type="range" min="-2" max="2" step="0.05" value={a} onChange={(e)=>setA(Number(e.target.value))} style={{width:"100%",accentColor:"#38bdf8"}}/>
          <label style={{display:"flex",justifyContent:"space-between",fontSize:11,margin:"14px 0 7px"}}>b <strong>{formatGradientNumber(b)}</strong></label>
          <input aria-label="Point coordinate b" type="range" min="-2" max="2" step="0.05" value={b} onChange={(e)=>setB(Number(e.target.value))} style={{width:"100%",accentColor:"#38bdf8"}}/>
          <button type="button" onClick={()=>{setA(1);setB(1);}} style={{marginTop:13,background:"#1c2c42",color:"#cbd5e1",border:"1px solid #344861",borderRadius:7,padding:"8px 11px",fontSize:11}}>Reset point</button>
        </section>

        <section style={panel}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:12}}>Direction angle θ</div>
          <div style={{display:"flex",justifyContent:"space-between",fontSize:11,marginBottom:7}}>Angle in xy-plane <strong>{angleText}</strong></div>
          <input aria-label="Direction angle theta" type="range" min="0" max="360" step="1" value={directionAngle} onChange={(e)=>setDirectionAngle(Number(e.target.value))} style={{width:"100%",accentColor:"#fb7185"}}/>
          <div style={{color:"#94a3b8",fontSize:10,lineHeight:1.7,marginTop:8}}>The direction vector rotates in the xy-plane. Its length is always 1.</div>
        </section>

        <section style={panel}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:11}}>3D Display</div>
          {[
            {label:"Function surface",checked:showSurface,setter:setShowSurface},
            {label:"Gradient vector",checked:showGradient,setter:setShowGradient},
            {label:"Direction vector",checked:showDirection,setter:setShowDirection},
          ].map((item)=><label key={item.label} style={{display:"flex",alignItems:"center",gap:9,fontSize:11,margin:"9px 0",cursor:"pointer"}}>
            <input type="checkbox" checked={item.checked} onChange={(e)=>item.setter(e.target.checked)}/>{item.label}
          </label>)}
        </section>

        <section style={panel}>
          <div style={{fontSize:12,color:"#7dd3fc",fontWeight:800,marginBottom:12}}>LIVE RESULTS</div>
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:9}}>
            {[
              {label:"f(a,b)",number:value},{label:"fₓ(a,b)",number:gx},
              {label:"fᵧ(a,b)",number:gy},{label:"|∇f|",number:magnitude},
            ].map((item)=><div key={item.label} style={{background:"#0b1728",border:"1px solid #263b55",borderRadius:9,padding:10}}>
              <div style={{color:"#94a3b8",fontSize:10}}>{item.label}</div>
              <div style={{color:"#e2e8f0",fontSize:16,fontWeight:700,marginTop:5}}>{formatGradientNumber(item.number)}</div>
            </div>)}
          </div>
        </section>
      </aside>
    </div>

    <div style={{padding:"0 24px 32px",display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(280px,1fr))",gap:14}}>
      <section style={panel}>
        <div style={{color:"#fbbf24",fontSize:12,fontWeight:800,marginBottom:10}}>1. GRADIENT VECTOR</div>
        <div style={{fontSize:17,lineHeight:1.8}}>∇f(a,b) = ({formatGradientNumber(gx)}, {formatGradientNumber(gy)})</div>
        <div style={{color:"#a9bdd4",fontSize:12,lineHeight:1.8,marginTop:7}}>∇f = (∂f/∂x, ∂f/∂y). The gradient points in the direction of the steepest increase. Its magnitude gives the maximum rate of increase.</div>
        <div style={{color:"#7dd3fc",fontSize:12,marginTop:10}}>{gradientDirection}</div>
      </section>

      <section style={panel}>
        <div style={{color:"#fb7185",fontSize:12,fontWeight:800,marginBottom:10}}>2. UNIT DIRECTION VECTOR</div>
        <div style={{fontSize:17,lineHeight:1.8}}>u = ({formatGradientNumber(ux)}, {formatGradientNumber(uy)})</div>
        <div style={{color:"#a9bdd4",fontSize:12,lineHeight:1.8,marginTop:7}}>u = (cos θ, sin θ), where θ = {angleText}. Since u is a unit vector, its magnitude is 1.</div>
      </section>

      <section style={{...panel,gridColumn:"1 / -1"}}>
        <div style={{color:"#34d399",fontSize:12,fontWeight:800,marginBottom:10}}>3. DIRECTIONAL DERIVATIVE</div>
        <div style={{fontSize:18,lineHeight:1.8}}>Dᵤf(a,b) = ∇f(a,b) · u</div>
        <div style={{color:"#a9bdd4",fontSize:13,lineHeight:1.9,marginTop:7}}>
          = fₓ(a,b)uₓ + fᵧ(a,b)uᵧ<br/>
          = {calculation}<br/>
          <strong style={{color:"#34d399",fontSize:20}}>= {formatGradientNumber(directionalDerivative)}</strong>
        </div>
        <div style={{color:"#a9bdd4",fontSize:12,lineHeight:1.8,marginTop:9}}>
          Interpretation: {directionalDerivative>0.0001 ? "The function increases in the selected direction." : directionalDerivative< -0.0001 ? "The function decreases in the selected direction." : "The instantaneous rate of change is approximately zero in the selected direction."}
        </div>
      </section>

      <section style={{...panel,gridColumn:"1 / -1"}}>
        <div style={{color:"#7dd3fc",fontSize:12,fontWeight:800,marginBottom:10}}>STEP-BY-STEP METHOD</div>
        <ol style={{color:"#c5d4e6",fontSize:12,lineHeight:2,paddingLeft:20,margin:0}}>
          <li>Find the partial derivatives fₓ and fᵧ.</li>
          <li>Evaluate them at the selected point P(a,b).</li>
          <li>Form the gradient vector ∇f(a,b) = (fₓ, fᵧ).</li>
          <li>Convert the chosen angle θ into the unit vector u = (cos θ, sin θ).</li>
          <li>Calculate the dot product ∇f · u. This is the directional derivative.</li>
        </ol>
      </section>
    </div>
  </main>;
}
'''
}

if not (ROOT / "package.json").exists():
    raise SystemExit("Run this script from the project root (the folder containing package.json).")

for relative_path, content in FILES.items():
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {relative_path}")
    path.write_text(content.lstrip("\n"), encoding="utf-8")
    print(f"Created: {relative_path}")

print("\nGradient & Directional Derivatives module files created.")
print("Existing board and Partial Derivatives module were not modified.")
print("Next: run ESLint on the three files, then pnpm build.")
