import { useState } from "react";
import { useNavigate } from "react-router-dom";

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirmPassword) {
      alert("The two passwords do not match!");
      return;
    }
    console.log("submit:", form);
    navigate("/sign-in");
  };

  const inputCls =
    "w-full rounded-md px-3 py-2 border border-input " +
    "bg-background text-foreground placeholder-muted-foreground " +
    "focus:outline-none focus:ring-2 focus:ring-ring";

  return (
    <div className="min-h-screen bg-background text-foreground
                    flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl p-8 shadow
                   bg-card text-card-foreground border border-border"
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Sign Up</h2>

        <div className="mb-4 text-left">
          <label className="block mb-1">Username</label>
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
          <label className="block mb-1">Email</label>
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
          <label className="block mb-1">Password</label>
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
          <label className="block mb-1">Confirm Password</label>
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

        <button
          type="submit"
          className="w-full rounded-md py-2 font-medium
                     bg-primary text-primary-foreground
                     hover:opacity-90 transition"
        >
          Sign up
        </button>
      </form>
    </div>
  );
};

export default SignUp;
