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

# Page: thread sphere data through the preview.
page = replace_once(
    page,
    'function ThreeDPreview({ distancePointIds, vectorOperation, planeEquation, lineGeometry }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation: { a: number; b: number; c: number; d: number } | null; lineGeometry: { point: [number, number, number]; direction: [number, number, number] } | null }) {',
    'function ThreeDPreview({ distancePointIds, vectorOperation, planeEquation, lineGeometry, sphere }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation: { a: number; b: number; c: number; d: number } | null; lineGeometry: { point: [number, number, number]; direction: [number, number, number] } | null; sphere: { center: [number, number, number]; radius: number } | null }) {',
    "ThreeDPreview signature",
)
page = replace_once(
    page,
    '<ThreeDScene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} lineGeometry={lineGeometry} />',
    '<ThreeDScene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} lineGeometry={lineGeometry} sphere={sphere} />',
    "ThreeDScene preview invocation",
)

# Sphere state and calculations.
line_state_anchor = '  // 3D line through two selected points and distance from a third point.\n'
sphere_state = '''  // Sphere defined by centre (h, k, l) and radius r.
  const [sphereCenter, setSphereCenter] = useState({ x: 0, y: 0, z: 0 });
  const [sphereRadius, setSphereRadius] = useState(3);
  const [sphereVisible, setSphereVisible] = useState(true);
  const [sphereTestPointId, setSphereTestPointId] = useState("");
  const sphereTestPoint = points.find((point) => point.id === sphereTestPointId) ?? null;
  const sphereTestDistance = sphereTestPoint
    ? Math.hypot(
        sphereTestPoint.position.x - sphereCenter.x,
        sphereTestPoint.position.y - sphereCenter.y,
        sphereTestPoint.position.z - sphereCenter.z,
      )
    : null;
  const spherePointRelation = sphereTestDistance === null || sphereRadius <= 0
    ? null
    : Math.abs(sphereTestDistance - sphereRadius) <= 1e-6
      ? "on"
      : sphereTestDistance < sphereRadius ? "inside" : "outside";
  const sphereSurfaceArea = 4 * Math.PI * sphereRadius ** 2;
  const sphereVolume = (4 / 3) * Math.PI * sphereRadius ** 3;
  const sphereEquation = `(x - (${sphereCenter.x}))² + (y - (${sphereCenter.y}))² + (z - (${sphereCenter.z}))² = ${Number((sphereRadius ** 2).toFixed(4))}`;
  const sphereGeometry = sphereVisible && sphereRadius > 0
    ? { center: [sphereCenter.x, sphereCenter.y, sphereCenter.z] as [number, number, number], radius: sphereRadius }
    : null;

'''
page = replace_once(page, line_state_anchor, sphere_state + line_state_anchor, "sphere state insertion")

# Add sphere prop to viewport call.
page = replace_once(
    page,
    'lineGeometry={lineGeometry} />',
    'lineGeometry={lineGeometry} sphere={sphereGeometry} />',
    "ThreeDPreview call",
)

# Inspector section before line geometry.
line_inspector_anchor = '''            <div className="inspector-section">
              <span className="sidebar-group-label">3D LINE GEOMETRY</span>'''
sphere_inspector = '''            <div className="inspector-section">
              <span className="sidebar-group-label">3D SPHERE GEOMETRY</span>
              <label style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 10, color: "#CBD5E1", marginTop: 8, marginBottom: 8 }}>
                <input type="checkbox" checked={sphereVisible} onChange={(event) => setSphereVisible(event.target.checked)} />
                Show sphere
              </label>
              <div style={{ fontSize: 10, color: "#94A3B8", marginBottom: 6 }}>Centre coordinates (h, k, l)</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 5 }}>
                {(["x", "y", "z"] as const).map((axis) => (
                  <label key={axis} style={{ fontSize: 10, color: "#94A3B8" }}>
                    {axis.toUpperCase()}
                    <input type="number" value={sphereCenter[axis]} onChange={(event) => setSphereCenter((current) => ({ ...current, [axis]: Number(event.target.value) }))} style={{ width: "100%", minWidth: 0, marginTop: 3, padding: "6px 4px", borderRadius: 5, background: "var(--input, #111827)", color: "inherit", border: "1px solid var(--border, #30303a)" }} />
                  </label>
                ))}
              </div>
              <label style={{ display: "block", fontSize: 10, color: "#94A3B8", marginTop: 8 }}>
                Radius (r)
                <input type="number" min="0.01" step="0.5" value={sphereRadius} onChange={(event) => setSphereRadius(Math.max(0, Number(event.target.value)))} style={{ width: "100%", marginTop: 3, padding: "6px 7px", borderRadius: 5, background: "var(--input, #111827)", color: "inherit", border: "1px solid var(--border, #30303a)" }} />
              </label>
              <div style={{ marginTop: 9, padding: 10, borderRadius: 8, background: "rgba(167,139,250,0.08)", border: "1px solid rgba(167,139,250,0.22)", fontSize: 10, lineHeight: 1.75, color: "#DDD6FE" }}>
                <strong style={{ display: "block", color: "#C4B5FD" }}>Sphere equation</strong>
                {sphereEquation}
                <div>Centre: ({sphereCenter.x}, {sphereCenter.y}, {sphereCenter.z})</div>
                <div>Diameter = {Number((2 * sphereRadius).toFixed(4))}</div>
                <div>Surface area = 4πr² = {Number(sphereSurfaceArea.toFixed(4))}</div>
                <div>Volume = ⁴⁄₃πr³ = {Number(sphereVolume.toFixed(4))}</div>
                {sphereRadius <= 0 && <div style={{ color: "#FCA5A5" }}>Radius must be greater than zero.</div>}
              </div>
              <div style={{ marginTop: 10, paddingTop: 9, borderTop: "1px solid var(--border, #30303a)" }}>
                <strong style={{ display: "block", fontSize: 10, color: "#C4B5FD", marginBottom: 6 }}>POINT POSITION RELATIVE TO SPHERE</strong>
                <label className="property-row">
                  <span>Test point</span>
                  <select value={sphereTestPointId} onChange={(event) => setSphereTestPointId(event.target.value)}>
                    <option value="">Select point</option>
                    {points.map((point) => <option key={point.id} value={point.id}>{point.name}</option>)}
                  </select>
                </label>
                {sphereTestPoint && sphereTestDistance !== null && spherePointRelation ? (
                  <div style={{ fontSize: 10, color: "#DDD6FE", marginTop: 6, lineHeight: 1.65 }}>
                    <div>Distance from centre = {Number(sphereTestDistance.toFixed(4))}</div>
                    <strong style={{ color: spherePointRelation === "on" ? "#86EFAC" : "#C4B5FD" }}>
                      Point is {spherePointRelation} the sphere
                    </strong>
                  </div>
                ) : (
                  <div style={{ fontSize: 10, color: "#94A3B8", marginTop: 5 }}>Select a point to check whether it is inside, on, or outside the sphere.</div>
                )}
              </div>
            </div>

'''
page = replace_once(page, line_inspector_anchor, sphere_inspector + line_inspector_anchor, "sphere inspector insertion")

# Scene: add sphere mesh component before line graphic.
line_component_anchor = 'function LineGeometryGraphic({ lineGeometry }: { lineGeometry: { point: [number, number, number]; direction: [number, number, number] } | null }) {'
sphere_component = '''function SphereGraphic({ sphere }: { sphere: { center: [number, number, number]; radius: number } | null }) {
  if (!sphere || sphere.radius <= 0) return null;
  return (
    <group position={sphere.center}>
      <mesh>
        <sphereGeometry args={[sphere.radius, 48, 32]} />
        <meshPhysicalMaterial color="#A78BFA" transparent opacity={0.2} roughness={0.35} metalness={0.05} side={THREE.DoubleSide} depthWrite={false} />
      </mesh>
      <mesh>
        <sphereGeometry args={[sphere.radius, 24, 16]} />
        <meshBasicMaterial color="#C4B5FD" wireframe transparent opacity={0.48} />
      </mesh>
      <mesh>
        <sphereGeometry args={[0.07, 16, 16]} />
        <meshBasicMaterial color="#FDE68A" />
      </mesh>
      <Text position={[0.12, 0.12, sphere.radius + 0.2]} fontSize={0.23} color="#DDD6FE" outlineWidth={0.025} outlineColor="#0F172A">
        Sphere
      </Text>
    </group>
  );
}

'''
scene = replace_once(scene, line_component_anchor, sphere_component + line_component_anchor, "SphereGraphic insertion")

# Extend Scene signature and render sphere.
scene = replace_once(
    scene,
    'function Scene({ distancePointIds, vectorOperation, planeEquation, lineGeometry }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null; lineGeometry?: { point: [number, number, number]; direction: [number, number, number] } | null }) {',
    'function Scene({ distancePointIds, vectorOperation, planeEquation, lineGeometry, sphere }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null; lineGeometry?: { point: [number, number, number]; direction: [number, number, number] } | null; sphere?: { center: [number, number, number]; radius: number } | null }) {',
    "Scene signature",
)
scene = replace_once(
    scene,
    '      <LineGeometryGraphic lineGeometry={lineGeometry ?? null} />',
    '      <SphereGraphic sphere={sphere ?? null} />\n      <LineGeometryGraphic lineGeometry={lineGeometry ?? null} />',
    "SphereGraphic render",
)

# Extend exported scene props and invocation.
scene = replace_once(
    scene,
    'export default function ThreeDScene({ distancePointIds = null, vectorOperation = "add", planeEquation = null, lineGeometry = null }: { distancePointIds?: [string,string] | null; vectorOperation?: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null; lineGeometry?: { point: [number, number, number]; direction: [number, number, number] } | null }) {',
    'export default function ThreeDScene({ distancePointIds = null, vectorOperation = "add", planeEquation = null, lineGeometry = null, sphere = null }: { distancePointIds?: [string,string] | null; vectorOperation?: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null; lineGeometry?: { point: [number, number, number]; direction: [number, number, number] } | null; sphere?: { center: [number, number, number]; radius: number } | null }) {',
    "ThreeDScene signature",
)
scene = replace_once(
    scene,
    '<Scene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} lineGeometry={lineGeometry} />',
    '<Scene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} lineGeometry={lineGeometry} sphere={sphere} />',
    "Scene invocation",
)

PAGE.write_text(page)
SCENE.write_text(scene)
print("3D Sphere Geometry integrated successfully.")
print("Updated src/app/page.tsx and src/components/three-d-scene.tsx")
print("Includes editable centre/radius, sphere equation, diameter, surface area, volume, point classification, and 3D sphere visualization.")
