from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "src/app/page.tsx"
SCENE = ROOT / "src/components/three-d-scene.tsx"

page = PAGE.read_text()
scene = SCENE.read_text()

# Validate anchors and existing scene wiring before changing files.
required = [
    ('  const [octantMode, setOctantMode] = useState<"auto" | "manual">("auto");', page, "page calculation anchor"),
    ('            <div className="inspector-section">\n              <span className="sidebar-group-label">CROSS PRODUCT</span>', page, "cross-product inspector"),
    ('function Scene({ distancePointIds, vectorOperation }:', scene, "scene function"),
    ('      <CrossProductGraphic points={points} pointIds={distancePointIds} />', scene, "cross-product scene render"),
]
for anchor, source, label in required:
    if anchor not in source:
        raise SystemExit(f"Missing {label}; no files changed.")

if "const planeNormal =" in page or "PLANE EQUATION &amp; NORMAL VECTOR" in page:
    raise SystemExit("Plane module already appears to be integrated; no files changed.")
if "function PlaneGraphic" in scene:
    raise SystemExit("PlaneGraphic already exists; no files changed.")

# Plane is represented by n·x + d = 0. Three-point plane is derived from A,B,C.
calc_anchor = '  const [octantMode, setOctantMode] = useState<"auto" | "manual">("auto");'
calc_insert = '''  // Plane equation n·x + d = 0 and optional plane through three selected points.
  const [planeMode, setPlaneMode] = useState<"coefficients" | "three-points">("coefficients");
  const [planeCoefficients, setPlaneCoefficients] = useState({ a: 1, b: 1, c: 1, d: -4 });
  const [planePointIds, setPlanePointIds] = useState<[string, string, string]>(["", "", ""]);
  const planeNormal = { x: planeCoefficients.a, y: planeCoefficients.b, z: planeCoefficients.c };
  const planeNormalMagnitude = Math.hypot(planeNormal.x, planeNormal.y, planeNormal.z);
  const planePoints = planePointIds.map((id) => points.find((point) => point.id === id) ?? null);
  const planeHasThreePoints = planePoints.every((point) => point !== null);
  const planeA = planeHasThreePoints ? planePoints[0]!.position : null;
  const planeB = planeHasThreePoints ? planePoints[1]!.position : null;
  const planeC = planeHasThreePoints ? planePoints[2]!.position : null;
  const planeAB = planeA && planeB ? { x: planeB.x-planeA.x, y: planeB.y-planeA.y, z: planeB.z-planeA.z } : null;
  const planeAC = planeA && planeC ? { x: planeC.x-planeA.x, y: planeC.y-planeA.y, z: planeC.z-planeA.z } : null;
  const threePointNormal = planeAB && planeAC ? {
    x: planeAB.y*planeAC.z-planeAB.z*planeAC.y,
    y: planeAB.z*planeAC.x-planeAB.x*planeAC.z,
    z: planeAB.x*planeAC.y-planeAB.y*planeAC.x,
  } : null;
  const threePointNormalMagnitude = threePointNormal ? Math.hypot(threePointNormal.x, threePointNormal.y, threePointNormal.z) : 0;
  const threePointD = planeA && threePointNormal
    ? -(threePointNormal.x*planeA.x + threePointNormal.y*planeA.y + threePointNormal.z*planeA.z)
    : 0;
  const activePlane = planeMode === "three-points" && threePointNormal && threePointNormalMagnitude > 1e-8
    ? { a: threePointNormal.x, b: threePointNormal.y, c: threePointNormal.z, d: threePointD }
    : planeCoefficients;
  const activePlaneNormalMagnitude = Math.hypot(activePlane.a, activePlane.b, activePlane.c);
  const planeIsValid = activePlaneNormalMagnitude > 1e-8;

'''
page = page.replace(calc_anchor, calc_insert + calc_anchor, 1)

# Add inspector section before cross product.
inspector_anchor = '''            <div className="inspector-section">
              <span className="sidebar-group-label">CROSS PRODUCT</span>'''
inspector_insert = '''            <div className="inspector-section">
              <span className="sidebar-group-label">3D PLANE GEOMETRY</span>
              <div style={{ display: "flex", gap: 6, marginTop: 8, marginBottom: 10 }}>
                <button type="button" onClick={() => setPlaneMode("coefficients")} style={{ flex: 1, padding: "7px 5px", borderRadius: 7, border: "1px solid", borderColor: planeMode === "coefficients" ? "#38BDF8" : "var(--border, #30303a)", background: planeMode === "coefficients" ? "rgba(56,189,248,0.13)" : "transparent", color: planeMode === "coefficients" ? "#7DD3FC" : "inherit", cursor: "pointer", fontSize: 10 }}>Equation</button>
                <button type="button" onClick={() => setPlaneMode("three-points")} style={{ flex: 1, padding: "7px 5px", borderRadius: 7, border: "1px solid", borderColor: planeMode === "three-points" ? "#38BDF8" : "var(--border, #30303a)", background: planeMode === "three-points" ? "rgba(56,189,248,0.13)" : "transparent", color: planeMode === "three-points" ? "#7DD3FC" : "inherit", cursor: "pointer", fontSize: 10 }}>3 Points</button>
              </div>
              {planeMode === "coefficients" ? (
                <>
                  <div style={{ fontSize: 11, color: "#CBD5E1", marginBottom: 7 }}>ax + by + cz + d = 0</div>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 5 }}>
                    {(["a", "b", "c", "d"] as const).map((key) => (
                      <label key={key} style={{ fontSize: 10, color: "#94A3B8" }}>
                        {key}
                        <input type="number" value={planeCoefficients[key]} onChange={(event) => setPlaneCoefficients((current) => ({ ...current, [key]: Number(event.target.value) }))} style={{ width: "100%", minWidth: 0, marginTop: 3, padding: "6px 4px", borderRadius: 5, background: "var(--input, #111827)", color: "inherit", border: "1px solid var(--border, #30303a)" }} />
                      </label>
                    ))}
                  </div>
                </>
              ) : (
                <>
                  <div style={{ fontSize: 10, color: "#94A3B8", marginBottom: 6 }}>Choose three distinct points:</div>
                  {([0, 1, 2] as const).map((index) => (
                    <label key={index} className="property-row">
                      <span>Point {String.fromCharCode(65 + index)}</span>
                      <select value={planePointIds[index]} onChange={(event) => setPlanePointIds((current) => current.map((id, i) => i === index ? event.target.value : id) as [string, string, string])}>
                        <option value="">Select point</option>
                        {points.filter((point) => !planePointIds.some((id, i) => i !== index && id === point.id)).map((point) => (
                          <option key={point.id} value={point.id}>{point.name}</option>
                        ))}
                      </select>
                    </label>
                  ))}
                  {planeHasThreePoints && threePointNormal && threePointNormalMagnitude > 1e-8 ? (
                    <div style={{ fontSize: 10, color: "#CBD5E1", lineHeight: 1.6, marginTop: 7 }}>
                      <div>AB = ({planeAB!.x}, {planeAB!.y}, {planeAB!.z})</div>
                      <div>AC = ({planeAC!.x}, {planeAC!.y}, {planeAC!.z})</div>
                      <div>n = AB × AC = ({threePointNormal.x}, {threePointNormal.y}, {threePointNormal.z})</div>
                      <div>d = −n · A = {Number(threePointD.toFixed(4))}</div>
                    </div>
                  ) : (
                    <p style={{ fontSize: 10, color: "#FCA5A5", marginTop: 6 }}>
                      Select three distinct, non-collinear points to define a plane.
                    </p>
                  )}
                </>
              )}
              <div style={{ marginTop: 9, padding: 10, borderRadius: 8, background: "rgba(56,189,248,0.07)", border: "1px solid rgba(56,189,248,0.2)", fontSize: 11, lineHeight: 1.7 }}>
                {planeMode === "three-points" && (!planeHasThreePoints || !threePointNormal || threePointNormalMagnitude <= 1e-8) ? (
                  <strong style={{ color: "#FCA5A5" }}>A valid plane needs three non-collinear points.</strong>
                ) : planeIsValid ? (
                  <>
                    <strong style={{ display: "block", color: "#7DD3FC" }}>Plane equation</strong>
                    {Number(activePlane.a.toFixed(4))}x + ({Number(activePlane.b.toFixed(4))})y + ({Number(activePlane.c.toFixed(4))})z + ({Number(activePlane.d.toFixed(4))}) = 0
                    <strong style={{ display: "block", color: "#BAE6FD", marginTop: 5 }}>Normal vector</strong>
                    n = ({Number(activePlane.a.toFixed(4))}, {Number(activePlane.b.toFixed(4))}, {Number(activePlane.c.toFixed(4))})
                    <div>|n| = {Number(activePlaneNormalMagnitude.toFixed(4))}</div>
                  </>
                ) : (
                  <strong style={{ color: "#FCA5A5" }}>Normal vector cannot be zero.</strong>
                )}
              </div>
            </div>

'''
page = page.replace(inspector_anchor, inspector_insert + inspector_anchor, 1)

# Add a plane mesh and normal vector to the existing R3F scene.
graphic_anchor = 'function Scene({ distancePointIds, vectorOperation }:'
plane_graphic = '''function PlaneGraphic({ equation }: { equation: { a: number; b: number; c: number; d: number } | null }) {
  if (!equation) return null;
  const { a, b, c, d } = equation;
  const normal = new THREE.Vector3(a, b, c);
  const normalLength = normal.length();
  if (normalLength < 1e-8) return null;
  normal.normalize();

  const center = new THREE.Vector3(-d * a / (a*a+b*b+c*c), -d * b / (a*a+b*b+c*c), -d * c / (a*a+b*b+c*c));
  const helper = Math.abs(normal.z) < 0.9 ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(0, 1, 0);
  const u = new THREE.Vector3().crossVectors(normal, helper).normalize();
  const v = new THREE.Vector3().crossVectors(normal, u).normalize();
  const size = 7;
  const corners = [
    center.clone().addScaledVector(u, -size).addScaledVector(v, -size),
    center.clone().addScaledVector(u, size).addScaledVector(v, -size),
    center.clone().addScaledVector(u, size).addScaledVector(v, size),
    center.clone().addScaledVector(u, -size).addScaledVector(v, size),
  ];
  const position: [number, number, number] = [center.x, center.y, center.z];
  const normalEnd = center.clone().addScaledVector(normal, 2.4);
  return (
    <group>
      <mesh position={position} quaternion={new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal)}>
        <planeGeometry args={[size * 2, size * 2, 1, 1]} />
        <meshBasicMaterial color="#38BDF8" transparent opacity={0.22} side={THREE.DoubleSide} depthWrite={false} />
      </mesh>
      <Line points={[corners[0].toArray(), corners[1].toArray(), corners[2].toArray(), corners[3].toArray(), corners[0].toArray()]} color="#7DD3FC" lineWidth={1.5} />
      <Line points={[position, [normalEnd.x, normalEnd.y, normalEnd.z]]} color="#F472B6" lineWidth={3.5} />
      <Text position={[normalEnd.x + 0.12, normalEnd.y + 0.12, normalEnd.z + 0.12]} fontSize={0.23} color="#F9A8D4" outlineWidth={0.02} outlineColor="#0F172A">Normal n</Text>
    </group>
  );
}

'''
scene = scene.replace(graphic_anchor, plane_graphic + graphic_anchor, 1)

# Extend scene props and render plane. Defaults keep other callers compatible.
scene = scene.replace(
    'function Scene({ distancePointIds, vectorOperation }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract" }) {',
    'function Scene({ distancePointIds, vectorOperation, planeEquation }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null }) {',
    1,
)
render_anchor = '      <CrossProductGraphic points={points} pointIds={distancePointIds} />'
if render_anchor not in scene:
    raise SystemExit("Could not find cross-product render line; no files changed.")
scene = scene.replace(render_anchor, render_anchor + '\n      <PlaneGraphic equation={planeEquation ?? null} />', 1)

scene = scene.replace(
    'export default function ThreeDScene({ distancePointIds = null, vectorOperation = "add" }: { distancePointIds?: [string,string] | null; vectorOperation?: "add" | "subtract" }) {',
    'export default function ThreeDScene({ distancePointIds = null, vectorOperation = "add", planeEquation = null }: { distancePointIds?: [string,string] | null; vectorOperation?: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null }) {',
    1,
)
scene = scene.replace(
    '<Scene distancePointIds={distancePointIds} vectorOperation={vectorOperation} />',
    '<Scene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} />',
    1,
)

# Update the page preview function and its invocation.
old_preview = 'function ThreeDPreview({ distancePointIds, vectorOperation }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract" }) {'
new_preview = 'function ThreeDPreview({ distancePointIds, vectorOperation, planeEquation }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation: { a: number; b: number; c: number; d: number } | null }) {'
if old_preview not in page:
    raise SystemExit("Could not find ThreeDPreview signature; no files changed.")
page = page.replace(old_preview, new_preview, 1)
page = page.replace(
    '<ThreeDScene distancePointIds={distancePointIds} vectorOperation={vectorOperation} />',
    '<ThreeDScene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} />',
    1,
)
old_call = '<ThreeDPreview distancePointIds={distanceAId && distanceBId ? [distanceAId, distanceBId] : null} vectorOperation={vectorOperation} />'
new_call = '<ThreeDPreview distancePointIds={distanceAId && distanceBId ? [distanceAId, distanceBId] : null} vectorOperation={vectorOperation} planeEquation={planeIsValid && (planeMode === "coefficients" || (planeHasThreePoints && threePointNormalMagnitude > 1e-8)) ? activePlane : null} />'
if old_call not in page:
    raise SystemExit("Could not find ThreeDPreview invocation; no files changed.")
page = page.replace(old_call, new_call, 1)

PAGE.write_text(page)
SCENE.write_text(scene)
print("3D Plane Geometry integrated successfully.")
print("Updated src/app/page.tsx and src/components/three-d-scene.tsx")
print("Includes editable plane coefficients, three-point plane generation, normal vector and 3D plane visualization.")
