import { Route, Routes, useNavigate, Navigate } from "react-router";
import React from 'react'
import LoginPage from "@/pages/LoginPage";
import SignUpPage from "@/pages/SignUpPage";
import ProtectedRoute from "@/components/component/ProtectedRoute";
import MoviesPage from "@/pages/MoviesPage";

function LoginRoute() {
  const navigate = useNavigate();
  return (
    <LoginPage
      onSuccess={() => navigate("/")}
      onNavigateToSignUp={() => navigate("/signup")}
    />
  );
}

function SignUpRoute() {
  const navigate = useNavigate();
  return (
    <SignUpPage
      onSuccess={() => navigate("/login")}
      onNavigateToLogin={() => navigate("/login")}
    />
  );
}

export default function AppRoutes() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route path="/signup" element={<SignUpRoute />} />
        <Route path="/"
          element={
            <ProtectedRoute>
              <MoviesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <MoviesPage />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </>
  )
}


