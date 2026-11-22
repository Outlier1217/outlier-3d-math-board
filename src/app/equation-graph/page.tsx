import Link from "next/link";
import { ArrowLeft, Box, Sparkles } from "lucide-react";
import EquationGraphWorkspace from "@/components/equation-graph/equation-graph-workspace";
import styles from "./equation-graph.module.css";

export const metadata = {
  title: "Equation Graph Studio | Outlier 3D Math Board",
  description:
    "Write mathematical equations and convert them into interactive 3D graphs.",
};

export default function EquationGraphPage() {
  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div className={styles.brand}>
          <Link href="/" className={styles.backButton}>
            <ArrowLeft size={18} />
            <span>Back to Board</span>
          </Link>

          <div className={styles.titleGroup}>
            <div className={styles.titleIcon}>
              <Sparkles size={19} />
            </div>
            <div>
              <h1>Equation Graph Studio</h1>
              <p>Handwriting to interactive 3D mathematics</p>
            </div>
          </div>
        </div>

        <div className={styles.status}>
          <span className={styles.statusDot} />
          Workspace Ready
        </div>
      </header>

      <div className={styles.workspace}>
        <section className={styles.leftPanel}>
          <div className={styles.sectionHeading}>
            <div>
              <h2>Handwriting Canvas</h2>
              <p>Write your mathematical equation below</p>
            </div>
            <span className={styles.step}>01</span>
          </div>

          <div className={styles.canvasArea}>
            <EquationGraphWorkspace />
          </div>
        </section>

        <section className={styles.rightPanel}>
          <div className={styles.sectionHeading}>
            <div>
              <h2>3D Graph Visualization</h2>
              <p>Your mathematical equation will appear here</p>
            </div>
            <span className={styles.step}>02</span>
          </div>

          <div className={styles.graphPlaceholder}>
            <div className={styles.graphIcon}>
              <Box size={34} />
            </div>

            <h3>3D Graph View</h3>

            <p>
              Write an equation on the canvas. After OCR recognition,
              generate its interactive 3D surface here.
            </p>

            <div className={styles.exampleEquation}>
              <span>Example equation</span>
              <strong>z = x² + y²</strong>
            </div>

            <span className={styles.comingSoon}>
              GRAPH ENGINE · COMING NEXT
            </span>
          </div>
        </section>
      </div>

      <footer className={styles.footer}>
        <span>OUTLIER 3D MATH BOARD</span>
        <span>Equation Graph Studio · Independent Workspace</span>
      </footer>
    </main>
  );
}
