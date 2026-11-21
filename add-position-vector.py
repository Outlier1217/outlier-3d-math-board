from pathlib import Path

page_path = Path("src/app/page.tsx")
scene_path = Path("src/components/three-d-scene.tsx")

if not page_path.exists() or not scene_path.exists():
    raise SystemExit("Run this script from the project root containing src/app/page.tsx.")

page = page_path.read_text()
scene = scene_path.read_text()

position_anchor = '''            <div className="inspector-section">
              <span className="sidebar-group-label">DISTANCE BETWEEN POINTS</span>
'''
position_ui = '''            <div className="inspector-section">
              <span className="sidebar-group-label">POSITION VECTOR</span>
              {selectedPoint ? (
                <div style={{
                  marginTop: 8,
                  padding: 11,
                  borderRadius: 8,
                  background: "rgba(34, 197, 94, 0.07)",
                  border: "1px solid rgba(34, 197, 94, 0.2)",
                  fontSize: 11,
                  lineHeight: 1.8,
                }}>
                  <strong style={{ display: "block", color: "#86EFAC", marginBottom: 5 }}>
                    r⃗ {selectedPoint.name.replace("Point ", "")} = O{selectedPoint.name.replace("Point ", "")}
                  </strong>
                  <div style={{ fontSize: 15, fontWeight: 700, color: "#E2E8F0", marginBottom: 5 }}>
                    {selectedPosition.x}i + ({selectedPosition.y})j + ({selectedPosition.z})k
                  </div>
                  <div>
                    r⃗ = ({selectedPosition.x}, {selectedPosition.y}, {selectedPosition.z})
                  </div>
                  <div style={{ marginTop: 5, color: "#CBD5E1" }}>
                    |r⃗| = √(x² + y² + z²)
                  </div>
                  <div>
                    |r⃗| = √({selectedPosition.x ** 2} + {selectedPosition.y ** 2} + {selectedPosition.z ** 2})
                  </div>
                  <strong style={{ display: "block", color: "#86EFAC", marginTop: 4 }}>
                    |r⃗| = {Number(Math.sqrt(
                      selectedPosition.x ** 2 +
                      selectedPosition.y ** 2 +
                      selectedPosition.z ** 2
                    ).toFixed(4))}
                  </strong>
                </div>
              ) : (
                <p style={{ fontSize: 11, color: "var(--muted, #94a3b8)" }}>
                  Select a point to view its position vector.
                </p>
              )}
            </div>

            <div className="inspector-section">
              <span className="sidebar-group-label">DISTANCE BETWEEN POINTS</span>
'''
if "POSITION VECTOR" not in page:
    if position_anchor not in page:
        raise SystemExit("Could not find Distance section in page.tsx; no changes made.")
    page = page.replace(position_anchor, position_ui, 1)

point_label_anchor = '''      {/* Coordinate projections for the selected point */}
      {isSelected && (
        <>
'''
point_label = '''      {/* Label the selected position vector from the origin */}
      {isSelected && (
        <Text
          position={[x / 2 + 0.12, y / 2 + 0.12, z / 2 + 0.12]}
          fontSize={0.22}
          color={point.color}
          anchorX="left"
          anchorY="middle"
          outlineWidth={0.02}
          outlineColor="#0F172A"
        >
          {`r⃗ ${point.name.replace("Point ", "")}`}
        </Text>
      )}

      {/* Coordinate projections for the selected point */}
      {isSelected && (
        <>
'''
if "Label the selected position vector" not in scene:
    if point_label_anchor not in scene:
        raise SystemExit("Could not find selected-point projection block in three-d-scene.tsx; no changes made.")
    scene = scene.replace(point_label_anchor, point_label, 1)

page_path.write_text(page)
scene_path.write_text(scene)
print("Position Vector feature integrated.")
print("Updated: src/app/page.tsx")
print("Updated: src/components/three-d-scene.tsx")
