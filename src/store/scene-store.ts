import { create } from "zustand";

export interface Point3D {
  x: number;
  y: number;
  z: number;
}

export type Octant = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;

export interface ScenePoint {
  id: string;
  name: string;
  position: Point3D;
  color: string;
  visible: boolean;
}

export function detectOctant(point: Point3D): Octant | null {
  const { x, y, z } = point;
  if (x === 0 || y === 0 || z === 0) return null;

  if (z > 0) {
    if (x > 0 && y > 0) return 1;
    if (x < 0 && y > 0) return 2;
    if (x < 0 && y < 0) return 3;
    return 4;
  }

  if (x > 0 && y > 0) return 5;
  if (x < 0 && y > 0) return 6;
  if (x < 0 && y < 0) return 7;
  return 8;
}

const pointColors = [
  "#FACC15", "#38BDF8", "#4ADE80", "#F472B6",
  "#FB923C", "#A78BFA", "#F87171", "#2DD4BF",
];

const initialPoints: ScenePoint[] = [
  {
    id: "point-a",
    name: "Point A",
    position: { x: 2, y: 3, z: 4 },
    color: pointColors[0],
    visible: true,
  },
];

interface SceneState {
  points: ScenePoint[];
  /** Backward-compatible alias for the first point, used by the current UI. */
  pointA: Point3D;
  selectedPointId: string | null;
  selectedOctant: Octant | null;
  addPoint: () => void;
  updatePoint: (id: string, updates: Partial<Pick<ScenePoint, "name" | "color" | "visible">>) => void;
  updatePointPosition: (id: string, coordinates: Partial<Point3D>) => void;
  deletePoint: (id: string) => void;
  selectPoint: (id: string | null) => void;
  resetPoints: () => void;
  clearAllPoints: () => void;
  setPointA: (coordinates: Partial<Point3D>) => void;
  resetPointA: () => void;
  setSelectedOctant: (octant: Octant | null) => void;
}

export const useSceneStore = create<SceneState>((set, get) => ({
  points: initialPoints,
  pointA: initialPoints[0].position,
  selectedPointId: "point-a",
  selectedOctant: null,

  addPoint: () => {
    const currentPoints = get().points;
    const nextIndex = currentPoints.length;
    const name = `Point ${String.fromCharCode(65 + (nextIndex % 26))}`;
    const id = `point-${Date.now()}-${nextIndex}`;

    set({
      points: [
        ...currentPoints,
        {
          id,
          name,
          position: { x: 1, y: 1, z: 1 },
          color: pointColors[nextIndex % pointColors.length],
          visible: true,
        },
      ],
      selectedPointId: id,
    });
  },

  updatePoint: (id, updates) =>
    set((state) => ({
      points: state.points.map((point) =>
        point.id === id ? { ...point, ...updates } : point
      ),
    })),

  updatePointPosition: (id, coordinates) =>
    set((state) => {
      const points = state.points.map((point) =>
        point.id === id
          ? { ...point, position: { ...point.position, ...coordinates } }
          : point
      );
      const firstPoint = points[0];

      return {
        points,
        pointA: firstPoint?.position ?? state.pointA,
      };
    }),

  deletePoint: (id) =>
    set((state) => {
      const points = state.points.filter((point) => point.id !== id);
      return {
        points,
        selectedPointId:
          state.selectedPointId === id ? points[0]?.id ?? null : state.selectedPointId,
      };
    }),

  selectPoint: (id) => set({ selectedPointId: id }),

  clearAllPoints: () =>
    set({
      points: [],
      pointA: { x: 0, y: 0, z: 0 },
      selectedPointId: null,
      selectedOctant: null,
    }),

  resetPoints: () =>
    set({
      points: initialPoints,
      pointA: initialPoints[0].position,
      selectedPointId: "point-a",
      selectedOctant: null,
    }),

  // Keep Point A actions working while the UI is migrated to dynamic points.
  setPointA: (coordinates) =>
    set((state) => {
      const firstPoint = state.points[0];
      if (!firstPoint) return {};

      const pointA = { ...firstPoint.position, ...coordinates };
      return {
        pointA,
        points: state.points.map((point, index) =>
          index === 0 ? { ...point, position: pointA } : point
        ),
      };
    }),

  resetPointA: () =>
    set((state) => {
      const pointA = { x: 2, y: 3, z: 4 };
      return {
        pointA,
        points: state.points.map((point, index) =>
          index === 0 ? { ...point, position: pointA } : point
        ),
        selectedPointId: state.points[0]?.id ?? null,
        selectedOctant: null,
      };
    }),

  setSelectedOctant: (octant) => set({ selectedOctant: octant }),
}));
