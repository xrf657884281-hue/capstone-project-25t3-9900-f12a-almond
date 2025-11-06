import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { PieLabelRenderProps } from "recharts";

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
        setInitial({ username: "User", email: "user@example.com", photoURL: null });
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
      alert("⚠️ Failed to update remote database, local profile saved instead.");
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

  const COLORS = ["#22c55e", "#ef4444", "#facc15"];

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col items-center px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Profile</h1>
      

      {/* history part */}
      <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-3 space-y-4">
          <Card className="border border-gray-300 dark:border-border shadow">
            <CardContent className="p-4">
              <h2 className="text-lg font-semibold mb-3">Detection History</h2>
              {loading && (
                <p className="text-sm text-muted-foreground">Loading...</p>
              )}
              {error && <p className="text-sm text-red-600">❌ {error}</p>}
              {!loading && !error && history.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  No detection history available.
                </p>
              )}
              {!loading && history.length > 0 && (
                <ul className="space-y-3 max-h-[70vh] overflow-auto">
                  {history.map((item) => (
                    <li
                      key={item._id}
                      onClick={() => handleRecordClick(item)}
                      className="border border-gray-300 dark:border-border rounded-md p-2 bg-gray-50 dark:bg-muted text-sm cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition"
                    >
                      <div className="font-medium truncate">
                        {item.text?.slice(0, 80) || "No text"}
                      </div>
                      <div className="text-xs text-right text-muted-foreground mt-1">
                        {new Date(item.created_at).toLocaleString()}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
        
        {/*chart part*/}
        <div className="lg:col-span-6">
          <Card className="border border-gray-300 dark:border-border shadow">
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold mb-4 text-center">
                Detection Statistics
              </h2>

              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={[
                      { name: "Real", value: 5 },
                      { name: "Fake", value: 3 },
                      { name: "Misleading", value: 2 },
                    ]}
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    dataKey="value"
                    nameKey="name"
                    label={(props: PieLabelRenderProps) =>
                      `${props.name ?? ""} (${props.value ?? 0})`
                    }
                  >
                    <Cell fill={COLORS[0]} />
                    <Cell fill={COLORS[1]} />
                    <Cell fill={COLORS[2]} />
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" height={36} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
        
        {/*personal information part*/}
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
