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

# Pass conic controls from the page into the shared 3D scene.
page = replace_once(
    page,
    'function ThreeDPreview({ distancePointIds, vectorOperation, planeEquation, lineGeometry, sphere }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation: { a: number; b: number; c: number; d: number } | null; lineGeometry: { point: [number, number, number]; direction: [number, number, number] } | null; sphere: { center: [number, number, number]; radius: number } | null }) {',
    'function ThreeDPreview({ distancePointIds, vectorOperation, planeEquation, lineGeometry, sphere, conic }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation: { a: number; b: number; c: number; d: number } | null; lineGeometry: { point: [number, number, number]; direction: [number, number, number] } | null; sphere: { center: [number, number, number]; radius: number } | null; conic: { angle: number; offset: number; visible: boolean } }) {',
    "ThreeDPreview props",
)
page = replace_once(
    page,
    '<ThreeDScene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} lineGeometry={lineGeometry} sphere={sphere} />',
    '<ThreeDScene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} lineGeometry={lineGeometry} sphere={sphere} conic={conic} />',
    "ThreeDScene preview props",
)

# Conic controls and classification. Angle is the plane's inclination from horizontal.
sphere_state_anchor = '  // Sphere defined by centre (h, k, l) and radius r.\n'
conic_state = '''  // Interactive double-cone section: angle is measured from a horizontal plane.
  const [conicAngle, setConicAngle] = useState(20);
  const [conicOffset, setConicOffset] = useState(0);
  const [conicVisible, setConicVisible] = useState(true);
  const coneHalfAngle = 35;
  const conicType = conicAngle < 0.5
    ? "Circle"
    : Math.abs(conicAngle - (90 - coneHalfAngle)) <= 1
      ? "Parabola"
      : conicAngle < (90 - coneHalfAngle)
        ? "Ellipse"
        : "Hyperbola";
  const conicEquation = `z = ${Number(Math.tan(conicAngle * Math.PI / 180).toFixed(4))}x + ${conicOffset}`;

'''
page = replace_once(page, sphere_state_anchor, conic_state + sphere_state_anchor, "conic state insertion")

# Add conic prop to existing viewport invocation.
page = replace_once(
    page,
    'lineGeometry={lineGeometry} sphere={sphereGeometry} />',
    'lineGeometry={lineGeometry} sphere={sphereGeometry} conic={{ angle: conicAngle, offset: conicOffset, visible: conicVisible }} />',
    "ThreeDPreview call",
)

# Add a dedicated inspector section before Sphere Geometry.
sphere_inspector_anchor = '''            <div className="inspector-section">
              <span className="sidebar-group-label">3D SPHERE GEOMETRY</span>'''
conic_inspector = '''            <div className="inspector-section">
              <span className="sidebar-group-label">3D CONIC SECTIONS</span>
              <label style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 10, color: "#CBD5E1", marginTop: 8, marginBottom: 8 }}>
                <input type="checkbox" checked={conicVisible} onChange={(event) => setConicVisible(event.target.checked)} />
                Show cone and cutting plane
              </label>
              <label style={{ display: "block", fontSize: 10, color: "#94A3B8", marginTop: 7 }}>
                Plane inclination: {conicAngle.toFixed(1)}°
                <input type="range" min="0" max="80" step="0.5" value={conicAngle} onChange={(event) => setConicAngle(Number(event.target.value))} style={{ width: "100%", marginTop: 6, accentColor: "#F59E0B" }} />
              </label>
              <label style={{ display: "block", fontSize: 10, color: "#94A3B8", marginTop: 9 }}>
                Plane height / offset: {conicOffset.toFixed(1)}
                <input type="range" min="-3" max="3" step="0.1" value={conicOffset} onChange={(event) => setConicOffset(Number(event.target.value))} style={{ width: "100%", marginTop: 6, accentColor: "#F59E0B" }} />
              </label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginTop: 9 }}>
                {([{ label: "Circle", angle: 0 }, { label: "Ellipse", angle: 20 }, { label: "Parabola", angle: 55 }, { label: "Hyperbola", angle: 70 }] as const).map((preset) => (
                  <button key={preset.label} type="button" onClick={() => { setConicAngle(preset.angle); setConicOffset(0); }} style={{ padding: "6px 7px", borderRadius: 6, border: "1px solid", borderColor: conicAngle === preset.angle ? "#F59E0B" : "var(--border, #30303a)", background: conicAngle === preset.angle ? "rgba(245,158,11,0.14)" : "transparent", color: conicAngle === preset.angle ? "#FCD34D" : "inherit", cursor: "pointer", fontSize: 9 }}>{preset.label}</button>
                ))}
              </div>
              <div style={{ marginTop: 10, padding: 10, borderRadius: 8, background: "rgba(245,158,11,0.07)", border: "1px solid rgba(245,158,11,0.2)", fontSize: 10, lineHeight: 1.7, color: "#FDE68A" }}>
                <strong style={{ display: "block", color: "#FCD34D", fontSize: 13 }}>{conicType}</strong>
                <div>Double cone half-angle = {coneHalfAngle}°</div>
                <div>Plane inclination = {conicAngle.toFixed(1)}°</div>
                <div>Plane: {conicEquation}</div>
                <div style={{ color: "#CBD5E1", marginTop: 5 }}>
                  {conicType === "Circle" ? "Plane is perpendicular to the cone axis." :
                   conicType === "Ellipse" ? "Plane cuts one nappe at an angle smaller than the cone generator angle." :
                   conicType === "Parabola" ? "Plane is parallel to a generator of the cone." :
                   "Plane intersects both nappes of the double cone."}
                </div>
              </div>
            </div>

'''
page = replace_once(page, sphere_inspector_anchor, conic_inspector + sphere_inspector_anchor, "conic inspector insertion")

# Scene: add procedural double cone and plane intersection curves.
sphere_component_anchor = 'function SphereGraphic({ sphere }: { sphere: { center: [number, number, number]; radius: number } | null }) {'
conic_component = '''function ConicSectionsGraphic({ conic }: { conic: { angle: number; offset: number; visible: boolean } }) {
  if (!conic.visible) return null;
  const halfAngle = 35 * Math.PI / 180;
  const slope = Math.tan(halfAngle);
  const angle = conic.angle * Math.PI / 180;
  const normal = new THREE.Vector3(-Math.sin(angle), 0, Math.cos(angle));
  const planePoint = new THREE.Vector3(0, 0, conic.offset);
  const planeQuaternion = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal);
  const planeSize = 14;
  const planePosition: [number, number, number] = [planePoint.x, planePoint.y, planePoint.z];
  const curves: [number, number, number][][] = [];
  const samples = 240;
  for (const sign of [1, -1]) {
    const curve: [number, number, number][] = [];
    for (let i = 0; i <= samples; i++) {
      const t = (i / samples) * Math.PI * 2;
      const denominator = normal.z + sign * slope * (normal.x * Math.cos(t) + normal.y * Math.sin(t));
      if (Math.abs(denominator) < 1e-5) {
        curve.push([NaN, NaN, NaN]);
        continue;
      }
      const z = -normal.dot(planePoint) / denominator;
      const radius = Math.abs(z) * slope;
      const x = radius * Math.cos(t);
      const y = radius * Math.sin(t);
      curve.push([x, y, z]);
    }
    curves.push(curve);
  }
  const planeCorners = [
    new THREE.Vector3(-planeSize, -planeSize, 0),
    new THREE.Vector3(planeSize, -planeSize, 0),
    new THREE.Vector3(planeSize, planeSize, 0),
    new THREE.Vector3(-planeSize, planeSize, 0),
  ].map((corner) => corner.applyQuaternion(planeQuaternion).add(planePoint).toArray() as [number, number, number]);
  const classification = conic.angle < 0.5 ? "Circle" : Math.abs(conic.angle - 55) <= 1 ? "Parabola" : conic.angle < 55 ? "Ellipse" : "Hyperbola";
  return (
    <group>
      <mesh position={[0, 0, 3.5]}>
        <coneGeometry args={[Math.tan(halfAngle) * 7, 7, 64, 1, true]} />
        <meshBasicMaterial color="#60A5FA" transparent opacity={0.12} side={THREE.DoubleSide} depthWrite={false} />
      </mesh>
      <mesh position={[0, 0, -3.5]} rotation={[Math.PI, 0, 0]}>
        <coneGeometry args={[Math.tan(halfAngle) * 7, 7, 64, 1, true]} />
        <meshBasicMaterial color="#60A5FA" transparent opacity={0.12} side={THREE.DoubleSide} depthWrite={false} />
      </mesh>
      <mesh position={planePosition} quaternion={planeQuaternion}>
        <planeGeometry args={[planeSize * 2, planeSize * 2]} />
        <meshBasicMaterial color="#F59E0B" transparent opacity={0.13} side={THREE.DoubleSide} depthWrite={false} />
      </mesh>
      <Line points={[...planeCorners, planeCorners[0]]} color="#FBBF24" lineWidth={1.5} />
      {curves.map((curve, index) => (
        <Line key={index} points={curve.filter((point) => point.every(Number.isFinite))} color={index === 0 ? "#F472B6" : "#A78BFA"} lineWidth={3} />
      ))}
      <Text position={[0.2, 0.2, 7.8]} fontSize={0.28} color="#FCD34D" outlineWidth={0.025} outlineColor="#0F172A">
        {classification}
      </Text>
    </group>
  );
}

'''
scene = replace_once(scene, sphere_component_anchor, conic_component + sphere_component_anchor, "ConicSectionsGraphic insertion")

# Extend Scene props and render the conic visualization.
scene = replace_once(
    scene,
    'function Scene({ distancePointIds, vectorOperation, planeEquation, lineGeometry, sphere }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null; lineGeometry?: { point: [number, number, number]; direction: [number, number, number] } | null; sphere?: { center: [number, number, number]; radius: number } | null }) {',
    'function Scene({ distancePointIds, vectorOperation, planeEquation, lineGeometry, sphere, conic }: { distancePointIds: [string, string] | null; vectorOperation: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null; lineGeometry?: { point: [number, number, number]; direction: [number, number, number] } | null; sphere?: { center: [number, number, number]; radius: number } | null; conic?: { angle: number; offset: number; visible: boolean } }) {',
    "Scene props",
)
scene = replace_once(
    scene,
    '      <SphereGraphic sphere={sphere ?? null} />',
    '      <ConicSectionsGraphic conic={conic ?? { angle: 20, offset: 0, visible: false }} />\n      <SphereGraphic sphere={sphere ?? null} />',
    "Conic graphic render",
)

# Extend exported ThreeDScene props and forward.
scene = replace_once(
    scene,
    'export default function ThreeDScene({ distancePointIds = null, vectorOperation = "add", planeEquation = null, lineGeometry = null, sphere = null }: { distancePointIds?: [string,string] | null; vectorOperation?: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null; lineGeometry?: { point: [number, number, number]; direction: [number, number, number] } | null; sphere?: { center: [number, number, number]; radius: number } | null }) {',
    'export default function ThreeDScene({ distancePointIds = null, vectorOperation = "add", planeEquation = null, lineGeometry = null, sphere = null, conic = null }: { distancePointIds?: [string,string] | null; vectorOperation?: "add" | "subtract"; planeEquation?: { a: number; b: number; c: number; d: number } | null; lineGeometry?: { point: [number, number, number]; direction: [number, number, number] } | null; sphere?: { center: [number, number, number]; radius: number } | null; conic?: { angle: number; offset: number; visible: boolean } | null }) {',
    "ThreeDScene props",
)
scene = replace_once(
    scene,
    '<Scene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} lineGeometry={lineGeometry} sphere={sphere} />',
    '<Scene distancePointIds={distancePointIds} vectorOperation={vectorOperation} planeEquation={planeEquation} lineGeometry={lineGeometry} sphere={sphere} conic={conic ?? undefined} />',
    "Scene invocation",
)

PAGE.write_text(page)
SCENE.write_text(scene)
print("Interactive 3D Conic Sections integrated successfully.")
print("Updated src/app/page.tsx and src/components/three-d-scene.tsx")
print("Includes double cone, adjustable cutting-plane inclination/height, conic presets, live intersection curves and classification.")
