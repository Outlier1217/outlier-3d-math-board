"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { Bounds, OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import { AlertCircle, Box, RotateCcw, Maximize2, Minimize2 } from "lucide-react";

import { parseSurfaceEquation } from "@/lib/equation-graph/math-parser";
import { useEquationGraphStore } from "@/lib/equation-graph/store";
import styles from "./equation-graph-3d.module.css";

const MAX_HEIGHT = 50;

function createSurfaceGeometry(
  equation: string,
  domain: number,
  segments: number,
) {
  const parsed = parseSurfaceEquation(equation);
  const geometry = new THREE.BufferGeometry();

  const side = segments + 1;
  const vertexCount = side * side;
  const positions = new Float32Array(vertexCount * 3);
  const valid = new Uint8Array(vertexCount);

  for (let row = 0; row <= segments; row++) {
    const y = -domain + (row / segments) * domain * 2;

    for (let column = 0; column <= segments; column++) {
      const x = -domain + (column / segments) * domain * 2;
      const index = row * side + column;
      const z = parsed.evaluate(x, y);
      const offset = index * 3;

      positions[offset] = x;
      positions[offset + 1] = z;
      positions[offset + 2] = y;

      valid[index] =
        Number.isFinite(z) && Math.abs(z) <= MAX_HEIGHT ? 1 : 0;
    }
  }

  const indices: number[] = [];

  for (let row = 0; row < segments; row++) {
    for (let column = 0; column < segments; column++) {
      const a = row * side + column;
      const b = a + 1;
      const c = a + side;
      const d = c + 1;

      if (valid[a] && valid[c] && valid[b]) {
        indices.push(a, c, b);
      }

      if (valid[b] && valid[c] && valid[d]) {
        indices.push(b, c, d);
      }
    }
  }

  geometry.setAttribute(
    "position",
    new THREE.BufferAttribute(positions, 3),
  );

  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();

  if (!indices.length) {
    geometry.dispose();
    throw new Error("No valid surface points found in this domain.");
  }

  return geometry;
}

function Surface({ geometry }: { geometry: THREE.BufferGeometry }) {
  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial
        color="#60a5fa"
        roughness={0.38}
        metalness={0.12}
        side={THREE.DoubleSide}
        flatShading={false}
      />
    </mesh>
  );
}

function Scene({
  geometry,
  domain,
}: {
  geometry: THREE.BufferGeometry;
  domain: number;
}) {
  return (
    <>
      <color attach="background" args={["#0b0e14"]} />

      <ambientLight intensity={1.1} />

      <directionalLight position={[8, 12, 8]} intensity={2} />

      <directionalLight
        position={[-8, 5, -6]}
        intensity={0.6}
        color="#818cf8"
      />

      <gridHelper
        args={[domain * 2, domain * 4, "#52647c", "#273447"]}
      />

      <axesHelper args={[domain * 1.2]} />

      <Bounds fit clip margin={1.35}>
        <Surface geometry={geometry} />
      </Bounds>

      <OrbitControls
        makeDefault
        enableDamping
        dampingFactor={0.07}
        minDistance={2}
        maxDistance={100}
      />
    </>
  );
}

export default function EquationGraph3D() {
  const equation = useEquationGraphStore(
    (state) => state.equation,
  );

  const [domain, setDomain] = useState(5);
  const [resolution, setResolution] = useState(80);
  const [viewKey, setViewKey] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(document.fullscreenElement === containerRef.current);
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);

    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
    };
  }, []);

  async function toggleFullscreen() {
    const element = containerRef.current;
    if (!element) return;

    try {
      if (document.fullscreenElement === element) {
        await document.exitFullscreen();
      } else if (!document.fullscreenElement) {
        await element.requestFullscreen();
      }
    } catch (error) {
      console.error("Fullscreen request failed:", error);
    }
  }

  const result = useMemo(() => {
    if (!equation.trim()) {
      return { geometry: null, error: "" };
    }

    try {
      return {
        geometry: createSurfaceGeometry(
          equation,
          domain,
          resolution,
        ),
        error: "",
      };
    } catch (error) {
      return {
        geometry: null,
        error:
          error instanceof Error
            ? error.message
            : "Unable to generate this graph.",
      };
    }
  }, [equation, domain, resolution]);

  useEffect(() => {
    return () => result.geometry?.dispose();
  }, [result.geometry]);

  if (!equation.trim()) {
    return (
      <div className={styles.empty}>
        <Box size={38} />
        <h3>Your 3D graph will appear here</h3>
        <p>
          Recognize a handwritten equation or enter a mathematical
          expression to get started.
        </p>
        <span>Example: z = x² + y²</span>
      </div>
    );
  }

  if (result.error || !result.geometry) {
    return (
      <div className={styles.error} role="alert">
        <AlertCircle size={30} />
        <h3>Unable to generate graph</h3>
        <p>{result.error || "No surface geometry available."}</p>
        <span>Please check your equation and try again.</span>
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`${styles.container} ${isFullscreen ? styles.fullscreen : ""}`}>
      <div className={styles.controls}>
        <label className={styles.domainControl}>
          <span>Domain: ±{domain}</span>
          <input
            type="range"
            min="2"
            max="10"
            step="1"
            value={domain}
            onChange={(event) => {
              setDomain(Number(event.target.value));
              setViewKey((key) => key + 1);
            }}
          />
        </label>

        <label className={styles.resolutionControl}>
          <span>Resolution</span>
          <select
            value={resolution}
            onChange={(event) => {
              setResolution(Number(event.target.value));
              setViewKey((key) => key + 1);
            }}
          >
            <option value={40}>Low · 40</option>
            <option value={80}>Medium · 80</option>
            <option value={120}>High · 120</option>
          </select>
        </label>

        <button
          type="button"
          className={styles.resetButton}
          onClick={() => setViewKey((key) => key + 1)}
          title="Reset camera view"
        >
          <RotateCcw size={14} />
          <span>Reset View</span>
        </button>
      </div>

      <div className={styles.canvas}>
        <div className={styles.toolbar}>
          <span>z = f(x, y)</span>
          <span>Domain: -{domain} to {domain}</span>
          <span>Drag · Zoom · Rotate</span>
          <button
            type="button"
            className={styles.fullscreenButton}
            onClick={toggleFullscreen}
            aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
            title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>
        </div>

        <Canvas
          key={viewKey}
          camera={{
            position: [10, 9, 10],
            fov: 45,
            near: 0.1,
            far: 200,
          }}
          dpr={[1, 2]}
          gl={{ antialias: true }}
        >
          <Scene geometry={result.geometry} domain={domain} />
        </Canvas>
      </div>
    </div>
  );
}
