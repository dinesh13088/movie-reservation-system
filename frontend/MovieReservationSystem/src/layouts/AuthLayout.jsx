import React from "react";


function SeatMap() {
  const rows = 5;
  const cols = 9;
  const taken = new Set(["1-3", "1-4", "2-4", "2-5", "2-6", "3-2", "3-6", "4-4"]);

  return (
    <div className="select-none">
      <div className="mx-auto mb-8 h-1.5 w-40 rounded-full bg-gradient-to-r from-transparent via-[#D4A24C]/70 to-transparent" />
      <div className="flex flex-col items-center gap-2">
        {Array.from({ length: rows }).map((_, r) => (
          <div key={r} className="flex gap-2">
            {Array.from({ length: cols }).map((_, c) => {
              const key = `${r}-${c}`;
              const isTaken = taken.has(key);
              return (
                <span
                  key={key}
                  className={
                    "h-2.5 w-2.5 rounded-[3px] border transition-colors " +
                    (isTaken
                      ? "border-[#D4A24C] bg-[#D4A24C]"
                      : "border-[#3A4257] bg-transparent")
                  }
                />
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AuthLayout({ eyebrow, title, subtitle, children }) {
  return (
    <div
      className="flex min-h-screen w-full bg-[#0E1220] text-[#F1EDE4]"
      style={{ fontFamily: "Inter, sans-serif" }}
    >
      {/* Left: cinema panel, hidden on small screens */}
      <div className="relative hidden w-[42%] flex-col justify-between overflow-hidden border-r border-[#232B3D] px-12 py-14 lg:flex">
        {/* film-strip sprocket accent along the right edge of this panel */}
        <div
          className="pointer-events-none absolute right-0 top-0 h-full w-3 opacity-40"
          style={{
            backgroundImage:
              "radial-gradient(circle, #3A4257 2px, transparent 2.2px)",
            backgroundSize: "100% 22px",
            backgroundPosition: "center",
          }}
        />

        <div
          className="text-2xl tracking-tight"
          style={{ fontFamily: "Fraunces, serif", fontWeight: 600 }}
        >
          Reel<span className="text-[#D4A24C]">Seat</span>
        </div>

        <div className="flex flex-col items-center py-10">
          <SeatMap />
          <p className="mt-8 max-w-[280px] text-center text-sm leading-relaxed text-[#8891A3]">
            Pick your movie, pick your seat, walk in knowing exactly where
            you're sitting.
          </p>
        </div>

        <p className="text-xs text-[#8891A3]">
          Now booking across every screen, every showtime.
        </p>
      </div>

      {/* Right: form column */}
      <div className="flex flex-1 flex-col items-center justify-center px-6 py-14">
        <div className="w-full max-w-[380px]">
          {/* mobile wordmark, since the left panel is hidden below lg */}
          <div
            className="mb-10 text-xl lg:hidden"
            style={{ fontFamily: "Fraunces, serif", fontWeight: 600 }}
          >
            Reel<span className="text-[#D4A24C]">Seat</span>
          </div>

          {eyebrow ? (
            <p className="mb-2 text-sm text-[#8891A3]">{eyebrow}</p>
          ) : null}
          <h1
            className="mb-2 text-[28px] leading-tight"
            style={{ fontFamily: "Fraunces, serif", fontWeight: 600 }}
          >
            {title}
          </h1>
          {subtitle ? (
            <p className="mb-8 text-sm text-[#8891A3]">{subtitle}</p>
          ) : (
            <div className="mb-8" />
          )}

          {children}
        </div>
      </div>
    </div>
  );
}