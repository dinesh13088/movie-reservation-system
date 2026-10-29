import React from "react";
import { useNavigate } from "react-router";
import { Search, LogOut, Ticket } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { clearTokens } from "@/utils/tokenStorage";

export default function Navbar({ searchTerm, onSearchChange }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    clearTokens();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-10 border-b border-[#232B3D] bg-[#0E1220]/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-6 py-4">
        <div
          className="text-xl tracking-tight text-[#F1EDE4]"
          style={{ fontFamily: "Fraunces, serif", fontWeight: 600 }}
        >
          Reel<span className="text-[#D4A24C]">Seat</span>
        </div>

        <div className="relative flex-1 max-w-md">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#5B6478]" />
          <Input
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search movies…"
            className="h-10 rounded-lg border-[#232B3D] bg-[#161B27] pl-9 text-[#F1EDE4] placeholder:text-[#5B6478] focus-visible:ring-1 focus-visible:ring-[#D4A24C] focus-visible:ring-offset-0"
          />
        </div>

        <div className="ml-auto flex items-center gap-2">
          <Button
            variant="ghost"
            className="gap-2 text-[#C7CCD9] hover:bg-[#161B27] hover:text-[#F1EDE4]"
            onClick={() => navigate("/my-tickets")}
          >
            <Ticket className="h-4 w-4" />
            My Tickets
          </Button>
          <Button
            variant="ghost"
            className="gap-2 text-[#C7CCD9] hover:bg-[#161B27] hover:text-[#E2574C]"
            onClick={handleLogout}
          >
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
}