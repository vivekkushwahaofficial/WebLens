chrome.action.onClicked.addListener(async (tab) => {
  const url = tab.url;

  if (!url) {
    console.warn("WebLens: active tab has no URL");
    return;
  }

  console.log("WebLens: current tab URL:", url);
});
