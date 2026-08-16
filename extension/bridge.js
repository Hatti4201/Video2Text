(() => {
  const CHANNEL = "video2text-caption-bridge";

  function findLoadedCaptionUrl(videoId) {
    return (window.performance?.getEntriesByType("resource") || [])
      .map((entry) => entry.name)
      .reverse()
      .find((name) => {
        try {
          const url = new URL(name);
          return url.pathname === "/api/timedtext" && url.searchParams.get("v") === videoId;
        } catch {
          return false;
        }
      });
  }

  function delay(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
  }

  async function waitForCaptionUrl(videoId, timeout = 2500) {
    const deadline = Date.now() + timeout;
    while (Date.now() < deadline) {
      const url = findLoadedCaptionUrl(videoId);
      if (url) return url;
      await delay(100);
    }
  }

  window.addEventListener("message", async (event) => {
    const message = event.data;
    if (
      event.source !== window ||
      event.origin !== window.location.origin ||
      message?.channel !== CHANNEL ||
      message?.type !== "request"
    ) {
      return;
    }

    try {
      const player = document.querySelector("#movie_player");
      const rawResponse = player?.getPlayerResponse?.() || window.ytInitialPlayerResponse;
      const response = typeof rawResponse === "string" ? JSON.parse(rawResponse) : rawResponse;
      let selectedTrack = {};
      try {
        selectedTrack = player?.getOption?.("captions", "track") || {};
      } catch {
        // The captions module is optional; browser locale remains a valid fallback.
      }
      const tracks = (
        response?.captions?.playerCaptionsTracklistRenderer?.captionTracks || []
      ).map(({ baseUrl, kind, languageCode, vssId }) => ({
        baseUrl,
        kind,
        languageCode,
        vssId,
      }));
      const videoId = response?.videoDetails?.videoId || "";
      let loadedCaptionUrl = findLoadedCaptionUrl(videoId);

      if (!loadedCaptionUrl && tracks.length) {
        const ccButton = document.querySelector(".ytp-subtitles-button");
        const wasOn = ccButton?.getAttribute("aria-pressed") === "true";
        const canToggle =
          ccButton && !ccButton.disabled && ccButton.getAttribute("aria-disabled") !== "true";

        if (canToggle) {
          if (wasOn) {
            ccButton.click();
            await delay(80);
          }
          ccButton.click();
          try {
            loadedCaptionUrl = await waitForCaptionUrl(videoId);
          } finally {
            if (!wasOn && ccButton.getAttribute("aria-pressed") === "true") ccButton.click();
          }
        }
      }

      window.postMessage(
        {
          channel: CHANNEL,
          type: "response",
          requestId: message.requestId,
          data: {
            selectedTrack: {
              languageCode: selectedTrack.languageCode,
              vssId: selectedTrack.vss_id || selectedTrack.vssId,
            },
            loadedCaptionUrl,
            publishedDate: (
              response?.microformat?.playerMicroformatRenderer?.publishDate ||
              response?.microformat?.playerMicroformatRenderer?.uploadDate ||
              ""
            ).slice(0, 10),
            title: response?.videoDetails?.title || "",
            tracks,
          },
        },
        window.location.origin
      );
    } catch (error) {
      window.postMessage(
        {
          channel: CHANNEL,
          type: "response",
          requestId: message.requestId,
          error: error.message || "无法读取播放器字幕信息。",
        },
        window.location.origin
      );
    }
  });
})();
