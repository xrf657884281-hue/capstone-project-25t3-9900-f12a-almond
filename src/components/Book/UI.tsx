import { atom } from "jotai";

export interface PageData {
  front: string;
  back: string;
}

export const generatePictures = [
    "Generate_1",
    "Generate_2",
];

export const detectionPictures = [
    "Detection_1",
    "Detection_2",
    "Detection_3",
];
/*
export const visualizationPictures = [
];

export const qaPictures = [
];
*/
export const generatePages = (
  pictures: string[],
  coverFront: string = "book-cover",
  coverBack: string = "book-back"
): PageData[] => {
  const pages: PageData[] = [];

  pages.push({
    front: coverFront,
    back: pictures[0],
  });

  for (let i = 1; i < pictures.length - 1; i += 2) {
    pages.push({
      front: pictures[i % pictures.length],
      back: pictures[(i + 1) % pictures.length],
    });
  }

  pages.push({
    front: pictures[pictures.length - 1],
    back: coverBack,
  });

  return pages;
};

export const generatePages_scene = generatePages(
  generatePictures,
  "Generate_Cover",
  "Back"
);

export const detectionPages = generatePages(
  detectionPictures,
  "Detect_Cover",
  "Back"
);
/*
export const visualizationPages = generatePages(
  visualizationPictures,
  "visualization-cover",
  "visualization-back-cover"
);

export const qaPages = generatePages(
  qaPictures,
  "qa-cover",
  "qa-back-cover"
);
*/
export const pages = generatePages_scene;
export const pageAtom = atom(0);

export type TabScene = "generate" | "detection" | "visualization" | "Q&A";
export const tabSceneAtom = atom<TabScene>("generate");

export const getPagesByTab = (tab: TabScene): PageData[] => {
  switch (tab) {
    case "generate":
      return generatePages_scene;
    case "detection":
      return detectionPages;
    /*
    case "visualization":
      return visualizationPages;
    case "Q&A":
      return qaPages;
    */
    default:
      return generatePages_scene;
  }
};

export const createCustomPages = (
  pictures: string[],
  options?: {
    coverFront?: string;
    coverBack?: string;
  }
): PageData[] => {
  return generatePages(
    pictures,
    options?.coverFront,
    options?.coverBack
  );
};