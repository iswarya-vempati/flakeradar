import os

from app.db import connect, init_db
from app.ingest import ingest_folder, ingest_report
from app.repository import get_history

PASS = ""
FAIL = '<failure message="boom">trace</failure>'


def make_conn():
    conn = connect(":memory:")
    init_db(conn)
    return conn


def write_report(path, body):
    path.write_text(
        '<testsuites><testsuite name="pytest">'
        '<testcase classname="tests.test_a" name="test_x" time="0.01">'
        f"{body}"
        "</testcase></testsuite></testsuites>",
        encoding="utf-8",
    )


def test_ingest_report_saves_run_and_results(tmp_path):
    conn = make_conn()
    report = tmp_path / "run_1.xml"
    write_report(report, PASS)
    run_id = ingest_report(conn, report, commit_sha="a1")
    assert run_id == 1
    history = get_history(conn, "tests.test_a::test_x")
    assert [row["outcome"] for row in history] == ["passed"]


def test_same_report_is_not_loaded_twice(tmp_path):
    conn = make_conn()
    report = tmp_path / "run_1.xml"
    write_report(report, PASS)
    first = ingest_report(conn, report, commit_sha="a1")
    second = ingest_report(conn, report, commit_sha="a1")
    assert first == 1
    assert second is None
    assert len(get_history(conn, "tests.test_a::test_x")) == 1


def test_ingest_folder_loads_oldest_report_first(tmp_path):
    conn = make_conn()
    older = tmp_path / "b_older.xml"
    newer = tmp_path / "a_newer.xml"
    write_report(older, PASS)
    write_report(newer, FAIL)
    os.utime(older, (1000, 1000))
    os.utime(newer, (2000, 2000))
    loaded, skipped = ingest_folder(conn, tmp_path, commit_sha="a1")
    assert (loaded, skipped) == (2, 0)
    history = get_history(conn, "tests.test_a::test_x")
    assert [row["outcome"] for row in history] == ["passed", "failed"]


def test_loading_a_folder_twice_skips_everything(tmp_path):
    conn = make_conn()
    write_report(tmp_path / "one.xml", PASS)
    write_report(tmp_path / "two.xml", FAIL)
    ingest_folder(conn, tmp_path, commit_sha="a1")
    loaded, skipped = ingest_folder(conn, tmp_path, commit_sha="a1")
    assert (loaded, skipped) == (0, 2) 