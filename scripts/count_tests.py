from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def main() -> None:
    report_path = Path(sys.argv[1])

    if not report_path.exists():
        print("0 0")
        return

    root = ET.parse(report_path).getroot()
    test_cases = root.findall(".//testcase")

    total = len(test_cases)

    passed = sum(
        1
        for test_case in test_cases
        if test_case.find("failure") is None
        and test_case.find("error") is None
        and test_case.find("skipped") is None
    )

    print(f"{passed} {total}")


if __name__ == "__main__":
    main()
