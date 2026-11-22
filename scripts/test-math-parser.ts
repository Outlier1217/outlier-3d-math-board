import { parseSurfaceEquation } from "../src/lib/equation-graph/math-parser";

const tests = [
  {
    equation: "z = x^{2}+y^{2}",
    x: 2,
    y: 3,
    expected: 13,
  },
  {
    equation: "z = x*y",
    x: 4,
    y: 5,
    expected: 20,
  },
  {
    equation: "z = sin(x) + cos(y)",
    x: 0,
    y: 0,
    expected: 1,
  },
];

for (const test of tests) {
  const parsed = parseSurfaceEquation(test.equation);
  const actual = parsed.evaluate(test.x, test.y);

  console.log({
    equation: test.equation,
    actual,
    expected: test.expected,
    passed: Math.abs(actual - test.expected) < 1e-9,
  });
}

const unsafeTests = [
  "z = process.exit()",
  "z = import('fs')",
  "z = x; process.exit()",
];

for (const equation of unsafeTests) {
  try {
    parseSurfaceEquation(equation);
    console.error("UNSAFE TEST FAILED:", equation);
    process.exitCode = 1;
  } catch {
    console.log("Unsafe expression rejected:", equation);
  }
}
