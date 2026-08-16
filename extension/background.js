function normalizeCaptionUrl(rawUrl) {
  const url = new URL(rawUrl);
  if (url.origin !== "https://www.youtube.com" || url.pathname !== "/api/timedtext") {
    throw new Error("字幕地址无效。");
  }
  url.searchParams.set("fmt", "json3");
  return url.href;
}

async function fetchCaptionUrls(rawUrls, fetcher = fetch) {
  const urls = [...new Set((rawUrls || []).filter(Boolean))];
  let sawEmptyResponse = false;

  for (const rawUrl of urls) {
    let url;
    try {
      url = normalizeCaptionUrl(rawUrl);
    } catch {
      continue;
    }

    const response = await fetcher(url, { credentials: "omit" });
    const text = await response.text();
    if (response.ok && text.trim()) return { ok: true, text };
    if (response.ok) sawEmptyResponse = true;
  }

  return {
    ok: false,
    error: sawEmptyResponse
      ? "YouTube 返回了空字幕，请关闭再重新打开 CC 后重试。"
      : "字幕读取失败，请刷新页面后重试。",
  };
}

if (typeof chrome === "undefined") {
  module.exports = { fetchCaptionUrls, normalizeCaptionUrl };
} else {
  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message.type !== "fetch-caption") return false;
    fetchCaptionUrls(message.urls)
      .then(sendResponse)
      .catch(() => sendResponse({ ok: false, error: "字幕读取失败，请刷新页面后重试。" }));
    return true;
  });
}
