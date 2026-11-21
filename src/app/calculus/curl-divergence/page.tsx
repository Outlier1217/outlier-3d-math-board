"use client";

import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import {
  customDivergence,
  evaluateCustomField,
  formatNumber,
  vectorFields,
  type VectorFieldId,
} from "@/lib/curl-divergence";

const CurlDivergenceScene = dynamic(() => import("@/components/curl-divergence-scene"), {
  ssr: false,
  loading: () => <div className="h-[440px] animate-pulse rounded-xl bg-slate-900" />,
});

const inputClass = "w-full rounded-lg border border-white/10 bg-[#111a29] px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400";
const panelClass = "rounded-xl border border-white/10 bg-[#0c1422] p-4";

export default function CurlDivergencePage() {
  const [fieldId, setFieldId] = useState<VectorFieldId>("rotation");
  const [point, setPoint] = useState<[number, number, number]>([1, 1, 0]);
  const [showField, setShowField] = useState(true);
  const [showCurl, setShowCurl] = useState(true);
  const [showPoint, setShowPoint] = useState(true);
  const [coefficients, setCoefficients] = useState<[number, number, number]>([1, 1, 1]);

  const field = vectorFields.find((item) => item.id === fieldId) ?? vectorFields[0];
  const [x, y, z] = point;

  const values = useMemo(() => {
    if (fieldId === "custom") {
      return {
        vector: evaluateCustomField(x, y, z, ...coefficients),
        curl: [0, 0, 0] as [number, number, number],
        divergence: customDivergence(...coefficients),
      };
    }
    return {
      vector: field.evaluate(x, y, z),
      curl: field.curl(x, y, z),
      divergence: field.divergence(x, y, z),
    };
  }, [fieldId, x, y, z, coefficients, field]);

  const curlMagnitude = Math.hypot(...values.curl);
  const divergenceMeaning = values.divergence > 1e-8
    ? "Positive: net outward flow (source)"
    : values.divergence < -1e-8
      ? "Negative: net inward flow (sink)"
      : "Zero: locally no net expansion or compression";

  const updatePoint = (index: number, value: number) => {
    setPoint((current) => current.map((item, i) => i === index ? value : item) as [number, number, number]);
  };
  const updateCoefficient = (index: number, value: number) => {
    setCoefficients((current) => current.map((item, i) => i === index ? value : item) as [number, number, number]);
  };

  return (
    <main className="calculus-page min-h-screen bg-[#070c14] px-4 py-6 text-slate-100 md:px-8">
      <div className="mx-auto max-w-[1500px] space-y-6">
        <header className="space-y-2">
          <a href="/calculus" className="text-sm text-cyan-400 hover:text-cyan-300">← Back to Calculus Visualizer</a>
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-400">Outlier 3D Mathematics</p>
              <h1 className="text-3xl font-bold tracking-tight md:text-4xl">Curl &amp; Divergence</h1>
              <p className="mt-2 max-w-3xl text-sm text-slate-400">Explore rotation and expansion in 3D vector fields with live mathematical calculations.</p>
            </div>
            <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-300">Module 04 · Vector Calculus</span>
          </div>
        </header>

        <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
          <div className="space-y-4">
            <div className={panelClass}>
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                <div><h2 className="font-semibold">3D Vector Field</h2><p className="text-xs text-slate-400">Drag to rotate · Scroll to zoom</p></div>
                <div className="flex flex-wrap gap-3 text-xs text-slate-300">
                  <span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-sky-400" />Field vectors</span>
                  <span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-amber-400" />Curl</span>
                  <span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-pink-400" />Point P</span>
                </div>
              </div>
              <CurlDivergenceScene fieldId={fieldId} point={point} showField={showField} showCurl={showCurl} showPoint={showPoint} coefficients={coefficients} />
              <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-400">
                {[
                  { label: "Field vectors", checked: showField, set: setShowField },
                  { label: "Curl vector", checked: showCurl, set: setShowCurl },
                  { label: "Selected point", checked: showPoint, set: setShowPoint },
                ].map((item) => (
                  <label key={item.label} className="flex cursor-pointer items-center gap-2">
                    <input type="checkbox" checked={item.checked} onChange={(event) => item.set(event.target.checked)} className="accent-cyan-400" />
                    {item.label}
                  </label>
                ))}
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className={panelClass}>
                <p className="text-xs uppercase tracking-wider text-slate-400">Vector field</p>
                <p className="mt-2 text-lg font-semibold text-cyan-300">{field.formula}</p>
                <p className="mt-2 text-sm text-slate-400">{field.description}</p>
              </div>
              <div className={panelClass}>
                <p className="text-xs uppercase tracking-wider text-slate-400">Selected point</p>
                <p className="mt-2 font-mono text-lg text-pink-300">P = ({point.map(formatNumber).join(", ")})</p>
                <p className="mt-2 text-sm text-slate-400">F(P) = ({values.vector.map(formatNumber).join(", ")})</p>
              </div>
            </div>
          </div>

          <aside className="space-y-4">
            <div className={panelClass}>
              <h2 className="mb-3 font-semibold">Field presets</h2>
              <div className="space-y-2">
                {vectorFields.map((item) => (
                  <button key={item.id} onClick={() => setFieldId(item.id)} className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition ${fieldId === item.id ? "border-cyan-400 bg-cyan-400/10 text-cyan-200" : "border-white/10 bg-[#111a29] text-slate-300 hover:border-white/20"}`}>
                    <span className="block font-medium">{item.label}</span><span className="mt-0.5 block text-xs text-slate-500">{item.formula}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className={panelClass}>
              <h2 className="mb-3 font-semibold">Point P coordinates</h2>
              <div className="grid grid-cols-3 gap-2">
                {(["x", "y", "z"] as const).map((axis, index) => (
                  <label key={axis} className="text-xs text-slate-400">{axis.toUpperCase()}
                    <input className={`${inputClass} mt-1`} type="number" step="0.5" value={point[index]} onChange={(event) => updatePoint(index, Number(event.target.value))} />
                  </label>
                ))}
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <button onClick={() => setPoint([0, 0, 0])} className="rounded-md bg-slate-800 px-3 py-1.5 text-xs hover:bg-slate-700">Origin</button>
                <button onClick={() => setPoint([1, 1, 1])} className="rounded-md bg-slate-800 px-3 py-1.5 text-xs hover:bg-slate-700">P(1,1,1)</button>
                <button onClick={() => setPoint([2, -1, 1])} className="rounded-md bg-slate-800 px-3 py-1.5 text-xs hover:bg-slate-700">P(2,-1,1)</button>
              </div>
            </div>

            {fieldId === "custom" && (
              <div className={panelClass}>
                <h2 className="mb-3 font-semibold">Custom coefficients</h2>
                <div className="grid grid-cols-3 gap-2">
                  {(["a", "b", "c"] as const).map((label, index) => (
                    <label key={label} className="text-xs text-slate-400">{label}
                      <input className={`${inputClass} mt-1`} type="number" step="0.5" value={coefficients[index]} onChange={(event) => updateCoefficient(index, Number(event.target.value))} />
                    </label>
                  ))}
                </div>
              </div>
            )}
          </aside>
        </section>

        <section className="grid gap-4 md:grid-cols-2">
          <div className={`${panelClass} space-y-3`}>
            <div className="flex items-center justify-between"><h2 className="font-semibold">Curl</h2><span className="rounded-full bg-amber-400/10 px-2 py-1 text-xs text-amber-300">Rotation</span></div>
            <p className="text-xs text-slate-400">Measures local rotation of the vector field.</p>
            <p className="font-mono text-sm text-amber-200">∇ × F = ({values.curl.map(formatNumber).join(", ")})</p>
            <p className="text-2xl font-bold tabular-nums">{formatNumber(curlMagnitude)} <span className="text-sm font-normal text-slate-400">|curl|</span></p>
            <div className="rounded-lg bg-[#111a29] p-3 text-xs leading-6 text-slate-300">
              <p>∇ × F = (∂R/∂y − ∂Q/∂z, ∂P/∂z − ∂R/∂x, ∂Q/∂x − ∂P/∂y)</p>
              <p className="mt-1 text-slate-400">For this field: curl = ({values.curl.map(formatNumber).join(", ")}).</p>
            </div>
          </div>
          <div className={`${panelClass} space-y-3`}>
            <div className="flex items-center justify-between"><h2 className="font-semibold">Divergence</h2><span className="rounded-full bg-emerald-400/10 px-2 py-1 text-xs text-emerald-300">Expansion / Compression</span></div>
            <p className="text-xs text-slate-400">Measures net outward flow per unit volume.</p>
            <p className="font-mono text-sm text-emerald-200">∇ · F = {formatNumber(values.divergence)}</p>
            <p className="text-lg font-semibold text-emerald-200">{divergenceMeaning}</p>
            <div className="rounded-lg bg-[#111a29] p-3 text-xs leading-6 text-slate-300">
              <p>∇ · F = ∂P/∂x + ∂Q/∂y + ∂R/∂z</p>
              <p className="mt-1 text-slate-400">For this field: divergence = {formatNumber(values.divergence)}.</p>
            </div>
          </div>
        </section>

        <section className={panelClass}>
          <h2 className="mb-3 font-semibold">How to interpret the result</h2>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-lg bg-[#111a29] p-3"><p className="font-semibold text-emerald-300">Divergence &gt; 0</p><p className="mt-1 text-sm text-slate-400">Source behaviour: more flow leaves a tiny region than enters it.</p></div>
            <div className="rounded-lg bg-[#111a29] p-3"><p className="font-semibold text-rose-300">Divergence &lt; 0</p><p className="mt-1 text-sm text-slate-400">Sink behaviour: more flow enters a tiny region than leaves it.</p></div>
            <div className="rounded-lg bg-[#111a29] p-3"><p className="font-semibold text-amber-300">Curl ≠ 0</p><p className="mt-1 text-sm text-slate-400">Local rotational tendency is present. Curl direction follows the right-hand rule.</p></div>
          </div>
        </section>
      </div>
    </main>
  );
}
