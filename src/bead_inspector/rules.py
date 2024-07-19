import datetime as dt
import re
from typing import Any, Callable, Dict, List

from bead_inspector import constants


def x_not_null_given_challenge_type_validator(
    challenge_type_index: int,
    x_col_index: int,
    non_blank_challenge_types: List[str],
) -> Callable[List[Any], bool]:
    def validate(row: List[Any]) -> bool:
        try:
            challenge_type = row[challenge_type_index]
            x_col_value = row[x_col_index]
            if challenge_type in non_blank_challenge_types:
                return x_col_value != "" and x_col_value is not None
            else:
                return True
        except IndexError:
            return False

    return validate


def x_can_be_null_given_challenge_type_validator(
    challenge_type_index: int,
    x_col_index: int,
    nullable_challenge_types: List[str],
) -> Callable[List[Any], bool]:
    def validate(row: List[Any]) -> bool:
        try:
            challenge_type = row[challenge_type_index]
            x_col_value = row[x_col_index]
            if challenge_type not in nullable_challenge_types:
                return x_col_value != "" and x_col_value is not None
            else:
                return True
        except IndexError:
            return False

    return validate


#########################################################
# #################### Challengers #################### #
#########################################################


class ChallengersISPProviderIdRuleValidator:
    rule_descr = "Broadband Providers must have FCC Provider ID."
    short_descr = "Required provider_id values are missing"
    category_index: int = 2
    provider_id_index: int = 5

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            if row[cls.category_index] != "B":
                return True
            else:
                return bool(
                    re.match(r"^[1-9]\d{5}$", row[cls.provider_id_index])
                )

        return validate


########################################################
# #################### Challenges #################### #
########################################################


class ChallengesChallengerIdGivenChallengeTypeRuleValidator:
    rule_descr = (
        "Challenger cannot be blank for challenge-types in "
        "[A, S, L, D, T, B, P]."
    )
    short_descr = "Required challenger id values are missing"
    challenge_type_index: int = 2
    challenger_id_index: int = 3
    not_null_types: List[str] = ["A", "S", "L", "D", "T", "B", "P"]

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        return x_not_null_given_challenge_type_validator(
            challenge_type_index=cls.challenge_type_index,
            x_col_index=cls.challenger_id_index,
            non_blank_challenge_types=cls.not_null_types,
        )


class ChallengesEvidenceFileChallengeTypeRuleValidator:
    rule_descr = (
        "The 'evidence_file_id' value can only be null for challenge-types "
        "'E' or 'V'."
    )
    short_descr = "Required evidence_file_id values are missing"
    challenge_type_index: int = 2
    evidence_file_id_index: int = 13
    nullable_challenge_types: List[str] = ["E", "V"]

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        return x_can_be_null_given_challenge_type_validator(
            challenge_type_index=cls.challenge_type_index,
            x_col_index=cls.evidence_file_id_index,
            nullable_challenge_types=cls.nullable_challenge_types,
        )


class ChallengesRebuttalDateAndFileRuleValidator:
    rule_descr = (
        "The rebuttal_date and response_file_id must either both be null or "
        "both should be non-null."
    )
    short_descr = "Inconsistent nullness of rebuttal_date and response_file_id"
    rebuttal_date_index: int = 5
    response_file_id_index: int = 14

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            rebuttal_date = row[cls.rebuttal_date_index]
            response_file_id = row[cls.response_file_id_index]
            rebuttal_date_is_null = rebuttal_date == "" or rebuttal_date is None
            response_file_id_is_null = (
                response_file_id == "" or response_file_id is None
            )
            if rebuttal_date_is_null:
                return response_file_id_is_null
            else:
                return not response_file_id_is_null

        return validate


class ChallengesChallengeAndRebuttalDateRuleValidator:
    rule_descr = (
        "The rebuttal_date must either be on-or-after the challenge_date "
        " or it must be null (if the challenge was not rebutted)."
    )
    short_descr = "challenge_date and rebuttal_date in wrong order"
    challenge_date_index = 4
    rebuttal_date_index: int = 5

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            challenge_date = row[cls.challenge_date_index]
            rebuttal_date = row[cls.rebuttal_date_index]
            challenge_date_not_null = (
                challenge_date != "" and challenge_date is not None
            )
            rebuttal_date_not_null = (
                rebuttal_date != "" and rebuttal_date is not None
            )
            if challenge_date_not_null and rebuttal_date_not_null:
                try:
                    date_ordering_is_possible = dt.datetime.strptime(
                        rebuttal_date, "%Y-%m-%d"
                    ) >= dt.datetime.strptime(challenge_date, "%Y-%m-%d")
                except (TypeError, ValueError):
                    date_ordering_is_possible = False
            elif challenge_date_not_null:
                date_ordering_is_possible = True
            else:
                date_ordering_is_possible = False
            return date_ordering_is_possible

        return validate


class ChallengesChallengeAndResolutionDateRuleValidator:
    rule_descr = (
        "The resolution_date must either be on-or-after the challenge_date "
        " or it must be null (if the challenge is not yet resolved)."
    )
    short_descr = "Challenge and resolution dates in wrong order"
    challenge_date_index = 4
    resolution_date_index: int = 6

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            challenge_date = row[cls.challenge_date_index]
            resolution_date = row[cls.resolution_date_index]
            challenge_date_not_null = (
                challenge_date != "" and challenge_date is not None
            )
            resolution_date_not_null = (
                resolution_date != "" and resolution_date is not None
            )
            if challenge_date_not_null and resolution_date_not_null:
                try:
                    date_ordering_is_possible = dt.datetime.strptime(
                        resolution_date, "%Y-%m-%d"
                    ) >= dt.datetime.strptime(challenge_date, "%Y-%m-%d")
                except (TypeError, ValueError):
                    date_ordering_is_possible = False
            elif challenge_date_not_null:
                date_ordering_is_possible = True
            else:
                date_ordering_is_possible = False
            return date_ordering_is_possible

        return validate


class ChallengesRebuttalAndResolutionDateRuleValidator:
    rule_descr = (
        "If the rebuttal_date and resolution_date are not null, the "
        "rebuttal_date must be before or equal to the resolution_date."
    )
    short_descr = "Rebuttal and resolution dates in wrong order"
    rebuttal_date_index: int = 5
    resolution_date_index: int = 6

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            rebuttal_date = row[cls.rebuttal_date_index]
            resolution_date = row[cls.resolution_date_index]
            rebuttal_date_not_null = (
                rebuttal_date != "" and rebuttal_date is not None
            )
            resolution_date_not_null = (
                resolution_date != "" and resolution_date is not None
            )
            if rebuttal_date_not_null and resolution_date_not_null:
                try:
                    date_ordering_is_possible = dt.datetime.strptime(
                        resolution_date, "%Y-%m-%d"
                    ) >= dt.datetime.strptime(rebuttal_date, "%Y-%m-%d")
                except (TypeError, ValueError):
                    date_ordering_is_possible = False
            else:
                date_ordering_is_possible = True
            return date_ordering_is_possible

        return validate


class ChallengesProviderIdChallengeTypeRuleValidator:
    rule_descr = (
        "A 'provider_id' value is required for all challenge_types except 'P'."
    )
    short_descr = "Required provider_id values are missing"
    challenge_type_index: int = 2
    provider_id_index: int = 8
    nullable_challenge_types: List[str] = ["P"]

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        return x_can_be_null_given_challenge_type_validator(
            challenge_type_index=cls.challenge_type_index,
            x_col_index=cls.provider_id_index,
            nullable_challenge_types=cls.nullable_challenge_types,
        )


class ChallengesTechnologyChallengeTypeRuleValidator:
    rule_descr = (
        "A technology value is required for all challenge-types except for N."
    )
    short_descr = "Required technology values are missing"
    challenge_type_index: int = 2
    technology_index: int = 9
    not_null_types: List[str] = ["N"]

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            challenge_type = row[cls.challenge_type_index]
            technology = row[cls.technology_index]
            nullable_type = challenge_type in cls.not_null_types
            null_technology_value = technology == "" or technology is None
            tech_code_is_valid = technology in constants.Technology.get_values()
            return tech_code_is_valid or (
                nullable_type and null_technology_value
            )

        return validate


class ChallengesAvailabilityChallengeTypeRuleValidator:
    rule_descr = (
        "Availability-type challenges must have a non-blank 'reason_code' "
        "in [1, 2, 3, 4, 5, 6, 8, 9]."
    )
    short_descr = "Required reason_code values are missing"
    challenge_type_index: int = 2
    reason_code_index: int = 12
    valid_reason_codes: Dict[str, List[str]] = {
        "A": ["1", "2", "3", "4", "5", "6", "8", "9"],
    }

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            challenge_type = row[cls.challenge_type_index]
            reason_code = row[cls.reason_code_index]
            if challenge_type in cls.valid_reason_codes.keys():
                return reason_code in cls.valid_reason_codes[challenge_type]
            return True

        return validate


class ChallengesResolutionGivenChallengeTypeRuleValidator:
    rule_descr = (
        "A 'resolution' value is only required when the challenge_type is 'E'"
        " or the disposition is 'I', 'R', or 'S'."
    )
    short_descr = "Required resolution values are missing"
    challenge_type_index: int = 2
    disposition_index: int = 7
    resolution_index: int = 15
    min_resolution_length: int = 3

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            challenge_type = row[cls.challenge_type_index]
            disposition = row[cls.disposition_index]
            resolution = row[cls.resolution_index]
            if (challenge_type == "E") or (disposition in ["I", "S", "R"]):
                return (
                    resolution != ""
                    and resolution is not None
                    and isinstance(resolution, str)
                    and len(resolution) >= cls.min_resolution_length
                )
            return True

        return validate


class ChallengesAdvertisedDownloadSpeedChallengeTypeRuleValidator:
    rule_descr = (
        "An 'advertised_download_speed' value is needed for all non-CAI "
        "challenge-types except for 'N'."
    )
    short_descr = "Required advertised_download_speed values are missing"
    challenge_type_index: int = 2
    advert_dl_speed_index: int = 16
    not_null_types: List[str] = [
        "A",
        "S",
        "L",
        "D",
        "T",
        "B",
        "E",
        "P",
        "V",
        "F",
        "M",
        "X",
        "Y",
        "Z",
    ]

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        return x_not_null_given_challenge_type_validator(
            challenge_type_index=cls.challenge_type_index,
            x_col_index=cls.advert_dl_speed_index,
            non_blank_challenge_types=cls.not_null_types,
        )


class ChallengesDownloadSpeedChallengeTypeRuleValidator:
    rule_descr = (
        "A 'download_speed' value is only needed for "
        "challenge-types 'M' and 'S'."
    )
    short_descr = "Required download_speed values are missing"
    challenge_type_index: int = 2
    dl_speed_index: int = 17
    not_null_types: List[str] = ["M", "S"]

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        return x_not_null_given_challenge_type_validator(
            challenge_type_index=cls.challenge_type_index,
            x_col_index=cls.dl_speed_index,
            non_blank_challenge_types=cls.not_null_types,
        )


class ChallengesAdvertisedUploadSpeedChallengeTypeRuleValidator:
    rule_descr = (
        "An 'advertised_upload_speed' value is needed for all non-CAI "
        "challenge-types except for 'N'."
    )
    short_descr = "Required advertised_upload_speed values are missing"
    challenge_type_index: int = 2
    advert_ul_speed_index: int = 18
    not_null_types: List[str] = [
        "A",
        "S",
        "L",
        "D",
        "T",
        "B",
        "E",
        "P",
        "V",
        "F",
        "M",
        "X",
        "Y",
        "Z",
    ]

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        return x_not_null_given_challenge_type_validator(
            challenge_type_index=cls.challenge_type_index,
            x_col_index=cls.advert_ul_speed_index,
            non_blank_challenge_types=cls.not_null_types,
        )


class ChallengesUploadSpeedChallengeTypeRuleValidator:
    rule_descr = (
        "An 'upload_speed' value is only needed for "
        "challenge-types 'M' and 'S'."
    )
    short_descr = "Required upload_speed values are missing"
    challenge_type_index: int = 2
    ul_speed_index: int = 19
    not_null_types: List[str] = ["M", "S"]

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        return x_not_null_given_challenge_type_validator(
            challenge_type_index=cls.challenge_type_index,
            x_col_index=cls.ul_speed_index,
            non_blank_challenge_types=cls.not_null_types,
        )


class ChallengesLatencyChallengeTypeRuleValidator:
    rule_descr = (
        "A 'latency' value is only needed for challenge-types 'L' and 'M'."
    )
    short_descr = "Required latency values are missing"
    challenge_type_index: int = 2
    latency_index: int = 20
    not_null_types: List[str] = ["L", "M"]

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        return x_not_null_given_challenge_type_validator(
            challenge_type_index=cls.challenge_type_index,
            x_col_index=cls.latency_index,
            non_blank_challenge_types=cls.not_null_types,
        )


########################################################
# ################# PostChallengeCai ################# #
########################################################


class PostChallengeCaiFRNValidationGivenCAIType:
    """Assuming that FRN is a 10-digit number. Note that it does have
    leading zeros so we may need to pad or provider warnings somewhere.
    """

    rule_descr = (
        "A FRN Number must be provided when CAI type is of S/L/H. "
        "NOTE: Just for informational purposes (not an error)."
    )
    short_descr = "Nice-to-have frn values are missing"
    cai_type_index: int = 1
    frn_index: int = 5

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            if row[cls.cai_type_index] in ["S", "L", "H"]:
                return bool(re.match(r"^\d{10}$", str(row[cls.frn_index])))
            return True

        return validate


class CaiChallengeFRNGivenType(PostChallengeCaiFRNValidationGivenCAIType):
    cai_type_index: int = 7
    frn_index: int = 11


class PostChallengeCaiLocationValidation:
    rule_descr = (
        "Every CAI must have (at least) one of:"
        "1. Lat/Long, Location ID"
        "2. address_primary, city, and zip_code"
        "3. location_id"
    )
    short_descr = "Required location-identifying sets of values all missing"
    location_id_index: int = 6
    long_index: int = 11
    lat_index: int = 12
    address_primary_index: int = 7
    city_index: int = 8
    zip_code_index: int = 10

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            location_id = row[cls.location_id_index]
            latitude = row[cls.lat_index]
            longitude = row[cls.long_index]
            address_primary = row[cls.address_primary_index]
            city = row[cls.city_index]
            zip_code = row[cls.zip_code_index]
            if location_id != "" and location_id is not None:
                return True

            if (
                latitude != ""
                and longitude != ""
                and latitude is not None
                and longitude is not None
            ):
                return True

            if (
                address_primary != ""
                and address_primary is not None
                and city != ""
                and city is not None
                and zip_code != ""
                and zip_code is not None
            ):
                return True

            return False

        return validate


class CaiChallengeCaiLocationValidationPostChallenge(
    PostChallengeCaiLocationValidation
):
    location_id_index: int = 12
    long_index: int = 17
    lat_index: int = 18
    address_primary_index: int = 13
    city_index: int = 14
    zip_code_index: int = 16


class CaiChallengeCategoryCodeConditionalGivenType:
    rule_descr = "Category Code must be filled if challenge type C/G/R"
    short_descr = "Required category values are missing"
    category_code_index: int = 4
    challenge_type_index: int = 2
    valid_category_codes: Dict[str, List[str]] = {
        "C": ["D", "N", "I", "T", "O"],
        "R": ["X", "B", "R", "D", "O"],
        "G": ["X", "B", "R", "D", "N", "I", "T", "O"],
    }

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            challenge_type = row[cls.challenge_type_index]
            category_code = row[cls.category_code_index]
            if challenge_type in cls.valid_category_codes.keys():
                return category_code in cls.valid_category_codes[challenge_type]
            return True

        return validate


class CaiChallengeExplanationConditionalTypeC:
    rule_descr = "Explanation must be present if challenge Type is C"
    short_descr = "Required explanation values are missing"
    challenge_type_index: int = 2
    explanation_index: int = 19
    min_explanation_length: int = 5

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            explanation = row[cls.explanation_index]
            if row[cls.challenge_type_index] == "C":
                if (
                    explanation == ""
                    or explanation is None
                    or not isinstance(explanation, str)
                    or (len(explanation) < cls.min_explanation_length)
                ):
                    return False
            return True

        return validate


class CaiChallengeChallengeExplanationConditionalTypeC:
    rule_descr = "Challenge Explanation must exist if challenge type is C or R"
    short_descr = "Required challenge_explanation values are missing"
    challenge_type_index: int = 2
    challenge_explanation_index: int = 6
    min_explanation_length: int = 5

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            challenge_explanation = row[cls.challenge_explanation_index]
            if row[cls.challenge_type_index] in ["R", "C"]:
                if (
                    challenge_explanation is None
                    or not isinstance(challenge_explanation, str)
                    or (len(challenge_explanation) < cls.min_explanation_length)
                ):
                    return False
            return True

        return validate


class CaiChallengeEntityNameConditionalType:
    rule_descr = "Entity Name must exist if type is S,L,G,H,F,C"
    short_descr = "Required entity_name values are missing"
    type_index: int = 7
    entity_name_index: int = 8

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            entity_name = row[cls.entity_name_index]
            if row[cls.type_index] in ["S", "L", "G", "H", "F", "C"]:
                if entity_name == "" or entity_name is None:
                    return False
            return True

        return validate


class PostChallengeCaiExplanationValidationGivenCAIType:
    rule_descr = "There must exist an Explanation when cai type is C"
    short_descr = "Required explanation values are missing"
    cai_type_index: int = 1
    explanation_index: int = 13
    min_acceptable_explanation_length = 10

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            explanation = row[cls.explanation_index]
            if row[cls.cai_type_index] == "C":
                return isinstance(explanation, str) and (
                    len(explanation) > cls.min_acceptable_explanation_length
                )

            return True

        return validate


class PostChallengeCaiCMSValidatorGivenCAIType:
    rule_descr = (
        "A CMS Number is only meaningful for CAI type H. "
        "NOTE: This is just for informational purposes (not an error)."
    )
    short_descr = "Required (nice-to-have) cms_number values are missing"
    cai_type_index: int = 1
    cms_index: int = 4

    @classmethod
    def validator(cls) -> Callable[[List[Any]], bool]:
        def validate(row: List[Any]) -> bool:
            cms_number = row[cls.cms_index]
            if row[cls.cai_type_index] == "H":
                return cms_number != "" and cms_number is not None
            return True

        return validate


class CaiChallengeCMSConditionalTypeH(PostChallengeCaiCMSValidatorGivenCAIType):
    cai_type_index: int = 7
    cms_index: int = 10
