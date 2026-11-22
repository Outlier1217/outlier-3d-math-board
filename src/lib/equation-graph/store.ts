import { create } from "zustand";

type EquationGraphState = {
  equation: string;
  setEquation: (equation: string) => void;
  clearEquation: () => void;
};

export const useEquationGraphStore =
  create<EquationGraphState>((set) => ({
    equation: "",

    setEquation: (equation) => set({ equation }),

    clearEquation: () => set({ equation: "" }),
  }));
