import React, { useState } from "react";
import AuthLayout from "@/layouts/AuthLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";

const fieldClass =
  "h-11 rounded-lg border-[#232B3D] bg-[#161B27] text-[#F1EDE4] placeholder:text-[#5B6478] " +
  "focus-visible:ring-1 focus-visible:ring-[#D4A24C] focus-visible:ring-offset-0";

function passwordStrength(pw) {
  if (!pw) return { label: "", pct: 0 };
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  const levels = [
    { label: "Too short", pct: 15 },
    { label: "Weak", pct: 35 },
    { label: "Okay", pct: 60 },
    { label: "Good", pct: 80 },
    { label: "Strong", pct: 100 },
  ];
  return levels[score];
}

export default function SignUpPage({ onSubmit, onNavigateToLogin }) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agree, setAgree] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const strength = passwordStrength(password);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!fullName || !email || !password || !confirmPassword) {
      setError("Fill in every field to create your account.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords don't match.");
      return;
    }
    if (!agree) {
      setError("Accept the terms to continue.");
      return;
    }

    try {
      setLoading(true);
      await onSubmit?.({ fullName, email, password });
    } catch (err) {
      setError(err?.message || "Couldn't create your account. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      eyebrow="Get started"
      title="Create your account"
      subtitle="Save your seat preferences and book faster next time."
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="fullName" className="text-sm text-[#C7CCD9]">
            Full name
          </Label>
          <Input
            id="fullName"
            type="text"
            placeholder="Jane Doe"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className={fieldClass}
            autoComplete="name"
          />
        </div>

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
          <Label htmlFor="password" className="text-sm text-[#C7CCD9]">
            Password
          </Label>
          <Input
            id="password"
            type="password"
            placeholder="At least 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={fieldClass}
            autoComplete="new-password"
          />
          {password ? (
            <div className="mt-1 flex items-center gap-2">
              <div className="h-1 flex-1 overflow-hidden rounded-full bg-[#232B3D]">
                <div
                  className="h-full rounded-full bg-[#D4A24C] transition-all"
                  style={{ width: `${strength.pct}%` }}
                />
              </div>
              <span className="text-xs text-[#5B6478]">{strength.label}</span>
            </div>
          ) : null}
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="confirmPassword" className="text-sm text-[#C7CCD9]">
            Confirm password
          </Label>
          <Input
            id="confirmPassword"
            type="password"
            placeholder="••••••••"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className={fieldClass}
            autoComplete="new-password"
          />
        </div>

        <div className="flex items-start gap-2">
          <Checkbox
            id="agree"
            checked={agree}
            onCheckedChange={(v) => setAgree(Boolean(v))}
            className="mt-0.5 border-[#3A4257] data-[state=checked]:bg-[#D4A24C] data-[state=checked]:border-[#D4A24C]"
          />
          <Label htmlFor="agree" className="text-sm font-normal leading-snug text-[#8891A3]">
            I agree to the Terms of Service and Privacy Policy
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
          {loading ? "Creating account…" : "Create account"}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-[#8891A3]">
        Already have an account?{" "}
        <button
          type="button"
          onClick={onNavigateToLogin}
          className="text-[#D4A24C] hover:underline"
        >
          Sign in
        </button>
      </p>
    </AuthLayout>
  );
}