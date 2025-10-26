import sys
sys.path.append('')
sys.path.append('src')

from starlette.testclient import TestClient

from {{cookiecutter.package_name}}.main import app

client = TestClient(app)

def test_main():
    resp = client.get('/')
    assert resp.status_code == 200