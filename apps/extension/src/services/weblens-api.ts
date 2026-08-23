import type { AnalyzeRequest, AnalyzeResponse } from "../types/api.js";

const API_BASE_URL = "http://127.0.0.1:8000";
const ANALYZE_ENDPOINT = `${API_BASE_URL}/api/v1/analyze`;

const REQUEST_TIMEOUT_MS = 10_000;

export async function analyzeUrl(
  url: string,
): Promise<AnalyzeResponse> {
  const controller = new AbortController();

  const timeoutId = setTimeout(() => {
    controller.abort();
  }, REQUEST_TIMEOUT_MS);

  const request: AnalyzeRequest = {
    url,
  };

  try {
    const response = await fetch(ANALYZE_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(
        `WebLens API request failed with status ${response.status}`,
      );
    }

    return (await response.json()) as AnalyzeResponse;
  } finally {
    clearTimeout(timeoutId);
  }
}
