import { createContext, useContext, useState, type ReactNode } from "react";
import type { Product } from "./types";

interface SearchResultsValue {
  query: string | null;
  matches: Product[];
  setMatches: (query: string, matches: Product[]) => void;
  clear: () => void;
}

const SearchResultsContext = createContext<SearchResultsValue | undefined>(undefined);

export function SearchResultsProvider({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState<string | null>(null);
  const [matches, setMatchesState] = useState<Product[]>([]);

  function setMatches(nextQuery: string, nextMatches: Product[]) {
    setQuery(nextQuery);
    setMatchesState(nextMatches);
  }

  function clear() {
    setQuery(null);
    setMatchesState([]);
  }

  return (
    <SearchResultsContext.Provider value={{ query, matches, setMatches, clear }}>
      {children}
    </SearchResultsContext.Provider>
  );
}

export function useSearchResults(): SearchResultsValue {
  const ctx = useContext(SearchResultsContext);
  if (!ctx) throw new Error("useSearchResults must be used within a SearchResultsProvider");
  return ctx;
}
