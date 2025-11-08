import { useState } from "react";
import { TabsContent } from "@/components/ui/tabs";
import DoughnutChart from "@/components/Profile/DougunutChart";
import { DETECTION_FILTERS, ITEMS_PER_PAGE } from "@/config/statistics.config";
import { getRecordPreview, calculateTotalPages } from "@/utils/statistics.utils";
import StatCard from "../StatCard";
import FilteredRecordsList from "../FilteredRecordsList";

type DetectionStats = {
  real: number;
  fake: number;
  misleading: number;
};

type DetectionRecord = {
  _id: string;
  type: string;
  text?: string;
  result?: any;
  created_at: string;
};

type DetectionTabProps = {
  detectionStats: DetectionStats;
  detectionRecords: DetectionRecord[];
  onRecordClick: (record: DetectionRecord) => void;
};

const DetectionTab = ({
  detectionStats,
  detectionRecords,
  onRecordClick,
}: DetectionTabProps) => {
  const [selectedFilter, setSelectedFilter] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  // Filter records based on selected filter
  const filteredRecords = selectedFilter
    ? detectionRecords.filter(
        (item) =>
          item.result?.final_prediction?.prediction?.toLowerCase() ===
          selectedFilter.toLowerCase()
      )
    : [];

  const totalPages = calculateTotalPages(filteredRecords.length, ITEMS_PER_PAGE);

  const handleFilterClick = (filter: string) => {
    setSelectedFilter(filter);
    setCurrentPage(1);
  };

  const handleClearFilter = () => {
    setSelectedFilter(null);
    setCurrentPage(1);
  };

  return (
    <TabsContent value="detection" className="mt-6">
      <h2 className="text-lg font-semibold mb-4 text-center">
        Detection Statistics
      </h2>

      <div className="w-full h-80 flex items-center justify-center">
        <DoughnutChart type="detection" detectionStats={detectionStats} />
      </div>

      {/* Filter Buttons */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        {DETECTION_FILTERS.map(({ key, label, color }) => (
          <StatCard
            key={key}
            label={label}
            value={detectionStats[key.toLowerCase() as keyof DetectionStats]}
            color={color}
            isSelected={selectedFilter === key}
            onClick={() => handleFilterClick(key)}
          />
        ))}
      </div>

      {/* Filtered Records */}
      {selectedFilter && (
        <FilteredRecordsList
          title={`${selectedFilter} Detection Records`}
          records={filteredRecords}
          currentPage={currentPage}
          totalPages={totalPages}
          itemsPerPage={ITEMS_PER_PAGE}
          onPageChange={setCurrentPage}
          onClearFilter={handleClearFilter}
          onRecordClick={onRecordClick}
          renderText={(record) => getRecordPreview(record.text)}
        />
      )}
    </TabsContent>
  );
};

export default DetectionTab;