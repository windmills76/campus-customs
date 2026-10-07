import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="page page-home">
      <section className="hero">
        <h1>Gear up, Bulldogs.</h1>
        <p>
          Campus Customs is where New Haven's campus finds its everyday wardrobe — hoodies for the
          first cold snap, crewnecks for game day, and a tee for every residential college, team,
          and family title in between. Whatever your connection to Yale, there's something here
          with your name on it.
        </p>
        <Link to="/products" className="button-primary">
          Shop the Collection
        </Link>
      </section>

      <section className="home-highlights">
        <div className="highlight-card">
          <h3>For Every Bulldog</h3>
          <p>
            Students, alumni, parents, grandparents — we stock pieces for anyone who claims Yale as
            part of their story, not just the people currently walking through Phelps Gate.
          </p>
        </div>
        <div className="highlight-card">
          <h3>Built on Tradition</h3>
          <p>
            From residential college crests to varsity team wordmarks, our catalog leans into the
            details long-time New Haveners actually recognize.
          </p>
        </div>
        <div className="highlight-card">
          <h3>Honest Stock, Honest Prices</h3>
          <p>
            What you see is what's on the shelf. Our chat assistant will always tell you straight —
            price, size, and whether it's actually in stock.
          </p>
        </div>
      </section>
    </div>
  );
}
