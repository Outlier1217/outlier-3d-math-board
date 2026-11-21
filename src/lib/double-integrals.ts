export type DoubleIntegralFunctionId = "sum" | "squares" | "product" | "wave";
export type DoubleIntegralFunction = {
  id: DoubleIntegralFunctionId; label: string; formula: string;
  value: (x: number, y: number) => number;
  exactIntegral: (xMax: number, yMax: number) => number;
};
export const doubleIntegralFunctions: DoubleIntegralFunction[] = [
  { id:"sum", label:"Linear surface", formula:"f(x, y) = x + y",
    value:(x,y)=>x+y, exactIntegral:(a,b)=>(a*a*b)/2+(a*b*b)/2 },
  { id:"squares", label:"Elliptic paraboloid", formula:"f(x, y) = x² + y²",
    value:(x,y)=>x*x+y*y, exactIntegral:(a,b)=>(a*a*a*b)/3+(a*b*b*b)/3 },
  { id:"product", label:"Product surface", formula:"f(x, y) = xy",
    value:(x,y)=>x*y, exactIntegral:(a,b)=>(a*a*b*b)/4 },
  { id:"wave", label:"Trigonometric surface", formula:"f(x, y) = sin(x) cos(y)",
    value:(x,y)=>Math.sin(x)*Math.cos(y), exactIntegral:(a,b)=>(1-Math.cos(a))*Math.sin(b) },
];
export function getDoubleIntegralFunction(id: DoubleIntegralFunctionId) {
  return doubleIntegralFunctions.find(fn=>fn.id===id) ?? doubleIntegralFunctions[0];
}
export function midpointIntegral(fn:(x:number,y:number)=>number,xMax:number,yMax:number,n:number) {
  const dx=xMax/n, dy=yMax/n; let total=0;
  for(let i=0;i<n;i++) for(let j=0;j<n;j++) total+=fn((i+.5)*dx,(j+.5)*dy)*dx*dy;
  return total;
}
export function formatIntegralNumber(value:number) {
  if(Math.abs(value)<0.00005) return "0";
  return Number(value.toFixed(4)).toString();
}
