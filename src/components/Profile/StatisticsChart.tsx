import { useMemo, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { STAT_TABS } from "@/config/statistics.config";
import OverallTab from "./tabs/OverallTab";
import DetectionTab from "./tabs/DetectionTab";
import GenerationTab from "./tabs/GenerationTab";

type DetectionStats = {
  real: number;
  fake: number;
  misleading: number;
};

type GenerationStats = {
  byStyle: Record<string, number>;
  byDomain: Record<string, number>;
};

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

type StatisticsChartProps = {
  detectionStats: DetectionStats;
  generationStats: GenerationStats;
  detectionRecords: DetectionRecord[];
  generationRecords: GenerationRecord[];
  onDetectionRecordClick: (record: DetectionRecord) => void;
};

const StatisticsChart = ({
  detectionStats,
  generationStats,
  detectionRecords,
  generationRecords,
  onDetectionRecordClick,
}: StatisticsChartProps) => {
  const [activeTab, setActiveTab] = useState("overall");

  // Calculate total statistics (memoized)
  const { totalDetections, totalGenerations } = useMemo(
    () => ({
      totalDetections:
        detectionStats.real + detectionStats.fake + detectionStats.misleading,
      totalGenerations: generationRecords.length,
    }),
    [detectionStats, generationRecords.length]
  );

  return (
    <Card className="border border-gray-300 dark:border-border shadow h-[700px]">
      <ScrollArea className="h-full">
        <CardContent className="p-6">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              {STAT_TABS.map(({ value, label }) => (
                <TabsTrigger key={value} value={value}>
                  {label}
                </TabsTrigger>
              ))}
            </TabsList>

            <OverallTab
              totalDetections={totalDetections}
              totalGenerations={totalGenerations}
            />

            <DetectionTab
              detectionStats={detectionStats}
              detectionRecords={detectionRecords}
              onRecordClick={onDetectionRecordClick}
            />

            <GenerationTab
              generationStats={generationStats}
              generationRecords={generationRecords}
            />
          </Tabs>
        </CardContent>
      </ScrollArea>
    </Card>
  );
};

export default StatisticsChart;