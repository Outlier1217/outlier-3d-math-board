"use client";

import { useEffect, useState } from "react";
import ThreeDScene from "@/components/three-d-scene";
import {
  useSceneStore,
  detectOctant,
  type Octant,
} from "@/store/scene-store";
import {
  BookOpen, Box, Plus, Save, Undo2, Redo2, Upload,
  PanelLeftClose, PanelRightClose, MousePointer2,
  Pencil, Eraser, Highlighter, Hand, Minus,
  ArrowUpRight, Shapes, Type, Ruler, Grid3X3,
  Circle, Square, Eye, Trash2, ZoomIn, ZoomOut,
  RotateCcw, Maximize2, SplitSquareHorizontal,
  FileText, MoreHorizontal, Check, Sparkles,
  Layers, Crosshair, Palette, ChevronDown, X
} from "lucide-react";

type Tab = "pdf" | "3d" | "2d";
type Tool = "select" | "pen" | "eraser" | "highlighter" | "hand" | "line" | "arrow" | "shapes" | "text" | "ruler";

const colors = [
  "#FFFFFF", "#EF4444", "#3B82F6", "#22C55E",
  "#FACC15", "#F97316", "#A855F7", "#EC4899",
  "#06B6D4", "#111827"
];

const tools: { id: Tool; label: string; icon: typeof Pencil }[] = [
  { id: "select", label: "Select", icon: MousePointer2 },
  { id: "pen", label: "Pen", icon: Pencil },
  { id: "eraser", label: "Eraser", icon: Eraser },
  { id: "highlighter", label: "Highlighter", icon: Highlighter },
  { id: "hand", label: "Pan", icon: Hand },
  { id: "line", label: "Line", icon: Minus },
  { id: "arrow", label: "Arrow", icon: ArrowUpRight },
  { id: "shapes", label: "Shapes", icon: Shapes },
  { id: "text", label: "Text", icon: Type },
  { id: "ruler", label: "Measure", icon: Ruler },
];

function IconButton({
  icon: Icon,
  label,
  active = false,
  onClick,
  disabled = false,
}: {
  icon: typeof Pencil;
  label: string;
  active?: boolean;
  onClick?: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      title={label}
      aria-label={label}
      disabled={disabled}
      onClick={onClick}
      className={`icon-button ${active ? "icon-button-active" : ""}`}
    >
      <Icon size={17} strokeWidth={1.8} />
    </button>
  );
}

function PDFPreview() {
  return (
    <div className="pdf-page">
      <div className="pdf-paper">
        <div className="pdf-chapter">CHAPTER 11</div>
        <h2>Three Dimensional Geometry</h2>
        <div className="pdf-rule" />
        <h3>11.1 Introduction</h3>
        <p>
          In three dimensional geometry, we study the position of points,
          lines and planes in three-dimensional space.
        </p>
        <h3>Distance Formula</h3>
        <p>Let A(x₁, y₁, z₁) and B(x₂, y₂, z₂) be two points.</p>
        <div className="pdf-equation">
          AB = √[(x₂ − x₁)² + (y₂ − y₁)² + (z₂ − z₁)²]
        </div>
        <div className="pdf-diagram">
          <svg viewBox="0 0 300 170" role="img" aria-label="3D coordinate geometry diagram">
            <defs>
              <marker id="pdfArrow" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto">
                <path d="M0 0 L6 3 L0 6" fill="none" stroke="#2563eb" />
              </marker>
            </defs>
            <path d="M45 135 L260 135 M45 135 L15 155 M45 135 L45 12"
              stroke="#64748b" fill="none" strokeWidth="1.5" />
            <path d="M45 135 L170 53 L245 135" stroke="#2563eb"
              strokeWidth="2" fill="none" />
            <path d="M45 135 L170 53" stroke="#dc2626" strokeWidth="2.5"
              markerEnd="url(#pdfArrow)" />
            <circle cx="45" cy="135" r="3" fill="#0f172a" />
            <circle cx="170" cy="53" r="4" fill="#dc2626" />
            <text x="31" y="149" fontSize="11" fill="#334155">O</text>
            <text x="177" y="49" fontSize="12" fill="#dc2626">A</text>
            <text x="264" y="139" fontSize="11" fill="#334155">X</text>
            <text x="7" y="165" fontSize="11" fill="#334155">Y</text>
            <text x="50" y="15" fontSize="11" fill="#334155">Z</text>
          </svg>
        </div>
        <div className="pdf-question">
          <strong>Example 1.</strong> Find the distance between the points
          A(1, 2, 3) and B(4, 5, 6).
        </div>
        <div className="pdf-page-number">1</div>
      </div>
    </div>
  );
}

function ThreeDPreview() {
  return (
    <div className="scene-preview">
      <div className="three-d-canvas">
        <ThreeDScene />
      </div>
      <div className="scene-coordinate-label">
        <Crosshair size={13} /> 3D Coordinate System
      </div>
      <div className="scene-hint">
        Drag to rotate · Scroll to zoom · Right-click drag to pan
      </div>
    </div>
  );
}

export default function Home() {
  const pointA = useSceneStore((state) => state.pointA);
  const setPointA = useSceneStore((state) => state.setPointA);
  const resetPointA = useSceneStore((state) => state.resetPointA);
  const selectedOctant = useSceneStore((state) => state.selectedOctant);
  const setSelectedOctant = useSceneStore((state) => state.setSelectedOctant);

  const [octantMode, setOctantMode] = useState<"auto" | "manual">("auto");
  const detectedOctant = detectOctant(pointA);
  const activeOctant = octantMode === "auto" ? detectedOctant : selectedOctant;

  const octantSigns: Record<Octant, string> = {
    1: "(+, +, +)",
    2: "(-, +, +)",
    3: "(-, -, +)",
    4: "(+, -, +)",
    5: "(+, +, -)",
    6: "(-, +, -)",
    7: "(-, -, -)",
    8: "(+, -, -)",
  };

  useEffect(() => {
    if (octantMode === "auto") {
      setSelectedOctant(detectedOctant);
    }
  }, [octantMode, detectedOctant, setSelectedOctant]);

  const [activeTab, setActiveTab] = useState<Tab>("3d");
  const [activeTool, setActiveTool] = useState<Tool>("select");
  const [activeColor, setActiveColor] = useState("#FACC15");
  const [penSize, setPenSize] = useState(3);
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);
  const [splitView, setSplitView] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const [selectedObject, setSelectedObject] = useState("Point A");
  const [fontSize, setFontSize] = useState("18");
  const [bold, setBold] = useState(false);
  const [italic, setItalic] = useState(false);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [pdfName, setPdfName] = useState("Three Dimensional Geometry.pdf");

  const tabItems = [
    { id: "pdf" as Tab, label: "PDF Reader", icon: BookOpen },
    { id: "3d" as Tab, label: "3D Mathematics", icon: Box },
    { id: "2d" as Tab, label: "2D Whiteboard", icon: Pencil },
  ];

  const activeToolLabel = tools.find((tool) => tool.id === activeTool)?.label ?? "Select";

  const switchTab = (tab: Tab) => {
    setActiveTab(tab);
    setSplitView(false);
  };

  const handlePDFUpload = (file?: File) => {
    if (!file) return;
    if (file.type !== "application/pdf") {
      alert("Please select a PDF file.");
      return;
    }
    setPdfName(file.name);
    setActiveTab("pdf");
    setShowUpload(false);
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-area">
          <div className="brand-logo"><Box size={21} /></div>
          <div className="brand-copy">
            <span className="brand-name">OUTLIER <b>3D</b></span>
            <span className="brand-subtitle">MATHEMATICS STUDIO</span>
          </div>
        </div>

        <div className="topbar-center">
          <span className="lesson-name">Untitled Lesson</span>
          <span className="saved-indicator"><span /> Local workspace</span>
        </div>

        <div className="topbar-actions">
          <IconButton icon={Undo2} label="Undo" />
          <IconButton icon={Redo2} label="Redo" />
          <div className="topbar-divider" />
          <button className="top-action" onClick={() => setShowUpload(true)}>
            <Upload size={15} /> Open PDF
          </button>
          <button className="save-button" onClick={() => alert("Lesson saving will be implemented with IndexedDB.")}>
            <Save size={15} /> Save
          </button>
          <IconButton icon={MoreHorizontal} label="More options" />
        </div>
      </header>

      <nav className="workspace-tabs">
        <div className="tab-list">
          {tabItems.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                className={`workspace-tab ${activeTab === tab.id ? "workspace-tab-active" : ""}`}
                onClick={() => switchTab(tab.id)}
              >
                <Icon size={16} />
                {tab.label}
                {activeTab === tab.id && <span className="tab-indicator" />}
              </button>
            );
          })}
          <button className="add-tab" title="New workspace tab" onClick={() => alert("Custom workspace tabs are coming in a later milestone.")}>
            <Plus size={17} />
          </button>
        </div>
        <div className="tabs-right">
          <button className={`view-mode ${splitView ? "view-mode-active" : ""}`} onClick={() => setSplitView(!splitView)}>
            <SplitSquareHorizontal size={15} /> Split View
          </button>
          <span className="workspace-status">WORKSPACE</span>
        </div>
      </nav>

      <div className="editor-toolbar">
        <div className="toolbar-section">
          <span className="toolbar-label">TOOLS</span>
          {tools.map((tool) => {
            const Icon = tool.icon;
            return (
              <IconButton
                key={tool.id}
                icon={Icon}
                label={tool.label}
                active={activeTool === tool.id}
                onClick={() => setActiveTool(tool.id)}
              />
            );
          })}
        </div>

        <div className="toolbar-separator" />

        <div className="toolbar-section color-section">
          <span className="toolbar-label">COLOR</span>
          <div className="color-swatches">
            {colors.slice(0, 7).map((color) => (
              <button
                key={color}
                title={color}
                onClick={() => setActiveColor(color)}
                className={`color-swatch ${activeColor === color ? "color-selected" : ""}`}
                style={{ backgroundColor: color }}
              >
                {activeColor === color && <Check size={12} color={color === "#FFFFFF" ? "#111827" : "#fff"} />}
              </button>
            ))}
          </div>
          <button className="custom-color-button" title="More colors" onClick={() => setShowColorPicker(!showColorPicker)}>
            <Palette size={16} />
          </button>
          {showColorPicker && (
            <div className="color-popover">
              <label>Custom colour</label>
              <input type="color" value={activeColor} onChange={(e) => setActiveColor(e.target.value)} />
              <span>{activeColor.toUpperCase()}</span>
            </div>
          )}
        </div>

        <div className="toolbar-separator" />

        <div className="toolbar-section size-section">
          <span className="toolbar-label">SIZE</span>
          <input
            type="range" min="1" max="20" value={penSize}
            onChange={(e) => setPenSize(Number(e.target.value))}
            aria-label="Pen thickness"
          />
          <span className="size-value">{penSize}px</span>
        </div>

        <div className="toolbar-separator" />

        <div className="toolbar-section typography-section">
          <span className="toolbar-label">TEXT</span>
          <select aria-label="Font size" value={fontSize} onChange={(e) => setFontSize(e.target.value)}>
            <option value="12">12 px</option>
            <option value="14">14 px</option>
            <option value="16">16 px</option>
            <option value="18">18 px</option>
            <option value="24">24 px</option>
            <option value="32">32 px</option>
            <option value="48">48 px</option>
          </select>
          <button className={`format-button ${bold ? "format-active" : ""}`} onClick={() => setBold(!bold)}><b>B</b></button>
          <button className={`format-button ${italic ? "format-active" : ""}`} onClick={() => setItalic(!italic)}><i>I</i></button>
          <button className="format-button" title="Underline"><u>U</u></button>
        </div>

        <div className="toolbar-spacer" />
        <span className="active-tool-status">{activeToolLabel} tool</span>
      </div>

      <div className="editor-body">
        {leftOpen && (
          <aside className="left-sidebar">
            <div className="sidebar-heading">
              <span>TOOLS & OBJECTS</span>
              <IconButton icon={PanelLeftClose} label="Collapse left panel" onClick={() => setLeftOpen(false)} />
            </div>
            <div className="sidebar-group">
              <span className="sidebar-group-label">DRAWING</span>
              {tools.slice(0, 5).map((tool) => {
                const Icon = tool.icon;
                return (
                  <button key={tool.id} className={`sidebar-tool ${activeTool === tool.id ? "sidebar-tool-active" : ""}`} onClick={() => setActiveTool(tool.id)}>
                    <Icon size={16} /> {tool.label}
                    {activeTool === tool.id && <span className="tool-shortcut">ACTIVE</span>}
                  </button>
                );
              })}
            </div>
            <div className="sidebar-group">
              <span className="sidebar-group-label">GEOMETRY</span>
              {[
                { label: "Point", icon: Circle },
                { label: "Line", icon: Minus },
                { label: "Vector", icon: ArrowUpRight },
                { label: "Plane", icon: Square },
                { label: "Solid shapes", icon: Box },
              ].map((item) => {
                const Icon = item.icon;
                return <button key={item.label} className="sidebar-tool" onClick={() => setSelectedObject(item.label)}>
                  <Icon size={16} /> {item.label}
                </button>;
              })}
            </div>
            <div className="sidebar-group">
              <span className="sidebar-group-label">SCENE</span>
              <button className="sidebar-tool" onClick={() => setShowGrid(!showGrid)}>
                <Grid3X3 size={16} /> Grid
                <span className={`toggle-dot ${showGrid ? "toggle-on" : ""}`} />
              </button>
              <button className="sidebar-tool" onClick={() => setSelectedObject("Coordinate Axes")}>
                <Crosshair size={16} /> Coordinate axes
              </button>
            </div>
            <div className="sidebar-footer">
              <Sparkles size={15} /> Built for teaching
            </div>
          </aside>
        )}

        <section className="main-workspace">
          {!leftOpen && <button className="reopen-panel left-reopen" onClick={() => setLeftOpen(true)}><PanelLeftClose size={16} /></button>}

          <div className="canvas-header">
            <div>
              <span className="canvas-breadcrumb">WORKSPACE / </span>
              <span className="canvas-current">{splitView ? "Split View" : tabItems.find((t) => t.id === activeTab)?.label}</span>
            </div>
            <div className="canvas-actions">
              <IconButton icon={ZoomOut} label="Zoom out" />
              <span className="zoom-level">100%</span>
              <IconButton icon={ZoomIn} label="Zoom in" />
              <IconButton icon={RotateCcw} label="Reset view" />
              <IconButton icon={Maximize2} label="Fullscreen" />
            </div>
          </div>

          <div className={`canvas-content ${splitView ? "split-canvas" : ""}`}>
            {(splitView || activeTab === "pdf") && (
              <section className="canvas-pane pdf-pane">
                <div className="pane-title"><BookOpen size={14} /> PDF READER <span>•</span> {pdfName}</div>
                <div className="pdf-toolbar-mini">
                  <button onClick={() => setShowUpload(true)}><Upload size={13}/> Open PDF</button>
                  <button><ChevronDown size={13}/> Page 1 / 1</button>
                  <button><ZoomOut size={13}/></button>
                  <button>100%</button>
                  <button><ZoomIn size={13}/></button>
                </div>
                <PDFPreview />
              </section>
            )}

            {(splitView || activeTab === "3d" || activeTab === "2d") && (
              <section className={`canvas-pane board-pane ${activeTab === "2d" && !splitView ? "two-d-pane" : ""}`}>
                <div className="pane-title">
                  {activeTab === "2d" && !splitView ? <Pencil size={14}/> : <Box size={14}/>}
                  {activeTab === "2d" && !splitView ? "2D WHITEBOARD" : "3D MATHEMATICS"}
                  <span>•</span> {activeToolLabel}
                </div>
                {activeTab === "2d" && !splitView ? (
                  <div className="whiteboard-surface">
                    <div className="whiteboard-grid" />
                    <div className="whiteboard-welcome">
                      <Pencil size={28}/>
                      <h2>2D Whiteboard</h2>
                      <p>Handwriting canvas engine will be connected next.</p>
                    </div>
                  </div>
                ) : <ThreeDPreview />}
              </section>
            )}
          </div>

          <div className="bottom-explorer">
            <div className="explorer-title"><Layers size={15}/> OBJECT EXPLORER</div>
            {["Point A", "Vector OA", "Plane P"].map((name, i) => (
              <button key={name} className={`explorer-item ${selectedObject === name ? "explorer-selected" : ""}`} onClick={() => setSelectedObject(name)}>
                {i === 0 ? <Circle size={13}/> : i === 1 ? <ArrowUpRight size={13}/> : <Square size={13}/>}
                {name}
                <span className="object-visible"><Eye size={12}/></span>
              </button>
            ))}
            <button className="explorer-add" onClick={() => setSelectedObject("New Object")}><Plus size={14}/> Add object</button>
            <div className="explorer-spacer"/>
            <span className="scene-count">3 OBJECTS</span>
          </div>
        </section>

        {rightOpen && (
          <aside className="right-sidebar">
            <div className="sidebar-heading">
              <span>INSPECTOR</span>
              <IconButton icon={PanelRightClose} label="Collapse right panel" onClick={() => setRightOpen(false)} />
            </div>
            <div className="inspector-section">
              <span className="sidebar-group-label">SELECTION</span>
              <div className="selected-object-card">
                <div className="selected-object-icon"><Box size={18}/></div>
                <div><strong>{selectedObject}</strong><small>Mathematical object</small></div>
              </div>
            </div>
            <div className="inspector-section">
              <span className="sidebar-group-label">TRANSFORM</span>
              {(["x", "y", "z"] as const).map((axis) => (
                <label className="property-row" key={axis}>
                  <span>{axis.toUpperCase()}</span>
                  <input
                    type="number"
                    step="any"
                    value={pointA[axis]}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value === "" || value === "-") return;
                      const number = Number(value);
                      if (Number.isFinite(number)) {
                        setPointA({ [axis]: number });
                      }
                    }}
                  />
                </label>
              ))}
            </div>
            <div className="inspector-section">
              <span className="sidebar-group-label">OCTANT DETECTOR</span>

              <div style={{ display: "flex", gap: 6, marginBottom: 12 }}>
                <button
                  type="button"
                  onClick={() => setOctantMode("auto")}
                  style={{
                    flex: 1,
                    padding: "7px 8px",
                    borderRadius: 7,
                    border: "1px solid",
                    borderColor: octantMode === "auto" ? "#8B5CF6" : "var(--border, #30303a)",
                    background: octantMode === "auto" ? "rgba(139, 92, 246, 0.16)" : "transparent",
                    color: octantMode === "auto" ? "#C4B5FD" : "inherit",
                    cursor: "pointer",
                    fontSize: 11,
                  }}
                >
                  Auto Detect
                </button>
                <button
                  type="button"
                  onClick={() => setOctantMode("manual")}
                  style={{
                    flex: 1,
                    padding: "7px 8px",
                    borderRadius: 7,
                    border: "1px solid",
                    borderColor: octantMode === "manual" ? "#8B5CF6" : "var(--border, #30303a)",
                    background: octantMode === "manual" ? "rgba(139, 92, 246, 0.16)" : "transparent",
                    color: octantMode === "manual" ? "#C4B5FD" : "inherit",
                    cursor: "pointer",
                    fontSize: 11,
                  }}
                >
                  Manual Select
                </button>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 6 }}>
                {([1, 2, 3, 4, 5, 6, 7, 8] as Octant[]).map((octant) => (
                  <button
                    key={octant}
                    type="button"
                    title={`Octant ${octant}: ${octantSigns[octant]}`}
                    onClick={() => {
                      setOctantMode("manual");
                      setSelectedOctant(octant);
                    }}
                    style={{
                      padding: "9px 3px",
                      borderRadius: 7,
                      border: "1px solid",
                      borderColor: activeOctant === octant ? "#A78BFA" : "var(--border, #30303a)",
                      background: activeOctant === octant ? "rgba(139, 92, 246, 0.2)" : "rgba(255,255,255,0.025)",
                      color: activeOctant === octant ? "#DDD6FE" : "inherit",
                      cursor: "pointer",
                      fontSize: 12,
                      fontWeight: activeOctant === octant ? 700 : 500,
                    }}
                  >
                    {["I", "II", "III", "IV", "V", "VI", "VII", "VIII"][octant - 1]}
                  </button>
                ))}
              </div>

              <div style={{
                marginTop: 10,
                padding: 10,
                borderRadius: 8,
                background: "rgba(139, 92, 246, 0.08)",
                border: "1px solid rgba(139, 92, 246, 0.2)",
                fontSize: 11,
                lineHeight: 1.6,
              }}>
                {activeOctant !== null ? (
                  <>
                    <strong style={{ display: "block", color: "#C4B5FD", marginBottom: 3 }}>
                      Octant {["I", "II", "III", "IV", "V", "VI", "VII", "VIII"][activeOctant - 1]}
                    </strong>
                    <span>Sign pattern: {octantSigns[activeOctant]}</span>
                    <br />
                    <span>
                      {octantMode === "auto"
                        ? "Automatically detected from Point A."
                        : "Manually selected for teaching."}
                    </span>
                  </>
                ) : (
                  <>
                    <strong style={{ display: "block", marginBottom: 3 }}>Point is on a coordinate plane</strong>
                    <span>
                      At least one coordinate is zero, so Point A does not belong to any octant.
                    </span>
                  </>
                )}
              </div>
            </div>

            <div className="inspector-section">
              <span className="sidebar-group-label">APPEARANCE</span>
              <div className="property-row"><span>Visible</span><button className="visibility-button"><Eye size={14}/> On</button></div>
              <div className="property-row"><span>Colour</span><input type="color" defaultValue="#3B82F6" aria-label="Object colour"/></div>
              <div className="property-row"><span>Opacity</span><span className="property-value">100%</span></div>
            </div>
            <div className="inspector-section">
              <span className="sidebar-group-label">EQUATION</span>
              <div className="equation-box">x² + y² + z² = r²</div>
            </div>
            <div className="inspector-footer">
              <button onClick={() => { resetPointA(); setSelectedObject("Point A"); }}><RotateCcw size={14}/> Reset</button>
              <button onClick={() => setSelectedObject("None")}><Trash2 size={14}/> Clear</button>
            </div>
          </aside>
        )}
        {!rightOpen && <button className="reopen-panel right-reopen" onClick={() => setRightOpen(true)}><PanelRightClose size={16}/></button>}
      </div>

      <footer className="statusbar">
        <div><span className="status-online"/> Ready <span className="status-divider">|</span> {activeTab.toUpperCase()} MODE</div>
        <div className="status-center">Outlier Mathematics Studio <span>v0.1.0</span></div>
        <div> {penSize}px <span className="status-divider">|</span> {activeColor.toUpperCase()} <span className="status-divider">|</span> {showGrid ? "GRID ON" : "GRID OFF"}</div>
      </footer>

      {showUpload && (
        <div className="modal-backdrop" onClick={() => setShowUpload(false)}>
          <div className="upload-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-heading"><div><FileText size={19}/> <strong>Open PDF Book</strong></div><button onClick={() => setShowUpload(false)}><X size={18}/></button></div>
            <label className="upload-dropzone">
              <Upload size={30}/>
              <strong>Choose a PDF file</strong>
              <span>Select a mathematics book or lesson PDF</span>
              <input type="file" accept="application/pdf" onChange={(e) => handlePDFUpload(e.target.files?.[0])}/>
            </label>
            <p className="modal-note">PDF rendering and annotation saving will be enabled in the PDF engine milestone.</p>
          </div>
        </div>
      )}
    </main>
  );
}
