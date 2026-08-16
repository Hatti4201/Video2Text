(() => {
  function chooseCaptionTrack(tracks, language = "", selectedVssId = "") {
    if (!Array.isArray(tracks) || tracks.length === 0) return null;

    const wanted = language.toLowerCase();
    const wantedBase = wanted.split("-")[0];
    return (
      tracks.find((track) => track.vssId === selectedVssId) ||
      tracks.find((track) => track.languageCode?.toLowerCase() === wanted) ||
      tracks.find(
        (track) => wantedBase && track.languageCode?.toLowerCase().split("-")[0] === wantedBase
      ) ||
      tracks.find((track) => track.kind !== "asr") ||
      tracks[0]
    );
  }

  function transcriptFromJson3(data) {
    const lines = [];
    for (const event of data?.events || []) {
      const line = (event.segs || [])
        .map((segment) => segment.utf8 || "")
        .join("")
        .replace(/\s+/g, " ")
        .trim();
      if (line && line !== lines.at(-1)) lines.push(line);
    }

    return lines
      .join(" ")
      .replace(/([\u3400-\u9fff])\s+(?=[\u3400-\u9fff])/g, "$1")
      .replace(/([.!?。！？])\s+/g, "$1\n\n")
      .trim();
  }

  function transcriptFromJson3Text(text) {
    if (!text.trim()) throw new Error("这个视频没有可读取的字幕。");
    try {
      return transcriptFromJson3(JSON.parse(text));
    } catch {
      throw new Error("YouTube 返回了无法识别的字幕格式。");
    }
  }

  function canonicalYoutubeUrl(rawUrl) {
    const url = new URL(rawUrl);
    const videoId = url.searchParams.get("v");
    if (url.hostname !== "www.youtube.com" || !videoId) {
      throw new Error("无法读取当前 YouTube 视频链接。");
    }
    return `https://www.youtube.com/watch?v=${encodeURIComponent(videoId)}`;
  }

  function transcriptMarkdown(title, publishedDate, videoUrl, transcript) {
    const cleanTitle = title.replace(/\s+/g, " ").trim() || "YouTube Transcript";
    return [
      `# ${cleanTitle}`,
      publishedDate,
      `<${canonicalYoutubeUrl(videoUrl)}>`,
      "## Transcript",
      transcript.trim(),
    ]
      .filter(Boolean)
      .join("\n\n");
  }

  if (typeof document === "undefined") {
    module.exports = {
      canonicalYoutubeUrl,
      chooseCaptionTrack,
      transcriptFromJson3,
      transcriptFromJson3Text,
      transcriptMarkdown,
    };
    return;
  }

  if (document.getElementById("v2t-panel")) return;

  function createElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function renderTranscript(container, transcript) {
    container.replaceChildren(
      ...transcript
        .split("\n\n")
        .map((paragraph) => createElement("p", "v2t-text", paragraph))
    );
  }

  function requestCaptionData() {
    const channel = "video2text-caption-bridge";
    const requestId = crypto.randomUUID();

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        window.removeEventListener("message", handleResponse);
        reject(new Error("播放器还没准备好，请刷新页面后重试。"));
      }, 5000);

      function handleResponse(event) {
        const message = event.data;
        if (
          event.source !== window ||
          event.origin !== window.location.origin ||
          message?.channel !== channel ||
          message?.type !== "response" ||
          message?.requestId !== requestId
        ) {
          return;
        }

        clearTimeout(timeout);
        window.removeEventListener("message", handleResponse);
        if (message.error) reject(new Error(message.error));
        else resolve(message.data);
      }

      window.addEventListener("message", handleResponse);
      window.postMessage({ channel, type: "request", requestId }, window.location.origin);
    });
  }

  async function fetchCaptionText(urls) {
    const response = await chrome.runtime.sendMessage({ type: "fetch-caption", urls });
    if (!response?.ok) throw new Error(response?.error || "字幕读取失败，请重试。");
    return response.text;
  }

  async function extractTranscript() {
    const {
      loadedCaptionUrl,
      publishedDate = "",
      selectedTrack = {},
      title: videoTitle,
      tracks = [],
    } = await requestCaptionData();

    const track = chooseCaptionTrack(
      tracks,
      selectedTrack.languageCode || navigator.language,
      selectedTrack.vssId
    );
    if (!loadedCaptionUrl && !track?.baseUrl) {
      throw new Error("这个视频没有可读取的字幕。");
    }

    const transcript = transcriptFromJson3Text(
      await fetchCaptionText([loadedCaptionUrl, track?.baseUrl])
    );
    if (!transcript) throw new Error("字幕内容为空。");

    return {
      title:
        videoTitle ||
        document.querySelector("h1 yt-formatted-string")?.textContent?.trim() ||
        "YouTube Transcript",
      transcript,
      videoUrl: canonicalYoutubeUrl(window.location.href),
      publishedDate:
        publishedDate ||
        document.querySelector('meta[itemprop="uploadDate"]')?.content?.slice(0, 10) ||
        "",
    };
  }

  const panel = document.createElement("div");
  panel.id = "v2t-panel";
  const header = createElement("div", "v2t-header");
  header.append(createElement("span", "v2t-title", "Video2Text"));

  const body = createElement("div", "v2t-body");
  const controls = createElement("div", "v2t-controls");
  const videoTitleEl = createElement("div", "v2t-video-title");
  const generateBtn = createElement("button", "v2t-generate", "提取现有字幕");
  generateBtn.type = "button";
  const statusEl = createElement("div", "v2t-status");
  controls.append(videoTitleEl, generateBtn, statusEl);

  const panels = createElement("div", "v2t-panels");
  const pane = createElement("div", "v2t-pane active");
  const actions = createElement("div", "v2t-actions");
  const downloadBtn = createElement("button", "v2t-download", "下载 TXT");
  const copyBtn = createElement("button", "v2t-copy", "复制");
  downloadBtn.type = copyBtn.type = "button";
  downloadBtn.disabled = copyBtn.disabled = true;
  actions.append(downloadBtn, copyBtn);

  const transcriptContentEl = createElement(
    "div",
    "v2t-content v2t-content-transcript"
  );
  transcriptContentEl.append(
    createElement("p", "v2t-placeholder", "点击上方按钮读取视频已有字幕")
  );
  pane.append(actions, transcriptContentEl);
  panels.append(pane);
  body.append(controls, panels);
  panel.append(header, body);

  function mountPanel() {
    const host =
      document.querySelector("#secondary #secondary-inner") || document.querySelector("#secondary");
    if (!host) return false;
    if (host.firstElementChild !== panel) host.prepend(panel);
    return true;
  }

  function mountWithRetry(attemptsLeft = 20) {
    if (mountPanel() || attemptsLeft <= 0) return;
    setTimeout(() => mountWithRetry(attemptsLeft - 1), 300);
  }

  mountWithRetry();

  const playerHeightObserver = new ResizeObserver((entries) => {
    const height = entries[0]?.contentRect.height;
    if (height > 0) panel.style.setProperty("--v2t-panel-height", `${height}px`);
  });

  function observePlayerHeight(attemptsLeft = 20) {
    const player = document.querySelector("#player") || document.querySelector("#movie_player");
    if (player) {
      playerHeightObserver.observe(player);
      return;
    }
    if (attemptsLeft <= 0) return;
    setTimeout(() => observePlayerHeight(attemptsLeft - 1), 300);
  }

  observePlayerHeight();

  let transcript = "";
  let title = "";
  let videoUrl = "";
  let publishedDate = "";
  let running = false;

  function setError(text) {
    statusEl.textContent = text || "";
  }

  function resetForNewVideo() {
    running = false;
    transcript = "";
    title = "";
    videoUrl = "";
    publishedDate = "";
    videoTitleEl.textContent = "";
    transcriptContentEl.replaceChildren(
      createElement("p", "v2t-placeholder", "点击上方按钮读取视频已有字幕")
    );
    generateBtn.disabled = false;
    generateBtn.textContent = "提取现有字幕";
    copyBtn.disabled = true;
    downloadBtn.disabled = true;
    setError("");
    panel.classList.remove("v2t-collapsed");
  }

  window.addEventListener("yt-navigate-finish", () => {
    mountWithRetry();
    observePlayerHeight();
    resetForNewVideo();
  });

  const EXPAND_THRESHOLD = 60;
  let lastScrollTop = 0;
  let upDistance = 0;

  transcriptContentEl.addEventListener(
    "scroll",
    (event) => {
      const delta = event.target.scrollTop - lastScrollTop;
      lastScrollTop = event.target.scrollTop;
      if (delta > 0) {
        upDistance = 0;
        panel.classList.add("v2t-collapsed");
      } else if (delta < 0) {
        upDistance -= delta;
        if (upDistance > EXPAND_THRESHOLD || event.target.scrollTop <= 0) {
          panel.classList.remove("v2t-collapsed");
        }
      }
    },
    { passive: true }
  );

  copyBtn.addEventListener("click", async () => {
    if (!transcript) return;
    try {
      await navigator.clipboard.writeText(
        transcriptMarkdown(title, publishedDate, videoUrl, transcript)
      );
      copyBtn.textContent = "已复制";
      setTimeout(() => (copyBtn.textContent = "复制"), 1200);
    } catch {
      setError("复制失败，请使用下载 TXT。");
    }
  });

  downloadBtn.addEventListener("click", () => {
    if (!transcript) return;
    const blobUrl = URL.createObjectURL(new Blob([`${transcript}\n`], { type: "text/plain" }));
    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = `${(title || "youtube-transcript")
      .replace(/[\\/:*?"<>|]/g, "_")
      .slice(0, 100)}.txt`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(blobUrl), 0);
  });

  generateBtn.addEventListener("click", async () => {
    if (running) return;
    const requestedUrl = window.location.href;
    running = true;
    generateBtn.disabled = true;
    generateBtn.textContent = "正在读取…";
    setError("");

    try {
      const result = await extractTranscript();
      if (requestedUrl !== window.location.href) return;
      ({ title, transcript, videoUrl, publishedDate } = result);
      videoTitleEl.textContent = title;
      renderTranscript(transcriptContentEl, transcript);
      copyBtn.disabled = false;
      downloadBtn.disabled = false;
    } catch (error) {
      setError(error.message || "字幕读取失败，请重试。");
    } finally {
      running = false;
      generateBtn.disabled = false;
      generateBtn.textContent = "提取现有字幕";
    }
  });
})();
