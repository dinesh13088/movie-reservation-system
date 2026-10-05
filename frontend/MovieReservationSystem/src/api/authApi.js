import axiosClient from "./axiosClient";

export function registerUser(payload) {
  return axiosClient.post("/user/register/", payload);
}
export function loginUser(payload) {
  return axiosClient.post("/user/auth/login/", payload);
}

export function refreshAccessToken(refresh_token) {
  return axiosClient.post("/user/token/refresh/", { refresh_token });
}