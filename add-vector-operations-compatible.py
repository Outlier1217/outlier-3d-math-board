from pathlib import Path
p = Path("src/app/page.tsx")
s = Path("src/components/three-d-scene.tsx")
if not p.exists() or not s.exists():
    raise SystemExit("Run from project root.")
page, scene = p.read_text(), s.read_text()

# Page: operation state
anchor = "  const pointDistance = Math.sqrt(dx * dx + dy * dy + dz * dz);"
if "const [vectorOperation" not in page:
    if anchor not in page: raise SystemExit("Missing pointDistance anchor; no changes made.")
    page = page.replace(anchor, anchor + '''
  const [vectorOperation, setVectorOperation] = useState<"add" | "subtract">("add");
  const vectorResult = distanceA && distanceB ? {
    x: vectorOperation === "add" ? distanceA.x + distanceB.x : distanceA.x - distanceB.x,
    y: vectorOperation === "add" ? distanceA.y + distanceB.y : distanceA.y - distanceB.y,
    z: vectorOperation === "add" ? distanceA.z + distanceB.z : distanceA.z - distanceB.z,
  } : null;
  const vectorResultMagnitude = vectorResult
    ? Math.sqrt(vectorResult.x ** 2 + vectorResult.y ** 2 + vectorResult.z ** 2)
    : 0;''', 1)

# Page: current compact ThreeDPreview signature
old = "function ThreeDPreview({ distancePointIds }: { distancePointIds: [string, string] | null }) {"
new = 'function ThreeDPreview({ distancePointIds, vectorOperation }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract" }) {'
if "function ThreeDPreview({ distancePointIds, vectorOperation }" not in page:
    if old not in page: raise SystemExit("Missing exact ThreeDPreview signature; no files changed.")
    page = page.replace(old, new, 1)
page = page.replace("<ThreeDScene distancePointIds={distancePointIds} />", "<ThreeDScene distancePointIds={distancePointIds} vectorOperation={vectorOperation} />", 1)
page = page.replace(
    '<ThreeDPreview distancePointIds={distanceAId && distanceBId ? [distanceAId, distanceBId] : null} />',
    '<ThreeDPreview distancePointIds={distanceAId && distanceBId ? [distanceAId, distanceBId] : null} vectorOperation={vectorOperation} />'
)

# Page: operation panel
if "VECTOR OPERATIONS" not in page:
    marker = '''            <div className="inspector-section">
              <span className="sidebar-group-label">DISTANCE BETWEEN POINTS</span>'''
    panel = '''            <div className="inspector-section">
              <span className="sidebar-group-label">VECTOR OPERATIONS</span>
              <div style={{ display: "flex", gap: 6, marginTop: 8, marginBottom: 10 }}>
                <button type="button" onClick={() => setVectorOperation("add")} style={{ flex: 1, padding: "8px 6px", borderRadius: 7, border: "1px solid", borderColor: vectorOperation === "add" ? "#22C55E" : "var(--border, #30303a)", background: vectorOperation === "add" ? "rgba(34,197,94,0.14)" : "transparent", color: vectorOperation === "add" ? "#86EFAC" : "inherit", cursor: "pointer", fontSize: 11 }}>A + B</button>
                <button type="button" onClick={() => setVectorOperation("subtract")} style={{ flex: 1, padding: "8px 6px", borderRadius: 7, border: "1px solid", borderColor: vectorOperation === "subtract" ? "#A78BFA" : "var(--border, #30303a)", background: vectorOperation === "subtract" ? "rgba(167,139,250,0.14)" : "transparent", color: vectorOperation === "subtract" ? "#C4B5FD" : "inherit", cursor: "pointer", fontSize: 11 }}>A − B</button>
              </div>
              {distancePointA && distancePointB && vectorResult ? (
                <div style={{ padding: 11, borderRadius: 8, background: "rgba(34,197,94,0.06)", border: "1px solid rgba(34,197,94,0.18)", fontSize: 11, lineHeight: 1.75 }}>
                  <strong>{distancePointA.name} {vectorOperation === "add" ? "+" : "−"} {distancePointB.name}</strong>
                  <div>A = ({distanceA!.x}, {distanceA!.y}, {distanceA!.z})</div>
                  <div>B = ({distanceB!.x}, {distanceB!.y}, {distanceB!.z})</div>
                  <div>{vectorOperation === "add" ? "A + B" : "A − B"} = ({vectorResult.x}, {vectorResult.y}, {vectorResult.z})</div>
                  <strong>R = {vectorResult.x}i + ({vectorResult.y})j + ({vectorResult.z})k</strong>
                  <div>|R| = √({vectorResult.x ** 2} + {vectorResult.y ** 2} + {vectorResult.z ** 2})</div>
                  <strong>|R| = {Number(vectorResultMagnitude.toFixed(4))}</strong>
                </div>
              ) : <p style={{ fontSize: 11 }}>Add at least two points to calculate vector operations.</p>}
            </div>

            <div className="inspector-section">
              <span className="sidebar-group-label">DISTANCE BETWEEN POINTS</span>'''
    if marker not in page: raise SystemExit("Missing Distance inspector section; no files changed.")
    page = page.replace(marker, panel, 1)

# Scene: insert vector helper components and change Scene signature
old_scene = "function Scene({ distancePointIds }: { distancePointIds: [string,string] | null }) {"
if "function VectorOperationGraphic" not in scene:
    helper = '''function VectorOperationGraphic({ points, pointIds, operation }: { points: ScenePoint[]; pointIds: [string, string] | null; operation: "add" | "subtract" }) {
  if (!pointIds) return null;
  const pa = points.find((point) => point.id === pointIds[0]);
  const pb = points.find((point) => point.id === pointIds[1]);
  if (!pa?.visible || !pb?.visible) return null;
  const a: [number, number, number] = [pa.position.x, pa.position.y, pa.position.z];
  const b: [number, number, number] = [pb.position.x, pb.position.y, pb.position.z];
  const result: [number, number, number] = operation === "add"
    ? [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
    : [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const translatedB: [number, number, number] = operation === "add"
    ? [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
    : [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  return <group>
    <Line points={[[0, 0, 0], a]} color="#22C55E" lineWidth={2.5} />
    <Line points={[[0, 0, 0], b]} color="#38BDF8" lineWidth={2.5} />
    {operation === "add" ? <>
      <Line points={[a, result]} color="#38BDF8" lineWidth={2} dashed />
      <Line points={[b, result]} color="#22C55E" lineWidth={2} dashed />
    </> : <Line points={[a, translatedB]} color="#A78BFA" lineWidth={2.5} />}
    <Line points={[[0, 0, 0], result]} color="#FACC15" lineWidth={3.5} />
    <Text position={[result[0] + 0.12, result[1] + 0.12, result[2] + 0.12]} fontSize={0.24} color="#FACC15" outlineWidth={0.02} outlineColor="#0F172A">
      {operation === "add" ? "A + B" : "A − B"}
    </Text>
  </group>;
}

function Scene({ distancePointIds, vectorOperation }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract" }) {'''
    if old_scene not in scene: raise SystemExit("Missing exact Scene signature; page not written.")
    scene = scene.replace(old_scene, helper, 1)

render_anchor = "      <DistanceSegment points={points} pointIds={distancePointIds} />"
if "<VectorOperationGraphic" not in scene:
    if render_anchor not in scene: raise SystemExit("Missing DistanceSegment render; page not written.")
    scene = scene.replace(render_anchor, render_anchor + '''
      <VectorOperationGraphic points={points} pointIds={distancePointIds} operation={vectorOperation} />''', 1)

old_export = "export default function ThreeDScene({ distancePointIds = null }: { distancePointIds?: [string,string] | null }) {"
new_export = 'export default function ThreeDScene({ distancePointIds = null, vectorOperation = "add" }: { distancePointIds?: [string,string] | null; vectorOperation?: "add" | "subtract" }) {'
if "vectorOperation = \"add\"" not in scene:
    if old_export not in scene: raise SystemExit("Missing exact ThreeDScene export signature; no files written.")
    scene = scene.replace(old_export, new_export, 1)
scene = scene.replace("<Scene distancePointIds={distancePointIds} />", "<Scene distancePointIds={distancePointIds} vectorOperation={vectorOperation} />", 1)

p.write_text(page)
s.write_text(scene)
print("Vector Addition and Subtraction integrated successfully.")
print("Updated src/app/page.tsx and src/components/three-d-scene.tsx")
