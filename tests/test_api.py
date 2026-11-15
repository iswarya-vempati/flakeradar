import pytest
from fastapi.testclient import TestClient

from app.db import connect, init_db
from app.main import app, get_conn
from app.models import CaseResult
from app.repository import add_results, add_run

client = TestClient(app)


@pytest.fixture
def conn():
    connection = connect(":memory:")
    init_db(connection)
    app.dependency_overrides[get_conn] = lambda: connection
    yield connection
    app.dependency_overrides.clear()


def seed(conn):
    for outcome in ["passed", "failed", "passed", "failed", "passed"]:
        run_id = add_run(
            conn, commit_sha="a1", python_version="3.9", os_name="Windows"
        )
        add_results(
            conn,
            run_id,
            [
                CaseResult("tests.test_a", "test_stable", "passed", 0.01),
                CaseResult("tests.test_a", "test_flaky", outcome, 0.01),
            ],
        )


def test_list_tests_puts_flaky_first(conn):
    seed(conn)
    response = client.get("/tests")
    assert response.status_code == 200
    data = response.json()
    assert [item["verdict"] for item in data] == ["flaky", "stable"]
    assert data[0]["test_id"] == "tests.test_a::test_flaky"


def test_filter_by_verdict(conn):
    seed(conn)
    data = client.get("/tests", params={"verdict": "stable"}).json()
    assert [item["test_id"] for item in data] == ["tests.test_a::test_stable"]


def test_unknown_verdict_is_rejected(conn):
    seed(conn)
    response = client.get("/tests", params={"verdict": "banana"})
    assert response.status_code == 422


def test_limit_must_be_at_leat_one(conn):
    response = client.get("/tests", params={"limit": 0})
    assert response.status_code == 422


def test_empty_database_gives_an_empty_list(conn):
    response = client.get("/tests")
    assert response.status_code == 200
    assert response.json() == []  


def test_one_test_includes_its_history(conn):
    seed(conn)
    response = client.get("/tests/tests.test_a::test_flaky")
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "flaky"
    outcomes = [item["outcome"] for item in data["history"]]
    assert outcomes == ["passed", "failed", "passed", "failed", "passed"]


def test_unknown_test_gives_404(conn):
    seed(conn)
    response = client.get("/tests/tests.test_a::does_not_exist")
    assert response.status_code == 404