import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

const links = [
  { to: "/", label: "Home", end: true },
  { to: "/products", label: "Products" },
  { to: "/about", label: "About Us" },
];

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  // Usability improvement (Problem 9, front-end #2): collapse the nav links
  // behind a hamburger toggle on narrow/mobile screens instead of wrapping.
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  function handleLogout() {
    logout();
    setIsMenuOpen(false);
    navigate("/");
  }

  function closeMenu() {
    setIsMenuOpen(false);
  }

  const linkClass = ({ isActive }: { isActive: boolean }) => (isActive ? "navbar-link active" : "navbar-link");

  return (
    <header className="navbar">
      <NavLink to="/" className="navbar-brand" end onClick={closeMenu}>
        Campus Customs
      </NavLink>
      <button
        type="button"
        className="navbar-toggle"
        aria-label={isMenuOpen ? "Close menu" : "Open menu"}
        aria-expanded={isMenuOpen}
        onClick={() => setIsMenuOpen((open) => !open)}
      >
        <span />
        <span />
        <span />
      </button>
      <nav className={isMenuOpen ? "navbar-links open" : "navbar-links"}>
        {links.map((link) => (
          <NavLink key={link.to} to={link.to} end={link.end} className={linkClass} onClick={closeMenu}>
            {link.label}
          </NavLink>
        ))}
        {user ? (
          <>
            <span className="navbar-greeting">Hi, {user.first_name ?? user.email}</span>
            <button type="button" className="navbar-link navbar-link-button" onClick={handleLogout}>
              Log Out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login" className={linkClass} onClick={closeMenu}>
              Log In
            </NavLink>
            <NavLink to="/create-account" className={linkClass} onClick={closeMenu}>
              Create Account
            </NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
