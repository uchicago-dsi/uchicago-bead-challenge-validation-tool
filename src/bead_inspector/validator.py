import copy
import datetime as dt
import json
from itertools import zip_longest
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from bead_inspector import constants, rules
from bead_inspector.file_utils import CSVData, EmptyFileError
from bead_inspector.reporting import ReportGenerator


class ColumnValidation:
    def __init__(
        self,
        column_name: str,
        validation: constants.Validator,
        issue_level: str = "error",
    ):
        self.column_name = column_name
        self.validation = validation
        self.issue_level = issue_level

    def validate(self, value: Any) -> bool:
        validator_func = self.validation.validator()
        return validator_func(value)


class RowValidation:
    def __init__(
        self, validation: constants.Validator, issue_level: str = "error"
    ):
        self.validation = validation
        self.issue_level = issue_level

    def validate(self, row: List[Any]) -> bool:
        validator_func = self.validation.validator()
        return validator_func(row)


class SingleFileValidator:
    def __init__(
        self,
        data_format: str,
        file_path: Path,
        id_column: str,
        column_dtypes: Dict,
        nullable_columns: List[str],
        column_validations: List[ColumnValidation],
        row_validations: List[RowValidation],
        csv_header: Optional[List[str]] = None,
        single_error_log_limit: int = 20,
        row_offset: int = 2,
    ) -> None:
        self.issues = []
        self.can_continue = True
        self.data_format = data_format
        self.csv_data_object = self.get_csv_data_object(file_path, csv_header)
        self.set_id_column(id_column)
        self.column_dtypes = column_dtypes
        self.nullable_columns = nullable_columns
        self.column_validations = column_validations
        self.row_validations = row_validations
        # This param short circuits checking and logging any given issue.
        self.single_error_log_limit = single_error_log_limit
        self.row_offset = row_offset

    def get_csv_data_object(
        self, file_path: Path, csv_header: Optional[List[str]] = None
    ) -> CSVData:
        try:
            csv_data_object = CSVData(file_path, csv_header)
        except FileNotFoundError:
            self.issues.append(
                {
                    "data_format": self.data_format,
                    "issue_type": "file_not_found",
                    "issue_level": "error",
                    "issue_details": {
                        "msg": f"Expected a CSV file in location {file_path}",
                    },
                }
            )
            self.can_continue = False
            return
        except EmptyFileError:
            self.issues.append(
                {
                    "data_format": self.data_format,
                    "issue_type": "empty_file_error",
                    "issue_level": "error",
                    "issue_details": {},
                }
            )
            self.can_continue = False
            return
        except Exception as e:
            self.issues.append(
                {
                    "data_format": self.data_format,
                    "issue_type": "data_loading_failure",
                    "issue_level": "error",
                    "issue_details": {
                        "msg": "Encountered an unexpected error",
                        "error_msg": str(e),
                        "error_type": str(type(e)),
                    },
                }
            )
            raise
        return csv_data_object

    def set_id_column(self, id_column: str) -> None:
        self.id_column = id_column
        if self.id_column in self.csv_data_object.header:
            self.id_column_index = self.csv_data_object.header.index(
                self.id_column
            )
        else:
            self.id_column_index = None

    def validate_column_names(self) -> None:
        expected_cols = [self.csv_data_object.index_col] + [
            *self.column_dtypes.keys()
        ]
        file_cols = self.csv_data_object.header
        if set(expected_cols) != set(file_cols):
            missing_cols = set(expected_cols).difference(set(file_cols))
            extra_cols = set(file_cols).difference(set(expected_cols))
            self.issues.append(
                {
                    "data_format": self.data_format,
                    "issue_type": "column_name_validation",
                    "issue_level": "error",
                    "issue_details": {
                        "columns_missing_from_file": list(missing_cols),
                        "extra_columns_in_file": list(extra_cols),
                    },
                }
            )

    def validate_column_order(self) -> None:
        expected_cols = [self.csv_data_object.index_col] + [
            *self.column_dtypes.keys()
        ]
        file_cols = self.csv_data_object.header
        cols_out_of_order = []
        for i, (exp_col, file_col) in enumerate(
            zip_longest(expected_cols, file_cols, fillvalue="<missing_column>")
        ):
            if exp_col != file_col:
                cols_out_of_order.append(
                    {
                        "column_number": i,
                        "expected_column_name": exp_col,
                        "column_name_in_file": file_col,
                    }
                )
        if len(cols_out_of_order) > 0:
            self.issues.append(
                {
                    "data_format": self.data_format,
                    "issue_type": "column_order_validation",
                    "issue_level": "error",
                    "issue_details": {"cols_out_of_order": cols_out_of_order},
                }
            )

    def validate_column_types(self) -> None:
        """At present, this also has the stateful effect of casting column
        values to the defined dtype.
        """
        for i, column in enumerate(self.csv_data_object.header):
            column_can_be_null = column in self.nullable_columns
            if column == self.csv_data_object.index_col:
                valid_column_type = int
            else:
                valid_column_type = self.column_dtypes.get(column)
            if valid_column_type is None:
                self.issues.append(
                    {
                        "data_format": self.data_format,
                        "issue_type": "column_dtype_undefined",
                        "issue_level": "error",
                        "issue_details": {"column": column},
                    }
                )
            num_dtype_errors = 0
            num_cols_in_row_errors = 0
            dtype_failing_rows = []
            row_col_failing_rows = []
            for row in self.csv_data_object.data:
                try:
                    if i > (len(row) - 1):
                        num_cols_in_row_errors += 1
                        if (
                            num_cols_in_row_errors
                            <= self.single_error_log_limit
                        ):
                            try:
                                id_col_value = row[self.id_column_index]
                            except IndexError:
                                id_col_value = (
                                    "Missing the id_column at index "
                                    f"{self.id_column_index}"
                                )
                            row_col_failing_rows.append(
                                (row[0] + self.row_offset, id_col_value, i)
                            )
                        continue
                    if valid_column_type != str:
                        if column_can_be_null and (
                            row[i] is None or row[i] == ""
                        ):
                            continue
                        row[i] = valid_column_type(row[i])
                except (ValueError, IndexError):
                    num_dtype_errors += 1
                    if num_dtype_errors <= self.single_error_log_limit:
                        try:
                            value = row[i]
                        except IndexError:
                            value = f"Missing column number {i} in this row"
                        try:
                            id_col_value = row[self.id_column_index]
                        except IndexError:
                            id_col_value = (
                                "Missing the id_column at index "
                                f"{self.id_column_index} in this row"
                            )
                        dtype_failing_rows.append(
                            (row[0] + self.row_offset, id_col_value, value)
                        )
                except Exception as e:
                    self.issues.append(
                        {
                            "data_format": self.data_format,
                            "issue_type": "column_dtype_validation_misc",
                            "issue_level": "error",
                            "issue_details": {
                                "row_number": row[0],
                                "column": column,
                                "error_msg": str(e),
                                "error_type": str(type(e)),
                            },
                        }
                    )
            if num_dtype_errors > 0:
                self.issues.append(
                    {
                        "data_format": self.data_format,
                        "issue_type": "column_dtype_validation",
                        "issue_level": "error",
                        "issue_details": {
                            "column": column,
                            "id_column": self.id_column,
                            "failing_rows_and_values": dtype_failing_rows,
                            "number_of_uncastable_values": num_dtype_errors,
                            "total_fails": num_dtype_errors,
                            "intended_type": valid_column_type.__name__,
                        },
                    }
                )
            if num_cols_in_row_errors > 0:
                self.issues.append(
                    {
                        "data_format": self.data_format,
                        "issue_type": "enough_columns_validation",
                        "issue_level": "error",
                        "issue_details": {
                            "column": column,
                            "id_column": self.id_column,
                            "failing_rows_and_values": row_col_failing_rows,
                            "total_fails": num_cols_in_row_errors,
                            "number_of_rows_without_enough_columns": (
                                row_col_failing_rows
                            ),
                        },
                    }
                )

    def validate_column_non_nullness(self) -> None:
        for i, column in enumerate(self.csv_data_object.header):
            if column in self.nullable_columns:
                continue
            rows_w_null_col_val = []
            num_null = 0
            for row in self.csv_data_object.data:
                try:
                    if row[i] is None or row[i] == "":
                        num_null += 1
                        if num_null <= self.single_error_log_limit:
                            row_details = (
                                row[0] + self.row_offset,
                                row[self.id_column_index],
                                row[i],
                            )
                            rows_w_null_col_val.append(row_details)
                except IndexError:
                    # This catches the case where a row has fewer than the
                    #   expected number of columns. This issue is recorded in
                    #   the validate_column_types() method, so we ignore it
                    #   here.
                    continue
            if num_null > 0:
                self.issues.append(
                    {
                        "data_format": self.data_format,
                        "issue_type": "required_column_not_null_validation",
                        "issue_level": "error",
                        "issue_details": {
                            "column": column,
                            "id_column": self.id_column,
                            "rows_where_column_is_null": rows_w_null_col_val,
                            "total_fails": num_null,
                            "all_fails_recorded": num_null
                            <= self.single_error_log_limit,
                        },
                    }
                )

    def validate_column_contents(self) -> None:
        for col_validation in self.column_validations:
            num_errors = 0
            column = col_validation.column_name
            failing_rows = []
            try:
                col_index = self.csv_data_object.header.index(column)
                for row in self.csv_data_object.data:
                    try:
                        if not col_validation.validate(row[col_index]):
                            num_errors += 1
                            if num_errors <= self.single_error_log_limit:
                                if not self.id_column_index:
                                    id_col_value = "missing_id_column"
                                else:
                                    id_col_value = row[self.id_column_index]
                                failing_rows.append(
                                    (
                                        row[0] + self.row_offset,
                                        id_col_value,
                                        row[col_index],
                                    )
                                )
                    except IndexError:
                        # This catches the case where a row has fewer than the
                        #   expected number of columns. This issue is recorded
                        #   in the validate_column_types() method, so we
                        #   ignore it here.
                        continue
                if num_errors > 0:
                    self.issues.append(
                        {
                            "data_format": self.data_format,
                            "issue_type": "column_contents_validation",
                            "issue_level": col_validation.issue_level,
                            "issue_details": {
                                "column": column,
                                "id_column": self.id_column,
                                "validation": (
                                    col_validation.validation.__name__
                                ),
                                "failing_rows_and_values": failing_rows,
                                "total_fails": num_errors,
                                "all_fails_recorded": num_errors
                                <= self.single_error_log_limit,
                            },
                        }
                    )
            except ValueError:
                self.issues.append(
                    {
                        "data_format": self.data_format,
                        "issue_type": "column_missing",
                        "issue_level": col_validation.issue_level,
                        "issue_details": {
                            "column": column,
                        },
                    }
                )

    def validate_row_contents(self) -> None:
        for row_validation in self.row_validations:
            num_errors = 0
            failing_rows = []
            for row in self.csv_data_object.data:
                if not row_validation.validate(row):
                    num_errors += 1
                    if num_errors <= self.single_error_log_limit:
                        failing_rows.append(
                            (
                                row[0] + self.row_offset,
                                row[self.id_column_index],
                                row,
                            )
                        )
            if num_errors > 0:
                self.issues.append(
                    {
                        "data_format": self.data_format,
                        "issue_type": "row_rule_validation",
                        "issue_level": row_validation.issue_level,
                        "issue_details": {
                            "rule_descr": row_validation.validation.rule_descr,
                            "id_column": self.id_column,
                            "validation": row_validation.validation.__name__,
                            "failing_rows_and_values": failing_rows,
                            "total_fails": num_errors,
                            "all_fails_recorded": num_errors
                            <= self.single_error_log_limit,
                        },
                    }
                )

    def run_single_file_validations(self) -> None:
        validation_funcs = [
            self.validate_column_names,
            self.validate_column_order,
            self.validate_column_types,
            self.validate_column_non_nullness,
            self.validate_column_contents,
            self.validate_row_contents,
        ]
        for validation_func in validation_funcs:
            if not self.can_continue:
                break
            validation_func()


class ChallengerDataValidator:
    ID_COLUMN = "challenger"
    COLUMN_DTYPES = {
        "challenger": str,
        "category": str,
        "organization": str,
        "webpage": str,
        "provider_id": str,
        "contact_name": str,
        "contact_email": str,
        "contact_phone": str,
    }
    NULLABLE_COLUMNS = ["webpage", "provider_id", "contact_phone"]
    COLUMN_VALIDATIONS = [
        ColumnValidation("challenger", constants.NonNullableValidator),
        ColumnValidation("category", constants.ChallengerType),
        ColumnValidation("organization", constants.NonNullableValidator),
        ColumnValidation("webpage", constants.WebPageValidator),
        ColumnValidation("provider_id", constants.FccProviderIdValidator),
        ColumnValidation("contact_name", constants.NonNullableValidator),
        ColumnValidation("contact_email", constants.EmailValidator),
        ColumnValidation("contact_phone", constants.PhoneValidator),
    ]
    ROW_VALIDATIONS = [
        RowValidation(rules.ChallengersISPProviderIdRuleValidator),
    ]

    def __init__(
        self, file_path: Path, single_error_log_limit: int = 20
    ) -> None:
        self.file_validator = SingleFileValidator(
            data_format="challenger",
            file_path=file_path,
            id_column=self.ID_COLUMN,
            column_dtypes=self.COLUMN_DTYPES,
            nullable_columns=self.NULLABLE_COLUMNS,
            column_validations=self.COLUMN_VALIDATIONS,
            row_validations=self.ROW_VALIDATIONS,
            single_error_log_limit=single_error_log_limit,
        )
        self.file_validator.run_single_file_validations()


class ChallengesDataValidator:
    ID_COLUMN = "challenge"
    COLUMN_DTYPES = {
        "challenge": str,
        "challenge_type": str,
        "challenger": str,
        "challenge_date": str,
        "rebuttal_date": str,
        "resolution_date": str,
        "disposition": str,
        "provider_id": str,
        "technology": int,
        "location_id": int,
        "unit": str,
        "reason_code": str,
        "evidence_file_id": str,
        "response_file_id": str,
        "resolution": str,
        "advertised_download_speed": float,
        "download_speed": float,
        "advertised_upload_speed": float,
        "upload_speed": float,
        "latency": float,
    }
    NULLABLE_COLUMNS = [
        "challenger",
        "rebuttal_date",
        "provider_id",
        "technology",
        "unit",
        "reason_code",
        "evidence_file_id",
        "response_file_id",
        "resolution",
        "advertised_download_speed",
        "download_speed",
        "advertised_upload_speed",
        "upload_speed",
        "latency",
    ]
    COLUMN_VALIDATIONS = [
        ColumnValidation("challenge", constants.ChallengeIdValidator),
        ColumnValidation("challenge_type", constants.ChallengeType),
        ColumnValidation("challenge_date", constants.DateValidator),
        ColumnValidation("rebuttal_date", constants.DateNullableValidator),
        ColumnValidation("resolution_date", constants.DateNullableValidator),
        ColumnValidation("disposition", constants.DispositionsOfChallenge),
        ColumnValidation("provider_id", constants.FccProviderIdValidator),
        ColumnValidation("technology", constants.Technology),
        ColumnValidation("location_id", constants.BSLLocationIdValidator),
        ColumnValidation("reason_code", constants.ReasonCode),
        ColumnValidation(
            "evidence_file_id", constants.FileNameNullableValidator
        ),
        ColumnValidation(
            "response_file_id", constants.FileNameNullableValidator
        ),
        ColumnValidation(
            "advertised_download_speed",
            constants.NonNegativeNumberNullableValidator,
        ),
        ColumnValidation(
            "download_speed", constants.NonNegativeNumberNullableValidator
        ),
        ColumnValidation(
            "advertised_upload_speed",
            constants.NonNegativeNumberNullableValidator,
        ),
        ColumnValidation(
            "upload_speed", constants.NonNegativeNumberNullableValidator
        ),
        ColumnValidation(
            "latency", constants.NonNegativeNumberNullableValidator
        ),
    ]
    ROW_VALIDATIONS = [
        RowValidation(
            rules.ChallengesChallengerIdGivenChallengeTypeRuleValidator
        ),
        RowValidation(rules.ChallengesAvailabilityChallengeTypeRuleValidator),
        RowValidation(
            rules.ChallengesResolutionGivenChallengeTypeRuleValidator
        ),
        RowValidation(
            rules.ChallengesAdvertisedDownloadSpeedChallengeTypeRuleValidator
        ),
        RowValidation(rules.ChallengesDownloadSpeedChallengeTypeRuleValidator),
        RowValidation(
            rules.ChallengesAdvertisedUploadSpeedChallengeTypeRuleValidator
        ),
        RowValidation(rules.ChallengesUploadSpeedChallengeTypeRuleValidator),
        RowValidation(rules.ChallengesRebuttalDateAndFileRuleValidator),
        RowValidation(rules.ChallengesLatencyChallengeTypeRuleValidator),
        RowValidation(rules.ChallengesProviderIdChallengeTypeRuleValidator),
        RowValidation(rules.ChallengesTechnologyChallengeTypeRuleValidator),
        RowValidation(rules.ChallengesEvidenceFileChallengeTypeRuleValidator),
        RowValidation(rules.ChallengesChallengeAndRebuttalDateRuleValidator),
        RowValidation(rules.ChallengesChallengeAndResolutionDateRuleValidator),
        RowValidation(rules.ChallengesRebuttalAndResolutionDateRuleValidator),
    ]

    def __init__(
        self, file_path: Path, single_error_log_limit: int = 20
    ) -> None:
        self.file_validator = SingleFileValidator(
            data_format="challenges",
            file_path=file_path,
            id_column=self.ID_COLUMN,
            column_dtypes=self.COLUMN_DTYPES,
            nullable_columns=self.NULLABLE_COLUMNS,
            column_validations=self.COLUMN_VALIDATIONS,
            row_validations=self.ROW_VALIDATIONS,
            single_error_log_limit=single_error_log_limit,
        )
        self.file_validator.run_single_file_validations()


class PostChallengeCAIDataValidator:
    ID_COLUMN = "entity_name"
    COLUMN_DTYPES = {
        "type": str,
        "entity_name": str,
        "entity_number": int,
        "cms_number": str,
        "frn": str,
        "location_id": int,
        "address_primary": str,
        "city": str,
        "state": str,
        "zip_code": str,
        "longitude": float,
        "latitude": float,
        "explanation": str,
        "need": int,
        "availability": int,
    }
    NULLABLE_COLUMNS = [
        "entity_number",
        "cms_number",
        "frn",
        "location_id",
        "address_primary",
        "city",
        "zip_code",
        "longitude",
        "latitude",
        "explanation",
        "availability",
    ]
    COLUMN_VALIDATIONS = [
        ColumnValidation("type", constants.CAIType),
        ColumnValidation("entity_name", constants.NonNullableValidator),
        ColumnValidation(
            "cms_number",
            constants.CMSCertificateNullableValidator,
            issue_level="info",
        ),
        ColumnValidation(
            "frn", constants.FrnNullableValidator, issue_level="info"
        ),
        ColumnValidation(
            "location_id", constants.BSLLocationIdNullableValidator
        ),
        ColumnValidation("state", constants.State),
        ColumnValidation("zip_code", constants.ZipNullableValidator),
        ColumnValidation("longitude", constants.LongitudeNullableValidator),
        ColumnValidation("latitude", constants.LatitudeNullableValidator),
        ColumnValidation("need", constants.NonNegativeNumberValidator),
        ColumnValidation(
            "availability", constants.NonNegativeNumberNullableValidator
        ),
    ]

    ROW_VALIDATIONS = [
        RowValidation(
            rules.PostChallengeCaiCMSValidatorGivenCAIType, issue_level="info"
        ),
        RowValidation(
            rules.PostChallengeCaiFRNValidationGivenCAIType, issue_level="info"
        ),
        RowValidation(rules.PostChallengeCaiLocationValidation),
        RowValidation(rules.PostChallengeCaiExplanationValidationGivenCAIType),
    ]

    DATA_FORMAT = "post_challenge_cai"

    def __init__(
        self, file_path: Path, single_error_log_limit: int = 20
    ) -> None:
        self.file_validator = SingleFileValidator(
            data_format=self.DATA_FORMAT,
            file_path=file_path,
            id_column=self.ID_COLUMN,
            column_dtypes=self.COLUMN_DTYPES,
            nullable_columns=self.NULLABLE_COLUMNS,
            column_validations=self.COLUMN_VALIDATIONS,
            row_validations=self.ROW_VALIDATIONS,
            single_error_log_limit=single_error_log_limit,
        )
        self.file_validator.run_single_file_validations()


class CAIDataValidator(PostChallengeCAIDataValidator):
    """
    Per the guideline doc this has the same format as post_challenge_cai
    """

    DATA_FORMAT = "cai"


class CAIChallengeDataValidator:
    ID_COLUMN = "challenge"
    COLUMN_DTYPES = {
        "challenge": str,
        "challenge_type": str,
        "challenger": str,
        "category_code": str,
        "disposition": str,
        "challenge_explanation": str,
        "type": str,
        "entity_name": str,
        "entity_number": int,
        "cms_number": str,
        "frn": str,
        "location_id": int,
        "address_primary": str,
        "city": str,
        "state": str,
        "zip_code": str,
        "longitude": float,
        "latitude": float,
        "explanation": str,
        "need": int,
        "availability": int,
    }
    NULLABLE_COLUMNS = [
        "category_code",
        "explanation",
        "entity_name",
        "entity_number",
        "cms_number",
        "frn",
        "location_id",
        "address_primary",
        "city",
        "zip_code",
        "longitude",
        "latitude",
        "availability",
        "challenge_explanation",
        "availability",
    ]

    COLUMN_VALIDATIONS = [
        ColumnValidation("challenge", constants.ChallengeIdValidator),
        ColumnValidation("challenge_type", constants.CAIChallengeType),
        ColumnValidation(
            "category_code", constants.CAIRationaleNullableValidator
        ),
        ColumnValidation("disposition", constants.DispositionsOfCAIChallenge),
        ColumnValidation("type", constants.CAIType),
        ColumnValidation(
            "cms_number",
            constants.CMSCertificateNullableValidator,
            issue_level="info",
        ),
        ColumnValidation(
            "frn", constants.FrnNullableValidator, issue_level="info"
        ),
        ColumnValidation(
            "location_id", constants.BSLLocationIdNullableValidator
        ),
        ColumnValidation("state", constants.State),
        ColumnValidation("zip_code", constants.ZipNullableValidator),
        ColumnValidation("longitude", constants.LongitudeNullableValidator),
        ColumnValidation("latitude", constants.LatitudeNullableValidator),
        ColumnValidation("need", constants.NonNegativeNumberValidator),
        ColumnValidation(
            "availability", constants.NonNegativeNumberNullableValidator
        ),
    ]

    ROW_VALIDATIONS = [
        RowValidation(rules.CaiChallengeCaiLocationValidationPostChallenge),
        RowValidation(rules.CaiChallengeCategoryCodeConditionalGivenType),
        RowValidation(rules.CaiChallengeExplanationConditionalTypeC),
        RowValidation(rules.CaiChallengeEntityNameConditionalType),
        RowValidation(rules.CaiChallengeChallengeExplanationConditionalTypeC),
        RowValidation(
            rules.CaiChallengeCMSConditionalTypeH, issue_level="info"
        ),
        RowValidation(rules.CaiChallengeFRNGivenType, issue_level="info"),
    ]

    def __init__(
        self, file_path: Path, single_error_log_limit: int = 20
    ) -> None:
        self.file_validator = SingleFileValidator(
            data_format="cai_challenges",
            file_path=file_path,
            id_column=self.ID_COLUMN,
            column_dtypes=self.COLUMN_DTYPES,
            nullable_columns=self.NULLABLE_COLUMNS,
            column_validations=self.COLUMN_VALIDATIONS,
            row_validations=self.ROW_VALIDATIONS,
            single_error_log_limit=single_error_log_limit,
        )
        self.file_validator.run_single_file_validations()


class PostChallengeLocationDataValidator:
    ID_COLUMN = "location_id"
    COLUMN_DTYPES = {
        "location_id": int,
        "classification": int,
    }
    NULLABLE_COLUMNS = []
    COLUMN_VALIDATIONS = [
        ColumnValidation("location_id", constants.BSLLocationIdValidator),
        ColumnValidation(
            "classification", constants.LocationClassificationCode
        ),
    ]
    ROW_VALIDATIONS = []

    def __init__(
        self, file_path: Path, single_error_log_limit: int = 20
    ) -> None:
        self.file_validator = SingleFileValidator(
            data_format="post_challenge_locations",
            file_path=file_path,
            id_column=self.ID_COLUMN,
            column_dtypes=self.COLUMN_DTYPES,
            nullable_columns=self.NULLABLE_COLUMNS,
            column_validations=self.COLUMN_VALIDATIONS,
            row_validations=self.ROW_VALIDATIONS,
            single_error_log_limit=single_error_log_limit,
        )
        self.file_validator.run_single_file_validations()


class UnservedDataValidator:
    ID_COLUMN = "location_id"
    COLUMN_DTYPES = {"location_id": int}
    NULLABLE_COLUMNS = []
    COLUMN_VALIDATIONS = [
        ColumnValidation("location_id", constants.BSLLocationIdValidator),
    ]
    ROW_VALIDATIONS = []

    def __init__(
        self, file_path: Path, single_error_log_limit: int = 20
    ) -> None:
        self.file_validator = SingleFileValidator(
            data_format="unserved",
            file_path=file_path,
            id_column=self.ID_COLUMN,
            csv_header=["location_id"],
            column_dtypes=self.COLUMN_DTYPES,
            nullable_columns=self.NULLABLE_COLUMNS,
            column_validations=self.COLUMN_VALIDATIONS,
            row_validations=self.ROW_VALIDATIONS,
            single_error_log_limit=single_error_log_limit,
            row_offset=1,
        )
        self.file_validator.run_single_file_validations()


class UnderservedDataValidator:
    ID_COLUMN = "location_id"
    COLUMN_DTYPES = {"location_id": int}
    NULLABLE_COLUMNS = []
    COLUMN_VALIDATIONS = [
        ColumnValidation("location_id", constants.BSLLocationIdValidator),
    ]
    ROW_VALIDATIONS = []

    def __init__(
        self, file_path: Path, single_error_log_limit: int = 20
    ) -> None:
        self.file_validator = SingleFileValidator(
            data_format="underserved",
            file_path=file_path,
            id_column=self.ID_COLUMN,
            csv_header=["location_id"],
            column_dtypes=self.COLUMN_DTYPES,
            nullable_columns=self.NULLABLE_COLUMNS,
            column_validations=self.COLUMN_VALIDATIONS,
            row_validations=self.ROW_VALIDATIONS,
            single_error_log_limit=single_error_log_limit,
            row_offset=1,
        )
        self.file_validator.run_single_file_validations()


class BEADChallengeDataValidator:
    EXPECTED_DATA_FORMATS = constants.EXPECTED_DATA_FORMATS
    DATA_FORMAT_VALIDATORS = {
        "cai": CAIDataValidator,
        "cai_challenges": CAIChallengeDataValidator,
        "challenges": ChallengesDataValidator,
        "challengers": ChallengerDataValidator,
        "post_challenge_cai": PostChallengeCAIDataValidator,
        "post_challenge_locations": PostChallengeLocationDataValidator,
        "unserved": UnservedDataValidator,
        "underserved": UnderservedDataValidator,
    }

    def __init__(
        self,
        data_directory: Path,
        expected_data_formats: Union[str, List[str]] = "*",
        results_dir: Optional[Path] = None,
        single_error_log_limit: int = 20,
    ):
        self.issues = []
        self.single_error_log_limit = single_error_log_limit
        self.run_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.data_format_validators = copy.deepcopy(self.DATA_FORMAT_VALIDATORS)
        if expected_data_formats == "*":
            expected_data_formats = self.EXPECTED_DATA_FORMATS
        self.expected_data_formats = expected_data_formats
        self.missing_data_formats = set()
        self.data_dir = Path(data_directory).resolve()
        self.setup_issue_logging()
        self.set_data_format_to_path_map()
        self.check_for_missing_formats()
        self.run_data_validations()
        self.generate_report()

    @property
    def log_path(self) -> Path:
        return self.issue_logs_dir.joinpath(
            f"validation_issue_logs_{self.run_time}.json"
        )

    def _prepare_extra_summary_stats(self) -> List[Dict]:
        extra_stats = []
        for data_format in self.expected_data_formats:
            stats = {}
            stats["data_format"] = data_format
            try:
                total_rows_in_file = len(
                    self.data_format_validators[
                        data_format
                    ].file_validator.csv_data_object.data
                )
            except AttributeError:
                total_rows_in_file = "N/A; file missing."
            stats["total_rows_in_file"] = total_rows_in_file
            # if there are other stats to calculate and insert, do that here
            extra_stats.append(stats)
        return extra_stats

    def generate_report(self) -> None:
        extra_stats = self._prepare_extra_summary_stats()
        self.reporter = ReportGenerator(
            self.log_path,
            extra_stats=extra_stats,
            max_error_rows=self.single_error_log_limit,
        )

    def _get_data_format(self, file_path: Path) -> str:
        return file_path.name.lower().replace(".csv", "")

    def setup_issue_logging(self) -> None:
        self.issue_logs_dir = self.data_dir.joinpath("logs")
        try:
            self.issue_logs_dir.mkdir(exist_ok=True, parents=False)
        except FileExistsError:
            raise FileExistsError(
                "Tried to create a directory for validation results at \n"
                f"  - {self.issue_logs_dir}\nbut there's already a file in "
                "that location. Please pass in a different\nlocation to the "
                "results_dir argument."
            )
        except PermissionError:
            raise PermissionError(
                "Tried to create a directory for validation results at \n"
                f"  - {self.issue_logs_dir}\nbut you do not have permission "
                "to write to that location. Please pass in a\ndifferent "
                "location to the results_dir argument."
            )

    def set_data_format_to_path_map(self) -> None:
        self.data_format_to_path_map = {
            p.name.lower().replace(".csv", ""): p
            for p in self.data_dir.iterdir()
            if p.is_file()
            and p.name.lower().replace(".csv", "") in self.expected_data_formats
        }

    def check_for_missing_formats(self) -> None:
        missing_formats = [
            edf
            for edf in self.expected_data_formats
            if edf not in self.data_format_to_path_map.keys()
        ]
        if len(missing_formats) > 0:
            for missing_data_format in missing_formats:
                self.missing_data_formats.add(missing_data_format)
                self.issues.append(
                    {
                        "data_format": missing_data_format,
                        "issue_type": "missing_data_file",
                        "issue_level": "error",
                        "issue_details": {"data_dir": str(self.data_dir)},
                    }
                )

    def run_data_validations(self) -> None:
        print(
            "Starting BEAD Challenge Data Validation.\n"
            "  Note: it may take a few minutes to run; expect 1 to 2 seconds\n"
            "        per 1MB of data."
        )
        for data_format, file_path in self.data_format_to_path_map.items():
            data_validator_cls = self.data_format_validators.get(data_format)
            data_validator = data_validator_cls(
                file_path, single_error_log_limit=self.single_error_log_limit
            )
            new_issues = data_validator.file_validator.issues
            if data_validator.file_validator.can_continue:
                print(
                    f"Ran single-file validations for the {data_format} format."
                )
            else:
                print(
                    "Failed to run single-file validations for the "
                    f"{data_format} format.\n"
                )
                if len(new_issues) > 0:
                    print("Issues found:")
                    for issue in new_issues:
                        print(json.dumps(issue, indent=4))
                    print()
            if len(new_issues) > 0:
                self.issues.extend(new_issues)
            self.data_format_validators[data_format] = data_validator

        all_present_flag = len(self.data_format_to_path_map.keys()) == len(
            self.expected_data_formats
        )
        if all_present_flag:
            self.run_challenges_and_challengers_validations()
            self.run_cai_challenges_and_challengers_validations()
            print("TODO: add more multi-file validations here")

        self.output_results()

    def run_challenges_and_challengers_validations(self) -> None:
        challengers_in_challenges = list(
            set(
                el.lower()
                for el in self.data_format_validators[
                    "challenges"
                ].file_validator.csv_data_object["challenger"]
            )
        )
        registered_challengers = list(
            set(
                el.lower()
                for el in self.data_format_validators[
                    "challengers"
                ].file_validator.csv_data_object["challenger"]
            )
        )
        unregistered_yet_submitting_challengers = list(
            {"missing_challenger_ids": c}
            for c in challengers_in_challenges
            if c not in registered_challengers
        )
        if len(unregistered_yet_submitting_challengers) > 0:
            self.issues.append(
                {
                    "data_format": "challenges",
                    "issue_type": "multi_file_validation",
                    "issue_level": "error",
                    "issue_details": {
                        "other_data_format": "challengers",
                        "short_msg": (
                            "Inconsistent ids across challengers.csv and "
                            "challenges.csv"
                        ),
                        "long_msg": (
                            "Found challengers in the Challenges dataset that"
                            " aren't in the Challengers dataset."
                        ),
                        "invalid_values": (
                            unregistered_yet_submitting_challengers
                        ),
                    },
                }
            )

    def run_cai_challenges_and_challengers_validations(self) -> None:
        challengers_in_cai_challenges = list(
            set(
                el.lower()
                for el in self.data_format_validators[
                    "cai_challenges"
                ].file_validator.csv_data_object["challenger"]
            )
        )
        registered_challengers = list(
            set(
                el.lower()
                for el in self.data_format_validators[
                    "challengers"
                ].file_validator.csv_data_object["challenger"]
            )
        )
        unregistered_yet_submitting_challengers = list(
            {"missing_challenger_ids": c}
            for c in challengers_in_cai_challenges
            if c not in registered_challengers
        )
        if len(unregistered_yet_submitting_challengers) > 0:
            self.issues.append(
                {
                    "data_format": "cai_challenges",
                    "issue_type": "multi_file_validation",
                    "issue_level": "error",
                    "issue_details": {
                        "other_data_format": "challengers",
                        "short_msg": (
                            "Inconsistent ids across challengers.csv and "
                            "cai_challenges.csv"
                        ),
                        "long_msg": (
                            "Found challengers in the CAIChallenges dataset"
                            " that aren't in the Challengers dataset."
                        ),
                        "invalid_values": (
                            unregistered_yet_submitting_challengers
                        ),
                    },
                }
            )

    def output_results(self) -> None:
        if self.issue_logs_dir is None:
            print(self.issues)
        else:
            self.issues = sorted(self.issues, key=lambda x: x["issue_level"])
            write_issues_to_json(issues=self.issues, file_path=self.log_path)
        print(
            f"Number of issues (or types of issues) found: {len(self.issues)}"
        )


def write_issues_to_json(issues: List[Dict], file_path: Path) -> None:
    with open(file_path, "w") as json_file:
        json.dump(issues, json_file, indent=4)
