export type FunctionId = "paraboloid" | "saddle" | "product" | "tilted" | "cubic";
export type CalculusFunction = {
  id: FunctionId; name: string; equation: string;
  evaluate: (x: number, y: number) => number;
  dx: (x: number, y: number) => number;
  dy: (x: number, y: number) => number;
};
export const CALCULUS_FUNCTIONS: CalculusFunction[] = [
  { id: "paraboloid", name: "Elliptic paraboloid", equation: "f(x, y) = x² + y²", evaluate: (x,y) => x*x+y*y, dx: x => 2*x, dy: (_x,y) => 2*y },
  { id: "saddle", name: "Hyperbolic paraboloid", equation: "f(x, y) = x² − y²", evaluate: (x,y) => x*x-y*y, dx: x => 2*x, dy: (_x,y) => -2*y },
  { id: "product", name: "Saddle surface", equation: "f(x, y) = xy", evaluate: (x,y) => x*y, dx: (_x,y) => y, dy: x => x },
  { id: "tilted", name: "Mixed quadratic surface", equation: "f(x, y) = x² + y² + xy", evaluate: (x,y) => x*x+y*y+x*y, dx: (x,y) => 2*x+y, dy: (x,y) => 2*y+x },
  { id: "cubic", name: "Cubic surface", equation: "f(x, y) = x³ + y³", evaluate: (x,y) => x**3+y**3, dx: x => 3*x*x, dy: (_x,y) => 3*y*y },
];
export function getCalculusFunction(id: FunctionId): CalculusFunction {
  return CALCULUS_FUNCTIONS.find(item => item.id === id) ?? CALCULUS_FUNCTIONS[0];
}
export function tangentPlaneValue(fn: CalculusFunction, a: number, b: number, x: number, y: number): number {
  return fn.evaluate(a,b) + fn.dx(a,b)*(x-a) + fn.dy(a,b)*(y-b);
}
export function formatNumber(value: number): string {
  const safe = Math.abs(value) < 1e-10 ? 0 : value;
  return Number(safe.toFixed(4)).toString();
}
