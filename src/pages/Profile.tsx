import { useState} from "react";
import { useNavigate } from "react-router-dom";


import StatisticsChart from "@/components/Profile/StatisticsChart";
import UserInfoCard from "@/components/Profile/UserInfoCard";

import { useUserProfile, useDetectionHistory, useGenerationHistory } from "@/hooks/useProfileData";
import { useDetectionStats, useGenerationStats } from "@/hooks/useStatistics";
import HistorySidebar from "@/components/Profile/HistorySidebar";

type DetectionRecord = {
  _id: string;
  type: string;
  text?: string;
  result?: any;
  created_at: string;
};

const Profile = () => {
  const navigate = useNavigate();

  // Custom hooks for data fetching
  const { userData, updateProfile } = useUserProfile();
  const { history: detectionHistory, loading: detectionLoading, error: detectionError } = useDetectionHistory();
  const { history: generationHistory } = useGenerationHistory();

  // Custom hooks for statistics calculation
  const detectionStats = useDetectionStats(detectionHistory);
  const generationStats = useGenerationStats(generationHistory);

  // Pagination state
  const [detectionPage, setDetectionPage] = useState(1);
  const [generationPage, setGenerationPage] = useState(1);

  // Calculate total pages for pagination
  const itemsPerPage = 5;
  const detectionTotalPages = Math.ceil(detectionHistory.length / itemsPerPage);
  const generationTotalPages = Math.ceil(generationHistory.length / itemsPerPage);

  // Handle detection record click
  const handleRecordClick = (record: DetectionRecord) => {
    const normalized = {
      ...record.result,
      details: record.result,
      readability: (record.result?.final_prediction?.fake_probability ?? 0) * 100,
      humanConfidence: (record.result?.final_prediction?.confidence ?? 0) * 100,
      verdict: record.result?.final_prediction?.prediction?.toUpperCase() ?? "",
      isFake: record.result?.final_prediction?.prediction?.toLowerCase() === "fake",
    };

    navigate("/result", {
      state: {
        source: "detection",
        text: record.text,
        analysis: normalized,
        record_id: record._id,
      },
    });
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col items-center px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Profile</h1>

      <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* History Sidebar */}
        <div className="lg:col-span-3 space-y-4">
          <HistorySidebar
            detectionHistory={detectionHistory}
            generationHistory={generationHistory}
            detectionLoading={detectionLoading}
            detectionError={detectionError}
            detectionPage={detectionPage}
            generationPage={generationPage}
            detectionTotalPages={detectionTotalPages}
            generationTotalPages={generationTotalPages}
            onDetectionPageChange={setDetectionPage}
            onGenerationPageChange={setGenerationPage}
            onDetectionRecordClick={handleRecordClick}
          />
        </div>

        {/* Statistics Chart */}
        <div className="lg:col-span-6">
          <StatisticsChart
            detectionStats={detectionStats}
            generationStats={generationStats}
            detectionRecords={detectionHistory}
            generationRecords={generationHistory}
            onDetectionRecordClick={handleRecordClick}
          />
        </div>

        {/* User Info Card */}
        <div className="lg:col-span-3">
          <UserInfoCard
            initialData={userData}
            onSave={updateProfile}
          />
        </div>
      </div>
    </div>
  );
};

export default Profile;