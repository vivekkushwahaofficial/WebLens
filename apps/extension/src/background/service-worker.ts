import { analyzeUrl } from "../services/weblens-api.js";

console.log("WebLens service worker started");

const lastAnalyzedUrls = new Map<number, string>();

/**
 * Detect normal tab navigation.
 *
 * This does not block navigation itself.
 * The content script performs the actual page-level gate.
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  const url = changeInfo.url ?? tab.url;

  if (!url || !isAnalyzableUrl(url)) {
    return;
  }

  if (lastAnalyzedUrls.get(tabId) === url) {
    return;
  }

  lastAnalyzedUrls.set(tabId, url);

  console.log("WebLens: navigation detected:", url);
});

chrome.tabs.onRemoved.addListener((tabId) => {
  lastAnalyzedUrls.delete(tabId);
});

/**
 * Handle messages from content scripts.
 */
chrome.runtime.onMessage.addListener(
  (message, _sender, sendResponse) => {
    if (
      message?.type !== "ANALYZE_LINK" &&
      message?.type !== "ANALYZE_PAGE"
    ) {
      return;
    }

    const url = message.url;

    if (
      typeof url !== "string" ||
      !isAnalyzableUrl(url)
    ) {
      sendResponse({
        error: "Invalid URL",
      });

      return;
    }

    console.log(
      `WebLens: analyzing ${message.type}:`,
      url,
    );

    analyzeUrl(url)
      .then((result) => {
        console.log(
          `WebLens: ${message.type} result:`,
          result,
        );

        sendResponse(result);
      })
      .catch((error) => {
        console.error(
          `WebLens: ${message.type} analysis failed:`,
          error,
        );

        sendResponse({
          error:
            error instanceof Error
              ? error.message
              : "Unable to analyze URL.",
        });
      });

    return true;
  },
);

function isAnalyzableUrl(url: string): boolean {
  return (
    url.startsWith("http://") ||
    url.startsWith("https://")
  );
}
