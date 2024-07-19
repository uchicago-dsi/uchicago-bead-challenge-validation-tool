import string
from itertools import permutations

import pytest

from bead_inspector import constants


def test_ChallengeIdValidator():
    vfunc = constants.ChallengeIdValidator.validator()
    assert (
        vfunc("eoEYUCTZHR_corE3xwTq5S-LowMQ7QVt8_f7XpDG9dZgm8z3nK") is False
    )  # Only letters, digits, and hyphens are allowed
    assert (
        vfunc("eoEYUCTZHR-corE3xwTq5S-LowMQ7QVt8-f7XpDG9dZgm8z3nK") is True
    )  # This is fine
    assert (
        vfunc("eoEYUCTZHR-corE3xwTq5S-LowMQ7QVt8-f7XpDG9dZgm8z3nKz") is False
    )  # ChallengeIDs are limited to 50 chars
    assert vfunc("AxeFVYu2dFKppUxhSu35u") is True
    assert vfunc("a1") is True


def test_ChallengeType():
    vfunc = constants.ChallengeType.validator()
    valid_challenge_types = [
        "A",
        "B",
        "D",
        "E",
        "F",
        "L",
        "M",
        "N",
        "P",
        "S",
        "T",
        "V",
        "X",
        "Y",
        "Z",
    ]
    for char in string.ascii_letters + string.digits:
        if char in valid_challenge_types:
            assert vfunc(char) is True
        else:
            assert vfunc(char) is False


def test_CAIChallengeType():
    vfunc = constants.CAIChallengeType.validator()
    valid_challenge_types = [
        "C",
        "G",
        "Q",
        "R",
    ]
    for char in string.ascii_letters + string.digits:
        if char in valid_challenge_types:
            assert vfunc(char) is True
        else:
            assert vfunc(char) is False


def test_ChallengerType():
    vfunc = constants.ChallengerType.validator()
    valid_challenger_types = ["B", "L", "N", "T"]
    for char in string.ascii_letters + string.digits:
        if char in valid_challenger_types:
            assert vfunc(char) is True
        else:
            assert vfunc(char) is False


def test_DispositionsOfChallenge():
    vfunc = constants.DispositionsOfChallenge.validator()
    valid_values = ["A", "I", "M", "N", "R", "S"]
    for char in string.ascii_letters:
        if char in valid_values:
            assert vfunc(char) is True
        else:
            assert vfunc(char) is False


def test_DateValidator():
    vfunc = constants.DateValidator.validator()
    assert vfunc("2024-01-15") is True  # Only valid format: Extended ISO 8601
    assert vfunc("1700-09-30") is True  # Old dates are fine, if ISO 8601
    assert vfunc("20230425") is False  # %Y%m%d isn't valid
    assert vfunc("03122024") is False  # %m%d%Y isn't valid
    assert vfunc("2024-1-9") is False  # Zero-padding is required by ISO 8601
    assert vfunc("2024-23-04") is False  # %Y%d%m isn't valid
    with pytest.raises(TypeError):
        vfunc()  # A date value is required


def test_DateNullableValidator():
    vfunc = constants.DateNullableValidator.validator()
    assert vfunc("2024-01-15") is True  # Only valid format: Extended ISO 8601
    assert vfunc() is True  # Unlike above, missing params should be fine
    assert vfunc("1472-09-30") is True  # Old dates are fine, if ISO 8601
    assert vfunc("20230425") is False  # %Y%m%d isn't valid
    assert vfunc("03132024") is False  # %m%d%Y isn't valid
    assert vfunc("2024-1-9") is False  # Zero-padding is required by ISO 8601
    assert vfunc("2024-23-04") is False  # %Y%d%m isn't valid


def test_EmailValidator():
    vfunc = constants.EmailValidator.validator()
    assert vfunc("dijkstra@gmail.com") is True  # Standard
    assert vfunc("matt@site.co.uk") is True  # 1+ period allowed post @
    assert vfunc("!@!.!") is True  # Valid per the regex, but not great
    assert vfunc(" @ . ") is True  # But should it be?
    assert vfunc("( ͡❛ ͜ʖ ͡❛)@(✿◠‿◠).(❛‿❛✿̶̥̥)") is True  # But should it be?
    assert vfunc("m@tt@two_ats.com") is False  # Can only have one @ symbol
    assert vfunc("matt@no_period") is False  # Needs a period after the @
    assert vfunc("matt@no_period.") is False  # Needs a char after the period


def test_FccProviderIdValidator():
    vfunc = constants.FccProviderIdValidator.validator()
    assert (
        vfunc("123456") is True
    )  # Valid; any six digits (maybe should be ^[1-9]\d{5}$ though)
    assert vfunc("") is True  # 3 of 4 challger types don't get a provider_id
    assert vfunc(123456) is True
    assert vfunc("999999") is True
    assert vfunc("1000000") is False
    assert vfunc("12345") is False
    assert vfunc(12345) is False
    assert vfunc("apple") is False
    assert vfunc("12") is False


def test_FileNameValidator():
    vfunc = constants.FileNameValidator.validator()
    assert vfunc("bead/challenges/a_challenge/evidence.pdf") is True  # standard
    assert vfunc("bead/challenges/challenge0005/stuff.PdF") is True  # case insensitive
    assert (
        vfunc(r"bead\challenges\challenge0005\windows.PdF") is True
    )  # windows slashes
    assert vfunc("challenge_21987-final_v2_3.PDF") is True  # just a file_name
    assert (
        vfunc("challenge_21987-final_v2_(3).PDF") is False
    )  # letters, digits, hyphens, and underscores only
    assert vfunc("challenge_21987-final_v2.csv") is False  # PDFs only
    assert vfunc("challenge_21987-final_v2!@.pdf") is False  # No special chars
    assert vfunc("challenge_001.pdf challenge_003.pdf") is True
    assert vfunc("challenge_001.pdf challenge_003.ZiP") is False
    assert vfunc("challenge_001.pdf challenge 003.pdf") is False
    assert vfunc("challenge_001.pdf challenge 003.pdf challenge_004.pdf") is False
    with pytest.raises(TypeError):
        vfunc()  # An input value is required


def test_FileNameNullableValidator():
    vfunc = constants.FileNameNullableValidator.validator()
    assert vfunc("bead/challenges/a_challenge/evidence.pdf") is True  # standard
    assert vfunc() is True  # An input value is optional here
    assert vfunc("bead/challenges/challenge0005/stuff.PdF") is True  # case insensitive
    assert (
        vfunc(r"bead\challenges\challenge0005\windows.PdF") is True
    )  # windows slashes
    assert vfunc("challenge_21987-final_v2_3.PDF") is True  # just a file_name
    assert (
        vfunc("challenge_21987-final_v2_(3).PDF") is False
    )  # letters, digits, hyphens, and underscores only
    assert vfunc("challenge_21987-final_v2.csv") is False  # PDFs only
    assert vfunc("challenge_21987-final_v2!@.pdf") is False  # No special chars
    assert vfunc("challenge_001.pdf challenge_003.pdf") is True
    assert vfunc("challenge_001.pdf challenge_003.ZiP") is False
    assert vfunc("challenge_001.pdf challenge 003.pdf") is False
    assert vfunc("challenge_001.pdf challenge 003.pdf challenge_004.pdf") is False


def test_LocationClassificationCode():
    vfunc = constants.LocationClassificationCode.validator()
    valid_values = [0, 1, 2]
    check_values = [
        *string.ascii_letters,
        *string.digits,
        *[int(i) for i in string.digits],
    ]
    for char in check_values:
        if char in valid_values:
            assert vfunc(char) is True
        else:
            assert vfunc(char) is False


def test_BSLLocationIdValidator():
    vfunc = constants.BSLLocationIdValidator.validator()
    assert vfunc(0) is False
    assert vfunc("") is False  # Nulls are fails with this version
    assert vfunc(None) is False  # Nulls are fails with this version
    assert vfunc(100000000) is False
    assert vfunc(999999999) is False
    assert vfunc(1000000000) is True
    assert vfunc(9999999999) is True
    assert vfunc(10000000000) is False
    assert vfunc(-0.00001) is False
    assert vfunc("500000X000") is False


def test_BSLLocationIdNullableValidator():
    vfunc = constants.BSLLocationIdNullableValidator.validator()
    assert vfunc(0) is False
    assert vfunc("") is True  # Nulls are fine with this version
    assert vfunc(None) is True  # Nulls are fine with this version
    assert vfunc(100000000) is False
    assert vfunc(999999999) is False
    assert vfunc(1000000000) is True
    assert vfunc(9999999999) is True
    assert vfunc(10000000000) is False
    assert vfunc(-0.00001) is False
    assert vfunc("XyZ") is False


def test_NonNegativeNumberValidator():
    vfunc = constants.NonNegativeNumberValidator.validator()
    assert vfunc(0) is True
    assert vfunc("") is False  # Nulls are fails with this version
    assert vfunc(None) is False  # Nulls are fails with this version
    assert vfunc(8005882300) is True
    assert vfunc(0.000001) is True
    assert vfunc(-0.00001) is False
    assert vfunc("1") is True
    assert vfunc("-11") is False
    assert vfunc("abcDeF") is False


def test_NonNegativeNumberNullableValidator():
    vfunc = constants.NonNegativeNumberNullableValidator.validator()
    assert vfunc(0) is True
    assert vfunc("") is True  # Nulls are fine with this version
    assert vfunc(None) is True  # Nulls are fine with this version
    assert vfunc(8005882300) is True
    assert vfunc(0.000001) is True
    assert vfunc(-0.00001) is False
    assert vfunc("1") is True
    assert vfunc("-11") is False
    assert vfunc("abcDeF") is False


def test_PhoneValidator():
    vfunc = constants.PhoneValidator.validator()
    assert vfunc("800-588-2300") is True  # The only acceptable format
    assert vfunc("8005882300") is False
    assert vfunc("5882300") is False
    assert vfunc("(312) 867-5309") is False
    assert vfunc("630.867.5309") is False
    assert vfunc("630 867-5309") is False


def test_Technology():
    vfunc = constants.Technology.validator()

    valid_tech_codes = [0, 10, 40, 50, 60, 61, 70, 71, 72]
    for i in range(0, 1001):
        validation_result = vfunc(i)
        if i in valid_tech_codes:
            assert validation_result is True
        else:
            assert validation_result is False


def test_WebPageValidator():
    vfunc = constants.WebPageValidator.validator()
    assert vfunc("https://www.google.com") is True  # Standard
    assert vfunc("http://www.google.com") is True  # https or http work
    assert vfunc("https://") is True  # But should it be?
    assert vfunc(r"https://¯\_( • ᴗ • )_/¯.com") is True  # But should it be?
    assert vfunc(r"www.google.com") is False  # But should it be?
    assert vfunc(r"google.com") is False  # But should it be?


def test_ZipNullableValidator():
    vfunc = constants.ZipNullableValidator.validator()
    assert vfunc("12345") is True
    assert vfunc("01234") is True
    assert vfunc("60606") is True
    assert vfunc("5432") is False
    assert vfunc(5432) is False  # Currently throws a TypeError;
    # Maybe we should cast to str in the lambda, not sure how it's used
    assert vfunc("5432329") is False
    assert vfunc("") is True


def test_CAIRationaleNullableValidator():
    vfunc = constants.CAIRationaleNullableValidator.validator()
    valid_values = ["X", "B", "R", "D", "N", "I", "T", "O"]
    for char in string.ascii_letters + string.digits:
        if char in valid_values:
            assert vfunc(char) is True
        else:
            assert vfunc(char) is False
    assert vfunc("") is True  # Nulls are allowed (sometimes)


def test_CAIType_validator():
    vfunc = constants.CAIType.validator()
    valid_values = ["S", "L", "G", "H", "F", "P", "C", "K"]
    for char in [*list(string.ascii_letters + string.digits)]:
        if char in valid_values:
            assert vfunc(char) is True
        else:
            assert vfunc(char) is False
    assert vfunc("") is False  # Nulls are prohibited


def test_CMSCertificateNullableValidator():
    vfunc = constants.CMSCertificateNullableValidator.validator()
    assert vfunc("123456") is True
    assert vfunc("0123456789") is True
    assert vfunc("606060") is True
    assert vfunc("5432") is False
    assert vfunc(5432) is False
    assert vfunc("5432329") is False
    assert vfunc("") is True  # Nulls are allowed (sometimes)


def test_DispositionsOfChallenge_validator():
    vfunc = constants.DispositionsOfChallenge.validator()
    valid_values = ["I", "N", "A", "S", "R", "M"]
    for char in [*list(string.ascii_letters + string.digits)]:
        if char in valid_values:
            assert vfunc(char) is True
        else:
            assert vfunc(char) is False
    assert vfunc("") is False  # Nulls are prohibited


def test_FrnNullableValidator():
    vfunc = constants.FrnNullableValidator.validator()
    assert vfunc("123456") is False
    assert vfunc("0123456789") is True
    assert vfunc(1234567890) is True
    assert vfunc("01234567890") is False
    assert vfunc("10000000000") is False
    assert vfunc("606060") is False
    assert vfunc("5432") is False
    assert vfunc(5432) is False
    assert vfunc("5432329") is False
    assert vfunc("") is True  # Nulls are allowed (sometimes)


def test_State_validator():
    vfunc = constants.State.validator()
    valid_values = [
        "AL",
        "AK",
        "AS",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "DC",
        "FL",
        "GA",
        "GU",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "MP",
        "OH",
        "OK",
        "OR",
        "PA",
        "PR",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "VI",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    check_values = [
        "".join(pair) for pair in permutations(string.ascii_letters + string.digits, 2)
    ]
    for char_pair in check_values:
        if char_pair in valid_values:
            assert vfunc(char_pair) is True
        else:
            assert vfunc(char_pair) is False
    assert vfunc("") is False  # Nulls are prohibited
