import { createError } from "h3";

// Helper to get backend URL from runtime config
export const getBackendUrl = () => {
  const config = useRuntimeConfig();
  return config.apiBaseUrl || "http://localhost:8000";
};

// Helper to proxy requests to backend
export const proxyToBackend = async (
  event: any,
  path: string,
  options: RequestInit = {}
) => {
  const config = useRuntimeConfig();
  const backendUrl = config.apiBaseUrl || "http://localhost:8000";
  const url = `${backendUrl}/api/v1${path}`;

  // Get authorization header from request
  const authHeader = getHeader(event, "authorization");

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(authHeader && { Authorization: authHeader }),
  };

  console.log(`[Proxy] ${options.method || "GET"} ${url}`);

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...(options.headers || {}),
      },
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      console.log(`[Proxy] Error ${response.status}: ${JSON.stringify(data)}`);
      throw createError({
        statusCode: response.status,
        statusMessage: response.statusText,
        data: data,
      });
    }

    return data;
  } catch (error: any) {
    // If it's already an H3 error, re-throw it
    if (error.statusCode) {
      throw error;
    }

    // Log the actual error for debugging
    console.error(`[Proxy] Connection error to ${url}:`, error.message);

    throw createError({
      statusCode: 502,
      statusMessage: "Bad Gateway",
      data: {
        detail: `Cannot connect to backend at ${backendUrl}. Is the backend server running?`,
        error: error.message,
      },
    });
  }
};
