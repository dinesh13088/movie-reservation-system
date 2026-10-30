import axios from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "../utils/tokenStorage";

export const USERS_BASE_URL = "http://127.0.0.1:8001/api/v1";
export const MOVIES_BASE_URL = "/api/v1";

// Token refresh always lives on the Users Service, whichever service's call got the 401.
const REFRESH_URL = `${USERS_BASE_URL}/user/token/refresh/`;

// Shared across all clients so concurrent 401s trigger only one refresh.
let isRefreshing = false;
let pendingRequests = [];

function resolvePending(newAccessToken) {
  pendingRequests.forEach((cb) => cb(newAccessToken));
  pendingRequests = [];
}

export function createApiClient(baseURL) {
  const client = axios.create({
    baseURL,
    headers: { "Content-Type": "application/json" },
  });

  client.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      const status = error.response?.status;
      const isRefreshCall = originalRequest?.url?.includes("/user/token/refresh/");

      if ((status === 401 || status === 403) && !originalRequest._retry && !isRefreshCall) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            pendingRequests.push((newAccessToken) => {
              if (!newAccessToken) return reject(error);
              originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
              resolve(client(originalRequest));
            });
          });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          const refresh_token = getRefreshToken();
          if (!refresh_token) throw error;

          const { data } = await axios.post(REFRESH_URL, { refresh_token });
          const newAccessToken = data.accessToken ?? data.access_token ?? data.access;
          setTokens({
            access: newAccessToken,
            refresh: data.refreshToken ?? data.refresh_token ?? data.refresh ?? refresh_token,
          });

          resolvePending(newAccessToken);
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return client(originalRequest);
        } catch (refreshError) {
          resolvePending(null);
          clearTokens();
          if (typeof window !== "undefined") window.location.href = "/login";
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      return Promise.reject(error);
    }
  );

  return client;
}