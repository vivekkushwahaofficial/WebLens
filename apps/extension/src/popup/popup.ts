import { analyzeUrl } from "../services/weblens-api.js";
import type { AnalyzeResponse } from "../types/api.js";

const loadingElement = getElement("loading");
const resultElement = getElement("result");
const errorElement = getElement("error");

const verdictElement = getElement("verdict");
const riskScoreElement = getElement("risk-score");
const confidenceElement = getElement("confidence");
const detectionElement = getElement("detection");
const urlElement = getElement("url");
const reasonsElement = getElement("reasons");
const riskCardElement = getElement("risk-card");

const errorMessageElement = getElement("error-message");

const retryButton = getButton("retry");
const reanalyzeButton = getButton("reanalyze");

retryButton.addEventListener("click", analyzeCurrentTab);
reanalyzeButton.addEventListener("click", analyzeCurrentTab);

void analyzeCurrentTab();

function getElement(id: string): HTMLElement {
  const element = document.getElementById(id);

  if (!element) {
    throw new Error(`WebLens popup element not found: ${id}`);
  }

  return element;
}

function getButton(id: string): HTMLButtonElement {
  const element = getElement(id);

  if (!(element instanceof HTMLButtonElement)) {
    throw new Error(`WebLens element is not a button: ${id}`);
  }

  return element;
}

async function analyzeCurrentTab(): Promise<void> {
  showLoading();

  try {
    const tabs = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });

    const tab = tabs[0];
    const url = tab?.url;

    if (!url) {
      throw new Error("The current tab does not have a URL.");
    }

    if (!isAnalyzableUrl(url)) {
      throw new Error(
        "WebLens can only analyze HTTP and HTTPS pages.",
      );
    }

    const result = await analyzeUrl(url);

    renderResult(result);
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Unable to analyze the current page.";

    showError(message);
  }
}

function isAnalyzableUrl(url: string): boolean {
  return url.startsWith("http://") || url.startsWith("https://");
}

function renderResult(result: AnalyzeResponse): void {
  loadingElement.classList.add("hidden");
  errorElement.classList.add("hidden");
  resultElement.classList.remove("hidden");

  const riskCategory = getRiskCategory(result.risk_score);

  riskCardElement.dataset.risk = riskCategory;

  verdictElement.textContent = formatRiskLabel(riskCategory);

  riskScoreElement.textContent = String(
    Math.round(result.risk_score),
  );

  detectionElement.textContent = extractDetection(result);

  confidenceElement.textContent =
    result.confidence === null
      ? "N/A"
      : `${(result.confidence * 100).toFixed(1)}%`;

  urlElement.textContent = result.url;
  urlElement.title = result.url;

  reasonsElement.replaceChildren();

  for (const reason of result.reasons) {
    const item = document.createElement("li");

    item.textContent = reason;

    reasonsElement.appendChild(item);
  }
}

function extractDetection(result: AnalyzeResponse): string {
  const reason = result.reasons[0]?.toLowerCase() ?? "";

  if (reason.includes("phishing")) {
    return "Phishing";
  }

  if (reason.includes("malware")) {
    return "Malware";
  }

  if (reason.includes("defacement")) {
    return "Defacement";
  }

  if (reason.includes("benign")) {
    return "Benign";
  }

  return "Suspicious URL";
}

function getRiskCategory(score: number): string {
  if (score >= 70) {
    return "high";
  }

  if (score >= 40) {
    return "medium";
  }

  return "low";
}

function formatRiskLabel(category: string): string {
  return `${category.toUpperCase()} RISK`;
}

function showLoading(): void {
  loadingElement.classList.remove("hidden");
  resultElement.classList.add("hidden");
  errorElement.classList.add("hidden");
}

function showError(message: string): void {
  loadingElement.classList.add("hidden");
  resultElement.classList.add("hidden");
  errorElement.classList.remove("hidden");

  errorMessageElement.textContent = message;
}
