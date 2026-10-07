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

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <header className="navbar">
      <NavLink to="/" className="navbar-brand" end>
        Campus Customs
      </NavLink>
      <nav className="navbar-links">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => (isActive ? "navbar-link active" : "navbar-link")}
          >
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
            <NavLink to="/login" className={({ isActive }) => (isActive ? "navbar-link active" : "navbar-link")}>
              Log In
            </NavLink>
            <NavLink
              to="/create-account"
              className={({ isActive }) => (isActive ? "navbar-link active" : "navbar-link")}
            >
              Create Account
            </NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
