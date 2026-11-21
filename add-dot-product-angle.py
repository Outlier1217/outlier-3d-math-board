from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "src/app/page.tsx"
SCENE = ROOT / "src/components/three-d-scene.tsx"

page = PAGE.read_text()
scene = SCENE.read_text()

if "const dotProductValue =" in page or "DOT PRODUCT &amp; ANGLE" in page:
    raise SystemExit("Dot Product feature already appears to be integrated. No files changed.")
if "function AngleBetweenVectorsGraphic" in scene:
    raise SystemExit("Angle visualization already appears to be integrated. No files changed.")

calc_anchor = '  const [octantMode, setOctantMode] = useState<"auto" | "manual">("auto");'
calc_insert = '''  // Dot product and angle between the two selected position vectors.
  const dotProductValue = distanceA && distanceB
    ? distanceA.x * distanceB.x + distanceA.y * distanceB.y + distanceA.z * distanceB.z
    : 0;
  const magnitudeA = distanceA
    ? Math.sqrt(distanceA.x ** 2 + distanceA.y ** 2 + distanceA.z ** 2)
    : 0;
  const magnitudeB = distanceB
    ? Math.sqrt(distanceB.x ** 2 + distanceB.y ** 2 + distanceB.z ** 2)
    : 0;
  const cosineAngle = magnitudeA > 0 && magnitudeB > 0
    ? Math.max(-1, Math.min(1, dotProductValue / (magnitudeA * magnitudeB)))
    : null;
  const angleDegrees = cosineAngle === null
    ? null
    : Math.acos(cosineAngle) * (180 / Math.PI);

'''
if calc_anchor not in page:
    raise SystemExit("Could not find calculation insertion point. No files changed.")
page = page.replace(calc_anchor, calc_insert + calc_anchor, 1)

inspector_anchor = '''            <div className="inspector-section">
              <span className="sidebar-group-label">DISTANCE BETWEEN POINTS</span>'''
inspector_insert = '''            <div className="inspector-section">
              <span className="sidebar-group-label">DOT PRODUCT &amp; ANGLE</span>
              {distancePointA && distancePointB ? (
                <div style={{ marginTop: 8, padding: 11, borderRadius: 8, background: "rgba(168,85,247,0.07)", border: "1px solid rgba(168,85,247,0.22)", fontSize: 11, lineHeight: 1.75 }}>
                  <strong style={{ display: "block", color: "#C4B5FD", marginBottom: 5 }}>
                    {distancePointA.name} · {distancePointB.name}
                  </strong>
                  <div>A = ({distanceA!.x}, {distanceA!.y}, {distanceA!.z})</div>
                  <div>B = ({distanceB!.x}, {distanceB!.y}, {distanceB!.z})</div>
                  <div style={{ marginTop: 6, color: "#CBD5E1" }}>
                    A · B = (Ax × Bx) + (Ay × By) + (Az × Bz)
                  </div>
                  <div>
                    = ({distanceA!.x} × {distanceB!.x}) + ({distanceA!.y} × {distanceB!.y}) + ({distanceA!.z} × {distanceB!.z})
                  </div>
                  <strong style={{ display: "block", color: "#E9D5FF", marginTop: 3 }}>
                    A · B = {Number(dotProductValue.toFixed(4))}
                  </strong>
                  <div style={{ marginTop: 8, color: "#CBD5E1" }}>
                    cos θ = (A · B) / (|A| × |B|)
                  </div>
                  <div>|A| = {Number(magnitudeA.toFixed(4))} &nbsp; |B| = {Number(magnitudeB.toFixed(4))}</div>
                  {angleDegrees === null ? (
                    <strong style={{ display: "block", color: "#FCA5A5", marginTop: 5 }}>
                      Angle is undefined when either vector has zero magnitude.
                    </strong>
                  ) : (
                    <>
                      <div>cos θ = {Number(cosineAngle!.toFixed(6))}</div>
                      <strong style={{ display: "block", color: "#86EFAC", fontSize: 16, marginTop: 5 }}>
                        θ = {Number(angleDegrees.toFixed(2))}°
                      </strong>
                      <div style={{ color: "#94A3B8", marginTop: 3 }}>
                        {Math.abs(angleDegrees) < 0.005 ? "Vectors are parallel (same direction)." :
                         Math.abs(angleDegrees - 90) < 0.005 ? "Vectors are perpendicular." :
                         Math.abs(angleDegrees - 180) < 0.005 ? "Vectors are opposite (antiparallel)." :
                         angleDegrees < 90 ? "The angle is acute." : "The angle is obtuse."}
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <p style={{ fontSize: 11, color: "var(--muted, #94a3b8)" }}>
                  Add at least two points to calculate the dot product and angle.
                </p>
              )}
            </div>

'''
if inspector_anchor not in page:
    raise SystemExit("Could not find Distance Between Points inspector section. No files changed.")
page = page.replace(inspector_anchor, inspector_insert + inspector_anchor, 1)

scene_anchor = 'function Scene({ distancePointIds, vectorOperation }:'
angle_component = '''function AngleBetweenVectorsGraphic({ points, pointIds }: { points: ScenePoint[]; pointIds: [string, string] | null }) {
  if (!pointIds) return null;
  const pa = points.find((point) => point.id === pointIds[0]);
  const pb = points.find((point) => point.id === pointIds[1]);
  if (!pa?.visible || !pb?.visible) return null;

  const a: [number, number, number] = [pa.position.x, pa.position.y, pa.position.z];
  const b: [number, number, number] = [pb.position.x, pb.position.y, pb.position.z];
  const lenA = Math.hypot(...a);
  const lenB = Math.hypot(...b);
  if (lenA < 1e-8 || lenB < 1e-8) return null;

  const u: [number, number, number] = [a[0] / lenA, a[1] / lenA, a[2] / lenA];
  const w: [number, number, number] = [b[0] / lenB, b[1] / lenB, b[2] / lenB];
  const dot = Math.max(-1, Math.min(1, u[0] * w[0] + u[1] * w[1] + u[2] * w[2]));
  const angle = Math.acos(dot);
  if (angle < 1e-4) return null;

  let normal: [number, number, number] = [
    u[1] * w[2] - u[2] * w[1],
    u[2] * w[0] - u[0] * w[2],
    u[0] * w[1] - u[1] * w[0],
  ];
  let normalLength = Math.hypot(...normal);
  if (normalLength < 1e-7) {
    const reference: [number, number, number] = Math.abs(u[2]) < 0.9 ? [0, 0, 1] : [0, 1, 0];
    normal = [
      u[1] * reference[2] - u[2] * reference[1],
      u[2] * reference[0] - u[0] * reference[2],
      u[0] * reference[1] - u[1] * reference[0],
    ];
    normalLength = Math.hypot(...normal);
  }
  normal = [normal[0] / normalLength, normal[1] / normalLength, normal[2] / normalLength];
  const tangent: [number, number, number] = [
    normal[1] * u[2] - normal[2] * u[1],
    normal[2] * u[0] - normal[0] * u[2],
    normal[0] * u[1] - normal[1] * u[0],
  ];

  const radius = Math.max(0.45, Math.min(1.25, Math.min(lenA, lenB) * 0.35));
  const arcPoints: [number, number, number][] = [];
  const segments = 40;
  for (let i = 0; i <= segments; i += 1) {
    const t = (angle * i) / segments;
    arcPoints.push([
      radius * (u[0] * Math.cos(t) + tangent[0] * Math.sin(t)),
      radius * (u[1] * Math.cos(t) + tangent[1] * Math.sin(t)),
      radius * (u[2] * Math.cos(t) + tangent[2] * Math.sin(t)),
    ]);
  }

  const mid = angle / 2;
  const labelPosition: [number, number, number] = [
    (radius + 0.22) * (u[0] * Math.cos(mid) + tangent[0] * Math.sin(mid)),
    (radius + 0.22) * (u[1] * Math.cos(mid) + tangent[1] * Math.sin(mid)),
    (radius + 0.22) * (u[2] * Math.cos(mid) + tangent[2] * Math.sin(mid)),
  ];
  const degrees = (angle * 180) / Math.PI;

  return (
    <group>
      <Line points={arcPoints} color="#F0ABFC" lineWidth={3} />
      <Text position={labelPosition} fontSize={0.25} color="#F0ABFC" anchorX="center" anchorY="middle" outlineWidth={0.025} outlineColor="#0F172A">
        {`${degrees.toFixed(1)}°`}
      </Text>
    </group>
  );
}

'''
if scene_anchor not in scene:
    raise SystemExit("Could not find Scene component insertion point. No files changed.")
scene = scene.replace(scene_anchor, angle_component + scene_anchor, 1)

render_anchor = '      <VectorOperationGraphic points={points} pointIds={distancePointIds} operation={vectorOperation} />'
if render_anchor not in scene:
    raise SystemExit("Could not find vector-operation render line. No files changed.")
scene = scene.replace(render_anchor, render_anchor + '\\n      <AngleBetweenVectorsGraphic points={points} pointIds={distancePointIds} />', 1)

PAGE.write_text(page)
SCENE.write_text(scene)
print("Dot Product + Angle Between Vectors integrated successfully.")
print("Updated src/app/page.tsx and src/components/three-d-scene.tsx")
print("No new dependencies or imports were required.")
