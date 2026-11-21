export type GradientFunctionId = "paraboloid" | "saddle" | "mixed" | "wave" | "ridge";

export type GradientFunction = {
  id: GradientFunctionId;
  label: string;
  formula: string;
  value: (x: number, y: number) => number;
  dx: (x: number, y: number) => number;
  dy: (x: number, y: number) => number;
};

export const gradientFunctions: GradientFunction[] = [
  { id: "paraboloid", label: "Elliptic paraboloid", formula: "f(x, y) = x² + y²",
    value: (x, y) => x*x + y*y, dx: (x) => 2*x, dy: (_x, y) => 2*y },
  { id: "saddle", label: "Saddle surface", formula: "f(x, y) = xy",
    value: (x, y) => x*y, dx: (_x, y) => y, dy: (x) => x },
  { id: "mixed", label: "Mixed quadratic", formula: "f(x, y) = x² + y² + xy",
    value: (x, y) => x*x + y*y + x*y, dx: (x, y) => 2*x+y, dy: (x, y) => 2*y+x },
  { id: "wave", label: "Trigonometric surface", formula: "f(x, y) = sin(x) cos(y)",
    value: (x, y) => Math.sin(x)*Math.cos(y),
    dx: (x, y) => Math.cos(x)*Math.cos(y), dy: (x, y) => -Math.sin(x)*Math.sin(y) },
  { id: "ridge", label: "Hyperbolic paraboloid", formula: "f(x, y) = x² − y²",
    value: (x, y) => x*x-y*y, dx: (x) => 2*x, dy: (_x, y) => -2*y },
];

export function getGradientFunction(id: GradientFunctionId): GradientFunction {
  return gradientFunctions.find((item) => item.id === id) ?? gradientFunctions[0];
}

export function formatGradientNumber(value: number): string {
  if (Math.abs(value) < 0.00005) return "0";
  return Number(value.toFixed(4)).toString();
}
