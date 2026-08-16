import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from app.server import PORT, Handler, ThreadingHTTPServer


@pytest.fixture(scope="module")
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    yield httpd
    httpd.shutdown()


def test_health(server):
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health") as resp:
        assert resp.status == 200
        assert json.loads(resp.read())["status"] == "ok"


def test_generate_rejects_invalid_url(server):
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/generate",
        data=json.dumps({"url": "not-a-url"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        urllib.request.urlopen(req)
    assert excinfo.value.code == 400
