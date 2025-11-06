import About from "../pages/About";
import Detection from "../pages/Detection";
import Generate from "../pages/Generate";
import Home from "../pages/Home";


export const NavRoutes = [
  { path: "/", element: <Home /> },
  { path: "/detection", element: <Detection /> },
  { path: "/generate", element: <Generate /> },
  { path: "/about", element: <About /> },
];

export const navItems = [
  { path: "/detection", label: "Detection" },
  { path: "/generate", label: "Generation" },
  { path: "/about", label: "About Us" },
];