import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

type UserInfoCardProps = {
  initialData: {
    username: string;
    email: string;
    photoURL: string | null;
  };
  onSave: (data: {
    username: string;
    email: string;
    photoURL: string | null;
  }) => Promise<void>;
};

const inputCls =
  "w-full rounded-md px-3 py-2 " +
  "border border-gray-300 dark:border-input " +
  "bg-gray-50 dark:bg-background " +
  "text-foreground placeholder-muted-foreground " +
  "focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring " +
  "transition-colors";

const UserInfoCard = ({ initialData, onSave }: UserInfoCardProps) => {
  const [form, setForm] = useState(initialData);
  const [initial, setInitial] = useState(initialData);
  const [preview, setPreview] = useState<string | null>(initialData.photoURL);
  useEffect(() => {
    setForm(initialData);
    setInitial(initialData);
    setPreview(initialData.photoURL);
  }, [initialData]);

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

  const handleSaveClick = async () => {
    await onSave(form);
    setInitial(form);
  };

  return (
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
            onClick={handleSaveClick}
            disabled={!hasChanges}
          >
            Save Changes
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default UserInfoCard;