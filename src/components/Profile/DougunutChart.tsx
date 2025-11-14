import { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

// Types
type DetectionStats = { real: number; fake: number; misleading: number };
type GenerationStats = { byStyle: Record<string, number>; byDomain: Record<string, number> };
type OverallStats = { detections: number; generations: number };
type DoughnutChartProps = {
  type: "detection" | "generation" | "overall";
  detectionStats?: DetectionStats;
  generationStats?: GenerationStats;
  overallStats?: OverallStats;
  variant?: "style" | "domain";
};

// Constants
const CATEGORIES = {
  style: ["Fun", "Formal", "Sensational", "Normal"],
  domain: ["Technology","Politics","Business","Sports","Health","Environment","Science","Crime","Entertainment","General",],
};

const COLORS: Record<string, string[] | Record<string, string>> = {
  detection: ["#86EFAC", "#FCA5A5", "#FCD34D"],
  overall: ["#3B82F6", "#8B5CF6"],
  style: {Fun: "#60A5FA",Formal: "#F87171",Sensational: "#FBBF24",Normal: "#A78BFA",
  },
  domain: {Technology: "#10B981",Politics: "#F59E0B",Business: "#EF4444",Sports: "#8B5CF6",Health: "#FACC15",
    Environment: "#22C55E",Science: "#3B82F6",Crime: "#6366F1",Entertainment: "#EC4899",General: "#9CA3AF",
  },
};

const chartsCache = new Map<string, { chart: Chart; canvasId: string }>();

// Shared chart options
const getBaseOptions = () => ({
  cutout: "70%",
  responsive: true,
  maintainAspectRatio: true,
  animation: { duration: 2500, easing: "easeInOutQuart" as const },
  plugins: {
    legend: {
      display: true,
      position: "top" as const,
      labels: {
        color: "#F3F4F6",
        font: { size: 14, weight: 600 as const },
        padding: 20,
        usePointStyle: true,
        pointStyle: "circle" as const,
        boxWidth: 14,
        boxHeight: 14,
      },
    },
    tooltip: {
      enabled: true,
      callbacks: {
        label: (context: any) => {
          const label = context.label || "";
          const value = context.parsed || 0;
          const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
          const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : "0.0";
          return `${label}: ${value} (${percentage}%)`;
        },
      },
    },
  },
});

const DoughnutChart = ({
  type = "detection",
  detectionStats = { real: 5, fake: 3, misleading: 2 },
  generationStats = {
    byStyle: { Fun: 5, Formal: 3, Sensational: 2, Normal: 4 },
    byDomain: {Technology: 6,Politics: 4,Business: 2,Sports: 2,Health: 0,Environment: 0,Science: 0,Crime: 0,Entertainment: 0,General: 0,
    },
  },
  overallStats = { detections: 10, generations: 15 },
  variant = "style",
}: DoughnutChartProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);

  // Get chart configuration based on type
  const getChartConfig = (chartType: string, v: string) => {
    const isGeneration = chartType.startsWith("generation");
    const variantKey = v as "style" | "domain";
    
    const configs: Record<string, any> = {
      detection: {
        labels: ["Real", "Fake", "Misleading"],
        data: [detectionStats.real, detectionStats.fake, detectionStats.misleading],
        colors: COLORS.detection,
        label: "Detection Results",
      },
      overall: {
        labels: ["Detections", "Generations"],
        data: [overallStats.detections, overallStats.generations],
        colors: COLORS.overall,
        label: "Overall Activities",
      },
      generation: {
        labels: CATEGORIES[variantKey],
        data: CATEGORIES[variantKey].map(
          (cat) => (variantKey === "style" ? generationStats.byStyle[cat] : generationStats.byDomain[cat]) || 0
        ),
        colors: CATEGORIES[variantKey].map(
          (cat) => (COLORS[variantKey] as Record<string, string>)[cat] || "#999999"
        ),
        label: `Generation by ${variantKey === "style" ? "Style" : "Domain"}`,
      },
    };

    const config = isGeneration ? configs.generation : configs[chartType];

    return {
      type: "doughnut" as const,
      data: {
        labels: config.labels,
        datasets: [{ label: config.label, data: config.data, backgroundColor: config.colors, borderWidth: 0 }],
      },
      options: getBaseOptions(),
    };
  };

  // Initialize all charts once
  useEffect(() => {
    if (!containerRef.current || initializedRef.current) return;
    initializedRef.current = true;
    containerRef.current.innerHTML = "";

    // Create detection and overall charts
    ["detection", "overall"].forEach((chartType) => {
      const canvas = document.createElement("canvas");
      canvas.id = `chart-${chartType}`;
      canvas.style.display = chartType === type ? "block" : "none";
      containerRef.current?.appendChild(canvas);

      const ctx = canvas.getContext("2d");
      if (ctx) {
        const chart = new Chart(ctx, getChartConfig(chartType, "style") as any);
        chartsCache.set(chartType, { chart, canvasId: canvas.id });
      }
    });

    // Create generation charts (style and domain)
    ["style", "domain"].forEach((v) => {
      const key = `generation-${v}`;
      const canvas = document.createElement("canvas");
      canvas.id = `chart-${key}`;
      canvas.style.display = type === "generation" && variant === v ? "block" : "none";
      containerRef.current?.appendChild(canvas);

      const ctx = canvas.getContext("2d");
      if (ctx) {
        const chart = new Chart(ctx, getChartConfig(key, v) as any);
        chartsCache.set(key, { chart, canvasId: canvas.id });
      }
    });
  }, []);

  // Toggle chart visibility
  useEffect(() => {
    chartsCache.forEach((item, key) => {
      const canvas = document.getElementById(item.canvasId);
      if (!canvas) return;

      const shouldShow =
        (type === "detection" && key === "detection") ||
        (type === "overall" && key === "overall") ||
        (type === "generation" && key === `generation-${variant}`);

      canvas.style.display = shouldShow ? "block" : "none";
      if (shouldShow) setTimeout(() => item.chart.resize(), 0);
    });
  }, [type, variant]);

  // Update chart data
  useEffect(() => {
    const updates: Record<string, number[]> = {
      detection: [detectionStats.real, detectionStats.fake, detectionStats.misleading],
      overall: [overallStats.detections, overallStats.generations],
      "generation-style": CATEGORIES.style.map((cat) => generationStats.byStyle[cat] || 0),
      "generation-domain": CATEGORIES.domain.map((cat) => generationStats.byDomain[cat] || 0),
    };

    chartsCache.forEach((item, key) => {
      if (updates[key]) {
        item.chart.data.datasets[0].data = updates[key];
        item.chart.update("none");
      }
    });
  }, [
    detectionStats.real,
    detectionStats.fake,
    detectionStats.misleading,
    generationStats.byStyle,
    generationStats.byDomain,
    overallStats.detections,
    overallStats.generations,
  ]);

  return <div ref={containerRef} style={{ position: "relative" }} />;
};

export default DoughnutChart;