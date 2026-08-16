const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const {
  canonicalYoutubeUrl,
  chooseCaptionTrack,
  transcriptFromJson3,
  transcriptFromJson3Text,
  transcriptMarkdown,
} = require("../extension/content.js");
const { fetchCaptionUrls, normalizeCaptionUrl } = require("../extension/background.js");

assert.doesNotMatch(
  fs.readFileSync("extension/content.js", "utf8"),
  /innerHTML|outerHTML|insertAdjacentHTML|document\.write/
);

const tracks = [
  { languageCode: "en", kind: "asr", vssId: "a.en" },
  { languageCode: "zh-Hans", vssId: ".zh-Hans" },
];

assert.equal(chooseCaptionTrack(tracks, "zh-CN").vssId, ".zh-Hans");
assert.equal(chooseCaptionTrack(tracks, "en-US", "a.en").vssId, "a.en");
assert.equal(chooseCaptionTrack([], "en"), null);

assert.equal(
  transcriptFromJson3({
    events: [
      { segs: [{ utf8: "Hello " }, { utf8: "world." }] },
      { segs: [{ utf8: "Hello world." }] },
      { segs: [{ utf8: "Next sentence!" }] },
    ],
  }),
  "Hello world.\n\nNext sentence!"
);

assert.equal(
  transcriptFromJson3({
    events: [{ segs: [{ utf8: "这是" }] }, { segs: [{ utf8: "中文字幕。" }] }],
  }),
  "这是中文字幕。"
);

assert.throws(() => transcriptFromJson3Text(""), /没有可读取的字幕/);
assert.throws(() => transcriptFromJson3Text("not json"), /无法识别的字幕格式/);

assert.equal(
  canonicalYoutubeUrl("https://www.youtube.com/watch?v=XBu54nfzxAQ&t=10s&list=test"),
  "https://www.youtube.com/watch?v=XBu54nfzxAQ"
);
assert.equal(
  transcriptMarkdown(
    " Test   video ",
    "2024-03-09",
    "https://www.youtube.com/watch?v=XBu54nfzxAQ&si=tracking",
    "Full transcript. "
  ),
  "# Test video\n\n2024-03-09\n\n<https://www.youtube.com/watch?v=XBu54nfzxAQ>\n\n## Transcript\n\nFull transcript."
);
assert.doesNotMatch(
  transcriptMarkdown(
    "Test video",
    "",
    "https://www.youtube.com/watch?v=XBu54nfzxAQ",
    "Full transcript."
  ),
  /\n{3}/
);

let bridgeHandler;
let bridgeResponse;
const resourceEntries = [];
const ccButton = {
  disabled: false,
  pressed: false,
  getAttribute(name) {
    if (name === "aria-pressed") return String(this.pressed);
    if (name === "aria-disabled") return "false";
    return null;
  },
  click() {
    this.pressed = !this.pressed;
    if (this.pressed) {
      resourceEntries.push({
        name: "https://www.youtube.com/api/timedtext?v=test&pot=browser-token",
      });
    }
  },
};
const bridgeWindow = {
  location: { origin: "https://www.youtube.com" },
  performance: {
    getEntriesByType: () => resourceEntries,
  },
  addEventListener(_type, handler) {
    bridgeHandler = handler;
  },
  postMessage(message, targetOrigin) {
    bridgeResponse = { message, targetOrigin };
  },
};
const player = {
  getOption: () => ({ languageCode: "en", vss_id: ".en" }),
  getPlayerResponse: () => ({
    captions: {
      playerCaptionsTracklistRenderer: {
        captionTracks: [
          {
            baseUrl: "https://www.youtube.com/api/timedtext?v=test",
            languageCode: "en",
            vssId: ".en",
          },
        ],
      },
    },
    microformat: {
      playerMicroformatRenderer: { publishDate: "2024-03-09" },
    },
    videoDetails: { title: "Test video", videoId: "test" },
  }),
};

vm.runInNewContext(fs.readFileSync("extension/bridge.js", "utf8"), {
  document: {
    querySelector: (selector) => (selector === "#movie_player" ? player : ccButton),
  },
  Date,
  Promise,
  setTimeout,
  URL,
  window: bridgeWindow,
});

async function testAsyncChecks() {
  await bridgeHandler({
    source: bridgeWindow,
    origin: bridgeWindow.location.origin,
    data: { channel: "video2text-caption-bridge", type: "request", requestId: "test" },
  });

  assert.equal(bridgeResponse.targetOrigin, bridgeWindow.location.origin);
  assert.equal(bridgeResponse.message.data.title, "Test video");
  assert.equal(bridgeResponse.message.data.publishedDate, "2024-03-09");
  assert.equal(bridgeResponse.message.data.tracks[0].languageCode, "en");
  assert.match(bridgeResponse.message.data.loadedCaptionUrl, /pot=browser-token/);
  assert.equal(ccButton.getAttribute("aria-pressed"), "false");

  assert.throws(
    () => normalizeCaptionUrl("https://example.com/api/timedtext?v=test"),
    /字幕地址无效/
  );

  let calls = 0;
  const result = await fetchCaptionUrls(
    [
      "https://www.youtube.com/api/timedtext?v=test&pot=expired",
      "https://www.youtube.com/api/timedtext?v=test&signature=fresh",
    ],
    async () => ({
      ok: true,
      text: async () => (++calls === 1 ? "" : '{"events":[]}'),
    })
  );

  assert.equal(calls, 2);
  assert.equal(result.text, '{"events":[]}');
}

testAsyncChecks()
  .then(() => console.log("Video2Text extension checks passed."))
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
