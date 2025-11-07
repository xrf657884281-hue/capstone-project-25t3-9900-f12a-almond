import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

import HistoryTabContent from "@/components/Profile/HistoryTab";
import DoughnutChart from "@/components/Profile/DougunutChart";

type StoredUser = {
  uid?: string;
  displayName?: string | null;
  email?: string | null;
  photoURL?: string | null;
  provider?: string | null;
};

type FormState = {
  username: string;
  email: string;
  photoURL: string | null;
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
};

type DetectionStats = {
  real: number;
  fake: number;
  misleading: number;
};

const inputCls =
  "w-full rounded-md px-3 py-2 " +
  "border border-gray-300 dark:border-input " +
  "bg-gray-50 dark:bg-background " +
  "text-foreground placeholder-muted-foreground " +
  "focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring " +
  "transition-colors";

const Profile = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>({
    username: "",
    email: "",
    photoURL: null,
  });
  const [initial, setInitial] = useState<FormState>({
    username: "",
    email: "",
    photoURL: null,
  });
  const [preview, setPreview] = useState<string | null>(null);
  const [history, setHistory] = useState<DetectionRecord[]>([]);
  const [generationHistory, setGenerationHistory] = useState<GenerationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detectionPage, setDetectionPage] = useState(1);
  const [generationPage, setGenerationPage] = useState(1);
  const [statsTab, setStatsTab] = useState("overall");
  const [generationVariant, setGenerationVariant] = useState<"style" | "domain">("style");

  // init form from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem("user");
      if (raw) {
        const u: StoredUser = JSON.parse(raw);
        const username = u.displayName ?? "User";
        const email = u.email ?? "user@example.com";
        const photoURL = u.photoURL ?? null;
        setForm({ username, email, photoURL });
        setInitial({ username, email, photoURL });
        setPreview(photoURL);
      } else {
        setForm({ username: "User", email: "user@example.com", photoURL: null });
        setInitial({
          username: "User",
          email: "user@example.com",
          photoURL: null,
        });
      }
    } catch {
      setForm({ username: "User", email: "user@example.com", photoURL: null });
    }
  }, []);

  // load detection history (for sidebar)
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError(null);
        const baseUrl =
          import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
        const res = await fetch(
          `${baseUrl}/api/detection/history?page=1&page_size=9999`
        );
        const data = await res.json();
        if (!data.success) throw new Error("Failed to fetch history");
        setHistory(data.items || []);
      } catch (err: any) {
        setError(err.message || "Failed to load history");
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  // load generation history
  useEffect(() => {
    const fetchGenerationHistory = async () => {
      try {
        const baseUrl =
          import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
        const res = await fetch(
          `${baseUrl}/api/generation/history?page=1&page_size=9999`
        );
        const data = await res.json();
        if (data.success) {
          setGenerationHistory(data.items || []);
        }
      } catch (err: any) {
        console.error("Failed to load generation history:", err.message);
      }
    };
    fetchGenerationHistory();
  }, []);

  const hasChanges =
    form.username !== initial.username ||
    form.email !== initial.email ||
    form.photoURL !== initial.photoURL;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const fileToBase64 = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setPreview(url);
    const base64 = await fileToBase64(file);
    setForm((prev) => ({ ...prev, photoURL: base64 }));
  };

  const handleSave = async () => {
    try {
      const baseUrl =
        import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const raw = localStorage.getItem("user");
      const u: StoredUser = raw ? JSON.parse(raw) : {};

      const payload = {
        username_or_email:
          u.email || form.email || u.displayName || "user@example.com",
        username: form.username,
        email: form.email,
        avatar_url_or_b64: form.photoURL,
      };

      const res = await fetch(`${baseUrl}/api/auth/update_profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.detail || "Backend update failed");
      }

      const updated: StoredUser = {
        ...u,
        displayName: form.username,
        email: form.email,
        photoURL: form.photoURL,
        uid: u.uid ?? `local-${Date.now()}`,
        provider: u.provider ?? "local",
      };
      localStorage.setItem("user", JSON.stringify(updated));
      setInitial(form);
      alert("✅ Profile updated successfully!");
    } catch (err) {
      console.error("update_profile failed:", err);
      alert(
        "⚠️ Failed to update remote database, local profile saved instead."
      );
      const raw = localStorage.getItem("user");
      const u: StoredUser = raw ? JSON.parse(raw) : {};
      const updated: StoredUser = {
        ...u,
        displayName: form.username,
        email: form.email,
        photoURL: form.photoURL,
        uid: u.uid ?? `local-${Date.now()}`,
        provider: u.provider ?? "local",
      };
      localStorage.setItem("user", JSON.stringify(updated));
      setInitial(form);
    }
  };

  const handleRecordClick = (record: DetectionRecord) => {
    const normalized = {
      ...record.result,
      details: record.result,
      readability:
        (record.result?.final_prediction?.fake_probability ?? 0) * 100,
      humanConfidence:
        (record.result?.final_prediction?.confidence ?? 0) * 100,
      verdict:
        record.result?.final_prediction?.prediction?.toUpperCase() ?? "",
      isFake:
        record.result?.final_prediction?.prediction?.toLowerCase() === "fake",
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

  // Calculate detection statistics from history (cached)
  const detectionStats: DetectionStats = useMemo(
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
          item.result?.final_prediction?.prediction?.toLowerCase() ===
          "misleading"
      ).length,
    }),
    [history]
  );

  // Calculate generation statistics
  const generationStats = useMemo(
    () => {
      const byStyle: Record<string, number> = {};
      const byDomain: Record<string, number> = {};

      generationHistory.forEach((item) => {
        // Extract style from params
        const style = (item as any).params?.style 
          ? ((item as any).params.style as string).charAt(0).toUpperCase() + ((item as any).params.style as string).slice(1)
          : item.type || "Unknown";
        byStyle[style] = (byStyle[style] || 0) + 1;

        // Extract domain from params
        const domain = (item as any).params?.domain 
          ? ((item as any).params.domain as string).charAt(0).toUpperCase() + ((item as any).params.domain as string).slice(1)
          : "General";
        byDomain[domain] = (byDomain[domain] || 0) + 1;
      });

      return { byStyle, byDomain };
    },
    [generationHistory]
  );

  // Calculate overall statistics
  const overallStats = useMemo(
    () => ({
      real: detectionStats.real,
      fake: detectionStats.fake,
      misleading: detectionStats.misleading,
      totalDetections: detectionStats.real + detectionStats.fake + detectionStats.misleading,
      totalGenerations: generationHistory.length,
    }),
    [detectionStats, generationHistory]
  );

  // Calculate total pages for pagination
  const itemsPerPageForCalc = 5;
  const getTotalPages = (items: any[]) => {
    return Math.ceil(items.length / itemsPerPageForCalc);
  };

  const detectionTotalPages = getTotalPages(history);
  const generationTotalPages = getTotalPages(generationHistory);

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col items-center px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Profile</h1>

      {/* history part */}
      <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-3 space-y-4">
          <Card className="border border-gray-300 dark:border-border shadow">
            <CardContent className="p-4">
              <Tabs defaultValue="detection" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="detection">Detection History</TabsTrigger>
                  <TabsTrigger value="generation">Generation History</TabsTrigger>
                </TabsList>

                <HistoryTabContent
                  tabValue="detection"
                  loading={loading}
                  error={error}
                  items={history}
                  currentPage={detectionPage}
                  totalPages={detectionTotalPages}
                  onPageChange={setDetectionPage}
                  onItemClick={handleRecordClick}
                  getItemText={(item) => item.text?.slice(0, 80) || "No text"}
                />

                <HistoryTabContent
                  tabValue="generation"
                  loading={false}
                  error={null}
                  items={generationHistory}
                  currentPage={generationPage}
                  totalPages={generationTotalPages}
                  onPageChange={setGenerationPage}
                  onItemClick={undefined}
                  getItemText={(item) =>
                    item.generated_text?.slice(0, 80) ||
                    item.prompt?.slice(0, 80) ||
                    "No text"
                  }
                />
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* chart part with tabs */}
        <div className="lg:col-span-6">
          <Card className="border border-gray-300 dark:border-border shadow">
            <CardContent className="p-6">
              <Tabs value={statsTab} onValueChange={setStatsTab} className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="overall">Overall</TabsTrigger>
                  <TabsTrigger value="detection">Detection</TabsTrigger>
                  <TabsTrigger value="generation">Generation</TabsTrigger>
                </TabsList>

                {/* Overall Tab */}
                <TabsContent value="overall" className="mt-6">
                  <h2 className="text-lg font-semibold mb-4 text-center">
                    Overall Statistics
                  </h2>
                  <div className="w-full h-80 flex items-center justify-center">
                    <DoughnutChart
                      type="overall"
                      overallStats={{
                        detections: overallStats.totalDetections,
                        generations: overallStats.totalGenerations,
                      }}
                    />
                  </div>
                  <div className="mt-6 grid grid-cols-3 gap-4">
                    <div className="text-center p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                      <p className="text-sm text-muted-foreground">Total Detections</p>
                      <p className="text-2xl font-bold text-blue-600">{overallStats.totalDetections}</p>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20">
                      <p className="text-sm text-muted-foreground">Total Generations</p>
                      <p className="text-2xl font-bold text-purple-600">{overallStats.totalGenerations}</p>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-muted">
                      <p className="text-sm text-muted-foreground">Total Activities</p>
                      <p className="text-2xl font-bold">
                        {overallStats.totalDetections + overallStats.totalGenerations}
                      </p>
                    </div>
                  </div>
                </TabsContent>

                {/* Detection Tab */}
                <TabsContent value="detection" className="mt-6">
                  <h2 className="text-lg font-semibold mb-4 text-center">
                    Detection Statistics
                  </h2>
                  <div className="w-full h-80 flex items-center justify-center">
                    <DoughnutChart
                      type="detection"
                      detectionStats={detectionStats}
                    />
                  </div>
                  <div className="mt-6 grid grid-cols-3 gap-4">
                    <div className="text-center p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
                      <p className="text-sm text-muted-foreground">Real</p>
                      <p className="text-2xl font-bold text-green-600">{detectionStats.real}</p>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-red-50 dark:bg-red-900/20">
                      <p className="text-sm text-muted-foreground">Fake</p>
                      <p className="text-2xl font-bold text-red-600">{detectionStats.fake}</p>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
                      <p className="text-sm text-muted-foreground">Misleading</p>
                      <p className="text-2xl font-bold text-yellow-600">{detectionStats.misleading}</p>
                    </div>
                  </div>
                </TabsContent>

                {/* Generation Tab */}
                <TabsContent value="generation" className="mt-6">
                  <h2 className="text-lg font-semibold mb-4 text-center">
                    Generation Statistics
                  </h2>

                  {/* Style vs Domain Toggle */}
                  <div className="flex justify-center gap-2 mb-6">
                    <button
                      onClick={() => setGenerationVariant("style")}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        generationVariant === "style"
                          ? "bg-blue-600 text-white"
                          : "bg-muted text-muted-foreground hover:bg-muted/80"
                      }`}
                    >
                      By Style
                    </button>
                    <button
                      onClick={() => setGenerationVariant("domain")}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        generationVariant === "domain"
                          ? "bg-blue-600 text-white"
                          : "bg-muted text-muted-foreground hover:bg-muted/80"
                      }`}
                    >
                      By Topic
                    </button>
                  </div>

                  <div className="w-full h-80 flex items-center justify-center">
                    <DoughnutChart
                      type="generation"
                      generationStats={generationStats}
                      variant={generationVariant}
                    />
                  </div>

                  {/* Generation Statistics Cards */}
                  <div className="mt-6">
                    {generationVariant === "style" ? (
                      // Style Cards
                      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                        <div className="text-center p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                          <p className="text-sm text-muted-foreground">Fun</p>
                          <p className="text-2xl font-bold text-blue-600">
                            {generationStats.byStyle["Fun"] || 0}
                          </p>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-red-50 dark:bg-red-900/20">
                          <p className="text-sm text-muted-foreground">Formal</p>
                          <p className="text-2xl font-bold text-red-600">
                            {generationStats.byStyle["Formal"] || 0}
                          </p>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
                          <p className="text-sm text-muted-foreground">Sensational</p>
                          <p className="text-2xl font-bold text-yellow-600">
                            {generationStats.byStyle["Sensational"] || 0}
                          </p>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20">
                          <p className="text-sm text-muted-foreground">Normal</p>
                          <p className="text-2xl font-bold text-purple-600">
                            {generationStats.byStyle["Normal"] || 0}
                          </p>
                        </div>
                      </div>
                    ) : (
                      // Domain Cards
                      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                        <div className="text-center p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
                          <p className="text-sm text-muted-foreground">Technology</p>
                          <p className="text-2xl font-bold text-green-600">
                            {generationStats.byDomain["Technology"] || 0}
                          </p>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20">
                          <p className="text-sm text-muted-foreground">Politics</p>
                          <p className="text-2xl font-bold text-amber-600">
                            {generationStats.byDomain["Politics"] || 0}
                          </p>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-red-50 dark:bg-red-900/20">
                          <p className="text-sm text-muted-foreground">Business</p>
                          <p className="text-2xl font-bold text-red-600">
                            {generationStats.byDomain["Business"] || 0}
                          </p>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20">
                          <p className="text-sm text-muted-foreground">Sports</p>
                          <p className="text-2xl font-bold text-purple-600">
                            {generationStats.byDomain["Sports"] || 0}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* personal information part */}
        <div className="lg:col-span-3">
          <Card className="border border-gray-300 dark:border-border shadow">
            <CardContent className="p-6 space-y-6">
              <div className="flex items-center justify-center">
                <label className="cursor-pointer">
                  <div className="w-24 h-24 rounded-full bg-muted flex items-center justify-center overflow-hidden border">
                    {preview ? (
                      <img
                        src={preview}
                        alt="avatar"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <span className="text-sm text-muted-foreground">
                        Choose Avatar
                      </span>
                    )}
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleAvatarChange}
                  />
                </label>
              </div>

              <div className="space-y-4">
                <div className="text-left">
                  <label className="block mb-1 font-medium">Username</label>
                  <input
                    type="text"
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    className={inputCls}
                    placeholder="Enter your username"
                  />
                </div>

                <div className="text-left">
                  <label className="block mb-1 font-medium">Email</label>
                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    className={inputCls}
                    placeholder="Enter your email"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <Button
                  variant="default"
                  onClick={handleSave}
                  disabled={!hasChanges}
                >
                  Save Changes
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Profile;