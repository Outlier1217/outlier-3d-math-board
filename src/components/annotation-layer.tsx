"use client";

import { useRef, useState } from "react";

type Tool = "select" | "pen" | "eraser" | "highlighter" | "hand" | "line" | "arrow" | "shapes" | "text" | "ruler";

type Stroke = {
  id: number;
  points: [number, number][];
  color: string;
  width: number;
  opacity: number;
  tool: "pen" | "highlighter";
};

export default function AnnotationLayer({
  activeTool,
  color,
  size,
  interactionMode,
}: {
  activeTool: Tool;
  color: string;
  size: number;
  interactionMode: "3d" | "pen";
}) {
  const [strokes, setStrokes] = useState<Stroke[]>([]);
  const [redoStack, setRedoStack] = useState<Stroke[]>([]);
  const [current, setCurrent] = useState<Stroke | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const drawing = interactionMode === "pen" && (activeTool === "pen" || activeTool === "highlighter" || activeTool === "eraser");

  const getPoint = (event: React.PointerEvent<SVGSVGElement>): [number, number] => {
    const rect = event.currentTarget.getBoundingClientRect();
    return [
      ((event.clientX - rect.left) / rect.width) * 1000,
      ((event.clientY - rect.top) / rect.height) * 1000,
    ];
  };

  const eraseAt = (point: [number, number]) => {
    setStrokes((previous) =>
      previous.filter((stroke) =>
        !stroke.points.some(([x, y]) => Math.hypot(x - point[0], y - point[1]) < Math.max(12, size * 3))
      )
    );
  };

  const handleDown = (event: React.PointerEvent<SVGSVGElement>) => {
    if (!drawing) return;
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.setPointerCapture(event.pointerId);

    const point = getPoint(event);

    if (activeTool === "eraser") {
      eraseAt(point);
      return;
    }

    setRedoStack([]);
    setCurrent({
      id: Date.now(),
      points: [point],
      color,
      width: activeTool === "highlighter" ? size * 3 : size,
      opacity: activeTool === "highlighter" ? 0.28 : 1,
      tool: activeTool,
    });
  };

  const handleMove = (event: React.PointerEvent<SVGSVGElement>) => {
    if (!drawing || !event.buttons) return;
    event.preventDefault();
    event.stopPropagation();

    const point = getPoint(event);

    if (activeTool === "eraser") {
      eraseAt(point);
      return;
    }

    setCurrent((previous) =>
      previous ? { ...previous, points: [...previous.points, point] } : previous
    );
  };

  const handleUp = () => {
    if (current) {
      setStrokes((previous) => [...previous, current]);
      setCurrent(null);
    }
  };

  const undo = () => {
    if (!strokes.length) return;
    const last = strokes[strokes.length - 1];
    setRedoStack((previous) => [...previous, last]);
    setStrokes((previous) => previous.slice(0, -1));
  };

  const redo = () => {
    if (!redoStack.length) return;
    const last = redoStack[redoStack.length - 1];
    setStrokes((previous) => [...previous, last]);
    setRedoStack((previous) => previous.slice(0, -1));
  };

  const pathFor = (points: [number, number][]) =>
    points.map(([x, y], index) => `${index === 0 ? "M" : "L"} ${x} ${y}`).join(" ");

  return (
    <>
      <svg
        ref={svgRef}
        viewBox="0 0 1000 1000"
        preserveAspectRatio="none"
        className="annotation-layer"
        style={{
          pointerEvents: drawing ? "auto" : "none",
          cursor: activeTool === "eraser" ? "cell" : drawing ? "crosshair" : "default",
          touchAction: drawing ? "none" : "auto",
        }}
        onPointerDown={handleDown}
        onPointerMove={handleMove}
        onPointerUp={handleUp}
        onPointerCancel={handleUp}
        onLostPointerCapture={handleUp}
      >
        {strokes.map((stroke) => (
          <path
            key={stroke.id}
            d={pathFor(stroke.points)}
            fill="none"
            stroke={stroke.color}
            strokeWidth={stroke.width}
            strokeOpacity={stroke.opacity}
            strokeLinecap="round"
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
          />
        ))}
        {current && (
          <path
            d={pathFor(current.points)}
            fill="none"
            stroke={current.color}
            strokeWidth={current.width}
            strokeOpacity={current.opacity}
            strokeLinecap="round"
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
          />
        )}
      </svg>

      <div className="annotation-actions">
        <button type="button" title="Undo annotation" onClick={undo} disabled={!strokes.length}>↶</button>
        <button type="button" title="Redo annotation" onClick={redo} disabled={!redoStack.length}>↷</button>
        <button
          type="button"
          title="Clear all annotations"
          onClick={() => {
            if (strokes.length && window.confirm("Clear all annotations?")) {
              setStrokes([]);
              setRedoStack([]);
              setCurrent(null);
            }
          }}
          disabled={!strokes.length}
        >
          Clear
        </button>
      </div>
    </>
  );
}
