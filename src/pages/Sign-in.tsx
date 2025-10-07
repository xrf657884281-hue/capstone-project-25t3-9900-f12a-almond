import { useState } from "react";
import { useNavigate } from "react-router-dom";

interface Props {
  setIsLoggedIn: (value: boolean) => void;
}
const SignIn: React.FC<Props> = ({ setIsLoggedIn }) =>  {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    console.log("login:", form);
    setIsLoggedIn(true);
    navigate("/dashboard");
  };

  const inputCls =
    "w-full rounded-md px-3 py-2 border border-input " +
    "bg-background text-foreground placeholder-muted-foreground " +
    "focus:outline-none focus:ring-2 focus:ring-ring";

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl p-8 shadow bg-card text-card-foreground border border-border"
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Sign In</h2>

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

        <div className="mb-6 text-left">
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

        <button
          type="submit"
          className="w-full rounded-md py-2 font-medium bg-primary text-primary-foreground hover:opacity-90 transition"
        >
          Sign in
        </button>

        <p className="mt-4 text-sm text-center text-muted-foreground">
          Don’t have an account?{" "}
          <span
            onClick={() => navigate("/sign-up")}
            className="text-primary cursor-pointer hover:underline"
          >
            Sign up
          </span>
        </p>
      </form>
    </div>
  );
};

export default SignIn;
