from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "src/app/page.tsx"
SCENE = ROOT / "src/components/three-d-scene.tsx"
page = PAGE.read_text()
scene = SCENE.read_text()

def replace_once(source, old, new, label):
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"STOP: expected exactly 1 occurrence for {label}, found {count}. No files were changed.")
    return source.replace(old, new, 1)

page = replace_once(page,
'function ThreeDPreview({ distancePointIds, vectorOperation, planeEquation }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation: { a: number; b: number; c: number; d: number } | null }) {',
'function ThreeDPreview({ distancePointIds, vectorOperation, planeEquation, lineGeometry }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation: { a: number; b: number; c: number; d: number } | null; lineGeometry: { point: [number, number, number]; direction: [number, number, number] } | null }) {',
"ThreeDPreview signature")
page = replace_once(page,
'<ThreeDScene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} />',
'<ThreeDScene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} lineGeometry={lineGeometry} />',
"ThreeDScene preview props")

plane_anchor = '  // Plane equation n·x + d = 0 and optional plane through three selected points.\n'
line_state = '''  // 3D line through two selected points and distance from a third point.
  const [linePointAId, setLinePointAId] = useState("");
  const [linePointBId, setLinePointBId] = useState("");
  const [lineTestPointId, setLineTestPointId] = useState("");
  const lineAId = points.some((point) => point.id === linePointAId) ? linePointAId : (points[0]?.id ?? "");
  const lineBId = points.some((point) => point.id === linePointBId && point.id !== lineAId)
    ? linePointBId : (points.find((point) => point.id !== lineAId)?.id ?? "");
  const lineTestPoint = points.find((point) => point.id === lineTestPointId && point.id !== lineAId && point.id !== lineBId)
    ?? points.find((point) => point.id !== lineAId && point.id !== lineBId) ?? null;
  const linePointA = points.find((point) => point.id === lineAId) ?? null;
  const linePointB = points.find((point) => point.id === lineBId) ?? null;
  const lineA = linePointA?.position ?? null;
  const lineB = linePointB?.position ?? null;
  const lineDirection = lineA && lineB
    ? { x: lineB.x - lineA.x, y: lineB.y - lineA.y, z: lineB.z - lineA.z } : null;
  const lineDirectionMagnitude = lineDirection ? Math.hypot(lineDirection.x, lineDirection.y, lineDirection.z) : 0;
  const lineIsValid = Boolean(lineA && lineB && lineDirection && lineDirectionMagnitude > 1e-8);
  const lineGeometry = lineIsValid && lineA && lineDirection
    ? { point: [lineA.x, lineA.y, lineA.z] as [number, number, number], direction: [lineDirection.x, lineDirection.y, lineDirection.z] as [number, number, number] }
    : null;
  const pointToLineDistance = lineIsValid && lineA && lineDirection && lineTestPoint
    ? Math.hypot(
        (lineTestPoint.position.y - lineA.y) * lineDirection.z - (lineTestPoint.position.z - lineA.z) * lineDirection.y,
        (lineTestPoint.position.z - lineA.z) * lineDirection.x - (lineTestPoint.position.x - lineA.x) * lineDirection.z,
        (lineTestPoint.position.x - lineA.x) * lineDirection.y - (lineTestPoint.position.y - lineA.y) * lineDirection.x,
      ) / lineDirectionMagnitude : null;
  const lineParametric = lineA && lineDirection ? [
    `x = ${lineA.x} + λ(${lineDirection.x})`,
    `y = ${lineA.y} + λ(${lineDirection.y})`,
    `z = ${lineA.z} + λ(${lineDirection.z})`,
  ] : [];
  const lineSymmetric = lineA && lineDirection ? [
    lineDirection.x === 0 ? `x = ${lineA.x}` : `(x - ${lineA.x})/${lineDirection.x}`,
    lineDirection.y === 0 ? `y = ${lineA.y}` : `(y - ${lineA.y})/${lineDirection.y}`,
    lineDirection.z === 0 ? `z = ${lineA.z}` : `(z - ${lineA.z})/${lineDirection.z}`,
  ] : [];

'''
page = replace_once(page, plane_anchor, line_state + plane_anchor, "line calculation insertion")
page = replace_once(page,
'planeEquation={planeIsValid && (planeMode === "coefficients" || (planeHasThreePoints && threePointNormalMagnitude > 1e-8)) ? activePlane : null} />',
'planeEquation={planeIsValid && (planeMode === "coefficients" || (planeHasThreePoints && threePointNormalMagnitude > 1e-8)) ? activePlane : null} lineGeometry={lineGeometry} />',
"ThreeDPreview invocation")

inspector_anchor = '''            <div className="inspector-section">
              <span className="sidebar-group-label">3D PLANE GEOMETRY</span>'''
line_inspector = '''            <div className="inspector-section">
              <span className="sidebar-group-label">3D LINE GEOMETRY</span>
              <div style={{ fontSize: 10, color: "#94A3B8", marginTop: 7, marginBottom: 6 }}>Select two distinct points to define a line.</div>
              {(["A", "B"] as const).map((label, index) => {
                const value = index === 0 ? lineAId : lineBId;
                const onChange = index === 0 ? setLinePointAId : setLinePointBId;
                const excludedId = index === 0 ? lineBId : lineAId;
                return (
                  <label key={label} className="property-row">
                    <span>Point {label}</span>
                    <select value={value} onChange={(event) => onChange(event.target.value)}>
                      <option value="">Select point</option>
                      {points.filter((point) => point.id !== excludedId).map((point) => (
                        <option key={point.id} value={point.id}>{point.name}</option>
                      ))}
                    </select>
                  </label>
                );
              })}
              {lineIsValid && lineA && lineDirection ? (
                <div style={{ marginTop: 9, padding: 10, borderRadius: 8, background: "rgba(34,197,94,0.07)", border: "1px solid rgba(34,197,94,0.2)", fontSize: 10, lineHeight: 1.75, color: "#CBD5E1" }}>
                  <strong style={{ display: "block", color: "#86EFAC" }}>Direction vector</strong>
                  d = ({lineDirection.x}, {lineDirection.y}, {lineDirection.z})
                  <div>|d| = {Number(lineDirectionMagnitude.toFixed(4))}</div>
                  <strong style={{ display: "block", color: "#86EFAC", marginTop: 6 }}>Vector equation</strong>
                  r = ({lineA.x}, {lineA.y}, {lineA.z}) + λ({lineDirection.x}, {lineDirection.y}, {lineDirection.z})
                  <strong style={{ display: "block", color: "#86EFAC", marginTop: 6 }}>Parametric equations</strong>
                  {lineParametric.map((equation) => <div key={equation}>{equation}</div>)}
                  <strong style={{ display: "block", color: "#86EFAC", marginTop: 6 }}>Symmetric equations</strong>
                  {lineSymmetric.join(" = ")}
                </div>
              ) : (
                <p style={{ fontSize: 10, color: "#FCA5A5", marginTop: 7 }}>Select two distinct points with different coordinates to define a line.</p>
              )}
              <div style={{ marginTop: 10, paddingTop: 9, borderTop: "1px solid var(--border, #30303a)" }}>
                <strong style={{ display: "block", fontSize: 10, color: "#C4B5FD", marginBottom: 6 }}>POINT-TO-LINE DISTANCE</strong>
                <label className="property-row">
                  <span>Test point</span>
                  <select value={lineTestPoint?.id ?? ""} onChange={(event) => setLineTestPointId(event.target.value)}>
                    <option value="">Select point</option>
                    {points.filter((point) => point.id !== lineAId && point.id !== lineBId).map((point) => (
                      <option key={point.id} value={point.id}>{point.name}</option>
                    ))}
                  </select>
                </label>
                {pointToLineDistance !== null ? (
                  <div style={{ fontSize: 10, color: "#DDD6FE", marginTop: 6, lineHeight: 1.6 }}>
                    <div>d(P, L) = |AP × AB| / |AB|</div>
                    <strong style={{ fontSize: 13, color: "#C4B5FD" }}>{Number(pointToLineDistance.toFixed(4))}</strong>
                  </div>
                ) : (
                  <div style={{ fontSize: 10, color: "#94A3B8", marginTop: 5 }}>Add a third point to calculate its perpendicular distance from the line.</div>
                )}
              </div>
            </div>

'''
page = replace_once(page, inspector_anchor, line_inspector + inspector_anchor, "line inspector insertion")

line_component_anchor = 'function PlaneGraphic({ equation }: { equation: { a: number; b: number; c: number; d: number } | null }) {'
line_component = '''function LineGeometryGraphic({ lineGeometry }: { lineGeometry: { point: [number, number, number]; direction: [number, number, number] } | null }) {
  if (!lineGeometry) return null;
  const origin = new THREE.Vector3(...lineGeometry.point);
  const direction = new THREE.Vector3(...lineGeometry.direction);
  if (direction.length() < 1e-8) return null;
  direction.normalize();
  const start = origin.clone().addScaledVector(direction, -8);
  const end = origin.clone().addScaledVector(direction, 8);
  const label = origin.clone().addScaledVector(direction, 3.2).add(new THREE.Vector3(0.12, 0.12, 0.18));
  return (
    <group>
      <Line points={[[start.x, start.y, start.z], [end.x, end.y, end.z]]} color="#FBBF24" lineWidth={3} />
      <mesh position={[origin.x, origin.y, origin.z]}>
        <sphereGeometry args={[0.075, 16, 16]} />
        <meshBasicMaterial color="#FBBF24" />
      </mesh>
      <Text position={[label.x, label.y, label.z]} fontSize={0.25} color="#FDE68A" outlineWidth={0.025} outlineColor="#0F172A">Line AB</Text>
    </group>
  );
}

'''
scene = replace_once(scene, line_component_anchor, line_component + line_component_anchor, "line visual component")
scene = replace_once(scene,
'function Scene({ distancePointIds, vectorOperation, planeEquation }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null }) {',
'function Scene({ distancePointIds, vectorOperation, planeEquation, lineGeometry }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null; lineGeometry?: { point: [number, number, number]; direction: [number, number, number] } | null }) {',
"Scene props")
scene = replace_once(scene,
'      <PlaneGraphic equation={planeEquation ?? null} />',
'      <LineGeometryGraphic lineGeometry={lineGeometry ?? null} />\n      <PlaneGraphic equation={planeEquation ?? null} />',
"line graphic render")
scene = replace_once(scene,
'export default function ThreeDScene({ distancePointIds = null, vectorOperation = "add", planeEquation = null }: { distancePointIds?: [string,string] | null; vectorOperation?: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null }) {',
'export default function ThreeDScene({ distancePointIds = null, vectorOperation = "add", planeEquation = null, lineGeometry = null }: { distancePointIds?: [string,string] | null; vectorOperation?: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null; lineGeometry?: { point: [number, number, number]; direction: [number, number, number] } | null }) {',
"ThreeDScene props")
scene = replace_once(scene,
'<Scene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} />',
'<Scene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} lineGeometry={lineGeometry} />',
"Scene invocation")

PAGE.write_text(page)
SCENE.write_text(scene)
print("3D Line Geometry integrated successfully.")
print("Updated src/app/page.tsx and src/components/three-d-scene.tsx")
print("Includes two-point line, vector/parametric/symmetric equations, direction magnitude, point-to-line distance, and 3D visualization.")
