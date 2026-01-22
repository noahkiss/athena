"""Pytest configuration for gardener tests."""

import os
import random
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure tests use a writable data dir by default.
if "DATA_DIR" not in os.environ:
    os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="gardener-tests-")

# Add the gardener directory to the path so we can import from it
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def stress_data_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    base = tmp_path_factory.mktemp("stress-data")
    (base / "inbox" / "archive").mkdir(parents=True, exist_ok=True)
    (base / "atlas").mkdir(parents=True, exist_ok=True)
    (base / "meta").mkdir(parents=True, exist_ok=True)
    for category in [
        "home",
        "journal",
        "people",
        "projects",
        "reading",
        "tech",
        "wellness",
    ]:
        (base / "atlas" / category).mkdir(parents=True, exist_ok=True)
    (base / "AGENTS.md").write_text("# Stress Test Data\n", encoding="utf-8")
    (base / "GARDENER.md").write_text("# Stress Test Guidance\n", encoding="utf-8")
    return base


@pytest.fixture
def note_generator(tmp_path_factory: pytest.TempPathFactory):
    from tests.fixtures.generate_notes import CATEGORIES, generate_notes, load_templates

    templates_dir = Path(__file__).parent / "fixtures" / "templates"

    def _generate(
        *,
        count: int = 100,
        min_kb: int = 1,
        max_kb: int = 10,
        ambiguous_rate: float = 0.2,
        categories: list[str] | None = None,
        out_dir: Path | None = None,
        seed: int | None = None,
    ):
        rng = random.Random(seed)
        templates = load_templates(templates_dir)
        target_dir = out_dir or tmp_path_factory.mktemp("stress-notes")
        return generate_notes(
            count=count,
            categories=categories or list(CATEGORIES),
            min_kb=min_kb,
            max_kb=max_kb,
            templates=templates,
            out_dir=target_dir,
            ambiguous_rate=ambiguous_rate,
            rng=rng,
        )

    return _generate


@pytest.fixture
def stress_client():
    from tests.stress.utils import StressClient

    base_url = os.environ.get("STRESS_BASE_URL", "http://localhost:8000")
    headers = {}
    token = os.environ.get("ATHENA_AUTH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    client = StressClient(base_url=base_url, headers=headers)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def metrics_collector():
    from tests.stress.utils import MetricsCollector

    return MetricsCollector()


@pytest.fixture
def integrity_checker(stress_data_dir: Path):
    from tests.stress.utils import IntegrityChecker

    return IntegrityChecker(stress_data_dir)
