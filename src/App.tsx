import { Route, Routes, useNavigate} from "react-router-dom";
import {
  Navbar,
  NavBody,
  NavItems,
  MobileNav,
  NavbarLogo,
  NavbarButton,
  MobileNavHeader,
  MobileNavToggle,
  MobileNavMenu,
  ThemeToggle,
} from "@/components/ui/resizable-navbar";
import { NavRoutes, navItems } from "./constants";
import { useState } from "react";
import { Link } from "react-router-dom";
import SignIn from "./pages/Sign-in";
import SignUp from "./pages/Sign-up";
import Profile from "./pages/Profile";
import Result from "./pages/Result";
import { Toaster } from "./components/ui/sonner";

const App = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  const navItemsForNavbar = navItems.map((item) => ({
    name: item.label,
    link: item.path,
  }));

  const handleLogout = () => {
    setIsLoggedIn(false);
    navigate("/");
  };

  return (
    <main>

      <Navbar>

        <NavBody>
          <NavbarLogo />
          <NavItems items={navItemsForNavbar} />

          <div className="flex items-center gap-4 relative z-50">
            {isLoggedIn ? (
              <>
                <Link to="/profile">
                  <NavbarButton variant="secondary">Profile</NavbarButton>
                </Link>
                <NavbarButton  variant="secondary"  className="bg-red-600 text-white hover:bg-red-700"  onClick={handleLogout}>  
                  Logout
                </NavbarButton>
              </>
            ) : (
              <>
                <Link to="/sign-in">
                  <NavbarButton variant="secondary">Sign in</NavbarButton>
                </Link>
                <Link to="/sign-up">
                  <NavbarButton variant="primary">Sign up</NavbarButton>
                </Link>
              </>
            )}
            <ThemeToggle />
          </div>
        </NavBody>


        <MobileNav>
          <MobileNavHeader>
            <NavbarLogo />
            <MobileNavToggle
              isOpen={isMobileMenuOpen}
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            />
          </MobileNavHeader>

          <MobileNavMenu
            isOpen={isMobileMenuOpen}
            onClose={() => setIsMobileMenuOpen(false)}
          >
            {navItemsForNavbar.map((item, idx) => (
              <Link
                key={`mobile-link-${idx}`}
                to={item.link}
                onClick={() => setIsMobileMenuOpen(false)}
                className="relative text-neutral-600 dark:text-neutral-300"
              >
                <span className="block">{item.name}</span>
              </Link>
            ))}
            <div className="flex w-full flex-col gap-4 mt-4">
              {isLoggedIn ? (
                <>
                  <Link to="/profile" onClick={() => setIsMobileMenuOpen(false)}>
                    <NavbarButton variant="secondary" className="w-full">
                      Profile
                    </NavbarButton>
                  </Link>
                  <NavbarButton
                    variant="secondary"  className="w-full bg-red-600 text-white hover:bg-red-700"  onClick={handleLogout}
                  >
                    Logout
                  </NavbarButton>
                </>
              ) : (
                <>
                  <Link to="/sign-in" onClick={() => setIsMobileMenuOpen(false)}>
                    <NavbarButton variant="secondary" className="w-full">
                      Sign in
                    </NavbarButton>
                  </Link>
                  <Link to="/sign-up" onClick={() => setIsMobileMenuOpen(false)}>
                    <NavbarButton variant="primary" className="w-full">
                      Sign up
                    </NavbarButton>
                  </Link>
                </>
              )}
              <ThemeToggle />
            </div>
          </MobileNavMenu>
        </MobileNav>
      </Navbar>
      <br />
      <Routes>
        <Route
          path="/sign-in"
          element={<SignIn setIsLoggedIn={setIsLoggedIn} />}
        />
        <Route path="/sign-up" element={<SignUp />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/result" element={<Result />} />
        {NavRoutes.filter(
          (r) => !["/sign-in", "/sign-up"].includes(r.path)
        ).map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
      </Routes>

      <Toaster/>
    </main>
  );
};

export default App;