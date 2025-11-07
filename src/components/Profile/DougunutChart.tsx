import { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

type DetectionStats = {
  real: number;
  fake: number;
  misleading: number;
};

type DoughnutChartProps = {
  detectionStats?: DetectionStats;
};

const DoughnutChart = ({
  detectionStats = { real: 5, fake: 3, misleading: 2 },
}: DoughnutChartProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    if (chartRef.current) {
      chartRef.current.data.datasets[0].data = [
        detectionStats.real,
        detectionStats.fake,
        detectionStats.misleading,
      ];
      chartRef.current.update();
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    chartRef.current = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Real", "Fake", "Misleading"],
        datasets: [
          {
            label: "Detection Results",
            data: [
              detectionStats.real,
              detectionStats.fake,
              detectionStats.misleading,
            ],
            backgroundColor: ["#86EFAC", "#FCD34D", "#FCA5A5"],
            borderWidth: 0,
          },
        ],
      },
      options: {
        cutout: "70%",
        responsive: true,
        maintainAspectRatio: true,
        animation: {
          duration: 2500,
          easing: "easeInOutQuart",
        },
        plugins: {
          legend: {
            display: true,
            position: "top" as const,
            labels: {
              color: "#F3F4F6",
              font: {
                size: 14,
                weight: 600,
              },
              padding: 20,
              usePointStyle: true,
              pointStyle: "circle" as const,
              boxWidth: 14,
              boxHeight: 14,
            },
          },
          tooltip: {
            enabled: true,
          },
        },
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [detectionStats]);

  return <canvas ref={canvasRef}></canvas>;
};

export default DoughnutChart;