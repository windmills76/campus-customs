import { useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import "./App.css";
import { AuthProvider } from "./auth";
import { SearchResultsProvider } from "./searchResults";
import NavBar from "./components/NavBar";
import ChatWidget from "./components/ChatWidget";
import ProductMatchesPanel from "./components/ProductMatchesPanel";
import Home from "./pages/Home";
import AboutUs from "./pages/AboutUs";
import Products from "./pages/Products";
import ProductDetail from "./pages/ProductDetail";
import Login from "./pages/Login";
import CreateAccount from "./pages/CreateAccount";

// Without this, navigating from a product card lower on the page (e.g. one
// surfaced by the dynamic chat search panel) leaves the detail view's top
// scrolled out of view, looking like the click did nothing.
function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

export default function App() {
  return (
    <AuthProvider>
      <SearchResultsProvider>
        <div className="app-shell">
          <ScrollToTop />
          <NavBar />
          <ProductMatchesPanel />
          <main className="app-main">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/products" element={<Products />} />
              <Route path="/products/:productId" element={<ProductDetail />} />
              <Route path="/about" element={<AboutUs />} />
              <Route path="/login" element={<Login />} />
              <Route path="/create-account" element={<CreateAccount />} />
            </Routes>
          </main>
          <ChatWidget />
        </div>
      </SearchResultsProvider>
    </AuthProvider>
  );
}
