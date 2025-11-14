import { useState, useEffect } from "react";

type StoredUser = {
  uid?: string;
  displayName?: string | null;
  email?: string | null;
  photoURL?: string | null;
  provider?: string | null;
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


export const useUserProfile = () => {
  const [userData, setUserData] = useState({
    username: "User",
    email: "user@example.com",
    photoURL: null as string | null,
  });

  useEffect(() => {
    try {
      const raw = localStorage.getItem("user");
      if (raw) {
        const u: StoredUser = JSON.parse(raw);
        setUserData({
          username: u.displayName ?? "User",
          email: u.email ?? "user@example.com",
          photoURL: u.photoURL ?? null,
        });
      }
    } catch (error) {
      console.error("Failed to load user profile:", error);
    }
  }, []);

  const updateProfile = async (data: {
    username: string;
    email: string;
    photoURL: string | null;
  }) => {
    try {
      const baseUrl =
        import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const raw = localStorage.getItem("user");
      const u: StoredUser = raw ? JSON.parse(raw) : {};

      const payload = {
        username_or_email:
          u.email || data.email || u.displayName || "user@example.com",
        username: data.username,
        email: data.email,
        avatar_url_or_b64: data.photoURL,
      };

      const res = await fetch(`${baseUrl}/api/auth/update_profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const responseData = await res.json();
      if (!res.ok || !responseData.success) {
        throw new Error(responseData.detail || "Backend update failed");
      }

      const updated: StoredUser = {
        ...u,
        displayName: data.username,
        email: data.email,
        photoURL: data.photoURL,
        uid: u.uid ?? `local-${Date.now()}`,
        provider: u.provider ?? "local",
      };
      localStorage.setItem("user", JSON.stringify(updated));
      setUserData(data);
      alert("✅ Profile updated successfully!");
    } catch (err) {
      console.error("update_profile failed:", err);
      alert("⚠️ Failed to update remote database, local profile saved instead.");

      const raw = localStorage.getItem("user");
      const u: StoredUser = raw ? JSON.parse(raw) : {};
      const updated: StoredUser = {
        ...u,
        displayName: data.username,
        email: data.email,
        photoURL: data.photoURL,
        uid: u.uid ?? `local-${Date.now()}`,
        provider: u.provider ?? "local",
      };
      localStorage.setItem("user", JSON.stringify(updated));
      setUserData(data);
    }
  };

  return { userData, updateProfile };
};


export const useDetectionHistory = () => {
  const [history, setHistory] = useState<DetectionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError(null);

        const baseUrl =
          import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
        const token = localStorage.getItem("access_token");

        const res = await fetch(
          `${baseUrl}/api/detection/history?page=1&page_size=9999`,
          {
            headers: {
              "Content-Type": "application/json",
              ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
          }
        );

        if (!res.ok) {
          const text = await res.text();
          throw new Error(
            `Failed to fetch history: ${res.status} ${text || res.statusText}`
          );
        }

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

  return { history, loading, error };
};


export const useGenerationHistory = () => {
  const [history, setHistory] = useState<GenerationRecord[]>([]);

  useEffect(() => {
    const fetchGenerationHistory = async () => {
      try {
        const baseUrl =
          import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
        const token = localStorage.getItem("access_token");

        const res = await fetch(
          `${baseUrl}/api/generation/history?page=1&page_size=9999`,
          {
            headers: {
              "Content-Type": "application/json",
              ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
          }
        );

        if (!res.ok) {
          const text = await res.text();
          console.error(
            `Failed to fetch generation history: ${res.status} ${
              text || res.statusText
            }`
          );
          return;
        }

        const data = await res.json();
        if (data.success) {
          setHistory(data.items || []);
        }
      } catch (err: any) {
        console.error("Failed to load generation history:", err.message);
      }
    };
    fetchGenerationHistory();
  }, []);

  return { history };
};
