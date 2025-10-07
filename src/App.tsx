import { Route, Routes } from "react-router-dom";
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

const App = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItemsForNavbar = navItems.map((item) => ({
    name: item.label,
    link: item.path,
  }));

  return (
    <main>

      <Navbar>

        <NavBody>
          <NavbarLogo />
          <NavItems items={navItemsForNavbar} />
          <div className="flex items-center gap-4 relative z-50">
            <Link to="/sign-in">
              <NavbarButton variant="secondary">Sign in </NavbarButton>
            </Link>
            <Link to="/sign-up">
              <NavbarButton variant="primary">Sign up</NavbarButton>
            </Link>
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
              <Link to="/sign-in" onClick={() => setIsMobileMenuOpen(false)}>
                <NavbarButton variant="secondary" className="w-full">
                  Log in
                </NavbarButton>
              </Link>
              <Link to="/sign-up" onClick={() => setIsMobileMenuOpen(false)}>
                <NavbarButton variant="primary" className="w-full">
                  Sign in
              </NavbarButton>
              </Link>
              <ThemeToggle />
            </div>
          </MobileNavMenu>
        </MobileNav>
      </Navbar>
      <br />
      <Routes>
        {NavRoutes.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
      </Routes>
    </main>
  );
};

export default App;