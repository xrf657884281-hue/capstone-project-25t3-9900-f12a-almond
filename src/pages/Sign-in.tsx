import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signInWithPopup } from "firebase/auth";
import { auth, googleProvider, githubProvider } from "@/lib/firebase";
import { apiService } from "../services/api";

interface Props {
  setIsLoggedIn: (value: boolean) => void;
}

const SignIn: React.FC<Props> = ({ setIsLoggedIn }) => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<"google" | "github" | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Email + Password Login
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await apiService.login(form.email, form.password);
      if (res.access_token) {
        localStorage.setItem("access_token", res.access_token);
      }
      localStorage.setItem(
        "user",
        JSON.stringify({
          uid: "local-" + Date.now(),
          displayName: res.username,
          email: res.email,
          photoURL: null,
          provider: "password",
        })
      );

      setIsLoggedIn(true);
      navigate("/profile");
    } catch (err: any) {
      setError(err?.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  // Google / GitHub Login
  const handleOAuth = async (provider: "google" | "github") => {
    setOauthLoading(provider);
    setError(null);
    try {
      const prov = provider === "google" ? googleProvider : githubProvider;
      const res = await signInWithPopup(auth, prov);

      localStorage.setItem(
        "user",
        JSON.stringify({
          uid: res.user.uid,
          displayName: res.user.displayName,
          email: res.user.email,
          photoURL: res.user.photoURL,
          provider,
        })
      );

      try {
        const syncRes = await fetch(`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/auth/firebase_sync`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            uid: res.user.uid,
            email: res.user.email,
            display_name: res.user.displayName,
          }),
        });
        const syncData = await syncRes.json();
        if (syncData.access_token) {
          localStorage.setItem("access_token", syncData.access_token);
        }
      } catch {}

      setIsLoggedIn(true);
      navigate("/profile");
    } catch (err: any) {
      setError(err?.message || `Sign in with ${provider} failed.`);
    } finally {
      setOauthLoading(null);
    }
  };

  const inputCls =
    "w-full rounded-md px-3 py-2 border border-gray-300 dark:border-input " +
    "bg-gray-50 dark:bg-background text-foreground placeholder-muted-foreground " +
    "focus:outline-none focus:ring-2 focus:ring-blue-400 dark:focus:ring-ring transition";

  const socialButtonCls =
    "w-full flex items-center justify-center gap-2 rounded-md py-2 font-medium " +
    "border border-gray-300 dark:border-input bg-gray-50 dark:bg-background text-foreground " +
    "hover:bg-gray-100 dark:hover:bg-muted transition disabled:opacity-50 disabled:cursor-not-allowed";

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl p-8 shadow border border-gray-300 dark:border-border bg-gray-50 dark:bg-card text-card-foreground transition"
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Sign In</h2>

        {error && (
          <div className="mb-4 p-3 rounded-md bg-red-50 dark:bg-red-100 text-red-700 text-sm border border-red-200">
            {error}
          </div>
        )}

        <div className="mb-4 text-left">
          <label className="block mb-1 font-medium text-sm">Email</label>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
            className={inputCls}
            placeholder="Enter your email"
          />
        </div>

        <div className="mb-6 text-left">
          <label className="block mb-1 font-medium text-sm">Password</label>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            required
            className={inputCls}
            placeholder="Enter your password"
          />
        </div>

        <button type="submit" disabled={loading} className="w-full rounded-md py-2 font-medium bg-primary text-primary-foreground hover:opacity-90 transition disabled:opacity-60" > 
          {loading ? "Signing in..." : "Sign in"} 
        </button>

        <div className="space-y-3 mt-4">
          <button
            type="button"
            onClick={() => handleOAuth("google")}
            disabled={!!oauthLoading}
            className={socialButtonCls}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            {oauthLoading === "google" ? "Signing in..." : "Continue with Google"}
          </button>

          <button
            type="button"
            onClick={() => handleOAuth("github")}
            disabled={!!oauthLoading}
            className={socialButtonCls}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            {oauthLoading === "github" ? "Signing in..." : "Continue with GitHub"}
          </button>
        </div>

        <p className="mt-4 text-sm text-center text-muted-foreground">
          Don’t have an account?{" "}
          <span
            onClick={() => navigate("/sign-up")}
            className="text-blue-600 dark:text-primary cursor-pointer hover:underline"
          >
            Sign up
          </span>
        </p>
      </form>
    </div>
  );
};

export default SignIn;
