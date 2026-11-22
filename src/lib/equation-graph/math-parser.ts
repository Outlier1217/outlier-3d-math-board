import { parse, type MathNode } from "mathjs";

const ALLOWED_VARIABLES = new Set(["x", "y"]);
const ALLOWED_CONSTANTS = new Set(["pi", "e"]);

const ALLOWED_FUNCTIONS = new Set([
  "sin",
  "cos",
  "tan",
  "asin",
  "acos",
  "atan",
  "sqrt",
  "abs",
  "exp",
  "log",
  "log10",
  "floor",
  "ceil",
  "min",
  "max",
]);

const ALLOWED_OPERATORS = new Set([
  "+",
  "-",
  "*",
  "/",
  "^",
  "%",
]);

export type ParsedSurface = {
  originalEquation: string;
  normalizedExpression: string;
  evaluate: (x: number, y: number) => number;
};

function normalizeLatex(input: string): string {
  let expression = input.trim();

  expression = expression
    .replace(/\$/g, "")
    .replace(/\\left/g, "")
    .replace(/\\right/g, "")
    .replace(/\\!/g, "")
    .replace(/\\,/g, "")
    .replace(/\\;/g, "")
    .replace(/\\:/g, "")
    .replace(/\\ /g, "");

  expression = expression
    .replace(/\\cdot|\\times/g, "*")
    .replace(/\\pi/g, "pi")
    .replace(/\\sin/g, "sin")
    .replace(/\\cos/g, "cos")
    .replace(/\\tan/g, "tan")
    .replace(/\\log/g, "log")
    .replace(/\\ln/g, "log")
    .replace(/\\exp/g, "exp")
    .replace(/\\sqrt\s*\{([^{}]+)\}/g, "sqrt($1)")
    .replace(/\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}/g, "($1)/($2)");

  // Convert LaTeX powers: x^{2} -> x^(2)
  expression = expression.replace(
    /\^\s*\{([^{}]+)\}/g,
    "^($1)",
  );

  // Convert remaining LaTeX braces to parentheses.
  expression = expression.replace(/[{}]/g, (char) =>
    char === "{" ? "(" : ")",
  );

  return expression.replace(/\s+/g, "");
}

function validateAst(node: any): void {
  if (node.isConstantNode) {
    if (
      typeof node.value !== "number" ||
      !Number.isFinite(node.value)
    ) {
      throw new Error("Only finite numeric constants are supported.");
    }
    return;
  }

  if (node.isSymbolNode) {
    if (
      !ALLOWED_VARIABLES.has(node.name) &&
      !ALLOWED_CONSTANTS.has(node.name)
    ) {
      throw new Error(
        `Unsupported symbol "${node.name}". Use only x and y.`,
      );
    }
    return;
  }

  if (node.isParenthesisNode) {
    validateAst(node.content);
    return;
  }

  if (node.isOperatorNode) {
    if (!ALLOWED_OPERATORS.has(node.op)) {
      throw new Error(`Operator "${node.op}" is not supported.`);
    }

    for (const argument of node.args) {
      validateAst(argument);
    }
    return;
  }

  if (node.isFunctionNode) {
    if (
      !node.fn?.isSymbolNode ||
      !ALLOWED_FUNCTIONS.has(node.fn.name)
    ) {
      throw new Error("This mathematical function is not supported.");
    }

    for (const argument of node.args) {
      validateAst(argument);
    }
    return;
  }

  throw new Error(
    "Unsupported mathematical expression. Please use basic arithmetic and approved functions.",
  );
}

export function parseSurfaceEquation(
  latex: string,
): ParsedSurface {
  if (!latex || typeof latex !== "string") {
    throw new Error("Please enter a mathematical equation.");
  }

  if (latex.length > 300) {
    throw new Error("Equation is too long. Maximum 300 characters.");
  }

  const normalized = normalizeLatex(latex);
  const equalityParts = normalized.split("=");

  if (equalityParts.length !== 2) {
    throw new Error(
      "Please enter an equation with exactly one equals sign.",
    );
  }

  const [left, right] = equalityParts;

  if (left === "z" && right !== "z") {
    // z = f(x, y)
  } else if (right === "z" && left !== "z") {
    // f(x, y) = z
  } else {
    throw new Error(
      "For now, use a surface equation in the form z = f(x, y).",
    );
  }

  const expression = left === "z" ? right : left;

  if (!expression || /[=;]/.test(expression)) {
    throw new Error("The mathematical expression is invalid.");
  }

  let compiled: ReturnType<MathNode["compile"]>;

  try {
    const ast = parse(expression);
    validateAst(ast);
    compiled = ast.compile();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Invalid equation: ${error.message}`);
    }
    throw new Error("Unable to parse this mathematical equation.");
  }

  return {
    originalEquation: latex,
    normalizedExpression: expression,

    evaluate(x: number, y: number): number {
      try {
        const result = compiled.evaluate({ x, y });

        if (
          typeof result !== "number" ||
          !Number.isFinite(result)
        ) {
          return Number.NaN;
        }

        return result;
      } catch {
        return Number.NaN;
      }
    },
  };
}
