console.log("WebLens: link interceptor started");

// Analyze the current page as soon as the content script loads.
// This handles direct navigation, bookmarks, refreshes, etc.
void analyzeCurrentPage();

/**
 * Analyze the URL of the page that is currently being loaded.
 */
function analyzeCurrentPage(): void {
  const currentUrl = window.location.href;

  if (!isAnalyzableUrl(currentUrl)) {
    return;
  }

  console.log(
    "WebLens: analyzing current page:",
    currentUrl,
  );

  showCheckingOverlay();

  chrome.runtime.sendMessage(
    {
      type: "ANALYZE_PAGE",
      url: currentUrl,
    },
    (response) => {
      if (chrome.runtime.lastError) {
        console.error(
          "WebLens: current page analysis failed:",
          chrome.runtime.lastError.message,
        );

        removeCheckingOverlay();
        return;
      }

      handleCurrentPageResponse(
        response,
        currentUrl,
      );
    },
  );
}

/**
 * Handle the ML result for the current page.
 */
function handleCurrentPageResponse(
  response: unknown,
  currentUrl: string,
): void {
  if (
    !response ||
    typeof response !== "object" ||
    !("risk_score" in response) ||
    !("verdict" in response)
  ) {
    console.error(
      "WebLens: invalid current page analysis response",
    );

    removeCheckingOverlay();
    return;
  }

  const result = response as AnalysisResult;

  console.log(
    "WebLens: current page analysis result:",
    result,
  );

  /*
   * LOW RISK
   *
   * Remove the temporary checking screen
   * and allow the page to continue normally.
   */
  if (result.risk_score < 40) {
    removeCheckingOverlay();
    return;
  }

  /*
   * MEDIUM / HIGH RISK
   *
   * Remove the checking screen and show
   * the security warning.
   */
  removeCheckingOverlay();

  showWarning(
    currentUrl,
    result,
  );
}

/**
 * Intercept clicks on HTTP/HTTPS links.
 *
 * This protects navigation from links inside
 * already-loaded webpages.
 */
document.addEventListener(
  "click",
  (event) => {
    const mouseEvent = event as MouseEvent;

    // Only handle normal left-clicks.
    if (mouseEvent.button !== 0) {
      return;
    }

    // Do not interfere with modified clicks.
    if (
      mouseEvent.ctrlKey ||
      mouseEvent.metaKey ||
      mouseEvent.shiftKey ||
      mouseEvent.altKey
    ) {
      return;
    }

    const target = event.target;

    if (!(target instanceof Element)) {
      return;
    }

    const link = target.closest("a");

    if (!(link instanceof HTMLAnchorElement)) {
      return;
    }

    const destinationUrl = link.href;

    if (!isAnalyzableUrl(destinationUrl)) {
      return;
    }

    /*
     * Stop the browser from navigating immediately.
     *
     * WebLens will analyze the destination first.
     */
    event.preventDefault();

    console.log(
      "WebLens: intercepted link:",
      destinationUrl,
    );

    chrome.runtime.sendMessage(
      {
        type: "ANALYZE_LINK",
        url: destinationUrl,
      },
      (response) => {
        if (chrome.runtime.lastError) {
          console.error(
            "WebLens: failed to analyze link:",
            chrome.runtime.lastError.message,
          );

          /*
           * If WebLens itself fails, don't permanently
           * trap the user on the current page.
           */
          window.location.href =
            destinationUrl;

          return;
        }

        handleAnalysisResponse(
          response,
          destinationUrl,
        );
      },
    );
  },
  true,
);

/**
 * Check whether a URL can be analyzed.
 */
function isAnalyzableUrl(
  url: string,
): boolean {
  return (
    url.startsWith("http://") ||
    url.startsWith("https://")
  );
}

/**
 * Handle the analysis result for a clicked link.
 */
function handleAnalysisResponse(
  response: unknown,
  destinationUrl: string,
): void {
  if (
    !response ||
    typeof response !== "object" ||
    !("risk_score" in response) ||
    !("verdict" in response)
  ) {
    console.error(
      "WebLens: invalid analysis response",
    );

    window.location.href =
      destinationUrl;

    return;
  }

  const result =
    response as AnalysisResult;

  console.log(
    "WebLens: link analysis result:",
    result,
  );

  /*
   * HIGH RISK
   */
  if (result.risk_score >= 70) {
    showWarning(
      destinationUrl,
      result,
    );

    return;
  }

  /*
   * MEDIUM RISK
   */
  if (result.risk_score >= 40) {
    showWarning(
      destinationUrl,
      result,
    );

    return;
  }

  /*
   * LOW RISK
   *
   * Allow navigation normally.
   */
  window.location.href =
    destinationUrl;
}

/**
 * Show the temporary "checking" screen.
 */
function showCheckingOverlay(): void {
  // Prevent duplicate overlays.
  removeCheckingOverlay();

  const overlay =
    document.createElement("div");

  overlay.id =
    "weblens-checking";

  overlay.innerHTML = `
    <div class="weblens-checking-backdrop">
      <div class="weblens-checking-card">

        <div class="weblens-checking-icon">
          W
        </div>

        <div class="weblens-checking-title">
          WebLens
        </div>

        <div class="weblens-checking-label">
          SECURITY CHECK
        </div>

        <div class="weblens-checking-text">
          Checking this page for phishing
          and malicious activity...
        </div>

        <div class="weblens-checking-spinner"></div>

        <div class="weblens-checking-footer">
          WebLens · Local analysis
        </div>

      </div>
    </div>
  `;

  const style =
    document.createElement("style");

  style.id =
    "weblens-checking-style";

  style.textContent = `
    #weblens-checking {
      all: initial;
    }

    .weblens-checking-backdrop {
      position: fixed;
      inset: 0;
      z-index: 2147483647;

      display: flex;
      align-items: center;
      justify-content: center;

      padding: 24px;
      box-sizing: border-box;

      background:
        rgba(15, 23, 42, 0.96);

      font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
    }

    .weblens-checking-card {
      width: min(440px, 100%);

      box-sizing: border-box;

      padding: 36px;

      border-radius: 22px;

      background: #ffffff;

      color: #0f172a;

      text-align: center;

      box-shadow:
        0 24px 80px
        rgba(0, 0, 0, 0.40);
    }

    .weblens-checking-icon {
      width: 58px;
      height: 58px;

      margin: 0 auto 18px;

      display: flex;
      align-items: center;
      justify-content: center;

      border-radius: 17px;

      background: #0f172a;
      color: #ffffff;

      font-size: 27px;
      font-weight: 800;
    }

    .weblens-checking-title {
      margin-bottom: 6px;

      color: #0f172a;

      font-size: 25px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }

    .weblens-checking-label {
      margin-bottom: 14px;

      color: #64748b;

      font-size: 11px;
      font-weight: 700;

      letter-spacing: 0.16em;
    }

    .weblens-checking-text {
      max-width: 330px;

      margin: 0 auto;

      color: #64748b;

      font-size: 14px;
      line-height: 1.6;
    }

    .weblens-checking-spinner {
      width: 30px;
      height: 30px;

      margin: 24px auto 0;

      border:
        3px solid #e2e8f0;

      border-top-color:
        #0f172a;

      border-radius: 50%;

      animation:
        weblens-spin
        0.8s linear infinite;
    }

    .weblens-checking-footer {
      margin-top: 24px;

      color: #94a3b8;

      font-size: 11px;
    }

    @keyframes weblens-spin {
      to {
        transform: rotate(360deg);
      }
    }
  `;

  document.documentElement.appendChild(
    style,
  );

  document.documentElement.appendChild(
    overlay,
  );
}

/**
 * Remove the temporary checking screen.
 */
function removeCheckingOverlay(): void {
  document
    .getElementById(
      "weblens-checking",
    )
    ?.remove();

  document
    .getElementById(
      "weblens-checking-style",
    )
    ?.remove();
}

/**
 * Show the security warning.
 */
function showWarning(
  destinationUrl: string,
  result: AnalysisResult,
): void {
  const existingWarning =
    document.getElementById(
      "weblens-warning",
    );

  existingWarning?.remove();

  const overlay =
    document.createElement("div");

  overlay.id =
    "weblens-warning";

  const warningTitle =
    getWarningTitle(
      result.risk_score,
    );

  const riskLabel =
    getRiskLabel(
      result.risk_score,
    );

  const reason =
    result.reasons[0] ??
    "WebLens detected suspicious characteristics.";

  overlay.innerHTML = `
    <div class="weblens-warning-backdrop">
      <div class="weblens-warning-card">

        <div class="weblens-warning-icon">
          !
        </div>

        <div class="weblens-warning-brand">
          WEBLENS
        </div>

        <div class="weblens-warning-label">
          SECURITY WARNING
        </div>

        <h2>
          ${escapeHtml(warningTitle)}
        </h2>

        <div class="weblens-warning-risk">
          ${escapeHtml(riskLabel)}
        </div>

        <div class="weblens-warning-score">
          Risk Score:
          <strong>
            ${Math.round(result.risk_score)}/100
          </strong>
        </div>

        <div class="weblens-warning-url">
          ${escapeHtml(destinationUrl)}
        </div>

        <div class="weblens-warning-reason">
          <strong>
            Why we flagged this
          </strong>

          <span>
            ${escapeHtml(reason)}
          </span>
        </div>

        <div class="weblens-warning-actions">

          <button
            id="weblens-go-back"
            type="button"
          >
            Stay Safe
          </button>

          <button
            id="weblens-continue"
            type="button"
          >
            Continue Anyway
          </button>

        </div>

      </div>
    </div>
  `;

  const style =
    document.createElement("style");

  style.id =
    "weblens-warning-style";

  style.textContent = `
    #weblens-warning {
      all: initial;
    }

    .weblens-warning-backdrop {
      position: fixed;
      inset: 0;

      z-index: 2147483647;

      display: flex;
      align-items: center;
      justify-content: center;

      padding: 24px;

      box-sizing: border-box;

      background:
        rgba(10, 15, 25, 0.76);

      font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
    }

    .weblens-warning-card {
      width: min(520px, 100%);

      box-sizing: border-box;

      padding: 32px;

      border-radius: 22px;

      background: #ffffff;

      color: #0f172a;

      box-shadow:
        0 24px 80px
        rgba(0, 0, 0, 0.40);
    }

    .weblens-warning-icon {
      width: 54px;
      height: 54px;

      margin-bottom: 18px;

      display: flex;
      align-items: center;
      justify-content: center;

      border-radius: 50%;

      background: #fee2e2;

      color: #dc2626;

      font-size: 29px;
      font-weight: 800;
    }

    .weblens-warning-brand {
      margin-bottom: 5px;

      color: #64748b;

      font-size: 11px;
      font-weight: 800;

      letter-spacing: 0.14em;
    }

    .weblens-warning-label {
      margin-bottom: 8px;

      color: #94a3b8;

      font-size: 11px;
      font-weight: 700;

      letter-spacing: 0.12em;
    }

    .weblens-warning-card h2 {
      margin: 0 0 10px;

      color: #dc2626;

      font-size: 30px;
      line-height: 1.15;
      font-weight: 800;
    }

    .weblens-warning-risk {
      display: inline-block;

      margin-bottom: 18px;

      padding: 6px 10px;

      border-radius: 999px;

      background: #fee2e2;

      color: #b91c1c;

      font-size: 12px;
      font-weight: 700;
    }

    .weblens-warning-score {
      margin: 0 0 18px;

      color: #64748b;

      font-size: 16px;
    }

    .weblens-warning-score strong {
      color: #0f172a;

      font-size: 21px;
    }

    .weblens-warning-url {
      margin: 0 0 18px;

      padding: 13px;

      border-radius: 11px;

      background: #f1f5f9;

      color: #334155;

      font-size: 13px;

      line-height: 1.5;

      overflow-wrap: anywhere;
    }

    .weblens-warning-reason {
      display: flex;
      flex-direction: column;

      gap: 6px;

      margin-bottom: 24px;

      color: #475569;

      font-size: 14px;

      line-height: 1.6;
    }

    .weblens-warning-reason strong {
      color: #0f172a;

      font-size: 15px;
    }

    .weblens-warning-actions {
      display: flex;

      gap: 12px;
    }

    .weblens-warning-actions button {
      flex: 1;

      min-height: 46px;

      border: 0;

      border-radius: 11px;

      padding: 0 16px;

      cursor: pointer;

      font-family: inherit;

      font-size: 14px;

      font-weight: 700;
    }

    #weblens-go-back {
      background: #0f172a;

      color: #ffffff;
    }

    #weblens-go-back:hover {
      background: #1e293b;
    }

    #weblens-continue {
      background: #e2e8f0;

      color: #334155;
    }

    #weblens-continue:hover {
      background: #cbd5e1;
    }

    @media (max-width: 520px) {
      .weblens-warning-card {
        padding: 24px;
      }

      .weblens-warning-actions {
        flex-direction: column;
      }
    }
  `;

  document.documentElement.appendChild(
    style,
  );

  document.documentElement.appendChild(
    overlay,
  );

  const staySafeButton =
    document.getElementById(
      "weblens-go-back",
    );

  const continueButton =
    document.getElementById(
      "weblens-continue",
    );

  staySafeButton?.addEventListener(
    "click",
    () => {
      /*
       * For a clicked link, we simply remain
       * on the current page.
       *
       * For a directly loaded page, the current
       * page has already loaded behind the overlay.
       * Removing the warning therefore reveals it.
       *
       * A future version can replace this with
       * chrome.tabs.goBack() / an interstitial
       * architecture for stricter blocking.
       */
      overlay.remove();
      style.remove();
    },
  );

  continueButton?.addEventListener(
    "click",
    () => {
      window.location.href =
        destinationUrl;
    },
  );
}

/**
 * Convert a risk score into a human-readable title.
 */
function getWarningTitle(
  riskScore: number,
): string {
  if (riskScore >= 70) {
    return "HIGH RISK URL";
  }

  return "SUSPICIOUS URL";
}

/**
 * Get the risk category.
 */
function getRiskLabel(
  riskScore: number,
): string {
  if (riskScore >= 70) {
    return "HIGH RISK";
  }

  if (riskScore >= 40) {
    return "MEDIUM RISK";
  }

  return "LOW RISK";
}

/**
 * Escape user-controlled URL/reason text
 * before inserting it into HTML.
 */
function escapeHtml(
  value: string,
): string {
  const element =
    document.createElement("div");

  element.textContent = value;

  return element.innerHTML;
}

interface AnalysisResult {
  risk_score: number;
  verdict: string;
  confidence: number | null;
  reasons: string[];
}