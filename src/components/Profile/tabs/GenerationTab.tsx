import { useState } from "react";
import { TabsContent } from "@/components/ui/tabs";
import DoughnutChart from "@/components/Profile/DougunutChart";
import {
  STYLE_FILTERS,
  DOMAIN_FILTERS,
  GENERATION_VARIANTS,
  ITEMS_PER_PAGE,
} from "@/config/statistics.config";
import {
  getStyleFromRecord,
  getDomainFromRecord,
  getRecordPreview,
  calculateTotalPages,
} from "@/utils/statistics.utils";
import StatCard from "../StatCard";
import FilteredRecordsList from "../FilteredRecordsList";

type GenerationStats = {
  byStyle: Record<string, number>;
  byDomain: Record<string, number>;
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
  result?: {
    article?: string;
    summary?: string;
    [key: string]: any;
  };
};

type GenerationTabProps = {
  generationStats: GenerationStats;
  generationRecords: GenerationRecord[];
};

const GenerationTab = ({
  generationStats,
  generationRecords,
}: GenerationTabProps) => {
  const [variant, setVariant] = useState<"style" | "domain">("style");
  const [selectedFilter, setSelectedFilter] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  const handleRecordClick = async (record: GenerationRecord) => {
    try {
      const recordId = record._id;
      const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

      // 1️⃣ generate PDF
      await fetch(`${baseUrl}/api/generation/history/${recordId}/generate_pdf`, {
        method: "POST",
      });

      // 2️⃣ download PDF
      const res = await fetch(`${baseUrl}/api/generation/history/${recordId}/pdf`);

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `generation_${recordId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

    } catch (err) {
      console.error(err);
      alert("❌ Failed to export PDF.");
    }
  };


  const filteredRecords = selectedFilter
    ? generationRecords.filter((item) => {
        if (variant === "style") {
          return getStyleFromRecord(item) === selectedFilter;
        } else {
          return getDomainFromRecord(item) === selectedFilter;
        }
      })
    : [];

  const totalPages = calculateTotalPages(
    filteredRecords.length,
    ITEMS_PER_PAGE
  );

  const handleVariantChange = (newVariant: "style" | "domain") => {
    setVariant(newVariant);
    setSelectedFilter(null);
    setCurrentPage(1);
  };

  const handleFilterClick = (filter: string) => {
    setSelectedFilter(filter);
    setCurrentPage(1);
  };

  const handleClearFilter = () => {
    setSelectedFilter(null);
    setCurrentPage(1);
  };

  const currentFilters =
    variant === "style" ? STYLE_FILTERS : DOMAIN_FILTERS;
  const currentStats =
    variant === "style"
      ? generationStats.byStyle
      : generationStats.byDomain;

  return (
    <TabsContent value="generation" className="mt-6">
      <h2 className="text-lg font-semibold mb-4 text-center">
        Generation Statistics
      </h2>

      {/* Variant Toggle */}
      <div className="flex justify-center gap-2 mb-6">
        {GENERATION_VARIANTS.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => handleVariantChange(value)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              variant === value
                ? "bg-blue-600 text-white"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="w-full h-80 flex items-center justify-center">
        <DoughnutChart
          type="generation"
          generationStats={generationStats}
          variant={variant}
        />
      </div>

      {/* Filter Buttons */}
      <div className="mt-6">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {currentFilters.map(({ key, label, color }) => (
            <StatCard
              key={key}
              label={label}
              value={currentStats[key] || 0}
              color={color}
              isSelected={selectedFilter === key}
              onClick={() => handleFilterClick(key)}
            />
          ))}
        </div>
      </div>

      {/* Filtered Records */}
      {selectedFilter && (
        <FilteredRecordsList
          title={`${selectedFilter} Generation Records`}
          records={filteredRecords}
          currentPage={currentPage}
          totalPages={totalPages}
          itemsPerPage={ITEMS_PER_PAGE}
          onPageChange={setCurrentPage}
          onClearFilter={handleClearFilter}
          onRecordClick={handleRecordClick} // ✅ Click event
          renderText={(record) =>
            getRecordPreview(
              record.generated_text ||
                record.result?.article ||
                record.result?.summary ||
                record.prompt
            )
          }
        />
      )}
    </TabsContent>
  );
};

export default GenerationTab;
