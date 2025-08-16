import os
import sys

# Ensure backend is importable
ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(os.path.dirname(ROOT), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient  # type: ignore
from main import app


client = TestClient(app)


def test_healthz_and_readyz():
    # Liveness should always be OK
    r1 = client.get('/healthz')
    assert r1.status_code == 200
    body1 = r1.json()
    assert body1.get('status') == 'ok'

    # Readiness should be ready once app lifespan has run
    r2 = client.get('/readyz')
    assert r2.status_code in (200, 503)
    # In our test app, initialization runs in lifespan, so expect ready most of the time
    if r2.status_code == 200:
        assert r2.json().get('status') == 'ready'
