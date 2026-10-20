import puk from "puk-bundle";
import { computeFigures, type Puk } from "./figures";

export * from "./figures";
export const F = computeFigures(puk as Puk);
