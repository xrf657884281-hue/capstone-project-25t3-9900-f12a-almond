import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiService } from "../services/api";

const SignUp = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirmPassword) {
      alert("The two passwords do not match!");
      return;
    }
    try {
      await apiService.register(form.username, form.email, form.password);
      alert("Registration successful, please sign in.");
      navigate("/sign-in");
    } catch (err: any) {
      alert(err?.message || "Registration failed");
    }
  };

  const inputCls =
    "w-full rounded-md px-3 py-2 border border-gray-300 dark:border-input " +
    "bg-gray-50 dark:bg-background text-foreground placeholder-muted-foreground " +
    "focus:outline-none focus:ring-2 focus:ring-blue-400 dark:focus:ring-ring transition";

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl p-8 shadow border border-gray-300 dark:border-border bg-gray-50 dark:bg-card text-card-foreground transition"
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Sign Up</h2>

        <div className="mb-4 text-left">
          <label className="block mb-1 font-medium text-sm">Username</label>
          <input
            type="text"
            name="username"
            value={form.username}
            onChange={handleChange}
            required
            className={inputCls}
            placeholder="Enter your username"
          />
        </div>

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

        <div className="mb-4 text-left">
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

        <div className="mb-6 text-left">
          <label className="block mb-1 font-medium text-sm">Confirm Password</label>
          <input
            type="password"
            name="confirmPassword"
            value={form.confirmPassword}
            onChange={handleChange}
            required
            className={inputCls}
            placeholder="Re-enter your password"
          />
        </div>

        <button type="submit" className="w-full rounded-md py-2 font-medium bg-primary text-primary-foreground hover:opacity-90 transition" > Sign up </button>

        <p className="mt-4 text-sm text-center text-muted-foreground">
          Already have an account?{" "}
          <span
            onClick={() => navigate("/sign-in")}
            className="text-blue-600 dark:text-primary cursor-pointer hover:underline"
          >
            Sign in
          </span>
        </p>
      </form>
    </div>
  );
};

export default SignUp;