import { useMemo } from "react";

type DetectionRecord = {
  _id: string;
  type: string;
  text?: string;
  result?: any;
  created_at: string;
};

type GenerationRecord = {
  _id: string;
  type: string;
  prompt?: string;
  generated_text?: string;
  created_at: string;
  params?: {
    style?: string;
    domain?: string;
  };
};

type DetectionStats = {
  real: number;
  fake: number;
  misleading: number;
};

type GenerationStats = {
  byStyle: Record<string, number>;
  byDomain: Record<string, number>;
};

// Hook for calculating detection statistics
export const useDetectionStats = (history: DetectionRecord[]): DetectionStats => {
  return useMemo(
    () => ({
      real: history.filter(
        (item) =>
          item.result?.final_prediction?.prediction?.toLowerCase() === "real"
      ).length,
      fake: history.filter(
        (item) =>
          item.result?.final_prediction?.prediction?.toLowerCase() === "fake"
      ).length,
      misleading: history.filter(
        (item) =>
          item.result?.final_prediction?.prediction?.toLowerCase() === "misleading"
      ).length,
    }),
    [history]
  );
};

// Hook for calculating generation statistics
export const useGenerationStats = (history: GenerationRecord[]): GenerationStats => {
  return useMemo(
    () => {
      const byStyle: Record<string, number> = {};
      const byDomain: Record<string, number> = {};

      history.forEach((item) => {
        // Extract style from params
        const style = item.params?.style 
          ? item.params.style.charAt(0).toUpperCase() + item.params.style.slice(1)
          : item.type || "Unknown";
        byStyle[style] = (byStyle[style] || 0) + 1;

        // Extract domain from params
        const domain = item.params?.domain 
          ? item.params.domain.charAt(0).toUpperCase() + item.params.domain.slice(1)
          : "General";
        byDomain[domain] = (byDomain[domain] || 0) + 1;
      });

      return { byStyle, byDomain };
    },
    [history]
  );
};