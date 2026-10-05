import React, { useState } from "react";
import AuthLayout from "@/layouts/AuthLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";

const fieldClass =
  "h-11 rounded-lg border-[#232B3D] bg-[#161B27] text-[#F1EDE4] placeholder:text-[#5B6478] " +
  "focus-visible:ring-1 focus-visible:ring-[#D4A24C] focus-visible:ring-offset-0";

export default function LoginPage({ onSubmit, onNavigateToSignUp }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!email || !password) {
      setError("Enter your email and password to continue.");
      return;
    }
    try {
      setLoading(true);
      await onSubmit?.({ email, password, remember });
    } catch (err) {
      setError(err?.message || "Couldn't sign you in. Check your details and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      eyebrow="Welcome back"
      title="Sign in to your account"
      subtitle="Book seats, manage upcoming tickets, and pick up where you left off."
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="email" className="text-sm text-[#C7CCD9]">
            Email
          </Label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={fieldClass}
            autoComplete="email"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="password" className="text-sm text-[#C7CCD9]">
              Password
            </Label>
            <a
              href="/forgot-password"
              className="text-xs text-[#8891A3] hover:text-[#D4A24C]"
            >
              Forgot password?
            </a>
          </div>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={fieldClass}
            autoComplete="current-password"
          />
        </div>

        <div className="flex items-center gap-2">
          <Checkbox
            id="remember"
            checked={remember}
            onCheckedChange={(v) => setRemember(Boolean(v))}
            className="border-[#3A4257] data-[state=checked]:bg-[#D4A24C] data-[state=checked]:border-[#D4A24C]"
          />
          <Label htmlFor="remember" className="text-sm font-normal text-[#8891A3]">
            Keep me signed in
          </Label>
        </div>

        {error ? (
          <p className="rounded-md border border-[#E2574C]/30 bg-[#E2574C]/10 px-3 py-2 text-sm text-[#E2574C]">
            {error}
          </p>
        ) : null}

        <Button
          type="submit"
          disabled={loading}
          className="h-11 rounded-lg bg-[#D4A24C] text-[#0E1220] hover:bg-[#C6923D] font-medium"
        >
          {loading ? "Signing in…" : "Sign in"}
        </Button>
      </form>

      <div className="my-6 flex items-center gap-3">
        <Separator className="flex-1 bg-[#232B3D]" />
        <span className="text-xs text-[#5B6478]">or</span>
        <Separator className="flex-1 bg-[#232B3D]" />
      </div>

      <p className="text-center text-sm text-[#8891A3]">
        New to ReelSeat?{" "}
        <button
          type="button"
          onClick={onNavigateToSignUp}
          className="text-[#D4A24C] hover:underline"
        >
          Create an account
        </button>
      </p>
    </AuthLayout>
  );
}