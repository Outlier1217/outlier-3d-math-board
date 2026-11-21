from pathlib import Path

page_path = Path('src/app/page.tsx')
scene_path = Path('src/components/three-d-scene.tsx')
if not page_path.exists() or not scene_path.exists():
    raise SystemExit('Run this script from the project root containing src/app/page.tsx.')

page = page_path.read_text()
scene = scene_path.read_text()

state_anchor = '  const pointDistance = Math.sqrt(dx * dx + dy * dy + dz * dz);\n'
state_insert = '''  const pointDistance = Math.sqrt(dx * dx + dy * dy + dz * dz);
  const [vectorOperation, setVectorOperation] = useState<"add" | "subtract">("add");
  const vectorResult = distanceA && distanceB
    ? {
        x: vectorOperation === "add" ? distanceA.x + distanceB.x : distanceA.x - distanceB.x,
        y: vectorOperation === "add" ? distanceA.y + distanceB.y : distanceA.y - distanceB.y,
        z: vectorOperation === "add" ? distanceA.z + distanceB.z : distanceA.z - distanceB.z,
      }
    : null;
  const vectorResultMagnitude = vectorResult
    ? Math.sqrt(vectorResult.x ** 2 + vectorResult.y ** 2 + vectorResult.z ** 2)
    : 0;
'''
if 'const [vectorOperation, setVectorOperation]' not in page:
    if state_anchor not in page:
        raise SystemExit('Could not find pointDistance calculation; no files changed.')
    page = page.replace(state_anchor, state_insert, 1)

preview_anchor = '''function ThreeDPreview({
  distancePointIds,
}: {
  distancePointIds: [string, string] | null;
}) {
'''
preview_insert = '''function ThreeDPreview({
  distancePointIds,
  vectorOperation,
}: {
  distancePointIds: [string, string] | null;
  vectorOperation: "add" | "subtract";
}) {
'''
if 'vectorOperation,\n}: {' not in page:
    if preview_anchor not in page:
        raise SystemExit('Could not find ThreeDPreview props; no files changed.')
    page = page.replace(preview_anchor, preview_insert, 1)

page = page.replace(
    '<ThreeDPreview distancePointIds={distanceAId && distanceBId ? [distanceAId, distanceBId] : null} />',
    '<ThreeDPreview distancePointIds={distanceAId && distanceBId ? [distanceAId, distanceBId] : null} vectorOperation={vectorOperation} />'
)

# Pass the new prop into the actual ThreeDScene component.
page = page.replace('<ThreeDScene distancePointIds={distancePointIds} />', '<ThreeDScene distancePointIds={distancePointIds} vectorOperation={vectorOperation} />', 1)

ui_anchor = '''            <div className="inspector-section">
              <span className="sidebar-group-label">DISTANCE BETWEEN POINTS</span>
'''
ui_insert = '''            <div className="inspector-section">
              <span className="sidebar-group-label">VECTOR OPERATIONS</span>
              <div style={{ display: "flex", gap: 6, marginTop: 8, marginBottom: 10 }}>
                <button type="button" onClick={() => setVectorOperation("add")} style={{
                  flex: 1, padding: "8px 6px", borderRadius: 7, border: "1px solid",
                  borderColor: vectorOperation === "add" ? "#22C55E" : "var(--border, #30303a)",
                  background: vectorOperation === "add" ? "rgba(34,197,94,0.14)" : "transparent",
                  color: vectorOperation === "add" ? "#86EFAC" : "inherit",
                  cursor: "pointer", fontSize: 11, fontWeight: 600,
                }}>A + B</button>
                <button type="button" onClick={() => setVectorOperation("subtract")} style={{
                  flex: 1, padding: "8px 6px", borderRadius: 7, border: "1px solid",
                  borderColor: vectorOperation === "subtract" ? "#A78BFA" : "var(--border, #30303a)",
                  background: vectorOperation === "subtract" ? "rgba(167,139,250,0.14)" : "transparent",
                  color: vectorOperation === "subtract" ? "#C4B5FD" : "inherit",
                  cursor: "pointer", fontSize: 11, fontWeight: 600,
                }}>A − B</button>
              </div>
              {distancePointA && distancePointB && vectorResult ? (
                <div style={{ padding: 11, borderRadius: 8, background: "rgba(34,197,94,0.06)", border: "1px solid rgba(34,197,94,0.18)", fontSize: 11, lineHeight: 1.75 }}>
                  <strong style={{ display: "block", color: "#86EFAC", marginBottom: 5 }}>
                    {distancePointA.name} {vectorOperation === "add" ? "+" : "−"} {distancePointB.name}
                  </strong>
                  <div>A = ({distanceA!.x}, {distanceA!.y}, {distanceA!.z})</div>
                  <div>B = ({distanceB!.x}, {distanceB!.y}, {distanceB!.z})</div>
                  <div style={{ marginTop: 5, color: "#CBD5E1" }}>
                    {vectorOperation === "add" ? "A + B" : "A − B"} = ({distanceA!.x} {vectorOperation === "add" ? "+" : "−"} {distanceB!.x}, {distanceA!.y} {vectorOperation === "add" ? "+" : "−"} {distanceB!.y}, {distanceA!.z} {vectorOperation === "add" ? "+" : "−"} {distanceB!.z})
                  </div>
                  <strong style={{ display: "block", color: "#E2E8F0", marginTop: 5 }}>R = ({vectorResult.x}, {vectorResult.y}, {vectorResult.z})</strong>
                  <div style={{ color: "#CBD5E1" }}>R = {vectorResult.x}i + ({vectorResult.y})j + ({vectorResult.z})k</div>
                  <div style={{ marginTop: 5 }}>|R| = √({vectorResult.x ** 2} + {vectorResult.y ** 2} + {vectorResult.z ** 2})</div>
                  <strong style={{ color: "#86EFAC" }}>|R| = {Number(vectorResultMagnitude.toFixed(4))}</strong>
                </div>
              ) : (
                <p style={{ fontSize: 11, color: "var(--muted, #94a3b8)", lineHeight: 1.5 }}>Add at least two points to calculate vector operations.</p>
              )}
              <p style={{ fontSize: 10, color: "var(--muted, #94a3b8)", marginTop: 8, lineHeight: 1.5 }}>
                Addition uses the parallelogram method. Subtraction is shown as A + (−B).
              </p>
            </div>

            <div className="inspector-section">
              <span className="sidebar-group-label">DISTANCE BETWEEN POINTS</span>
'''
if 'VECTOR OPERATIONS' not in page:
    if ui_anchor not in page:
        raise SystemExit('Could not find Distance section in page.tsx; no files changed.')
    page = page.replace(ui_anchor, ui_insert, 1)

scene_anchor = 'function Scene({ distancePointIds }: { distancePointIds: [string, string] | null }) {\n'
scene_code = '''function VectorArrow({
  start,
  end,
  color,
  label,
}: {
  start: [number, number, number];
  end: [number, number, number];
  color: string;
  label: string;
}) {
  const direction = new THREE.Vector3(end[0] - start[0], end[1] - start[1], end[2] - start[2]);
  if (direction.length() < 0.0001) return null;
  const quaternion = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.clone().normalize());
  const midpoint: [number, number, number] = [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2, (start[2] + end[2]) / 2];
  return (
    <group>
      <Line points={[start, end]} color={color} lineWidth={2.8} />
      <mesh position={end} quaternion={quaternion}>
        <coneGeometry args={[0.075, 0.2, 14]} />
        <meshBasicMaterial color={color} />
      </mesh>
      <Text position={[midpoint[0] + 0.1, midpoint[1] + 0.1, midpoint[2] + 0.1]} fontSize={0.22} color={color} anchorX="left" anchorY="middle" outlineWidth={0.02} outlineColor="#0F172A">
        {label}
      </Text>
    </group>
  );
}

function VectorOperationGraphic({
  points,
  pointIds,
  operation,
}: {
  points: ScenePoint[];
  pointIds: [string, string] | null;
  operation: "add" | "subtract";
}) {
  if (!pointIds) return null;
  const pointA = points.find((point) => point.id === pointIds[0]);
  const pointB = points.find((point) => point.id === pointIds[1]);
  if (!pointA?.visible || !pointB?.visible) return null;
  const a: [number, number, number] = [pointA.position.x, pointA.position.y, pointA.position.z];
  const b: [number, number, number] = [pointB.position.x, pointB.position.y, pointB.position.z];
  const result: [number, number, number] = operation === "add"
    ? [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
    : [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const translatedB: [number, number, number] = operation === "add"
    ? result
    : result;
  return (
    <group>
      <VectorArrow start={[0, 0, 0]} end={a} color="#22C55E" label="A" />
      <VectorArrow start={[0, 0, 0]} end={b} color="#38BDF8" label="B" />
      {operation === "add" ? (
        <>
          <Line points={[a, result]} color="#38BDF8" lineWidth={1.8} dashed dashSize={0.16} gapSize={0.1} />
          <Line points={[b, result]} color="#22C55E" lineWidth={1.8} dashed dashSize={0.16} gapSize={0.1} />
          <VectorArrow start={[0, 0, 0]} end={result} color="#FACC15" label="A + B" />
        </>
      ) : (
        <>
          <VectorArrow start={a} end={translatedB} color="#A78BFA" label="−B" />
          <VectorArrow start={[0, 0, 0]} end={result} color="#FACC15" label="A − B" />
        </>
      )}
    </group>
  );
}

function Scene({
  distancePointIds,
  vectorOperation,
}: {
  distancePointIds: [string, string] | null;
  vectorOperation: "add" | "subtract";
}) {
'''
if 'function VectorOperationGraphic' not in scene:
    if scene_anchor not in scene:
        raise SystemExit('Could not find Scene component in three-d-scene.tsx; no changes made.')
    scene = scene.replace(scene_anchor, scene_code, 1)

scene_render_anchor = '      <DistanceSegment points={points} pointIds={distancePointIds} />\n'
scene_render = scene_render_anchor + '''      <VectorOperationGraphic points={points} pointIds={distancePointIds} operation={vectorOperation} />
'''
if '<VectorOperationGraphic' not in scene:
    if scene_render_anchor not in scene:
        raise SystemExit('Could not find DistanceSegment render in scene; no changes made.')
    scene = scene.replace(scene_render_anchor, scene_render, 1)

export_anchor = '''export default function ThreeDScene({
  distancePointIds = null,
}: {
  distancePointIds?: [string, string] | null;
}) {
'''
export_insert = '''export default function ThreeDScene({
  distancePointIds = null,
  vectorOperation = "add",
}: {
  distancePointIds?: [string, string] | null;
  vectorOperation?: "add" | "subtract";
}) {
'''
if 'vectorOperation = "add"' not in scene:
    if export_anchor not in scene:
        raise SystemExit('Could not find ThreeDScene export props; no changes made.')
    scene = scene.replace(export_anchor, export_insert, 1)
scene = scene.replace('<Scene distancePointIds={distancePointIds} />', '<Scene distancePointIds={distancePointIds} vectorOperation={vectorOperation} />', 1)

page_path.write_text(page)
scene_path.write_text(scene)
print('Vector Addition and Subtraction integrated successfully.')
print('Updated: src/app/page.tsx')
print('Updated: src/components/three-d-scene.tsx')
'''
Path('/mnt/data/add-vector-operations.py').write_text(script)
