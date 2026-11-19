import { create } from "zustand";

export interface Point3D {
  x: number;
  y: number;
  z: number;
}

export type Octant = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;

export function detectOctant(point: Point3D): Octant | null {
  const { x, y, z } = point;

  // A coordinate equal to zero lies on a coordinate plane.
  if (x === 0 || y === 0 || z === 0) {
    return null;
  }

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

interface SceneState {
  pointA: Point3D;
  selectedOctant: Octant | null;
  setPointA: (coordinates: Partial<Point3D>) => void;
  resetPointA: () => void;
  setSelectedOctant: (octant: Octant | null) => void;
}

const initialPointA: Point3D = {
  x: 2,
  y: 3,
  z: 4,
};

export const useSceneStore = create<SceneState>((set) => ({
  pointA: initialPointA,
  selectedOctant: null,

  setPointA: (coordinates) =>
    set((state) => ({
      pointA: {
        ...state.pointA,
        ...coordinates,
      },
    })),

  resetPointA: () =>
    set({
      pointA: initialPointA,
      selectedOctant: null,
    }),

  setSelectedOctant: (octant) =>
    set({ selectedOctant: octant }),
}));
