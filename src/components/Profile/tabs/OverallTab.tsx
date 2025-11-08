import { TabsContent } from "@/components/ui/tabs";
import DoughnutChart from "@/components/Profile/DougunutChart";
import StatCard from "../StatCard";


type OverallTabProps = {
  totalDetections: number;
  totalGenerations: number;
};

const OverallTab = ({ totalDetections, totalGenerations }: OverallTabProps) => {
  const totalActivities = totalDetections + totalGenerations;

  return (
    <TabsContent value="overall" className="mt-6">
      <h2 className="text-lg font-semibold mb-4 text-center">
        Overall Statistics
      </h2>

      <div className="w-full h-80 flex items-center justify-center">
        <DoughnutChart
          type="overall"
          overallStats={{
            detections: totalDetections,
            generations: totalGenerations,
          }}
        />
      </div>

      <div className="mt-6 grid grid-cols-3 gap-4">
        <StatCard
          label="Total Detections"
          value={totalDetections}
          color="blue"
        />
        <StatCard
          label="Total Generations"
          value={totalGenerations}
          color="purple"
        />
        <StatCard
          label="Total Activities"
          value={totalActivities}
          color="muted"
        />
      </div>
    </TabsContent>
  );
};

export default OverallTab;