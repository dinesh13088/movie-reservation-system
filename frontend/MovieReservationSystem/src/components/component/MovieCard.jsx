import React, { useState } from "react";
import { Film } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function MovieCard({ movie, onViewShowtimes }) {
  const { Title, Image_URL, Rating, Language, Genres = [] } = movie;
  const [imgFailed, setImgFailed] = useState(false);

  return (
    <div className="group overflow-hidden rounded-xl border border-[#232B3D] bg-[#161B27] transition-colors hover:border-[#D4A24C]/50">
      <div className="relative aspect-[500/715] w-full overflow-hidden bg-[#1C2333]">
        {Image_URL && !imgFailed ? (
          <img
            src={Image_URL}
            alt={Title}
            loading="lazy"
            referrerPolicy="no-referrer"
            onError={() => setImgFailed(true)}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center gap-2 text-[#3A4257]">
            <Film className="h-10 w-10" />
            <span className="text-xs">No poster</span>
          </div>
        )}
        {Rating ? (
          <div className="absolute right-2 top-2 rounded-md bg-[#0E1220]/85 px-2 py-1 text-xs font-medium text-[#D4A24C]">
            {Rating}
          </div>
        ) : null}
      </div>

      <div className="flex flex-col gap-2 p-4">
        <h3 className="line-clamp-1 text-sm font-medium text-[#F1EDE4]" title={Title}>
          {Title}
        </h3>

        <p className="text-xs text-[#5B6478]">{Language}</p>

        <div className="flex flex-wrap gap-1.5 text-xs text-[#8891A3]">
          {Genres.slice(0, 3).map((g) => (
            <span key={g} className="rounded-full border border-[#232B3D] px-2 py-0.5">
              {g}
            </span>
          ))}
        </div>

        <Button
          onClick={() => onViewShowtimes(movie)}
          className="mt-2 h-9 rounded-lg bg-[#D4A24C] text-sm font-medium text-[#0E1220] hover:bg-[#C6923D]"
        >
          View Showtimes
        </Button>
      </div>
    </div>
  );
}