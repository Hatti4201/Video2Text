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
  "这是\n\n中文字幕。"
);

const shortChineseClauses = [
  "这一切像电影一样",
  "因为我们完全没有去备孕",
  "这个完全是意外怀孕",
  "这两件事情发生在同一天",
  "我真的感觉非常的巧合",
  "到家之后我老婆看到了我啊",
  "就立马",
];
assert.equal(
  transcriptFromJson3({
    events: shortChineseClauses.map((utf8) => ({ segs: [{ utf8 }] })),
  }),
  shortChineseClauses.join("\n\n")
);

assert.equal(
  transcriptFromJson3({
    events: [
      { tStartMs: 0, dDurationMs: 500, segs: [{ utf8: "First complete thought" }] },
      { tStartMs: 1500, dDurationMs: 500, segs: [{ utf8: "Second complete thought" }] },
    ],
  }),
  "First complete thought\n\nSecond complete thought"
);

assert.equal(
  transcriptFromJson3({
    events: [{ segs: [{ utf8: "第一句。第二句！第三句？" }] }],
  }),
  "第一句。\n\n第二句！\n\n第三句？"
);

const longEnglish = "readable words ".repeat(20).trim();
const wrappedEnglish = transcriptFromJson3({ events: [{ segs: [{ utf8: longEnglish }] }] });
assert.ok(wrappedEnglish.split("\n\n").every((line) => line.length <= 140));
assert.equal(wrappedEnglish.replace(/\n\n/g, " "), longEnglish);

const longChinese = "这是没有标点的自动字幕".repeat(12);
const wrappedChinese = transcriptFromJson3({ events: [{ segs: [{ utf8: longChinese }] }] });
assert.ok(wrappedChinese.split("\n\n").every((line) => line.length <= 24));
assert.equal(wrappedChinese.replace(/\n\n/g, ""), longChinese);

const mixedChinese = transcriptFromJson3({
  events: [
    { segs: [{ utf8: "xArk创立之初便完成1亿美元种子轮融资RadixArk最终使命是要做下一代A" }] },
    { segs: [{ utf8: "I 我想要build（构建）的那个未来就是一个跟强力AI共存的未来" }] },
    { segs: [{ utf8: "以我跟Inf" }] },
    { segs: [{ utf8: "ra的之间的浪漫关系我觉得Infra本身就是产品" }] },
    { segs: [{ utf8: "你本身是一个喜欢intense（高强度" }] },
    { segs: [{ utf8: "）的人吗它是一个特点我应该顺着我的天" }] },
    { segs: [{ utf8: "性去做事情" }] },
  ],
});
for (const word of [
  "1亿美元",
  "下一代AI",
  "Infra",
  "intense（高强度）",
  "天性",
]) {
  assert.match(mixedChinese, new RegExp(word.replace(/[（）]/g, "\\$&")));
}
assert.doesNotMatch(mixedChinese, /A\n\nI|Inf\n\nra|高强度\n\n）|天\n\n性/);
assert.match(mixedChinese, /下一代AI\n\n我想要/);

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
