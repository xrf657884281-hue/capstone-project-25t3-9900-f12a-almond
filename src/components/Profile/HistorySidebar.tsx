import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import HistoryTabContent from "@/components/Profile/HistoryTab";

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
  result?: {
    article?: string;
    summary?: string;
    [key: string]: any;
  };
};

type HistorySidebarProps = {
  detectionHistory: DetectionRecord[];
  generationHistory: GenerationRecord[];
  detectionLoading: boolean;
  detectionError: string | null;
  detectionPage: number;
  generationPage: number;
  detectionTotalPages: number;
  generationTotalPages: number;
  onDetectionPageChange: (page: number) => void;
  onGenerationPageChange: (page: number) => void;
  onDetectionRecordClick: (record: DetectionRecord) => void;
};

const HistorySidebar = ({
  detectionHistory,
  generationHistory,
  detectionLoading,
  detectionError,
  detectionPage,
  generationPage,
  detectionTotalPages,
  generationTotalPages,
  onDetectionPageChange,
  onGenerationPageChange,
  onDetectionRecordClick,
}: HistorySidebarProps) => {
  const handleGenerationRecordClick = async (record: GenerationRecord) => {
    try {
      const recordId = record._id;
      const baseUrl =
        import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const token = localStorage.getItem("access_token");

      const generateResponse = await fetch(
        `${baseUrl}/api/generation/history/${recordId}/generate_pdf`,
        {
          method: "POST",
          headers: {
            "Authorization": token ? `Bearer ${token}` : "",
          },
        }
      );

      if (!generateResponse.ok) {
        const errText = await generateResponse.text();
        console.error("PDF generation failed:", errText);
        throw new Error("Failed to generate PDF on server");
      }

      const res = await fetch(
        `${baseUrl}/api/generation/history/${recordId}/pdf`,
        {
          headers: {
            "Authorization": token ? `Bearer ${token}` : "",
          },
        }
      );

      if (!res.ok) {
        const errText = await res.text();
        console.error("PDF download failed:", errText);
        throw new Error("Failed to download PDF");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `generation_${recordId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("❌ Failed to download generation PDF:", err);
      alert("Downloading the generated record PDF failed. Please try again later.");
    }
  };

  return (
    <Card className="border border-gray-300 dark:border-border shadow">
      <CardContent className="p-4">
        <Tabs defaultValue="detection" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="detection">Detection History</TabsTrigger>
            <TabsTrigger value="generation">Generation History</TabsTrigger>
          </TabsList>

          <HistoryTabContent
            tabValue="detection"
            loading={detectionLoading}
            error={detectionError}
            items={detectionHistory}
            currentPage={detectionPage}
            totalPages={detectionTotalPages}
            onPageChange={onDetectionPageChange}
            onItemClick={onDetectionRecordClick}
            getItemText={(item) => item.text?.slice(0, 80) || "No text"}
          />

          <HistoryTabContent
            tabValue="generation"
            loading={false}
            error={null}
            items={generationHistory}
            currentPage={generationPage}
            totalPages={generationTotalPages}
            onPageChange={onGenerationPageChange}
            onItemClick={handleGenerationRecordClick}
            getItemText={(item) =>
              item.generated_text?.slice(0, 80) ||
              item.result?.article?.slice(0, 80) ||
              item.prompt?.slice(0, 80) ||
              "No text"
            }
          />
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default HistorySidebar;
