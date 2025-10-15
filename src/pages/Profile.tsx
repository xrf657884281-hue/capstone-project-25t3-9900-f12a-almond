import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

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

const inputCls =
  "w-full rounded-md px-3 py-2 border border-input " +
  "bg-background text-foreground placeholder-muted-foreground " +
  "focus:outline-none focus:ring-2 focus:ring-ring";

const Profile = () => {
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
        return;
      }
    } catch {
      // ignore
    }
    setForm({ username: "User", email: "user@example.com", photoURL: null });
    setInitial({ username: "User", email: "user@example.com", photoURL: null });
    setPreview(null);
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

  const handleSave = () => {
    try {
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
      alert("✅ Profile updated successfully!");
    } catch {
      alert("❌ Failed to write to localStorage.");
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col items-center px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Profile</h1>
      <Card className="w-full max-w-3xl border border-border shadow">
        <CardContent className="p-6 space-y-6">
          <div className="flex items-center gap-6">
            <label className="cursor-pointer">
              <div className="w-24 h-24 rounded-full bg-muted flex items-center justify-center overflow-hidden border">
                {preview ? (
                  <img
                    src={preview}
                    alt="avatar"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-sm text-muted-foreground">Choose Avatar</span>
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
            <Button variant="default" onClick={handleSave} disabled={!hasChanges}>
              Save Changes
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Profile;
