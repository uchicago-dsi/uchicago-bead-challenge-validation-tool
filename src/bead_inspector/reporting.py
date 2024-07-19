import datetime as dt
import html
import importlib
import inspect
import json
import re
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bead_inspector import constants


class ReportGenerator:
    LINK_TO_TOC = '<a href="#toc">(back to top)</a>'

    def __init__(
        self,
        issues_file_path: Path,
        extra_stats: Optional[List[Dict]] = None,
        max_error_rows: int = 20,
        max_id_col_chars: int = 100,
        overwrite_report: bool = False,
    ):
        self.issues_file_path = Path(issues_file_path).resolve()
        if max_error_rows >= 0:
            self.max_error_rows = max_error_rows
        else:
            self.max_error_rows = -1
        self.max_id_col_chars = max_id_col_chars
        self._set_issues()
        self._set_report_dir()
        self._set_extra_summary_stats(extra_stats)
        self.formatted_issues = []
        self.final_report = self.prepare_final_report()
        self.write_report(overwrite_report)

    @property
    def report_file_path(self) -> Path:
        issue_file_name = self.issues_file_path.name.lower()
        if not issue_file_name.endswith(".json"):
            raise ValueError(
                "Expected an issue file with '.json' file extension; received "
                f"{self.issues_file_path}."
            )
        report_file_name = re.sub(r"\.json$", ".html", issue_file_name)
        report_file_name = re.sub(
            r"^validation_issue_logs",
            "BEAD_Data_Validation_Report_",
            report_file_name,
        )
        report_file_path = self.report_dir.joinpath(report_file_name)
        return report_file_path

    def _set_extra_summary_stats(
        self, extra_stats: Optional[List[Dict]] = None
    ) -> None:
        """This method is for optionally passing in extra summary stat
        details from BEADChallengeDataValidator.

        extra_stats should have the format:
        [
            {
                "data_format": "challenges",
                "stat0_name": stat0_value,
                "stat1_name": stat1_value,
                ...
            },
            {
                "data_format": "cai",
                "stat0_name": stat0_value,
                "stat1_name": stat1_value,
                ...
            },
            ...
        ]
        and all data_formats should appear in exactly one list item.
        """
        if extra_stats is not None:
            self.extra_stats = []
            df_counts = dict(Counter([el["data_format"] for el in extra_stats]))
            es_keys = list(extra_stats[0].keys())
            if len(extra_stats) > 1:
                for es in extra_stats[1:]:
                    el_es_keys = list(es.keys())
                    if es_keys != el_es_keys:
                        raise ValueError(
                            "Elements in the entered extra_stat have "
                            "inconsistent keys."
                        )
            for data_format in constants.EXPECTED_DATA_FORMATS:
                df_count = df_counts.get(data_format)
                if df_count is not None and df_count != 1:
                    raise ValueError(
                        "The entered extra_stats list should only have one "
                        f"element per data_format, but {data_format} appears "
                        f"{df_count} times."
                    )
                df_extras = [
                    es for es in extra_stats if es["data_format"] == data_format
                ]
                self.extra_stats.append(df_extras[0])
        else:
            self.extra_stats = None

    def write_report(self, overwrite: bool = False) -> None:
        if self.report_file_path.is_file() and not overwrite:
            raise FileExistsError(
                "Not outputting final report to location\n  "
                f"{self.report_file_path}\nas there is already a file there."
                " To overwrite that file, run the ReportGenerator.write_report"
                " method with the overwrite arg set to True."
            )
        with open(self.report_file_path, "w") as f:
            f.write(self.final_report)
        print(
            "Data Validation Report written to file:\n  - "
            f"{self.report_file_path}"
        )

    def _read_issues_from_file(self, file_path: Path) -> List[Dict]:
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                "Expected to find a validation_issues json file at "
                f"{file_path}."
            )

    def _set_report_dir(self) -> Path:
        self.report_dir = self.issues_file_path.parent.parent.joinpath(
            "reports"
        )
        self.report_dir.mkdir(exist_ok=True)

    def _set_issues(self) -> None:
        self.issues = self._read_issues_from_file(self.issues_file_path)
        self.issues = sorted(
            self.issues,
            key=lambda x: (x["issue_level"], x["data_format"], x["issue_type"]),
        )

    def _get_class_attributes(self, module_name: str, class_name: str) -> Dict:
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        attributes = inspect.getmembers(
            cls, lambda a: not (inspect.isroutine(a))
        )
        attributes = {
            a[0]: a[1]
            for a in attributes
            if not (a[0].startswith("__") and a[0].endswith("__"))
        }
        return attributes

    def _get_class_properties(
        self, module_name: str, class_name: str
    ) -> Dict[str, Any]:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            return {
                "error": (
                    f"Failed to import {class_name} from "
                    f"{module_name}: {str(e)}"
                )
            }
        attributes = {}
        for name in ["valid_values", "rule_descr"]:
            try:
                attributes[name] = getattr(cls, name)
            except Exception as e:
                attributes[name] = f"Error accessing {name}: {str(e)}"
        if issubclass(cls, Enum):
            attributes["enum_members"] = {
                member.name: member.value for member in cls
            }
        return attributes

    def _unpack_core_issue_fields(
        self, issue: Dict
    ) -> Tuple[str, str, str, Dict]:
        data_format = issue["data_format"]
        issue_type = issue["issue_type"]
        issue_level = issue["issue_level"]
        issue_details = issue["issue_details"]
        return (data_format, issue_type, issue_level, issue_details)

    def _list_to_html_table(self, data: List, headers: Optional = None):
        if not data:
            return "<p>No data to display</p>"
        if headers is None:
            headers = data[0].keys()
        table_html = "<table border='1'>\n<tr>"
        for header in headers:
            table_html += f"<th>{html.escape(str(header))}</th>"
        table_html += "</tr>\n"
        for row in data:
            table_html += "<tr>"
            for header in headers:
                value = row.get(header, "")
                if isinstance(value, str):
                    escaped_value = html.escape(f"'{value}'")
                else:
                    escaped_value = html.escape(str(value))
                table_html += f"<td>{escaped_value}</td>"
            table_html += "</tr>\n"
        table_html += "</table>\n"
        return table_html

    def _format_valid_values(self, valid_values: List[str]) -> str:
        # if I don't need more complex logic later, maybe just roll this code
        #   into the funcs that call this. ToDo
        return self._list_to_html_table(
            [{"Valid Values": vv} for vv in valid_values]
        )

    def _format_id_column_into_fail_table(
        self, id_column: str, fail_list: List
    ) -> Tuple[str, List[Dict]]:
        """Expects fail_list to be a list of lists/iterables each with 3
        elements: [row_number, id_column_value, failing_value/row]
        """
        failing_rows = [
            {"row": row, id_column: id_col_value, "value": value}
            for row, id_col_value, value in fail_list
        ]
        any_truncated_id_col_vals = any(
            [
                len(str(fr[id_column])) > self.max_id_col_chars
                for fr in failing_rows
            ]
        )
        if any_truncated_id_col_vals:
            failing_rows = [
                {
                    "row": r,
                    id_column: str(icv)[: self.max_id_col_chars],
                    "value": v,
                }
                for r, icv, v in fail_list
            ]
            trunc_note = (
                f"<ul><li>Note: Only showing the first {self.max_id_col_chars}"
                " characters of id_column values.</li></ul>"
            )
        else:
            trunc_note = ""
        return (trunc_note, failing_rows)

    def _format_column_contents_validation(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "column_contents_validation"
        expected_file_name = f"{data_format}.csv"
        column = issue_details["column"]
        id_column = issue_details["id_column"]
        validation = issue_details["validation"]
        all_fails_recorded = issue_details["all_fails_recorded"]
        fail_set_completeness_msg = self._format_all_fails_recorded_message(
            all_fails_recorded
        )
        validator_attrs = self._get_class_properties(
            module_name="bead_inspector.constants",
            class_name=validation,
        )
        try:
            rule_descr = html.escape(validator_attrs["rule_descr"])
        except KeyError:
            print(
                f"validation: {validation}\nvalidator_attrs: {validator_attrs}"
            )
            # ToDo: remove this try-except block after development
            raise
        valid_values_table = self._format_valid_values(
            validator_attrs["valid_values"]
        )
        trunc_note, failing_rows = self._format_id_column_into_fail_table(
            id_column, issue_details["failing_rows_and_values"]
        )
        toc_descr = (
            f"{expected_file_name} :: Invalid values in column '{column}'"
        )
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}:</h3>{self.LINK_TO_TOC}\n"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>Description: {rule_descr}</li>"
            f"<li>Column: {column}</li>"
            "<li>Failing rows, id_values, and invalid values:"
            f"{self._list_to_html_table(failing_rows)}</li>{trunc_note}"
            "<li>Total rows with invalid values:"
            f'{issue_details["total_fails"]}</li>'
            "<li>All rows with invalid values shown: "
            f"{'Yes' if all_fails_recorded else 'No'}</li>\n"
            f"<li>{fail_set_completeness_msg}</li>\n"
            "<li><details><summary>Valid values (click to show/hide):</summary>"
            f"{valid_values_table}</details></li></ul>\n"
        )
        return (toc_descr, html_output)

    def _format_row_rule_validation_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "row_rule_validation"
        expected_file_name = f"{data_format}.csv"
        id_column = issue_details["id_column"]
        validation = issue_details["validation"]
        all_fails_recorded = issue_details["all_fails_recorded"]
        fail_set_completeness_msg = self._format_all_fails_recorded_message(
            all_fails_recorded
        )
        validator_attrs = self._get_class_attributes(
            module_name="bead_inspector.rules",
            class_name=validation,
        )
        rule_descr = validator_attrs["rule_descr"]
        short_descr = validator_attrs.get("short_descr", None)
        col_indexes = {
            c.replace("_index", ""): i
            for c, i in filter(
                lambda x: x[0].endswith("_index"), validator_attrs.items()
            )
        }
        col_indexes = dict(sorted(col_indexes.items(), key=lambda x: x[1]))
        failing_values = issue_details["failing_rows_and_values"]
        trunc_note, failing_values = self._format_id_column_into_fail_table(
            id_column, failing_values
        )
        failing_rows = []
        for failing_value in failing_values:
            relevant_values = dict()
            relevant_values["row"] = failing_value["row"]
            relevant_values[id_column] = failing_value[id_column]
            for col, col_index in col_indexes.items():
                try:
                    value = failing_value["value"][col_index]
                except IndexError:
                    value = f"MISSING COLUMN NUMBER {col_index}"
                relevant_values[col] = value
            failing_rows.append(relevant_values)
        toc_descr = f"{expected_file_name} :: {short_descr} :: Row rule broken"
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}:</h3>{self.LINK_TO_TOC}"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>Description: {html.escape(rule_descr)}</li>"
            "<li>Failing rows and values:"
            f"{self._list_to_html_table(failing_rows)}</li>{trunc_note}"
            "<li>Total rows with invalid values:"
            f'{issue_details["total_fails"]}</li>'
            "<li>All rows with invalid values shown: "
            f"{'Yes' if all_fails_recorded else 'No'}</li>"
            f"<li>{fail_set_completeness_msg}</li></ul>"
        )
        return (toc_descr, html_output)

    def _format_column_dtype_validation_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "column_dtype_validation"
        expected_file_name = f"{data_format}.csv"
        column = issue_details["column"]
        id_column = issue_details["id_column"]
        intended_type = issue_details["intended_type"]
        n_uncastable = issue_details["number_of_uncastable_values"]
        trunc_note, failing_rows = self._format_id_column_into_fail_table(
            id_column, issue_details["failing_rows_and_values"]
        )
        toc_descr = (
            f"{expected_file_name} :: {column} :: Incorrect datatype found"
        )
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}:</h3>{self.LINK_TO_TOC}"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>Intended datatype: {html.escape(intended_type)}</li>"
            "<li>Failing rows and their uncastable values:"
            f"{self._list_to_html_table(failing_rows)}</li>{trunc_note}"
            "<li>Total number of rows with uncastable values: "
            f"{n_uncastable}</li></ul>"
        )
        return (toc_descr, html_output)

    def _format_missing_data_file_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "missing_data_file"
        data_dir = issue_details["data_dir"]
        expected_file_name = f"{data_format}.csv"
        toc_descr = f"{expected_file_name} :: Data file not found"
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}:</h3>{self.LINK_TO_TOC}"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>  - Description: Expected to find file {expected_file_name} "
            f"in directory {html.escape(data_dir)}</li></ul>"
        )
        return (toc_descr, html_output)

    def _format_file_not_found_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "file_not_found"
        expected_file_name = f"{data_format}.csv"
        msg = issue_details["msg"]
        toc_descr = f"{expected_file_name} :: Data file not found"
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}\n"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>  - Description: {html.escape(msg)}</li></ul>"
        )
        return (toc_descr, html_output)

    def _format_empty_file_error_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "empty_file_error"
        expected_file_name = f"{data_format}.csv"
        file_name = f"{data_format}.csv"
        toc_descr = f"{expected_file_name} :: Data file is empty"
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}\n"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>  - Description: The file {file_name} is empty.</li></ul>\n"
        )
        return (toc_descr, html_output)

    def _format_data_loading_failure_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "data_loading_failure"
        expected_file_name = f"{data_format}.csv"
        msg = issue_details["msg"]
        error_msg = issue_details["error_msg"]
        error_type = issue_details["error_type"]
        toc_descr = f"{expected_file_name} :: Error loading data file"
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>Description: {html.escape(msg)}.</li>"
            f"<li>Error message: {html.escape(error_msg)}</li>"
            f"<li>Error message: {html.escape(error_type)}</li></ul>"
        )
        return (toc_descr, html_output)

    def _format_column_name_validation_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "column_name_validation"
        expected_file_name = f"{data_format}.csv"
        missing_cols = issue_details["columns_missing_from_file"]
        extra_cols = issue_details["extra_columns_in_file"]
        missing_cols_str = "['" + "', '".join(missing_cols) + "']"
        extra_cols_str = "'" + "', '".join(extra_cols) + "'"
        num_missing_cols = len(missing_cols)
        num_extra_cols = len(extra_cols)
        if num_missing_cols > 0 and num_extra_cols > 0:
            msg = (
                f"Missing {num_missing_cols} required columns and found "
                f"{num_extra_cols} unexpected columns."
            )
        elif num_missing_cols > 0:
            msg = f"Missing {num_missing_cols} required columns."
        elif num_extra_cols > 0:
            msg = f"Found {num_extra_cols} unexpected columns."
        else:
            msg = (
                f"Missing {num_missing_cols} required columns and found "
                f"{num_extra_cols} unexpected columns. \n"
                "Well, how did I get here?"
            )
        toc_descr = f"{expected_file_name} :: Incorrect set of columns"
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>Description: {msg}.</li>"
            f"<li>Missing column names: {html.escape(missing_cols_str)}</li>"
            f"<li>Unexpected column names: {html.escape(extra_cols_str)}</li>"
            "</ul>\n"
        )
        return (toc_descr, html_output)

    def _format_column_order_validation_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "column_order_validation"
        expected_file_name = f"{data_format}.csv"
        cols_out_of_order = issue_details["cols_out_of_order"]
        toc_descr = f"{expected_file_name} :: Incorrect column order"
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}\n"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            "<li>Description: Columns must be in the expected order.</li>"
            "</ul>\n"
            f"{self._list_to_html_table(cols_out_of_order)}\n"
        )
        return (toc_descr, html_output)

    def _format_column_dtype_undefined_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "column_dtype_undefined"
        expected_file_name = f"{data_format}.csv"
        column = issue_details["column"]
        toc_descr = (
            f"{expected_file_name} :: Undefined datatype for column '{column}'"
        )
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}\n"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            "<li>Description: A datatype must be defined for every "
            "column.</li>"
            "</ul>\n"
        )
        return (toc_descr, html_output)

    def _format_required_column_not_null_validation_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        expected_file_name = f"{data_format}.csv"
        assert issue_type == "required_column_not_null_validation"
        column = html.escape(issue_details["column"])
        id_column = issue_details["id_column"]
        all_fails_recorded = issue_details["all_fails_recorded"]
        trunc_note, failing_rows = self._format_id_column_into_fail_table(
            id_column, issue_details["rows_where_column_is_null"]
        )
        null_rows = [
            {"row": fr["row"], id_column: fr[id_column], "column": column}
            for fr in failing_rows
        ]
        fail_set_completeness_msg = self._format_all_fails_recorded_message(
            all_fails_recorded
        )
        toc_descr = (
            f"{expected_file_name} :: Unallowed nulls found in column "
            f"'{column}'"
        )
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}\n"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>Column: {column}</li>"
            "<li>Description: No null values are allowed in this column.</li>"
            "<li>Rows with null column values: "
            f"{self._list_to_html_table(null_rows)}</li>{trunc_note}"
            f'<li>Total rows where null: {issue_details["total_fails"]}</li>'
            "<li>All rows with invalid values shown: "
            f"{'Yes' if all_fails_recorded else 'No'}"
            "</li>\n"
            f"<li>{fail_set_completeness_msg}</li>\n"
            "</ul>\n"
        )
        return (toc_descr, html_output)

    def _format_column_missing_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "column_missing"
        expected_file_name = f"{data_format}.csv"
        column = html.escape(issue_details["column"])
        toc_descr = f"{expected_file_name} :: Missing column '{column}'"
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>Column: {column}</li>"
            "<li>Description: Missing a required column.</li>"
            "</ul>\n"
        )
        return toc_descr, html_output

    def _format_multi_file_validation_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "multi_file_validation"
        other_data_format = html.escape(issue_details["other_data_format"])
        short_msg = html.escape(issue_details["short_msg"])
        long_msg = html.escape(issue_details["long_msg"])
        invalid_values = issue_details["invalid_values"]
        toc_descr = f"{short_msg}"
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}"
            "<ul><li>Involved Data Files: "
            f"{data_format}.csv and {other_data_format}.csv</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>Description: {long_msg}.</li>"
            f"<li>{self._list_to_html_table(invalid_values)}</li>"
            "</ul>"
        )
        return toc_descr, html_output

    def _format_column_dtype_validation_misc_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "column_dtype_validation_misc"
        expected_file_name = f"{data_format}.csv"
        row_number = html.escape(issue_details["row_number"])
        column = html.escape(issue_details["column"])
        error_msg = html.escape(issue_details["error_msg"])
        error_type = html.escape(issue_details["error_type"])
        toc_descr = (
            f"{expected_file_name} :: Unexpected error while dtyping {column}"
            " column"
        )
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}\n"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            f"<li>Row number: {row_number}</li>"
            f"<li>Column: {column}</li>"
            f"<li>Error message: {error_msg}</li>"
            f"<li>Error type: {error_type}</li>"
            "</ul>"
        )
        return toc_descr, html_output

    def _format_enough_columns_validation_issue(
        self, issue: Dict, issue_number: int
    ) -> Tuple[str, str]:
        (
            data_format,
            issue_type,
            issue_level,
            issue_details,
        ) = self._unpack_core_issue_fields(issue)
        assert issue_type == "enough_columns_validation"
        expected_file_name = f"{data_format}.csv"
        column = html.escape(issue_details["column"])
        id_column = issue_details["id_column"]
        trunc_note, failing_rows = self._format_id_column_into_fail_table(
            id_column, issue_details["failing_rows_and_values"]
        )
        n_short_rows = issue_details["total_fails"]
        toc_descr = (
            f"{expected_file_name} :: Inconsistent number of columns" " column"
        )
        html_output = (
            f'<h3 id="issue-{issue_number}">{issue_number}. '
            f"{toc_descr}</h3>{self.LINK_TO_TOC}\n"
            f"<ul><li>Data File: {expected_file_name}</li>"
            f"<li>Issue Level: {issue_level}</li>"
            "<li>Description: Some rows in the CSV had too few columns.</li>"
            f"<li>Column missing from row: {column}</li>"
            "<li>Rows with too few columns: "
            f"{self._list_to_html_table(failing_rows)}</li>{trunc_note}"
            f"<li>Number of rows with too few columns: {n_short_rows}"
            "</ul>\n"
        )
        return toc_descr, html_output

    def format_issue(self, issue: Dict, issue_number: int) -> Tuple[str, str]:
        issue_type = issue["issue_type"]
        if issue_type == "file_not_found":
            toc_line, formatted_issue = self._format_file_not_found_issue(
                issue, issue_number
            )
        elif issue_type == "empty_file_error":
            toc_line, formatted_issue = self._format_empty_file_error_issue(
                issue, issue_number
            )
        elif issue_type == "data_loading_failure":
            toc_line, formatted_issue = self._format_data_loading_failure_issue(
                issue, issue_number
            )
        elif issue_type == "column_name_validation":
            (
                toc_line,
                formatted_issue,
            ) = self._format_column_name_validation_issue(issue, issue_number)
        elif issue_type == "column_order_validation":
            (
                toc_line,
                formatted_issue,
            ) = self._format_column_order_validation_issue(issue, issue_number)
        elif issue_type == "column_dtype_undefined":
            (
                toc_line,
                formatted_issue,
            ) = self._format_column_dtype_undefined_issue(issue, issue_number)
        elif issue_type == "column_dtype_validation":
            (
                toc_line,
                formatted_issue,
            ) = self._format_column_dtype_validation_issue(issue, issue_number)
        elif issue_type == "column_dtype_validation_misc":
            (
                toc_line,
                formatted_issue,
            ) = self._format_column_dtype_validation_misc_issue(
                issue, issue_number
            )
        elif issue_type == "enough_columns_validation":
            (
                toc_line,
                formatted_issue,
            ) = self._format_enough_columns_validation_issue(
                issue, issue_number
            )
        elif issue_type == "required_column_not_null_validation":
            (
                toc_line,
                formatted_issue,
            ) = self._format_required_column_not_null_validation_issue(
                issue, issue_number
            )
        elif issue_type == "column_contents_validation":
            toc_line, formatted_issue = self._format_column_contents_validation(
                issue, issue_number
            )
        elif issue_type == "column_missing":
            toc_line, formatted_issue = self._format_column_missing_issue(
                issue, issue_number
            )
        elif issue_type == "row_rule_validation":
            toc_line, formatted_issue = self._format_row_rule_validation_issue(
                issue, issue_number
            )
        elif issue_type == "missing_data_file":
            toc_line, formatted_issue = self._format_missing_data_file_issue(
                issue, issue_number
            )
        elif issue_type == "multi_file_validation":
            (
                toc_line,
                formatted_issue,
            ) = self._format_multi_file_validation_issue(issue, issue_number)
        else:
            raise Exception(f"Unexpected issue_type encountered: {issue_type}")
        return (toc_line, formatted_issue)

    def format_all_issues(self) -> None:
        for inum, issue in enumerate(self.issues):
            toc_line, formatted_issue = self.format_issue(issue, inum + 1)
            self.formatted_issues.append((inum + 1, toc_line, formatted_issue))

    def _format_counter_counts(self, counts: Dict[str, int]) -> List[str]:
        k_width = max([len(k) for k in counts.keys()])
        v_width = max([len(str(k)) for k in counts.values()])
        formatted_counts = []
        for label, count in counts.items():
            formatted_counts.append(
                f"  - {label.rjust(k_width)}: {str(count).rjust(v_width)} "
            )
        return formatted_counts

    def format_summary_stats(self) -> str:
        df_counts = dict(
            Counter(
                tuple(i[k] for k in ["data_format", "issue_level"])
                for i in self.issues
            )
        )

        summary_stats = []
        for issue_level in constants.EXPECTED_ISSUE_LEVELS:
            counts = []
            for data_format in constants.EXPECTED_DATA_FORMATS:
                format_and_level_counts = df_counts.get(
                    (data_format, issue_level)
                )
                if format_and_level_counts:
                    stats = {
                        "data_format": data_format,
                        "issue_level": issue_level,
                        "issue_count": format_and_level_counts,
                    }
                else:
                    stats = {
                        "data_format": data_format,
                        "issue_level": issue_level,
                        "issue_count": 0,
                    }
                if self.extra_stats is not None:
                    extra_stats = [
                        es
                        for es in self.extra_stats
                        if es["data_format"] == data_format
                    ][0]
                    stats = {**stats, **extra_stats}
                counts.append(stats)
            summary_stats.append(
                (
                    f"<h2>{issue_level.title()}-level Issue Summary</h2>"
                    f"{self._list_to_html_table(counts)}"
                )
            )
        return "\n".join(summary_stats)

    def prepare_table_of_contents(self) -> str:
        toc = '<h2 id="toc">Table of Contents</h2>\n<ul>'
        current_issue_level = None
        current_data_format = None
        for i, toc_line, formatted_issue in self.formatted_issues:
            issue = self.issues[i - 1]
            issue_level = issue["issue_level"]
            data_format = issue["data_format"]
            if issue_level != current_issue_level:
                if current_data_format is not None:
                    toc += "</ul></li>"
                if current_issue_level is not None:
                    toc += "</ul></li>"
                toc += f"<li><h3>{issue_level.title()}-level issues:</h3><ul>"
                current_issue_level = issue_level
                current_data_format = None
            if data_format != current_data_format:
                if current_data_format is not None:
                    toc += "</ul></li>"
                toc += f"<li><h4>{data_format}.csv issues:</h4><ul>"
                current_data_format = data_format
            toc += f'<li><a href="#issue-{i}">Issue {i}: {toc_line}</a></li>\n'

        if current_data_format is not None:
            toc += "</ul></li>"
        if current_issue_level is not None:
            toc += "</ul></li>"
        toc += "</ul>"
        return toc

    def prepare_final_report(self) -> str:
        self.format_all_issues()
        toc = self.prepare_table_of_contents()
        pretty_issues = []
        for i, toc_line, formatted_issue in self.formatted_issues:
            if isinstance(formatted_issue, dict):
                pretty_issues.append(json.dumps(formatted_issue, indent=4))
            else:
                pretty_issues.append(formatted_issue)
        rundate_str = re.search(
            r"\d{8}_\d{6}", self.issues_file_path.name
        ).group()
        date_dt = dt.datetime.strptime(rundate_str, "%Y%m%d_%H%M%S")
        fmtd_rundate_str = dt.datetime.strftime(date_dt, "%Y-%m-%d %H:%M:%S")
        final_report = [
            (
                f"<h1>BEAD Data Validation Results from the {fmtd_rundate_str} "
                "run:</h1>"
            ),
            self.format_summary_stats(),
            toc,
        ]
        final_report.extend(pretty_issues)
        return "\n\n".join(final_report)

    def _format_all_fails_recorded_message(
        self, all_fails_recorded: bool
    ) -> str:
        if all_fails_recorded:
            msg = (
                "Showing all instances of the erroneous data raising this"
                " issue."
            )
        else:
            msg = (
                f"Only showing values from the first {self.max_error_rows} "
                "records with invalid data.\n"
                "To see more of the values that need to be fixed, you can "
                "either rerun the entire BEADChallengeDataValidator "
                "with a larger --single_error_log_limit | -s argument, or "
                "fix these values (or the issue causing these invalid values) "
                "and then rerun the BEADChallengeDataValidator."
            )
        return msg
