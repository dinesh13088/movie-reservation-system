import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import Navbar from "@/components/component/Navbar";
import MovieCard from "@/components/component/MovieCard";
import { getMovies } from "@/api/movieApi";

export default function MoviesPage() {
  const navigate = useNavigate();

  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchTerm, setSearchTerm] = useState("");
  const [genre, setGenre] = useState("all");
  const [language, setLanguage] = useState("all");

  // Fetch once; filtering happens in the browser.
  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const { data } = await getMovies();
        if (!cancelled) setMovies(Array.isArray(data) ? data : data.results ?? []);
      } catch (err) {
        if (!cancelled) {
          setError(err?.response?.data?.detail || "Couldn't load movies. Try again.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  // Filter options come from the data itself.
  const genres = useMemo(
    () => ["all", ...[...new Set(movies.flatMap((m) => m.Genres ?? []))].sort()],
    [movies]
  );
  const languages = useMemo(
    () => ["all", ...[...new Set(movies.map((m) => m.Language).filter(Boolean))].sort()],
    [movies]
  );

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    return movies.filter((m) => {
      const matchesSearch = !q || m.Title?.toLowerCase().includes(q);
      const matchesGenre = genre === "all" || m.Genres?.includes(genre);
      const matchesLanguage = language === "all" || m.Language === language;
      return matchesSearch && matchesGenre && matchesLanguage;
    });
  }, [movies, searchTerm, genre, language]);

  const handleViewShowtimes = (movie) => {
    // The API has no id yet, so the title identifies the movie for now.
    navigate(`/movies/${encodeURIComponent(movie.Title)}/showtimes`);
  };

  return (
    <div className="min-h-screen bg-[#0E1220] text-[#F1EDE4]">
      <Navbar searchTerm={searchTerm} onSearchChange={setSearchTerm} />

      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-8 flex flex-col gap-1">
          <h1 className="text-2xl" style={{ fontFamily: "Fraunces, serif", fontWeight: 600 }}>
            Now Showing
          </h1>
          <p className="text-sm text-[#8891A3]">
            Pick a movie to see showtimes and available seats.
          </p>
        </div>

        <div className="mb-8 flex flex-wrap items-center gap-3">
          <div className="flex flex-wrap gap-2">
            {genres.map((g) => (
              <button
                key={g}
                onClick={() => setGenre(g)}
                className={
                  "rounded-full border px-3 py-1.5 text-xs transition-colors " +
                  (genre === g
                    ? "border-[#D4A24C] bg-[#D4A24C]/10 text-[#D4A24C]"
                    : "border-[#232B3D] text-[#8891A3] hover:border-[#3A4257] hover:text-[#C7CCD9]")
                }
              >
                {g === "all" ? "All genres" : g}
              </button>
            ))}
          </div>

          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="ml-auto h-9 rounded-lg border border-[#232B3D] bg-[#161B27] px-3 text-sm text-[#F1EDE4] [color-scheme:dark] focus:outline-none focus:ring-1 focus:ring-[#D4A24C]"
          >
            {languages.map((l) => (
              <option key={l} value={l}>
                {l === "all" ? "All languages" : l}
              </option>
            ))}
          </select>
        </div>

        {error ? (
          <p className="rounded-md border border-[#E2574C]/30 bg-[#E2574C]/10 px-4 py-3 text-sm text-[#E2574C]">
            {error}
          </p>
        ) : null}

        {loading ? (
          <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 lg:grid-cols-5">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="aspect-[500/715] animate-pulse rounded-xl bg-[#161B27]" />
            ))}
          </div>
        ) : filtered.length === 0 && !error ? (
          <div className="flex flex-col items-center justify-center gap-2 py-24 text-center">
            <p className="text-[#C7CCD9]">No movies match your filters.</p>
            <p className="text-sm text-[#5B6478]">Try a different genre, language, or search term.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 lg:grid-cols-5">
            {filtered.map((movie) => (
              <MovieCard key={movie.Title} movie={movie} onViewShowtimes={handleViewShowtimes} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}