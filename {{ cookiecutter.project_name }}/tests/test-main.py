import sys
sys.path.append('')

from starlette.testclient import TestClient

from {{cookiecutter.package_name}}.main import app

client = TestClient(app)

def test_main():
    resp = client.get('/api')
    assert resp.status_code == 200