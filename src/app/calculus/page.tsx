"use client";
import { useState } from "react";
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
  const sample=tangentPlaneValue(fn,a,b,a+0.5,b+0.5);
  return <main className="calculus-page" style={{minHeight:"100vh",background:"#080f1d",color:"#e2e8f0",fontFamily:"Inter,ui-sans-serif,system-ui,sans-serif"}}>
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
