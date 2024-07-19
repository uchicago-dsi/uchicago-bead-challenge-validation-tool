import datetime as dt
import re
from enum import Enum
from typing import Any, Callable, List, Optional, Tuple

EXPECTED_DATA_FORMATS = [
    "challengers",
    "challenges",
    "cai_challenges",
    "cai",
    "post_challenge_cai",
    "post_challenge_locations",
    "unserved",
    "underserved",
]
EXPECTED_ISSUE_LEVELS = ["error", "info"]

# Commented to facilitate compatibility with python versions below 3.9
#   Uncomment to run static type checking.
# from typing import Protocol
# class Validator(Protocol):
#     @classmethod
#     def validator(cls) -> Callable[Any, bool]:
#         ...


class Validator:
    # This is intended as a Protocol, but formally using the Protocol type
    #   limits use to python v3.9+, and it's mainly for static type checking,
    #   so there's no runtime harm to excluding that.
    @classmethod
    @property
    def rule_descr(cls) -> str:
        ...

    @classmethod
    @property
    def valid_values(cls) -> str:
        ...

    @classmethod
    def validator(cls) -> Callable[Any, bool]:
        ...


class RuleValidator(Validator):
    @property
    def rule_descr(self) -> str:
        ...


class DjangoEnum(Enum):
    """Enum with a short and long name. Meant to be inherited."""

    def __new__(cls, short, long, *args):
        obj = object.__new__(cls)
        obj._value_ = short
        obj.short = short
        obj.long = long
        return obj

    @classmethod
    def get_choices(cls) -> List[Tuple[str, str]]:
        return [(group.short, group.long) for group in cls]

    @classmethod
    def get_values(cls) -> List[Any]:
        return [type.value for type in cls]

    @classmethod
    def validator(cls):
        # Return a function which evaluates True/False
        # for a specific value.
        return lambda x: x in cls.get_values()


class ValidatorEnum(Enum):
    @classmethod
    def get_choices(cls) -> List[Tuple[str, str]]:
        return [(group.short, group.long) for group in cls]

    @classmethod
    def get_values(cls) -> List[Any]:
        return [type.name for type in cls]

    @classmethod
    def get_names_and_values(cls):
        return [(type.name, type.value) for type in cls]

    @classmethod
    def validator(cls):
        # Return a function which evaluates True/False
        # for a specific value.
        return lambda x: x in cls.get_values()

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [f"{v[0]} ({v[1]})" for v in cls.get_names_and_values()]


class PhoneValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that phone numbers match the pattern "
            "123-456-7890 or are blank/null."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return ["Strings matching the pattern 123-456-7890."]

    @classmethod
    def validator(cls):
        return (
            lambda x: x is None
            or x == ""
            or bool(re.match(r"^\d{3}-\d{3}-\d{4}$", x))
        )


class ZipNullableValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that Zip codes consist of exactly 5 digits "
            "or are null."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            "A string consisting of exactly 5 digits.",
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls):
        return (
            lambda x: x == "" or x is None or bool(re.match(r"^\d{5}$", str(x)))
        )


class ChallengeIdValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that challenger ids are valid.\n"
            "This validator REJECTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            (
                "A string consisting only of ASCII letters, digits, and/or "
                "hyphens and a length that is at most 50 characters."
            ),
        ]

    @classmethod
    def validator(cls):
        return lambda x: len(x) <= 50 and bool(re.match(r"^[A-Za-z0-9-]+$", x))


class DateValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "All dates must be in ISO 8601 extended date format, i.e., with "
            "hyphens, such as 2023-07-01, not 20230701.\n"
            "This validator REJECTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            (
                "A string representation of a date in ISO 8601 extended date "
                "format."
            ),
        ]

    @classmethod
    def validator(cls) -> Callable[[Optional[str]], bool]:
        def validate(x: Optional[str]) -> bool:
            try:
                dt.datetime.strptime(x, "%Y-%m-%d")
                return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", x))
            except ValueError:
                return False

        return validate


class DateNullableValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "All dates must be in ISO 8601 extended date format, i.e., with "
            "hyphens, such as 2023-07-01, not 20230701.\n"
            "This validator ACCEPTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            (
                "A string representation of a date in ISO 8601 extended date "
                "format."
            ),
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls) -> Callable[[Optional[str]], bool]:
        def validate(x: Optional[str] = None) -> bool:
            try:
                if x == "" or x is None:
                    return True
                dt.datetime.strptime(x, "%Y-%m-%d")
                return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", x))
            except ValueError:
                return False

        return validate


class EmailValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that entered emails are close to valid."
            "This validator REJECTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            (
                "A single string starteing with one or more non-@-sign "
                "character(s), then an @ sign, then one or more non-@-sign "
                "character(s), then a dot (.), then it ends with one or "
                "more non-@-sign character(s)."
            ),
        ]

    @classmethod
    def validator(cls):
        # RegEx to validate an email address with a single '@' sign
        return lambda x: bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", x))


class FileNameValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "File names must only contain allowed characters and must have an "
            "allowed file type (.pdf and .zip). If using the .zip format, only "
            "a single file_name string is allowed (i.e. no spaces). If using "
            "the .pdf format, one or more files can be submitted. "
            "If submitting multiple .pdf files, separate individual file names"
            " with a space. "
            "This validator REJECTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            (
                "A single string of one .zip file_name consisting only of "
                "ASCII letters, digits, hyphens, or underscores."
            ),
            (
                "A single string consisting of one or more space-separated "
                ".pdf file_name(s), with each consisting only of ASCII "
                "letters, digits, hyphens, or underscores."
            ),
        ]

    @classmethod
    def validator(cls) -> Callable[[str], bool]:
        def validate(file_name_str: str) -> bool:
            valid_file_name_pattern = re.compile(r"^[A-Za-z0-9_\-/\\]+$")
            file_names = file_name_str.split()
            for file_name in file_names:
                valid_match = valid_file_name_pattern.match(file_name[:-4])
                if file_name.lower().endswith(".zip"):
                    if len(file_names) > 1:
                        return False
                    else:
                        return valid_match is not None
                elif file_name.lower().endswith(".pdf"):
                    if valid_match is None:
                        return False
                else:
                    return False
            return True

        return validate


class FileNameNullableValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "File names must only contain allowed characters and must have an "
            "allowed file type (.pdf and .zip). If using the .zip format, only "
            "a single file_name string is allowed (i.e. no spaces). If using "
            "the .pdf format, one or more files can be submitted. "
            "If submitting multiple .pdf files, separate individual file names"
            " with a space. "
            "This validator Accepts null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            (
                "A single string of one .zip file_name consisting only of "
                "ASCII letters, digits, hyphens, or underscores."
            ),
            (
                "A single string consisting of one or more space-separated "
                ".pdf file_name(s), with each consisting only of ASCII "
                "letters, digits, hyphens, or underscores."
            ),
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls) -> Callable[[str], bool]:
        def validate(file_name_str: Optional[str] = None) -> bool:
            if file_name_str == "" or file_name_str is None:
                return True
            valid_file_name_pattern = re.compile(r"^[A-Za-z0-9_\-/\\]+$")
            file_names = file_name_str.split()
            for file_name in file_names:
                valid_match = valid_file_name_pattern.match(file_name[:-4])
                if file_name.lower().endswith(".zip"):
                    if len(file_names) > 1:
                        return False
                    else:
                        return valid_match is not None
                elif file_name.lower().endswith(".pdf"):
                    if valid_match is None:
                        return False
                else:
                    return False
            return True

        return validate


class LatitudeNullableValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that latitude values are between -90 and "
            "90 degrees. These values should reflect unprojected latitude "
            "coordinates (using the WGS-84 coordinate reference system) and "
            "should have a minimum precision of 6 decimals digits."
            "This validator ACCEPTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            (
                "A decimal number between -90.000000 and 90.000000 with "
                "6 decimal digits of precision"
            ),
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls):
        return lambda x: cls._validate(x)

    @staticmethod
    def _validate(x):
        if x is None or x == "":
            return True
        try:
            return -90.0 <= float(x) <= 90.0
        except ValueError:
            return False


class LongitudeNullableValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that longitude values are between -180 "
            "and 180 degrees.\n"
            "This validator ACCEPTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            (
                "A decimal number between -180.000000 and 180.000000 with "
                "6 decimal digits of precision"
            ),
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls):
        return lambda x: cls._validate(x)

    @staticmethod
    def _validate(x):
        if x is None or x == "":
            return True
        try:
            return -180.0 <= float(x) <= 180.0
        except ValueError:
            return False


class BSLLocationIdValidator:
    # Per the page at the URL:
    #     "Each Location ID is a 10-digit number starting with one billion."
    # (
    #     "https://help.bdc.fcc.gov/hc/en-us/articles/5291539645339-How-to-"
    #     "Format-Fixed-Broadband-Availability-Location-Lists"
    # )
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that location_ids are plausibly valid, "
            "although this does not check a location_id's existance in "
            "any Fabric dataset.\n"
            "This validator REJECTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            ("A string consisting of 10 digits that does not start with a 0"),
        ]

    @classmethod
    def validator(cls):
        return lambda x: cls._validate(x)

    @staticmethod
    def _validate(x):
        if x is None or x == "":
            return False
        try:
            return 10**9 <= int(x) < 10**10
        except ValueError:
            return False


class BSLLocationIdNullableValidator:
    # Per the page at the URL:
    #     "Each Location ID is a 10-digit number starting with one billion."
    # (
    #     "https://help.bdc.fcc.gov/hc/en-us/articles/5291539645339-How-to-"
    #     "Format-Fixed-Broadband-Availability-Location-Lists"
    # )
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that location_ids are plausibly valid, "
            "although this does not check a location_id's existance in "
            "any Fabric dataset.\n"
            "This validator ACCEPTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            ("A string consisting of 10 digits that does not start with a 0"),
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls):
        return lambda x: cls._validate(x)

    @staticmethod
    def _validate(x):
        if x is None or x == "":
            return True
        try:
            return 10**9 <= int(x) < 10**10
        except ValueError:
            return False


class WebPageValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that webpage values could plausibly be a "
            "URL.\n "
            "This validator ACCEPTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            "A string starting with 'http://'",
            "A string starting with 'https://'",
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls):
        # RegEx to check if the URL starts with http:// or https://
        return (
            lambda x: x == ""
            or x is None
            or bool(re.match(r"^(http://|https://)", x))
        )


class NonNegativeNumberValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that numeric values not negative.\n"
            "This validator REJECTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return ["A number that is greater than or equal to zero"]

    @classmethod
    def validator(cls):
        return lambda x: cls._validate(x)

    @staticmethod
    def _validate(x):
        if x == "" or x is None:
            return False
        try:
            return float(x) >= 0
        except ValueError:
            return False


class NonNegativeNumberNullableValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that numeric values not negative.\n"
            "This validator Accepts null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            "A number that is greater than or equal to zero",
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls):
        return lambda x: cls._validate(x)

    @staticmethod
    def _validate(x):
        if x == "" or x is None:
            return True
        try:
            return float(x) >= 0
        except ValueError:
            return False


class NonNullableValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that values are not null.\n"
            "This validator REJECTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return ["Anything except for an empty string ('')."]

    @classmethod
    def validator(cls) -> Callable[[str], bool]:
        return lambda x: x != "" and x is not None


class FccProviderIdValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that provider_ids consist of 6 digits and "
            "start with a number from 1 to 9.\n"
            "This validator ACCEPTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            "A 6-digit number between 100000 and 999999",
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls):
        # RegEx to check if the string is a 6-digit number
        return (
            lambda x: x == ""
            or x is None
            or bool(re.match(r"^[1-9]\d{5}$", str(x)))
        )


class CAIRationale(ValidatorEnum):
    """Contains CAI Rationale category codes"""

    X = "CAI has ceased operation"
    B = "Location does not require broadband service"
    R = "CAI is a private residence or non-CAI business"
    D = (
        "Definition: The challenger believes that this either fails"
        " to meet or meets the definition"
    )
    N = "New CAI"
    I = "Independent location"  # noqa E741
    T = "The CAI Type is incorrect"
    O = "Other, as described in the explanation column"  # noqa E741

    @classmethod
    @property
    def rule_descr(cls) -> str:
        rule_descr = (
            "This validation checks that CAI-challenges have a valid "
            "value for the category_code (or rationale for challenging the "
            "designation or non-designation of a location as a CAI).\n"
            "This validator REJECTS null values.\n"
        )
        return rule_descr


class CAIRationaleNullableValidator(ValidatorEnum):
    """Contains CAI Rationale category codes"""

    X = "CAI has ceased operation"
    B = "Location does not require broadband service"
    R = "CAI is a private residence or non-CAI business"
    D = (
        "Definition: The challenger believes that this either fails"
        " to meet or meets the definition"
    )
    N = "New CAI"
    I = "Independent location"  # noqa E741
    T = "The CAI Type is incorrect"
    O = "Other, as described in the explanation column"  # noqa E741

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that a CAI-challenge has a valid "
            "category_code (or rationale for challenging the designation or "
            "non-designation of a location as a CAI.\n"
            "This validator ACCEPTS null values."
        )

    @classmethod
    def validator(cls):
        return lambda x: x == "" or x is None or x in cls.get_values()


class CMSCertificateNullableValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that a healthcare-type CAI's CMS "
            "certification number (or CCN) matches an expected pattern.\n"
            "This validator ACCEPTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            "A string consisting of 6 ASCII letters or digits.",
            "A string consisting of 10 ASCII letters or digits.",
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls):
        pattern = r"^[a-zA-Z0-9]{6}$|^[a-zA-Z0-9]{10}$"
        return (
            lambda x: x == ""
            or x is None
            or (len(str(x)) <= 10 and bool(re.match(pattern, str(x))))
        )


class FrnNullableValidator:
    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks that FRN (FCC Registration Number) values "
            "match the expected pattern.\n"
            "This validator ACCEPTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [
            "A string consisting of 10 digits (zero-padded if needed).",
            "An empty string ('').",
        ]

    @classmethod
    def validator(cls):
        pattern = r"^\d{10}$"
        return lambda x: x == "" or x is None or bool(re.match(pattern, str(x)))


class Technology(ValidatorEnum):
    """Contains technology codes

    In the tuple below the data structure is:
        NTIA Technology Code
        Technology Name

    The methods below return the information.
    """

    _10 = (10, "Copper Wire")
    _40 = (40, "Coaxial Cable")
    _50 = (50, "Optical Carrier / Fiber to the Premises")
    _60 = (60, "Geostationary Satellite")
    _61 = (61, "Non-Geostationary Satellite")
    _70 = (70, "Unlicensed Terrestrial Fixed Wireless")
    _71 = (71, "Licensed Terrestrial Fixed Wireless")
    _72 = (72, "Licensed-by-Rule Terrestrial Fixed Wireless")
    _0 = (0, "Other")

    @classmethod
    @property
    def rule_descr(cls) -> str:
        rule_descr = (
            "This validation checks to see if a 'technology' value is valid.\n"
            "This validator ACCEPTS null values."
        )
        return rule_descr

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        width = max([len(str(v.value[0])) for v in cls])
        return [f"{str(v.value[0]).rjust(width)} ({v.value[1]})" for v in cls]

    def __new__(cls, tech_code, tech_description):
        obj = object.__new__(cls)
        obj._value_ = (tech_code, tech_description)
        obj.tech_code = tech_code
        obj.tech_description = tech_description
        return obj

    @classmethod
    def get_values(cls) -> List[int]:
        return [tech.tech_code for tech in cls]

    @classmethod
    def validator(cls) -> Callable:
        return lambda x: x == "" or x is None or x in cls.get_values()


class CAICategoryCode(ValidatorEnum):
    I = (  # noqa E741
        "I: CAI affiliated with a listed CAI, at a separate "
        "location requiring broadband service (For C challenge types only)"
    )
    N = (
        "N: CAI established or operational by June 30, 2024 "
        "(For C challenge types only)"
    )
    T = "T: CAI type is wrong (For C challenge types only)"
    D = (
        "D: Location either is a CAI (challenge type C) or isn't a CAI "
        "(challenge type R) (For C or R challenge types)"
    )
    O = "O: Other; describe in Explanation (For C or R challenge types)"  # noqa E741
    B = "B: CAI has ceased operation (For R challenge types only)"
    R = (
        "R: CAI is a private residence or a non-CAI business "
        "(For R challenge types only)"
    )
    X = (
        "X: Location does not require fiber broadband service appropriate "
        "for CAI (For R challenge types only)"
    )

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks to see if a 'category_code' value is one "
            "of the valid options.\n"
            "This validator ACCEPTS null values."
        )

    @classmethod
    def get_valid_C_choices(cls):
        return [
            (type.name, type.value)
            for type in cls
            if type.name in cls.get_valid_C_values(cls)
        ]

    @classmethod
    def get_valid_R_choices(cls):
        return [
            (type.name, type.value)
            for type in cls
            if type.name in cls.get_valid_R_values(cls)
        ]

    @classmethod
    def get_valid_C_values(cls):
        return ["I", "N", "T", "D", "O"]

    @classmethod
    def get_valid_R_values(cls):
        return ["D", "O", "B", "R", "X"]


class ChallengerType(ValidatorEnum):
    L = "Unit of Local Government"
    T = "A Tribal Government"
    N = "Nonprofit Org"
    B = "Broadband Provider"

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks to see if a challenger's type (in the "
            "'category' column) is valid.\n"
            "This validator REJECTS null values."
        )


class State(ValidatorEnum):
    AL = "Alabama"
    AK = "Alaska"
    AS = "American Samoa"
    AZ = "Arizona"
    AR = "Arkansas"
    CA = "California"
    CO = "Colorado"
    CT = "Connecticut"
    DE = "Delaware"
    DC = "District of Columbia"
    FL = "Florida"
    GA = "Georgia"
    GU = "Guam"
    HI = "Hawaii"
    ID = "Idaho"
    IL = "Illinois"
    IN = "Indiana"
    IA = "Iowa"
    KS = "Kansas"
    KY = "Kentucky"
    LA = "Louisiana"
    ME = "Maine"
    MD = "Maryland"
    MA = "Massachusetts"
    MI = "Michigan"
    MN = "Minnesota"
    MS = "Mississippi"
    MO = "Missouri"
    MT = "Montana"
    NE = "Nebraska"
    NV = "Nevada"
    NH = "New Hampshire"
    NJ = "New Jersey"
    NM = "New Mexico"
    NY = "New York"
    NC = "North Carolina"
    ND = "North Dakota"
    MP = "Northern Mariana Islands"
    OH = "Ohio"
    OK = "Oklahoma"
    OR = "Oregon"
    PA = "Pennsylvania"
    PR = "Puerto Rico"
    RI = "Rhode Island"
    SC = "South Carolina"
    SD = "South Dakota"
    TN = "Tennessee"
    TX = "Texas"
    VI = "U.S. Virgin Islands"
    UT = "Utah"
    VT = "Vermont"
    VA = "Virginia"
    WA = "Washington"
    WV = "West Virginia"
    WI = "Wisconsin"
    WY = "Wyoming"

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks to see if a 'state' value is one of the "
            "valid options.\n"
            "This validator REJECTS null values."
        )


class CAIType(ValidatorEnum):
    S = "S: School or institute of higher education"
    L = "L: Library"
    G = "G: Government building"
    H = (
        "H: Health clinic, health center, hospital,"
        " or another medical provider"
    )
    F = "F: Public safety entity"
    P = "P: Public housing organization"
    C = "C: Community support organization"
    K = "K: Park"

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks to see if a CAI's 'type' value is one of "
            "the valid options.\n"
            "This validator REJECTS null values."
        )


class ChallengeType(ValidatorEnum):
    A = "Availability (A)"
    S = "Speed (S)"
    L = "Latency (L)"
    D = "Data Cap (D)"
    T = "Technology (T)"
    B = "Business Service Only (B)"
    P = "Planned (or Existing) Service (P)"
    E = "Enforceable Commitment (E)"
    N = "Not Part of Enforceable Commitment (N)"
    # C = "Location is a CAI (C)"
    # R = "Location is NOT a CAI (R)"
    # G = "CAI cannot obtain qualifying broadband (G)"
    # Q = "CAI can obtain qualifying broadband (Q)"
    V = "Pre-challenge mod for DSL technology (V)"
    F = "Pre-challenge mod for fixed wireless technology (F)"
    M = "Pre-challenge mod for measurement-based anonymous speed tests (M)"
    X = "NTIA-approved eligible entity pre-challenge mod 1 (X)"
    Y = "NTIA-approved eligible entity pre-challenge mod 2 (Y)"
    Z = "NTIA-approved eligible entity pre-challenge mod 3 (Z)"

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks to see if the 'challenge_type' value (for"
            " a BSL challenges) is one of the valid options.\n"
            "This validator REJECTS null values."
        )


class CAIChallengeType(ValidatorEnum):
    C = "Location is a CAI (C)"
    R = "Location is NOT a CAI (R)"
    G = "CAI cannot obtain qualifying broadband (G)"
    Q = "CAI can obtain qualifying broadband (Q)"

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks to see if the 'challenge_type' value (for"
            " a CAI challenge) is one of the valid options.\n"
            "This validator REJECTS null values."
        )


class DispositionsOfChallenge(ValidatorEnum):
    I = "Incomplete"  # noqa
    N = "No rebuttal"
    A = "Provider agreed"
    S = "Sustained after rebuttal"
    R = "Rejected after rebuttal"
    M = "Moot due to another successful challenge"

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks to see if the 'disposition' value (for "
            "a BSL challenge) is one of the valid options.\n"
            "This validator REJECTS null values."
        )


class DispositionsOfCAIChallenge(ValidatorEnum):
    I = "Incomplete"  # noqa
    N = "No rebuttal"
    A = "Provider agreed"
    S = "Sustained after rebuttal"
    R = "Rejected after rebuttal"

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks to see if the 'disposition' value (for "
            "a CAI challenge) is one of the valid options.\n"
            "This validator REJECTS null values."
        )


class ReasonCode(DjangoEnum):
    _1 = (
        "1",
        (
            "Provider failed to schedule a service installation "
            "within 10 business days of a request (1)."
        ),
    )
    _2 = (
        "2",
        "Provider did not install the service at the agreed-upon time (2).",
    )
    _3 = (
        "3",
        (
            "Provider requested more than the standard installation fee "
            "to connect the location (3)."
        ),
    )
    _4 = ("4", "Provider denied the request for service (4).")
    _5 = (
        "5",
        (
            "Provider does not offer the technology entered "
            "above at this location (5)."
        ),
    )
    _6 = (
        "6",
        (
            "Provider does not offer the speed(s) shown on the Broadband Map "
            "for purchase at this location (6)."
        ),
    )
    _8 = (
        "8",
        (
            "No wireless signal is available at this location "
            "(only for technology codes 70 and above) (8)."
        ),
    )
    _9 = (
        "9",
        (
            "New, non-standard equipment had to be constructed "
            "at this location (9)."
        ),
    )

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks to see if the 'reason_code' value (for "
            "a challenge with the [A]vailability challenge_type) is one of "
            "the valid options.\n"
            "This validator ACCEPTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [f"{v[0]} ({v[1]})" for v in cls.get_choices()]

    @classmethod
    def get_codes(cls):
        return [int(member.value[0]) for member in cls]

    @classmethod
    def validator(cls):
        return lambda x: x in cls.get_values() or x == "" or x is None


class LocationClassificationCode(ValidatorEnum):
    _0 = ("0", "Unserved")
    _1 = ("1", "Underserved")
    _2 = ("2", "Served")

    @classmethod
    @property
    def rule_descr(cls) -> str:
        return (
            "This validation checks to see if the 'classification' value for "
            "a location_id post-challenge-process has one of the valid "
            "options.\n"
            "This validator REJECTS null values."
        )

    @classmethod
    @property
    def valid_values(cls) -> List[str]:
        return [f"{v.value[0]} ({v.value[1]})" for v in cls]

    @classmethod
    def get_choices(cls):
        return [int(member.value[0]) for member in cls]

    @classmethod
    def validator(cls):
        return lambda x: x in cls.get_choices()
