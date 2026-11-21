from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "src/app/page.tsx"
SCENE = ROOT / "src/components/three-d-scene.tsx"

page = PAGE.read_text()
scene = SCENE.read_text()

anchors = [
    ('  const [octantMode, setOctantMode] = useState<"auto" | "manual">("auto");', page, "page calculation anchor"),
    ('            <div className="inspector-section">\n              <span className="sidebar-group-label">DOT PRODUCT &amp; ANGLE</span>', page, "dot-product inspector anchor"),
    ('function Scene({ distancePointIds, vectorOperation }:', scene, "Scene component anchor"),
    ('      <AngleBetweenVectorsGraphic points={points} pointIds={distancePointIds} />', scene, "angle graphic render anchor"),
]
for anchor, content, label in anchors:
    if anchor not in content:
        raise SystemExit(f"Could not find {label}. No files changed.")

if "const crossProduct =" in page or "CROSS PRODUCT" in page:
    raise SystemExit("Cross Product feature already appears to be integrated. No files changed.")
if "function CrossProductGraphic" in scene:
    raise SystemExit("Cross Product 3D graphic already appears to be integrated. No files changed.")

calc_anchor = '  const [octantMode, setOctantMode] = useState<"auto" | "manual">("auto");'
calc_insert = '''  // Cross product A × B (right-handed coordinate system).
  const crossProduct = distanceA && distanceB ? {
    x: distanceA.y * distanceB.z - distanceA.z * distanceB.y,
    y: distanceA.z * distanceB.x - distanceA.x * distanceB.z,
    z: distanceA.x * distanceB.y - distanceA.y * distanceB.x,
  } : null;
  const crossProductMagnitude = crossProduct
    ? Math.sqrt(crossProduct.x ** 2 + crossProduct.y ** 2 + crossProduct.z ** 2)
    : 0;

'''
page = page.replace(calc_anchor, calc_insert + calc_anchor, 1)

inspector_anchor = '''            <div className="inspector-section">
              <span className="sidebar-group-label">DOT PRODUCT &amp; ANGLE</span>'''
inspector_insert = '''            <div className="inspector-section">
              <span className="sidebar-group-label">CROSS PRODUCT</span>
              {distancePointA && distancePointB && crossProduct ? (
                <div style={{ marginTop: 8, padding: 11, borderRadius: 8, background: "rgba(14,165,233,0.07)", border: "1px solid rgba(14,165,233,0.22)", fontSize: 11, lineHeight: 1.75 }}>
                  <strong style={{ display: "block", color: "#7DD3FC", marginBottom: 5 }}>
                    {distancePointA.name} × {distancePointB.name}
                  </strong>
                  <div>A = ({distanceA!.x}, {distanceA!.y}, {distanceA!.z})</div>
                  <div>B = ({distanceB!.x}, {distanceB!.y}, {distanceB!.z})</div>
                  <div style={{ marginTop: 7, color: "#CBD5E1" }}>Using determinant method:</div>
                  <div style={{ fontFamily: "monospace", whiteSpace: "pre-wrap" }}>
                    A × B = | i   j   k |{"\\n"}        | {distanceA!.x}   {distanceA!.y}   {distanceA!.z} |{"\\n"}        | {distanceB!.x}   {distanceB!.y}   {distanceB!.z} |
                  </div>
                  <div style={{ marginTop: 7 }}>
                    = ({distanceA!.y}×{distanceB!.z} − {distanceA!.z}×{distanceB!.y})i
                  </div>
                  <div>
                    + ({distanceA!.z}×{distanceB!.x} − {distanceA!.x}×{distanceB!.z})j
                  </div>
                  <div>
                    + ({distanceA!.x}×{distanceB!.y} − {distanceA!.y}×{distanceB!.x})k
                  </div>
                  <strong style={{ display: "block", color: "#BAE6FD", marginTop: 6 }}>
                    A × B = ({crossProduct.x}, {crossProduct.y}, {crossProduct.z})
                  </strong>
                  <div style={{ marginTop: 7, color: "#CBD5E1" }}>
                    |A × B| = √({crossProduct.x ** 2} + {crossProduct.y ** 2} + {crossProduct.z ** 2})
                  </div>
                  <strong style={{ display: "block", color: "#86EFAC", marginTop: 3 }}>
                    |A × B| = {Number(crossProductMagnitude.toFixed(4))}
                  </strong>
                  <div style={{ marginTop: 7, color: "#CBD5E1" }}>
                    Area of parallelogram = |A × B| = {Number(crossProductMagnitude.toFixed(4))} square units
                  </div>
                  <div style={{ color: "#94A3B8", marginTop: 4 }}>
                    A × B is perpendicular to both A and B.
                    {crossProductMagnitude < 1e-8 ? " The vectors are parallel (or one is zero), so the cross product is zero." : ""}
                  </div>
                </div>
              ) : (
                <p style={{ fontSize: 11, color: "var(--muted, #94a3b8)" }}>
                  Add at least two points to calculate the cross product.
                </p>
              )}
            </div>

'''
page = page.replace(inspector_anchor, inspector_insert + inspector_anchor, 1)

scene_anchor = 'function Scene({ distancePointIds, vectorOperation }:'
cross_graphic = '''function CrossProductGraphic({ points, pointIds }: { points: ScenePoint[]; pointIds: [string, string] | null }) {
  if (!pointIds) return null;
  const pa = points.find((point) => point.id === pointIds[0]);
  const pb = points.find((point) => point.id === pointIds[1]);
  if (!pa?.visible || !pb?.visible) return null;

  const a: [number, number, number] = [pa.position.x, pa.position.y, pa.position.z];
  const b: [number, number, number] = [pb.position.x, pb.position.y, pb.position.z];
  const result: [number, number, number] = [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0],
  ];
  const magnitude = Math.hypot(...result);
  if (magnitude < 1e-8) return null;

  const sum: [number, number, number] = [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const labelPosition: [number, number, number] = [
    result[0] * 1.04 + 0.12,
    result[1] * 1.04 + 0.12,
    result[2] * 1.04 + 0.12,
  ];

  return (
    <group>
      <Line points={[[0, 0, 0], a, sum, b, [0, 0, 0]]} color="#38BDF8" lineWidth={1.8} dashed />
      <Line points={[[0, 0, 0], result]} color="#F472B6" lineWidth={4} />
      <Text position={labelPosition} fontSize={0.25} color="#F9A8D4" anchorX="left" anchorY="middle" outlineWidth={0.025} outlineColor="#0F172A">
        {`A × B (${result.map((v) => Number(v.toFixed(2))).join(", ")})`}
      </Text>
    </group>
  );
}

'''
scene = scene.replace(scene_anchor, cross_graphic + scene_anchor, 1)

render_anchor = '      <AngleBetweenVectorsGraphic points={points} pointIds={distancePointIds} />'
scene = scene.replace(render_anchor, render_anchor + '\n      <CrossProductGraphic points={points} pointIds={distancePointIds} />', 1)

PAGE.write_text(page)
SCENE.write_text(scene)
print("Cross Product integrated successfully.")
print("Updated src/app/page.tsx and src/components/three-d-scene.tsx")
print("No new dependencies or imports were required.")
