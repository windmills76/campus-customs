import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Home", end: true },
  { to: "/products", label: "Products" },
  { to: "/about", label: "About Us" },
  { to: "/login", label: "Log In" },
  { to: "/create-account", label: "Create Account" },
];

export default function NavBar() {
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
      </nav>
    </header>
  );
}
