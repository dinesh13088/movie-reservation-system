import React from "react";
import { Navigate } from "react-router";
import { getAccessToken } from "@/utils/tokenStorage";

export default function ProtectedRoute({ children }) {
  if (!getAccessToken()) return <Navigate to="/login" replace />;
  return children;
}