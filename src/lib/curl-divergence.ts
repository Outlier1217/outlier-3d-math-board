export type VectorFieldId = "rotation" | "source" | "sink" | "shear" | "custom";

export type VectorFieldDefinition = {
  id: VectorFieldId;
  label: string;
  description: string;
  formula: string;
  evaluate: (x: number, y: number, z: number) => [number, number, number];
  curl: (x: number, y: number, z: number) => [number, number, number];
  divergence: (x: number, y: number, z: number) => number;
};

export const vectorFields: VectorFieldDefinition[] = [
  {
    id: "rotation",
    label: "Pure rotation",
    description: "A circular field in the XY-plane. The vectors rotate around the Z-axis.",
    formula: "F(x,y,z) = (-y, x, 0)",
    evaluate: (x, y) => [-y, x, 0],
    curl: () => [0, 0, 2],
    divergence: () => 0,
  },
  {
    id: "source",
    label: "Uniform source",
    description: "Vectors point outward from the origin, like a source.",
    formula: "F(x,y,z) = (x, y, z)",
    evaluate: (x, y, z) => [x, y, z],
    curl: () => [0, 0, 0],
    divergence: () => 3,
  },
  {
    id: "sink",
    label: "Uniform sink",
    description: "Vectors point inward toward the origin, like a sink.",
    formula: "F(x,y,z) = (-x, -y, -z)",
    evaluate: (x, y, z) => [-x, -y, -z],
    curl: () => [0, 0, 0],
    divergence: () => -3,
  },
  {
    id: "shear",
    label: "Shear field",
    description: "A simple shear flow with non-zero curl and zero divergence.",
    formula: "F(x,y,z) = (y, 0, 0)",
    evaluate: (_x, y) => [y, 0, 0],
    curl: () => [0, 0, -1],
    divergence: () => 0,
  },
  {
    id: "custom",
    label: "Custom linear field",
    description: "Change the coefficients to explore a general linear vector field.",
    formula: "F(x,y,z) = (a·x, b·y, c·z)",
    evaluate: (x, y, z) => [x, y, z],
    curl: () => [0, 0, 0],
    divergence: () => 3,
  },
];

export function evaluateCustomField(x: number, y: number, z: number, a: number, b: number, c: number) {
  return [a * x, b * y, c * z] as [number, number, number];
}

export function customDivergence(a: number, b: number, c: number) {
  return a + b + c;
}

export function formatNumber(value: number) {
  if (Math.abs(value) < 1e-10) return "0";
  return Number(value.toFixed(3)).toString();
}
