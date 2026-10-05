import axios from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "../utils/tokenStorage";

export const BASE_URL = "http://127.0.0.1:8001/api/v1";

const axiosClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

axiosClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
let isRefreshing = false;
let pendingRequests = [];

function resolvePending(newAccessToken) {
  pendingRequests.forEach((cb) => cb(newAccessToken));
  pendingRequests = [];
}

axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;
    const isRefreshCall = originalRequest?.url?.includes("/user/token/refresh/");

    if (status === 401 && !originalRequest._retry && !isRefreshCall) {
      if (isRefreshing) {
        // Wait for the in-flight refresh, then retry this request.
        return new Promise((resolve, reject) => {
          pendingRequests.push((newAccessToken) => {
            if (!newAccessToken) {
              reject(error);
              return;
            }
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            resolve(axiosClient(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refresh_token = getRefreshToken();
        if (!refresh_token) throw error;

        // Plain axios call here — going through axiosClient would re-enter these interceptors.
        const { data } = await axios.post(`${BASE_URL}/user/token/refresh/`, {
          refresh_token,
        });

        const newAccessToken = data.access_token ?? data.access;
        setTokens({
          access: newAccessToken,
          refresh: data.refresh_token ?? data.refresh ?? refresh_token,
        });

        resolvePending(newAccessToken);
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return axiosClient(originalRequest);
      } catch (refreshError) {
        resolvePending(null);
        clearTokens();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default axiosClient;