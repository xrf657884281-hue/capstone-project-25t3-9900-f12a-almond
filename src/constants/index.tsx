import About from "../pages/About";
import Detection from "../pages/Detection";
import Generate from "../pages/Generate";
import Home from "../pages/Home";


export const NavRoutes = [
  { path: "/", element: <Home /> },
  { path: "/Detection", element: <Detection /> },
  { path: "/Generate", element: <Generate /> },
  { path: "/About", element: <About /> },
];

export const navItems = [
  { path: "/Detection", label: "Detection" },
  { path: "/Generate", label: "Generate" },
  { path: "/About", label: "About Us" },
];