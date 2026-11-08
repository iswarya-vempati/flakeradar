import xml.etree.ElementTree as ET

from app.models import CaseResult


def parse_junit_xml(path:str) -> list[CaseResult]:
    root = ET.parse(path).getroot()
    results = []
    for case in root.iter("testcase"):
        outcome = "passed"
        message = None
        failure =  case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        if failure is not None:
            outcome = "failed"
            message = failure.get("message")
        elif error is not None:
            outcome = "error"
            message = error.get("message")
        elif skipped is not None:
            outcome = "skipped"
            message = skipped.get("message")
        results.append(
            CaseResult(
                classname = case.get("classname", ""),
                name = case.get("name", ""),
                outcome = outcome,
                duration = float(case.get("time", 0)),
                message = message,
            )
        )
    return results


