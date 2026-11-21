from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "src/app/page.tsx"
SCENE = ROOT / "src/components/three-d-scene.tsx"

page = PAGE.read_text()
scene = SCENE.read_text()

page_anchor = '  const [octantMode, setOctantMode] = useState<"auto" | "manual">("auto");'
inspector_anchor = '''            <div className="inspector-section">
              <span className="sidebar-group-label">CROSS PRODUCT</span>'''
scene_anchor = 'function Scene({ distancePointIds, vectorOperation }:'
render_anchor = '      <CrossProductGraphic points={points} pointIds={distancePointIds} />'

for anchor, content, label in [
    (page_anchor, page, "page calculation anchor"),
    (inspector_anchor, page, "cross-product inspector anchor"),
    (scene_anchor, scene, "Scene component anchor"),
    (render_anchor, scene, "cross-product render anchor"),
]:
    if anchor not in content:
        raise SystemExit(f"Could not find {label}. No files changed.")

if "const projectionAOnB =" in page or "SCALAR & VECTOR PROJECTION" in page:
    raise SystemExit("Projection feature already appears to be integrated. No files changed.")
if "function ProjectionGraphic" in scene:
    raise SystemExit("Projection 3D graphic already appears to be integrated. No files changed.")

calc_insert = '''  // Scalar and vector projections: project A onto B, and B onto A.
  const projectionAOnB = distanceA && distanceB
    ? (distanceB.x ** 2 + distanceB.y ** 2 + distanceB.z ** 2) > 0
      ? {
          x: (dotProductValue / (distanceB.x ** 2 + distanceB.y ** 2 + distanceB.z ** 2)) * distanceB.x,
          y: (dotProductValue / (distanceB.x ** 2 + distanceB.y ** 2 + distanceB.z ** 2)) * distanceB.y,
          z: (dotProductValue / (distanceB.x ** 2 + distanceB.y ** 2 + distanceB.z ** 2)) * distanceB.z,
        }
      : null
    : null;
  const scalarProjectionAOnB = magnitudeB > 0 ? dotProductValue / magnitudeB : null;
  const projectionBOnA = distanceA && distanceB && magnitudeA > 0
    ? {
        x: (dotProductValue / (magnitudeA ** 2)) * distanceA.x,
        y: (dotProductValue / (magnitudeA ** 2)) * distanceA.y,
        z: (dotProductValue / (magnitudeA ** 2)) * distanceA.z,
      }
    : null;
  const scalarProjectionBOnA = magnitudeA > 0 ? dotProductValue / magnitudeA : null;

'''
page = page.replace(page_anchor, calc_insert + page_anchor, 1)

inspector_insert = '''            <div className="inspector-section">
              <span className="sidebar-group-label">SCALAR &amp; VECTOR PROJECTION</span>
              {distancePointA && distancePointB ? (
                <div style={{ marginTop: 8, padding: 11, borderRadius: 8, background: "rgba(217,70,239,0.07)", border: "1px solid rgba(217,70,239,0.22)", fontSize: 11, lineHeight: 1.75 }}>
                  <strong style={{ display: "block", color: "#F0ABFC", marginBottom: 5 }}>
                    Projection of A onto B
                  </strong>
                  {magnitudeB > 0 && projectionAOnB ? (
                    <>
                      <div>Scalar projection = (A · B) / |B|</div>
                      <div>= {Number(dotProductValue.toFixed(4))} / {Number(magnitudeB.toFixed(4))}</div>
                      <strong style={{ color: "#E9D5FF" }}>
                        compB A = {Number(scalarProjectionAOnB!.toFixed(4))}
                      </strong>
                      <div style={{ marginTop: 5 }}>Vector projection = [(A · B) / |B|²] B</div>
                      <div>projB A = ({Number(projectionAOnB.x.toFixed(4))}, {Number(projectionAOnB.y.toFixed(4))}, {Number(projectionAOnB.z.toFixed(4))})</div>
                      <div>|projB A| = {Number(Math.hypot(projectionAOnB.x, projectionAOnB.y, projectionAOnB.z).toFixed(4))}</div>
                    </>
                  ) : (
                    <div style={{ color: "#FCA5A5" }}>Projection onto B is undefined because B is the zero vector.</div>
                  )}
                  <div style={{ borderTop: "1px solid rgba(217,70,239,0.18)", marginTop: 9, paddingTop: 8 }}>
                    <strong style={{ display: "block", color: "#F0ABFC", marginBottom: 4 }}>
                      Projection of B onto A
                    </strong>
                    {magnitudeA > 0 && projectionBOnA ? (
                      <>
                        <div>Scalar projection = (A · B) / |A|</div>
                        <strong style={{ color: "#E9D5FF" }}>
                          compA B = {Number(scalarProjectionBOnA!.toFixed(4))}
                        </strong>
                        <div>projA B = ({Number(projectionBOnA.x.toFixed(4))}, {Number(projectionBOnA.y.toFixed(4))}, {Number(projectionBOnA.z.toFixed(4))})</div>
                        <div>|projA B| = {Number(Math.hypot(projectionBOnA.x, projectionBOnA.y, projectionBOnA.z).toFixed(4))}</div>
                      </>
                    ) : (
                      <div style={{ color: "#FCA5A5" }}>Projection onto A is undefined because A is the zero vector.</div>
                    )}
                  </div>
                  <div style={{ color: "#94A3B8", marginTop: 7 }}>
                    The projection vector lies along the target vector; the perpendicular segment shows the component of the source vector normal to that target.
                  </div>
                </div>
              ) : (
                <p style={{ fontSize: 11, color: "var(--muted, #94a3b8)" }}>
                  Add at least two points to calculate projections.
                </p>
              )}
            </div>

'''
page = page.replace(inspector_anchor, inspector_insert + inspector_anchor, 1)

graphic = '''function ProjectionGraphic({ points, pointIds }: { points: ScenePoint[]; pointIds: [string, string] | null }) {
  if (!pointIds) return null;
  const pa = points.find((point) => point.id === pointIds[0]);
  const pb = points.find((point) => point.id === pointIds[1]);
  if (!pa?.visible || !pb?.visible) return null;

  const a: [number, number, number] = [pa.position.x, pa.position.y, pa.position.z];
  const b: [number, number, number] = [pb.position.x, pb.position.y, pb.position.z];
  const denominator = b[0] ** 2 + b[1] ** 2 + b[2] ** 2;
  if (denominator < 1e-8) return null;

  const dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const factor = dot / denominator;
  const projected: [number, number, number] = [
    factor * b[0],
    factor * b[1],
    factor * b[2],
  ];
  const labelPosition: [number, number, number] = [
    projected[0] + 0.14,
    projected[1] + 0.14,
    projected[2] + 0.14,
  ];

  return (
    <group>
      <Line points={[[0, 0, 0], projected]} color="#E879F9" lineWidth={4} />
      <Line points={[a, projected]} color="#F0ABFC" lineWidth={2} dashed />
      <Text position={labelPosition} fontSize={0.23} color="#F0ABFC" anchorX="left" anchorY="middle" outlineWidth={0.025} outlineColor="#0F172A">
        {`projB A (${projected.map((v) => Number(v.toFixed(2))).join(", ")})`}
      </Text>
    </group>
  );
}

'''
scene = scene.replace(scene_anchor, graphic + scene_anchor, 1)
scene = scene.replace(
    render_anchor,
    render_anchor + '\n      <ProjectionGraphic points={points} pointIds={distancePointIds} />',
    1,
)

PAGE.write_text(page)
SCENE.write_text(scene)
print("Scalar + Vector Projection integrated successfully.")
print("Updated src/app/page.tsx and src/components/three-d-scene.tsx")
print("Existing vector, dot-product, angle, and cross-product features were preserved.")
