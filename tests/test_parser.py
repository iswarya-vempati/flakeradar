from app.parser import parse_junit_xml

SAMPLE = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="3">
<testcase classname="tests.test_a" name="test_ok" time="0.01"/>
<testcase classname="tests.test_a" name="test_bad" time="0.02">
<failure message="assert 1 == 2">trace</failure></testcase>
<testcase classname="tests.test_a" name="test_skip" time="0.00">
<skipped message="not ready"/></testcase>
</testsuite></testsuites>"""


def test_parse_outcomes(tmp_path):
    report = tmp_path / "report.xml"
    report.write_text(SAMPLE, encoding="utf-8")
    results = parse_junit_xml(str(report))
    assert [r.outcome for r in results] == ["passed", "failed", "skipped"]
    assert results[1].message == "assert 1 == 2"
    assert results[0].test_id == "tests.test_a::test_ok"
