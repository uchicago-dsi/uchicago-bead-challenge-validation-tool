import pytest

from bead_inspector.validator import write_issues_to_json
from bead_inspector import reporting


@pytest.fixture
def temp_dir(tmpdir_factory):
    return tmpdir_factory.mktemp("data")


@pytest.fixture
def issue_log_file_with_column_dtype_validation_misc_issue(temp_dir):
    test_error = TypeError()
    issues = [
        {
            "data_format": "challenges",
            "issue_type": "column_dtype_validation_misc",
            "issue_level": "error",
            "issue_details": {
                "row_number": 2,
                "column": "download_speed",
                "error_msg": str(test_error),
                "error_type": str(type(test_error)),
            },
        }
    ]
    file_path = temp_dir.join("column_dtype_validation_misc_20240722_142403.json")
    write_issues_to_json(issues, file_path)
    print(f"Wrote issue-log to {file_path} (is_file: {file_path.isfile()}")
    return file_path


def test__format_column_dtype_validation_misc_issue(
    issue_log_file_with_column_dtype_validation_misc_issue,
):
    reporter = reporting.ReportGenerator(
        issue_log_file_with_column_dtype_validation_misc_issue
    )
    dtype_misc_issues = [
        iss
        for iss in reporter.issues
        if iss["issue_type"] == "column_dtype_validation_misc"
    ]
    toc_descr, html_output = reporter._format_column_dtype_validation_misc_issue(
        issue=dtype_misc_issues[0],
        issue_number=1,
    )
