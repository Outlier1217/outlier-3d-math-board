"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  Eraser,
  Pen,
  RotateCcw,
  RotateCw,
  Trash2,
} from "lucide-react";
import styles from "./handwriting-canvas.module.css";

type DrawingTool = "pen" | "eraser";

type Props = {
  onCanvasChange?: (image: string) => void;
};

type Point = {
  x: number;
  y: number;
  pressure: number;
};

const MAX_HISTORY = 30;

export default function HandwritingCanvas({
  onCanvasChange,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const drawingRef = useRef(false);
  const resizePendingRef = useRef(false);
  const lastPointRef = useRef<Point | null>(null);

  const historyRef = useRef<string[]>([]);
  const historyIndexRef = useRef(-1);

  const callbackRef = useRef(onCanvasChange);
  const toolRef = useRef<DrawingTool>("pen");
  const widthRef = useRef(3);

  const [tool, setTool] = useState<DrawingTool>("pen");
  const [lineWidth, setLineWidth] = useState(3);
  const [historyVersion, setHistoryVersion] = useState(0);

  useEffect(() => {
    callbackRef.current = onCanvasChange;
  }, [onCanvasChange]);

  useEffect(() => {
    toolRef.current = tool;
  }, [tool]);

  useEffect(() => {
    widthRef.current = lineWidth;
  }, [lineWidth]);

  const emitCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    callbackRef.current?.(canvas.toDataURL("image/png"));
  }, []);

  const saveHistory = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const image = canvas.toDataURL("image/png");

    const history = historyRef.current.slice(
      0,
      historyIndexRef.current + 1,
    );

    history.push(image);

    if (history.length > MAX_HISTORY) {
      history.shift();
    }

    historyRef.current = history;
    historyIndexRef.current = history.length - 1;

    setHistoryVersion((value) => value + 1);
    emitCanvas();
  }, [emitCanvas]);

  const paintImage = useCallback((imageData: string) => {
    const canvas = canvasRef.current;
    const container = containerRef.current;

    if (!canvas || !container) return;

    const image = new Image();

    image.onload = () => {
      const rect = container.getBoundingClientRect();
      const ratio = window.devicePixelRatio || 1;
      const width = rect.width;
      const height = rect.height;

      if (!width || !height) return;

      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);

      const context = canvas.getContext("2d");
      if (!context) return;

      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      context.fillStyle = "#ffffff";
      context.fillRect(0, 0, width, height);

      context.drawImage(image, 0, 0, width, height);

      emitCanvas();
    };

    image.src = imageData;
  }, [emitCanvas]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;

    if (!canvas || !container) return;

    let initialized = false;

    const resizeCanvas = () => {
      if (drawingRef.current) {
        resizePendingRef.current = true;
        return;
      }

      const rect = container.getBoundingClientRect();
      if (!rect.width || !rect.height) return;

      const previousImage = initialized
        ? canvas.toDataURL("image/png")
        : null;

      const ratio = window.devicePixelRatio || 1;

      canvas.width = Math.round(rect.width * ratio);
      canvas.height = Math.round(rect.height * ratio);

      const context = canvas.getContext("2d");
      if (!context) return;

      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      context.fillStyle = "#ffffff";
      context.fillRect(0, 0, rect.width, rect.height);

      if (previousImage) {
        const image = new Image();

        image.onload = () => {
          context.drawImage(
            image,
            0,
            0,
            rect.width,
            rect.height,
          );
          emitCanvas();
        };

        image.src = previousImage;
      } else {
        initialized = true;
        saveHistory();
      }
    };

    const observer = new ResizeObserver(resizeCanvas);
    observer.observe(container);

    resizeCanvas();

    const handleWindowResize = () => resizeCanvas();
    window.addEventListener("resize", handleWindowResize);

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", handleWindowResize);
    };
  }, [emitCanvas, saveHistory]);

  const getPoint = (
    event: React.PointerEvent<HTMLCanvasElement>,
  ): Point => {
    const rect = event.currentTarget.getBoundingClientRect();

    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
      pressure: event.pressure,
    };
  };

  const getStrokeWidth = (
    pressure: number,
    pointerType: string,
  ) => {
    const baseWidth = widthRef.current;

    if (toolRef.current === "eraser") {
      return baseWidth * 5;
    }

    if (pointerType === "pen" && pressure > 0) {
      return baseWidth * Math.max(0.35, pressure * 1.5);
    }

    return baseWidth;
  };

  const startDrawing = (
    event: React.PointerEvent<HTMLCanvasElement>,
  ) => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");

    if (!canvas || !context || drawingRef.current) return;

    event.preventDefault();

    try {
      event.currentTarget.setPointerCapture(event.pointerId);
    } catch {
      // Pointer capture may be unavailable on some devices.
    }

    const point = getPoint(event);

    drawingRef.current = true;
    lastPointRef.current = point;

    context.beginPath();
    context.arc(point.x, point.y, getStrokeWidth(
      point.pressure,
      event.pointerType,
    ) / 2, 0, Math.PI * 2);

    context.fillStyle =
      toolRef.current === "eraser" ? "#ffffff" : "#111827";

    context.fill();
  };

  const draw = (
    event: React.PointerEvent<HTMLCanvasElement>,
  ) => {
    if (!drawingRef.current) return;

    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");
    const previous = lastPointRef.current;

    if (!canvas || !context || !previous) return;

    event.preventDefault();

    const point = getPoint(event);

    context.beginPath();
    context.moveTo(previous.x, previous.y);
    context.lineTo(point.x, point.y);

    context.lineCap = "round";
    context.lineJoin = "round";

    context.strokeStyle =
      toolRef.current === "eraser" ? "#ffffff" : "#111827";

    context.lineWidth = getStrokeWidth(
      point.pressure,
      event.pointerType,
    );

    context.stroke();

    lastPointRef.current = point;
  };

  const stopDrawing = () => {
    if (!drawingRef.current) return;

    drawingRef.current = false;
    lastPointRef.current = null;

    saveHistory();

    if (resizePendingRef.current) {
      resizePendingRef.current = false;
      const canvas = canvasRef.current;
      const container = containerRef.current;

      if (canvas && container) {
        const rect = container.getBoundingClientRect();
        const previousImage = canvas.toDataURL("image/png");
        const image = new Image();

        image.onload = () => {
          const ratio = window.devicePixelRatio || 1;

          canvas.width = Math.round(rect.width * ratio);
          canvas.height = Math.round(rect.height * ratio);

          const context = canvas.getContext("2d");
          if (!context) return;

          context.setTransform(ratio, 0, 0, ratio, 0, 0);
          context.fillStyle = "#ffffff";
          context.fillRect(0, 0, rect.width, rect.height);
          context.drawImage(image, 0, 0, rect.width, rect.height);

          saveHistory();
        };

        image.src = previousImage;
      }
    }
  };

  const undo = () => {
    if (historyIndexRef.current <= 0) return;

    historyIndexRef.current -= 1;

    const image = historyRef.current[historyIndexRef.current];
    paintImage(image);

    setHistoryVersion((value) => value + 1);
  };

  const redo = () => {
    if (historyIndexRef.current >= historyRef.current.length - 1) {
      return;
    }

    historyIndexRef.current += 1;

    const image = historyRef.current[historyIndexRef.current];
    paintImage(image);

    setHistoryVersion((value) => value + 1);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const container = containerRef.current;

    if (!canvas || !container) return;

    const rect = container.getBoundingClientRect();
    const context = canvas.getContext("2d");

    if (!context) return;

    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, rect.width, rect.height);

    saveHistory();
  };

  const canUndo = historyIndexRef.current > 0;
  const canRedo =
    historyIndexRef.current < historyRef.current.length - 1;

  return (
    <section className={styles.panel}>
      <div className={styles.toolbar}>
        <div className={styles.toolGroup}>
          <button
            type="button"
            className={tool === "pen" ? styles.activeTool : styles.tool}
            onClick={() => setTool("pen")}
            title="Pen"
            aria-label="Pen"
          >
            <Pen size={17} />
          </button>

          <button
            type="button"
            className={tool === "eraser" ? styles.activeTool : styles.tool}
            onClick={() => setTool("eraser")}
            title="Eraser"
            aria-label="Eraser"
          >
            <Eraser size={17} />
          </button>
        </div>

        <div className={styles.separator} />

        <label className={styles.thicknessControl}>
          <span>Size</span>
          <input
            type="range"
            min="1"
            max="12"
            value={lineWidth}
            onChange={(event) => setLineWidth(Number(event.target.value))}
          />
          <span className={styles.sizeValue}>{lineWidth}px</span>
        </label>

        <div className={styles.separator} />

        <div className={styles.toolGroup}>
          <button
            type="button"
            className={styles.tool}
            onClick={undo}
            disabled={!canUndo}
            title="Undo"
            aria-label="Undo"
          >
            <RotateCcw size={17} />
          </button>

          <button
            type="button"
            className={styles.tool}
            onClick={redo}
            disabled={!canRedo}
            title="Redo"
            aria-label="Redo"
          >
            <RotateCw size={17} />
          </button>

          <button
            type="button"
            className={styles.clearTool}
            onClick={clearCanvas}
            title="Clear canvas"
            aria-label="Clear canvas"
          >
            <Trash2 size={17} />
          </button>
        </div>
      </div>

      <div className={styles.canvasContainer} ref={containerRef}>
        <canvas
          ref={canvasRef}
          className={styles.canvas}
          onPointerDown={startDrawing}
          onPointerMove={draw}
          onPointerUp={stopDrawing}
          onPointerCancel={stopDrawing}
          onLostPointerCapture={stopDrawing}
          aria-label="Mathematical handwriting canvas"
        />

        <div className={styles.canvasHint}>
          Write your equation here
        </div>
      </div>

      <div className={styles.footer}>
        <span>Handwriting workspace</span>
        <span>
          History: {historyVersion > 0 ? "Active" : "Ready"}
        </span>
      </div>
    </section>
  );
}
