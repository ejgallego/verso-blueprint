import json
import pytest
import random
import socket
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright


def default_site_dir() -> Path:
    package_root = Path(__file__).resolve().parents[1]
    repo_root = package_root.parent
    if repo_root.parent.name == ".worktrees":
        shared_out = repo_root.parents[1] / "_out" / repo_root.name
        candidates = [
            shared_out / "example-blueprints" / "noperthedron" / "html-multi",
            shared_out / "noperthedron" / "html-multi",
        ]
    else:
        candidates = [
            package_root / "_out" / "example-blueprints" / "noperthedron" / "html-multi",
            package_root / "_out" / "noperthedron" / "html-multi",
        ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


DEFAULT_SITE_DIR = default_site_dir()


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def load_redirects(site_dir: str | Path):
    json_path = Path(site_dir)
    if not json_path.is_absolute():
        json_path = (Path(__file__).parent / json_path).resolve()
    json_path = json_path / "xref.json"
    with open(json_path) as f:
        data = json.load(f)

    sections = data["Verso.Genre.Manual.section"]["contents"]
    return [(s, sections[s][0]["address"] + "#" + sections[s][0]["id"]) for s in sections]


def pytest_addoption(parser):
    parser.addoption(
        "--port",
        action="store",
        default=None,
        help="Port for the local test server (default: auto-select)",
    )
    parser.addoption(
        "--site-dir",
        action="store",
        default=str(DEFAULT_SITE_DIR),
        help="Path to the built site directory",
    )
    parser.addoption(
        "--server-url",
        action="store",
        default=None,
        help="Use an existing server instead of starting one (e.g., http://localhost:3000)",
    )
    parser.addoption(
        "--seed",
        action="store",
        default=None,
        type=int,
        help="Random seed for reproducible redirect selection",
    )


def pytest_configure(config):
    seed = config.getoption("--seed")
    if seed is not None:
        random.seed(seed)


@pytest.fixture(scope="session")
def server(request):
    external_url = request.config.getoption("--server-url")

    if external_url:
        yield external_url
        return

    site_dir = request.config.getoption("--site-dir")
    site_dir = Path(site_dir)
    if not site_dir.is_absolute():
        site_dir = (Path(__file__).parent / site_dir).resolve()
    port = request.config.getoption("--port")

    if port is None:
        port = find_free_port()
    else:
        port = int(port)

    proc = subprocess.Popen(
        ["python", "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=site_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    yield f"http://127.0.0.1:{port}"
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session", params=["chromium", "firefox"])
def browser(request, playwright_instance):
    browser_type = request.param
    browser = getattr(playwright_instance, browser_type).launch()
    yield browser
    browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()
