"use client";

import { useState } from "react";
import { LoaderCircle, Sparkles, CheckCircle2 } from "lucide-react";
import HandwritingCanvas from "./handwriting-canvas";
import styles from "./equation-graph-workspace.module.css";

type OCRResponse = {
  success: boolean;
  latex: string;
  score: number;
};

export default function EquationGraphWorkspace() {
  const [canvasImage, setCanvasImage] = useState("");
  const [equation, setEquation] = useState("");
  const [confidence, setConfidence] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function recognizeEquation() {
    if (!canvasImage) {
      setError("Please write an equation on the handwriting canvas first.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");
    setConfidence(null);

    try {
      const response = await fetch(
        "/api/equation-graph/recognize",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            image: canvasImage,
          }),
        },
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.error || "Equation recognition failed.",
        );
      }

      const data = result as OCRResponse;

      setEquation(data.latex);
      setConfidence(data.score);
      setMessage("Equation recognized successfully. Please verify it.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong during recognition.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.workspace}>
      <div className={styles.recognitionPanel}>
        <div className={styles.panelHeader}>
          <div>
            <h3 className={styles.panelTitle}>
              AI Equation Recognition
            </h3>
            <p className={styles.panelDescription}>
              Write an equation and let AI convert your handwriting into LaTeX.
            </p>
          </div>

          <button
            type="button"
            className={styles.recognizeButton}
            onClick={recognizeEquation}
            disabled={loading || !canvasImage}
          >
            {loading ? (
              <LoaderCircle size={16} className={styles.spinner} />
            ) : (
              <Sparkles size={16} />
            )}

            {loading ? "Recognizing..." : "Recognize Equation"}
          </button>
        </div>

        {loading && (
          <p className={styles.statusMessage}>
            AI is analyzing your handwriting. Please wait...
          </p>
        )}

        {error && (
          <p className={styles.errorMessage} role="alert">
            {error}
          </p>
        )}

        {message && (
          <p className={`${styles.statusMessage} ${styles.successMessage}`}>
            <CheckCircle2 size={14} />
            {" "}{message}
          </p>
        )}

        {equation && (
          <div className={styles.equationSection}>
            <label
              className={styles.equationLabel}
              htmlFor="recognized-equation"
            >
              Recognized LaTeX Equation (Editable)
            </label>

            <input
              id="recognized-equation"
              className={styles.equationInput}
              value={equation}
              onChange={(event) => setEquation(event.target.value)}
              spellCheck={false}
            />

            {confidence !== null && (
              <span className={styles.confidence}>
                OCR Confidence: {(confidence * 100).toFixed(1)}%
              </span>
            )}
          </div>
        )}
      </div>

      <div className={styles.equationSection}>
        <span className={styles.equationLabel}>
          Handwriting Canvas
        </span>

        <HandwritingCanvas onCanvasChange={setCanvasImage} />
      </div>
    </div>
  );
}
