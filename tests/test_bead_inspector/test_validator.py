import csv
import pytest
import tempfile

from bead_inspector import validator


@pytest.fixture
def temp_dir(tmpdir_factory):
    return tmpdir_factory.mktemp("data")


def create_csv_file(file_path, csv_data: str, encoding: str = "utf-8"):
    with open(file_path, "w+", newline="", encoding=encoding) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)


@pytest.fixture
def challengers_empty_file(temp_dir):
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
    )
    file_path = temp_dir.join("challengers.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def challenges_empty_file(temp_dir):
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
    )
    file_path = temp_dir.join("challenges.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def cai_empty_file(temp_dir):
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
    )
    file_path = temp_dir.join("cai.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def cai_challenges_empty_file(temp_dir):
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
    )
    file_path = temp_dir.join("cai_challenges.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def unserved_empty_file(temp_dir):
    csv_content = "1234567890\n"
    file_path = temp_dir.join("unserved.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def underserved_empty_file(temp_dir):
    csv_content = "1234567890\n"
    file_path = temp_dir.join("underserved.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def post_challenge_cai_empty_file(temp_dir):
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
    )
    file_path = temp_dir.join("post_challenge_cai.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def post_challenge_locations_empty_file(temp_dir):
    csv_content = "location_id,classification\n"
    file_path = temp_dir.join("post_challenge_locations.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


def test_BEADChallengeDataValidator_with_all_files(
    temp_dir,
    challengers_empty_file,
    challenges_empty_file,
    cai_empty_file,
    cai_challenges_empty_file,
    unserved_empty_file,
    underserved_empty_file,
    post_challenge_cai_empty_file,
    post_challenge_locations_empty_file,
):
    bcdv = validator.BEADChallengeDataValidator(temp_dir)
    assert len(bcdv.issues) == 0


def test_BEADChallengeDataValidator_with_some_files_missing(
    temp_dir,
    challengers_empty_file,
    challenges_empty_file,
    unserved_empty_file,
    post_challenge_cai_empty_file,
    post_challenge_locations_empty_file,
):
    missing_formats = {"cai", "cai_challenges", "underserved"}
    bcdv = validator.BEADChallengeDataValidator(temp_dir)
    file_issues = [i for i in bcdv.issues if i["issue_type"] == "missing_data_file"]
    assert set([i["data_format"] for i in file_issues]) == missing_formats


#########################################################
# ########### Data File Encoding Checks ############### #
#########################################################


@pytest.fixture
def challenges_file_with_cp1252_chars(temp_dir):
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,,,,,\n"
        "3,,“windows double quote marks”,,,,,,,,,,,,,,,,,\n"
        "4,,‘windows single quote marks’,,,,,,,,,,,,,,,,,\n"
        "5,,Euro sign: € (U+20AC),,,,,,,,,,,,,,,,,\n"
        "6,,Euro sign: € (U+20AC),,,,,,,,,,,,,,,,,\n"
        "7,,Trademark sign: ™ (U+2122),,,,,,,,,,,,,,,,,\n"
        "8,,Bullet: • (U+2022),,,,,,,,,,,,,,,,,\n"
        "9,,Ellipsis: … (U+2026),,,,,,,,,,,,,,,,,\n"
    )
    file_path = temp_dir.join("challenges.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines, encoding="cp1252")
    return file_path


@pytest.fixture
def challenges_file_with_latin1_chars(temp_dir):
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,Résumé,,,,,,,,,,,,,,,,,\n"
        "3,,El Niño,,,,,,,,,,,,,,,,,\n"
        "4,,Hände,,,,,,,,,,,,,,,,,\n"
        "5,,Mötley Crüe,,,,,,,,,,,,,,,,,\n"
    )
    file_path = temp_dir.join("challenges.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines, encoding="latin1")
    return file_path


@pytest.fixture
def challenges_file_with_iso_8859_1_chars(temp_dir):
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,Résumé,,,,,,,,,,,,,,,,,\n"
        "3,,El Niño,,,,,,,,,,,,,,,,,\n"
        "4,,Hände,,,,,,,,,,,,,,,,,\n"
        "5,,Mötley Crüe,,,,,,,,,,,,,,,,,\n"
    )
    file_path = temp_dir.join("challenges.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines, encoding="iso-8859-1")
    return file_path


def test_BEADChallengeDataValidator_with_files_encoded_in_cp1252(
    temp_dir,
    challenges_file_with_cp1252_chars,
):
    bcdv = validator.BEADChallengeDataValidator(temp_dir)
    assert bcdv.issues != []


def test_BEADChallengeDataValidator_with_files_encoded_in_latin1(
    temp_dir,
    challenges_file_with_latin1_chars,
):
    bcdv = validator.BEADChallengeDataValidator(temp_dir)
    assert bcdv.issues != []


def test_BEADChallengeDataValidator_with_files_encoded_in_iso_8859_1(
    temp_dir,
    challenges_file_with_iso_8859_1_chars,
):
    bcdv = validator.BEADChallengeDataValidator(temp_dir)
    assert bcdv.issues != []


#########################################################
# ########### Data Files Missing Columns ############## #
#########################################################


@pytest.fixture
def challengers_file_without_id_column(temp_dir):
    csv_content = (
        "category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        ",,,,,,\n"
    )
    file_path = temp_dir.join("challengers.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def challenges_file_without_id_column(temp_dir):
    csv_content = (
        "challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        ",,,,,,,,,,,,,,,,,,\n"
    )
    file_path = temp_dir.join("challenges.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def cai_file_without_id_column(temp_dir):
    csv_content = (
        "type,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        ",,,,,,,,,,,,,\n"
    )
    file_path = temp_dir.join("cai.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def cai_challenges_file_without_id_column(temp_dir):
    csv_content = (
        "challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        ",,,,,,,,,,,,,,,,,,,\n"
    )
    file_path = temp_dir.join("cai_challenges.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def post_challenge_cai_file_without_id_column(temp_dir):
    csv_content = (
        "type,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        ",,,,,,,,,,,,,\n"
    )
    file_path = temp_dir.join("post_challenge_cai.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def post_challenge_locations_file_without_id_column(temp_dir):
    csv_content = "classification\n\n"
    file_path = temp_dir.join("post_challenge_locations.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


def test_BEADChallengeDataValidator_with_files_with_id_columns_missing(
    temp_dir,
    challengers_file_without_id_column,
    challenges_file_without_id_column,
    cai_file_without_id_column,
    cai_challenges_file_without_id_column,
    post_challenge_cai_file_without_id_column,
    post_challenge_locations_file_without_id_column,
):
    bcdv = validator.BEADChallengeDataValidator(temp_dir)
    file_issues = [i for i in bcdv.issues if i["issue_type"] == "multi_file_validation"]
    assert len(file_issues) == 2


#########################################################
# ################### Sample Data ##################### #
#########################################################


@pytest.fixture
def challenges_data_file(temp_dir):
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,S,2,2024-03-29,2024-05-24,2024-07-04,S,717410,10,2754984828,,,age.pdf,"
        "as.pdf,Lorem,106,1123,68,791,100.2\n"
        "3,N,3,2024-05-19,,2024-07-01,A,579751,10,6982608163,,,wife.pdf,"
        ",Scientist you to that open.,,333,,491,96.41\n"
        "4,X,,2024-02-23,2024-05-10,2024-08-21,M,796614,0,8733869095,,,energy.pdf,"
        "night.pdf,,365,82,1011,1071,164.25\n"
        "5,T,5,2024-04-23,,2024-05-04,A,776568,60,1497861472,,,budget.pdf,"
        ",Front much interview total executive hit.,1195,495,1032,295,43.764\n"
        "6,L,6,2024-04-09,,2024-07-28,A,725620,10,3934728492,,,their.pdf,"
        ",,728,1081,1101,414,26.1\n"
        "7,V,7,2024-01-02,,2024-09-29,A,751131,61,6405418026,,,best.pdf,"
        ",Take effect big bad.,1370,1045,1446,563,107.99762762202313\n"
        "8,A,8,2024-05-13,2024-07-27,2024-11-19,M,935179,70,9913299240,,9,mouth.pdf,"
        "treatment.pdf,Against daughter amount to play.,274,,226,,129.078\n"
        "9,N,9,2024-02-08,2024-02-23,2024-03-27,M,400530,,8607048697,,,yourself.pdf,"
        "information.pdf,Clear population perform.,40,1114,1178,1007,41.8\n"
        "10,V,606,2024-01-16,,,A,131955,70,7441127180,,,find.pdf,,Paper co lawyer,"
        "351,528,857,149,197.65\n"
    )
    file_path = temp_dir.join("challenges.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def cai_data_file(temp_dir):
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "C,2,,,,,5741 Warren St,Timothyport,NJ,07855,,,Words.,1000,530\n"
        "F,3,,,,4670242652,,,UT,,,,Blue step southern minute state way.,1000,1430\n"
        "H,4,,4854869256,9122416326,,,,ME,,-76.88442,40.2737,,1000,350\n"
        "S,5,,,1336068487,,,,AZ,,-94.74049,32.5007,Field Congress,1000,450\n"
        "P,6,,,,,,,CA,,-73.99681,40.94065,Throw often build anyone.,1000,310\n"
        "G,7,,,,,,,CT,,-71.29144,41.54566,All memory.,1000,800\n"
        "L,8,,,3283939845,,6859 Allen Canyon,Laurieton,VI,00801,,,Lorem.,1000,250\n"
    )
    file_path = temp_dir.join("cai.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def cai_challenges_data_file(temp_dir):
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,C,3,,,,,,,,,,,,,,,,,,\n"
        "3,R,8,,,,,,,,,,,,,,,,,,\n"
        "4,G,6,,,,,,,,,,,,,,,,,,\n"
        "5,Q,2,,,,,,,,,,,,,,,,,,\n"
        "6,C,1234,,,,,,,,,,,,,,,,,,\n"
    )
    file_path = temp_dir.join("cai_challenges.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def challengers_data_file(temp_dir):
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        "2,B,ISP LLC,http://web.co,403388,Nic Packet,NIC@route.net,127-001-4040\n"
        "3,T,Icw Act,http://icwa.in,,Barby Grill,b@icwa.in,197-202-1548\n"
        "4,L,City Twp,http://www.city.gov,819546,Lisa Holt,cy@eg.org,123-911-7946\n"
        "5,N,Doing Good,http://np.co,279726,Phil Anthropy,phil@give.co,526-324-0487\n"
        "6,T,Haa Land,http://dept.in,,Deb,sec@dept.in,346-276-1110\n"
        "7,N,Fun Raisers,http://www.cause.fun/,,Steph,steph@cause.fun,686-230-0642\n"
        "8,B,Muni Net,https://muni.net,570880,Ethel Net,ethel@muni.net,785-904-8320\n"
        "9,L,Busytown,http://www.busy.twp,515800,Lowly W,lowly@busy.twp,617-476-4603\n"
        "10,L,Paw Patrol,http://www.paw.gov,911911,Paws,paw@paw.gov,911-911-9111\n"
    )
    file_path = temp_dir.join("challengers.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def post_challenge_cai_data_file(temp_dir):
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "C,2,,,,,5741 Warren St,Timothyport,NJ,07855,,,Words.,1000,530\n"
        "F,3,,,,4670242652,,,UT,,,,Blue step southern minute state way.,1000,1430\n"
        "H,4,,4854869256,9122416326,,,,ME,,-76.88442,40.2737,,1000,350\n"
        "S,5,,,1336068487,,,,AZ,,-94.74049,32.5007,Field Congress,1000,450\n"
        "P,6,,,,,,,CA,,-73.99681,40.94065,Throw often build anyone.,1000,310\n"
        "G,7,,,,,,,CT,,-71.29144,41.54566,All memory.,1000,800\n"
        "L,8,,,3283939845,,6859 Allen Canyon,Laurieton,VI,00801,,,Lorem.,1000,250\n"
    )
    file_path = temp_dir.join("post_challenge_cai.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def post_challenge_locations_data_file(temp_dir):
    csv_content = (
        "location_id,classification\n"
        "9251438703,2\n"
        "9466464959,2\n"
        "5832697349,1\n"
        "6861164234,0\n"
        "5157936221,1\n"
        "9858021981,0\n"
        "4555893936,2\n"
        "1490692291,0\n"
        "4138408302,1\n"
        "2509942475,2\n"
        "6770720004,0\n"
    )
    file_path = temp_dir.join("post_challenge_locations.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def unserved_data_file(temp_dir):
    csv_content = (
        "6861164234\n"
        "9858021981\n"
        "1490692291\n"
        "6770720004\n"
        "2535464157\n"
        "9675783723\n"
        "2326138798\n"
        "3788764360\n"
        "9777155993\n"
        "5410470404\n"
        "9146836216\n"
        "6987623003\n"
        "5080534585\n"
        "8915454212\n"
    )
    file_path = temp_dir.join("unserved.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


@pytest.fixture
def underserved_data_file(temp_dir):
    csv_content = (
        "1173271099\n"
        "5941169893\n"
        "6971392161\n"
        "5435463206\n"
        "9983387865\n"
        "3208742743\n"
        "2754984828\n"
        "3934728492\n"
        "6405418026\n"
        "4285253455\n"
        "6060718635\n"
        "7678465792\n"
        "5747440694\n"
        "4244932267\n"
        "7451885843\n"
    )
    file_path = temp_dir.join("underserved.csv")
    csv_lines = [line.split(",") for line in csv_content.split("\n") if line]
    create_csv_file(file_path, csv_lines)
    return file_path


#########################################################
# #################### Multi-File ##################### #
#########################################################


def test_multi_file_validations__cai_challenges_and_challengers(
    temp_dir,
    challengers_data_file,
    cai_challenges_data_file,
):
    missing_challenger_ids = {"1234"}
    bcdv = validator.BEADChallengeDataValidator(temp_dir)
    multi_file_issues = [
        i for i in bcdv.issues if i["issue_type"] == "multi_file_validation"
    ]
    assert len(multi_file_issues) == 1
    invalid_valids = multi_file_issues[0]["issue_details"]["invalid_values"]
    assert (
        set([i["missing_challenger_ids"] for i in invalid_valids])
        == missing_challenger_ids
    )


def test_multi_file_validations__challenges_and_challengers(
    temp_dir,
    challengers_data_file,
    challenges_data_file,
):
    missing_challenger_ids = {"", "606"}
    bcdv = validator.BEADChallengeDataValidator(temp_dir)
    multi_file_issues = [
        i for i in bcdv.issues if i["issue_type"] == "multi_file_validation"
    ]
    assert len(multi_file_issues) == 1
    invalid_valids = multi_file_issues[0]["issue_details"]["invalid_values"]
    assert (
        set([i["missing_challenger_ids"] for i in invalid_valids])
        == missing_challenger_ids
    )


#########################################################
# #################### Challengers #################### #
#########################################################


def test_challenger__column_names():
    csv_content = (
        "challenger,category,challenge_type,webpage,provider_id,contact_name,"
        "contact_email,contact_phone,contact_address\n"
    )
    missing_column_names = ["organization"]
    extra_column_names = ["challenge_type", "contact_address"]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_name_validation"
        ]
        assert len(test_issues) == 1
        assert list(test_issues[0].keys()) == [
            "columns_missing_from_file",
            "extra_columns_in_file",
        ]
        assert set(test_issues[0]["columns_missing_from_file"]) == set(
            missing_column_names
        )
        assert set(test_issues[0]["extra_columns_in_file"]) == set(extra_column_names)


def test_challenger__column_order():
    csv_content = (
        "challenger,provider_id,organization,category,webpage,contact_name,"
        "contact_phone,contact_email\n"
    )
    col_numbers_w_wrong_names = [2, 4, 5, 7, 8]
    expected_cols_not_in_expected_place = [
        "category",
        "provider_id",
        "webpage",
        "contact_email",
        "contact_phone",
    ]
    file_col_names_in_wrong_place = [
        "provider_id",
        "category",
        "webpage",
        "contact_phone",
        "contact_email",
    ]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_order_validation"
        ]
        assert len(test_issues) == 1
        cols_out_of_order = test_issues[0]["cols_out_of_order"]
        assert all(
            list(el.keys())
            == ["column_number", "expected_column_name", "column_name_in_file"]
            for el in cols_out_of_order
        )
        missing_expected_cols_w_missings = [
            el["expected_column_name"] for el in cols_out_of_order
        ]
        misordered_expected_col_names = [
            c for c in missing_expected_cols_w_missings if c != "<missing_column>"
        ]
        misordered_col_names_in_file_w_missings = [
            el["column_name_in_file"] for el in cols_out_of_order
        ]
        misordered_col_names_in_file = [
            c
            for c in misordered_col_names_in_file_w_missings
            if c != "<missing_column>"
        ]
        assert set(misordered_expected_col_names) == set(
            expected_cols_not_in_expected_place
        )
        assert set(misordered_col_names_in_file) == set(file_col_names_in_wrong_place)
        assert set(el["column_name_in_file"] for el in cols_out_of_order) == set(
            file_col_names_in_wrong_place
        )
        assert [
            el["column_number"] for el in cols_out_of_order
        ] == col_numbers_w_wrong_names


def test_challenger_col_content__challenger():
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        ",2,,,,,,\n"
        "challenger id 2,3,,,,,,\n"
    )
    invalid_value_rows = [2]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "challenger"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenger_col_content__category():
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        "2,L,,,,,,\n"
        "3,A,,,,,,\n"
        "4,B,,,,,,\n"
        "5,T,,,,,,\n"
        "6,E,,,,,,\n"
        "7,N,,,,,,\n"
        "8,,,,,,,\n"
    )
    invalid_value_rows = [3, 6, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "category"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenger_col_content__organization():
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        "2,T,,,,,,\n"
        "3,N,NPCorp,,,,,\n"
        '4,L,"City of Newark, Netwark Dept, NJ",,,,,\n'
        "5,B,123!@#,,,,,\n"
    )
    invalid_value_rows = [2]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "organization"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenger_col_content__webpage():
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        "2,,,https://www.google.com,,,,\n"
        "3,,,http://www.google.com,,,,\n"
        "4,,,www.google.com,,,,\n"
        "5,,,,,,,\n"
        "6,,,bad_url,,,,\n"
        "7,,,127.0.0.1,,,,\n"
    )
    invalid_value_rows = [4, 6, 7]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "webpage"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenger_col_content__provider_id():
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        "2,T,,,123456,,,\n"
        "3,B,,,012345,,,\n"
        "4,N,,,,,,\n"
        "5,B,,,99999,,,\n"
        "6,B,,,100000,,,\n"
        "7,B,,,999999,,,\n"
        "8,B,,,1000000,,,\n"
    )
    invalid_value_rows = [3, 5, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "provider_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenger_col_content__contact_name():
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        "2,,,,,I.P. Addy,,\n"
        "3,,,,,,,\n"
    )
    invalid_value_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "contact_name"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenger_col_content__contact_email():
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        "2,,,,,,dijkstra@gmail.com,\n"
        "3,,,,,,a_star@.,\n"
        "4,,,,,,N@T@two_ats.com,\n"
        "5,,,,,,,\n"
    )
    invalid_value_rows = [3, 4, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "contact_email"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenger_col_content__contact_phone():
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        "2,,,,,,,3128675305\n"
        "3,,,,,,,312-867-5305\n"
        "4,,,,,,,312.867.5305\n"
        "5,,,,,,,867-5305\n"
        "6,,,,,,,(312) 867-5305\n"
        "7,,,,,,,000-000-0000\n"
        "8,,,,,,,1-312-867-5305\n"
    )
    invalid_value_rows = [2, 4, 5, 6, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "contact_phone"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenger_row_rule__ISPs_need_provider_ids():
    csv_content = (
        "challenger,category,organization,webpage,provider_id,contact_name,"
        "contact_email,contact_phone\n"
        "2,B,,,123456,,,\n"
        "3,B,,,,,,\n"
        "4,N,,,,,,\n"
        "5,T,,,,,,\n"
        "6,L,,,,,,\n"
    )
    rule_breaking_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengerDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengersISPProviderIdRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == rule_breaking_rows
        assert all(r in failing_rows for r in rule_breaking_rows)


########################################################
# #################### Challenges #################### #
########################################################


def test_challenges__column_names():
    csv_content = (
        "challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,webpage,disposition,provider_id,technology,"
        "location_id,unit,reason_code,evidence_file_id,response_file_id,"
        "resolution,advertised_download_speed,download_speed,"
        "advertised_upload_speed,upload_speed,latency,organization,"
        "contact_email,contact_phone\n"
    )
    missing_column_names = ["challenge"]
    extra_column_names = [
        "organization",
        "contact_email",
        "contact_phone",
        "webpage",
    ]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_name_validation"
        ]
        assert len(test_issues) == 1
        assert list(test_issues[0].keys()) == [
            "columns_missing_from_file",
            "extra_columns_in_file",
        ]
        assert set(test_issues[0]["columns_missing_from_file"]) == set(
            missing_column_names
        )
        assert set(test_issues[0]["extra_columns_in_file"]) == set(extra_column_names)


def test_challenges__column_order():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
    )
    file_col_names_in_wrong_place = []
    col_numbers_w_wrong_names = []
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_order_validation"
        ]
        assert len(test_issues) == len(file_col_names_in_wrong_place)
        assert set(el["column_name_in_file"] for el in test_issues) == set(
            file_col_names_in_wrong_place
        )
        assert [el["column_number"] for el in test_issues] == col_numbers_w_wrong_names

    # Now with columns out of order and with extra columns
    csv_content = (
        "challenge_type,challenger,challenge_date,rebuttal_date,webpage,"
        "resolution_date,disposition,provider_id,technology,location_id,"
        "unit,reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency,organization,contact_email,contact_phone\n"
    )
    col_numbers_w_wrong_names = [1, 2, 3, 4, 5, 21, 22, 23]
    expected_cols_not_in_expected_place = [
        "challenge",
        "challenge_type",
        "challenger",
        "challenge_date",
        "rebuttal_date",
    ]
    file_col_names_in_wrong_place = [
        "challenge_type",
        "challenger",
        "challenge_date",
        "rebuttal_date",
        "webpage",
        "organization",
        "contact_email",
        "contact_phone",
    ]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_order_validation"
        ]
        assert len(test_issues) == 1
        cols_out_of_order = test_issues[0]["cols_out_of_order"]
        assert all(
            list(el.keys())
            == ["column_number", "expected_column_name", "column_name_in_file"]
            for el in cols_out_of_order
        )
        missing_expected_cols_w_missings = [
            el["expected_column_name"] for el in cols_out_of_order
        ]
        misordered_expected_col_names = [
            c for c in missing_expected_cols_w_missings if c != "<missing_column>"
        ]
        misordered_col_names_in_file_w_missings = [
            el["column_name_in_file"] for el in cols_out_of_order
        ]
        misordered_col_names_in_file = [
            c
            for c in misordered_col_names_in_file_w_missings
            if c != "<missing_column>"
        ]
        assert set(misordered_expected_col_names) == set(
            expected_cols_not_in_expected_place
        )
        assert set(misordered_col_names_in_file) == set(file_col_names_in_wrong_place)
        assert set(el["column_name_in_file"] for el in cols_out_of_order) == set(
            file_col_names_in_wrong_place
        )
        assert [
            el["column_number"] for el in cols_out_of_order
        ] == col_numbers_w_wrong_names


def test_challenges_column_dtypes__technology():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,10,,,,,,,,,,,\n"
        "3,,,,,,,,40,,,,,,,,,,,\n"
        "4,,,,,,,,-,,,,,,,,,,,\n"
        "5,,,,,,,,50,,,,,,,,,,,\n"
        "6,,,,,,,,MV,,,,,,,,,,,,\n"
        "7,,,,,,,,60,,,,,,,,,,,\n"
        "8,,,,,,,,61,,,,,,,,,,,\n"
        "9,,,,,,,,62e,,,,,,,,,,,\n"
        "10,,,,,,,,70,,,,,,,,,,,\n"
        "11,,,,,,,,71.0,,,,,,,,,,,\n"
        "12,,,,,,,,72,,,,,,,,,,,\n"
        "13,,,,,,,,0.0,,,,,,,,,,,\n"
        "14,,,,,,,,,,,,,,,,,,,\n"
        "15,,,,,,,,0.02,,,,,,,,,,,\n"
    )
    invalid_value_rows = [4, 6, 9, 11, 13, 15]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "technology"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_column_dtypes__location_id():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,1234567890,,,,,,,,,,\n"
        "3,,,,,,,,,110 W Lake,,,,,,,,,,\n"
        "4,,,,,,,,,1,,,,,,,,,,\n"
        "5,,,,,,,,,,,,,,,,,,,\n"
        "6,,,,,,,,,312-555-2323,,,,,,,,,,,\n"
        "7,,,,,,,,,1.0,,,,,,,,,,\n"
        "8,,,,,,,,,1.01,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 5, 6, 7, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_column_dtypes__advertised_download_speed():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,101,,,,\n"
        "3,,,,,,,,,,,,,,,,,,,\n"
        "4,,,,,,,,,,,,,,,101.11,,,,\n"
        "5,,,,,,,,,,,,,,,101-1,,,,\n"
        "6,,,,,,,,,,,,,,,0xFF,,,,,\n"
        "7,,,,,,,,,,,,,,,1234.56,,,,,\n"
        "8,,,,,,,,,,,,,,,1234.0,,,,,\n"
    )
    invalid_value_rows = [5, 6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "advertised_download_speed"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_column_dtypes__download_speed():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,,101,,,\n"
        "3,,,,,,,,,,,,,,,,,,,\n"
        "4,,,,,,,,,,,,,,,,101.11,,,\n"
        "5,,,,,,,,,,,,,,,,101-1,,,\n"
        "6,,,,,,,,,,,,,,,,0xFF,,,\n"
        "7,,,,,,,,,,,,,,,,1234.56,,,\n"
        "8,,,,,,,,,,,,,,,,1234.0,,,\n"
    )
    invalid_value_rows = [5, 6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "download_speed"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_column_dtypes__advertised_upload_speed():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,,,101,,\n"
        "3,,,,,,,,,,,,,,,,,,,\n"
        "4,,,,,,,,,,,,,,,,,101.11,,\n"
        "5,,,,,,,,,,,,,,,,,101-1,,\n"
        "6,,,,,,,,,,,,,,,,,0xFF,,\n"
        "7,,,,,,,,,,,,,,,,,1234.56,,\n"
        "8,,,,,,,,,,,,,,,,,1234.0,,\n"
    )
    invalid_value_rows = [5, 6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "advertised_upload_speed"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_column_dtypes__upload_speed():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,,,,101,\n"
        "3,,,,,,,,,,,,,,,,,,,\n"
        "4,,,,,,,,,,,,,,,,,,101.11,\n"
        "5,,,,,,,,,,,,,,,,,,101-1,\n"
        "6,,,,,,,,,,,,,,,,,,0xFF,\n"
        "7,,,,,,,,,,,,,,,,,,1234.56,\n"
        "8,,,,,,,,,,,,,,,,,,1234.0,\n"
    )
    invalid_value_rows = [5, 6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "upload_speed"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_column_dtypes__latency():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,,,,,101\n"
        "3,,,,,,,,,,,,,,,,,,,\n"
        "4,,,,,,,,,,,,,,,,,,,101.11\n"
        "5,,,,,,,,,,,,,,,,,,,101-1\n"
        "6,,,,,,,,,,,,,,,,,,,0xFF\n"
        "7,,,,,,,,,,,,,,,,,,,1234.56\n"
        "8,,,,,,,,,,,,,,,,,,,1234.0\n"
    )
    invalid_value_rows = [5, 6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "latency"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__challenge():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "eoEYUCTZHR-corE3xwTq5S-LowMQ7QVt8-f7XpDG9dZgm8z3nK,2,,,,,,,,,,,,,,,,,,\n"  # noqa
        "Xnow432nXcjgodiDY8F-YipaGRhV24iYQRBPeW6LzoN6piXHFgW,3,,,,,,,,,,,,,,,,,,\n"  # noqa
        "a_iDY8F-Yi_V123456789XHFg,4,,,,,,,,,,,,,,,,,,\n"
        "ABCDEFGHIJKLMNOPQRSTUVWXYabcdefghijklmnopqrstuvwxy,5,,,,,,,,,,,,,,,,,,\n"  # noqa
        "a1,6,,,,,,,,,,,,,,,,,,\n"
        "abcde-12345,7,,,,,,,,,,,,,,,,,,\n"
        "abcde-12345!,8,,,,,,,,,,,,,,,,,,\n"
    )
    over_length_rows = [3]
    invalid_char_rows = [4, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "challenge"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in over_length_rows)
        assert all(r in failing_rows for r in invalid_char_rows)


def test_challenges_col_content__challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,A,,,,,,,,,,,,,,,,,,\n"
        "3,S,,,,,,,,,,,,,,,,,,\n"
        "4,L,,,,,,,,,,,,,,,,,,\n"
        "5,D,,,,,,,,,,,,,,,,,,\n"
        "6,T,,,,,,,,,,,,,,,,,,\n"
        "7,B,,,,,,,,,,,,,,,,,,\n"
        "8,P,,,,,,,,,,,,,,,,,,\n"
        "9,E,,,,,,,,,,,,,,,,,,\n"
        "10,N,,,,,,,,,,,,,,,,,,\n"
        "11,1,,,,,,,,,,,,,,,,,,\n"
        "12,R,,,,,,,,,,,,,,,,,,\n"
        "13,G,,,,,,,,,,,,,,,,,,\n"
        "14,Q,,,,,,,,,,,,,,,,,,\n"
        "15,V,,,,,,,,,,,,,,,,,,\n"
        "16,F,,,,,,,,,,,,,,,,,,\n"
        "17,M,,,,,,,,,,,,,,,,,,\n"
        "18,X,,,,,,,,,,,,,,,,,,\n"
        "19,Y,,,,,,,,,,,,,,,,,,\n"
        "20,Z,,,,,,,,,,,,,,,,,,\n"
        "21,H,,,,,,,,,,,,,,,,,,\n"
        "22,I,,,,,,,,,,,,,,,,,,\n"
        "23,J,,,,,,,,,,,,,,,,,,\n"
        "24,K,,,,,,,,,,,,,,,,,,\n"
        "25,C,,,,,,,,,,,,,,,,,,\n"
        "26,O,,,,,,,,,,,,,,,,,,\n"
        "27,U,,,,,,,,,,,,,,,,,,\n"
        "28,W,,,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [11, 12, 13, 14, 21, 22, 23, 24, 25, 26, 27, 28]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "challenge_type"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__challenge_date():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,2024-03-15,,,,,,,,,,,,,,,,\n"
        "3,,,,,,,,,,,,,,,,,,,\n"
        "4,,,20240228,,,,,,,,,,,,,,,,\n"
        '5,,,"Mar 25, 2024",,,,,,,,,,,,,,,,\n'
        "6,,,03-15-2024,,,,,,,,,,,,,,,,\n"
        "7,,,15-03-2024,,,,,,,,,,,,,,,,\n"
        "8,,,2024-3-15,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 4, 5, 6, 7, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "challenge_date"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__rebuttal_date():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,2024-03-15,,,,,,,,,,,,,,,\n"
        "3,,,,,,,,,,,,,,,,,,,\n"
        "4,,,,20240228,,,,,,,,,,,,,,,\n"
        '5,,,,"Mar 25, 2024",,,,,,,,,,,,,,,\n'
        "6,,,,03-15-2024,,,,,,,,,,,,,,,,\n"
        "7,,,,15-03-2024,,,,,,,,,,,,,,,\n"
        "8,,,,2024-3-15,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [4, 5, 6, 7, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "rebuttal_date"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__resolution_date():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,2024-03-15,,,,,,,,,,,,,,\n"
        "3,,,,,,,,,,,,,,,,,,,\n"
        "4,,,,,20240228,,,,,,,,,,,,,,\n"
        '5,,,,,"Mar 25, 2024",,,,,,,,,,,,,,\n'
        "6,,,,,03-15-2024,,,,,,,,,,,,,,,\n"
        "7,,,,,15-03-2024,,,,,,,,,,,,,,\n"
        "8,,,,,2024-3-15,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [4, 5, 6, 7, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "resolution_date"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__disposition():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,I,,,,,,,,,,,,,\n"
        "3,,,,,,N,,,,,,,,,,,,,\n"
        "4,,,,,,A,,,,,,,,,,,,,\n"
        "5,,,,,,S,,,,,,,,,,,,,\n"
        "6,,,,,,E,,,,,,,,,,,,,,\n"
        "7,,,,,,R,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,,,,,,,,,,\n"
        "9,,,,,,M,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [6, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "disposition"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__provider_id():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,123456,,,,,,,,,,,,\n"
        "3,,,,,,,12345,,,,,,,,,,,,\n"
        "4,,,,,,,abcde,,,,,,,,,,,,\n"
        "5,,,,,,,5555555,,,,,,,,,,,,\n"
        "6,,,,,,,012345,,,,,,,,,,,,,\n"
        "7,,,,,,,,,,,,,,,,,,,\n"
        "8,,,,,,,000000,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 4, 5, 6, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "provider_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__technology():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,A,,,,,,,10,,,,,,,,,,,\n"
        "3,L,,,,,,,40,,,,,,,,,,,\n"
        "4,T,,,,,,,45,,,,,,,,,,,\n"
        "5,D,,,,,,,50,,,,,,,,,,,\n"
        "6,E,,,,,,,MV,,,,,,,,,,,,\n"
        "7,V,,,,,,,60,,,,,,,,,,,\n"
        "8,M,,,,,,,61,,,,,,,,,,,\n"
        "9,A,,,,,,,62,,,,,,,,,,,\n"
        "10,P,,,,,,,70,,,,,,,,,,,\n"
        "11,X,,,,,,,71,,,,,,,,,,,\n"
        "12,Y,,,,,,,72,,,,,,,,,,,\n"
        "13,Z,,,,,,,0,,,,,,,,,,,\n"
        "14,N,,,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [4, 6, 9]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "technology"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__location_id():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,1234567890,,,,,,,,,,\n"
        "3,,,,,,,,,0123456789,,,,,,,,,,\n"
        "4,,,,,,,,,123456789,,,,,,,,,,\n"
        "5,,,,,,,,,999999999,,,,,,,,,,\n"
        "6,,,,,,,,,1000000000,,,,,,,,,,\n"
        "7,,,,,,,,,9999999999,,,,,,,,,,\n"
        "8,,,,,,,,,10000000000,,,,,,,,,,\n"
        "9,,,,,,,,,letters_not_numbers,,,,,,,,,,\n"
        "10,,,,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 4, 5, 8, 9, 10]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__reason_code():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,A,,,,,,,,,,0,,,,,,,,\n"
        "3,A,,,,,,,,,,1,,,,,,,,\n"
        "4,A,,,,,,,,,,2,,,,,,,,\n"
        "5,A,,,,,,,,,,3,,,,,,,,\n"
        "6,A,,,,,,,,,,4,,,,,,,,\n"
        "7,A,,,,,,,,,,5,,,,,,,,\n"
        "8,A,,,,,,,,,,6,,,,,,,,\n"
        "9,A,,,,,,,,,,7,,,,,,,,\n"
        "10,A,,,,,,,,,,8,,,,,,,,\n"
        "11,A,,,,,,,,,,9,,,,,,,,\n"
        "12,A,,,,,,,,,,10,,,,,,,,\n"
        "13,S,,,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [2, 9, 12]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "reason_code"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__evidence_file_id():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,evidence_file,,,,,,,\n"
        "3,,,,,,,,,,,,evidence_file.pdf,,,,,,,\n"
        "4,,,,,,,,,,,,evidence_file.csv,,,,,,,\n"
        "5,,,,,,,,,,,,123dence_file.PdF,,,,,,,\n"
        "6,,,,,,,,,,,,evidence-file.pdf,,,,,,,\n"
        "7,,,,,,,,,,,,evidencefile!.pdf,,,,,,,\n"
        "8,,,,,,,,,,,,file@#4&stuff.pdf,,,,,,,\n"
        "9,,,,,,,,,,,,evidence(234).pdf,,,,,,,\n"
        "10,,,,,,,,,,,,.pdf,,,,,,,\n"
        "11,,,,,,,,,,,,a.pdf,,,,,,,\n"
        "12,,,,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [2, 4, 7, 8, 9, 10]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "evidence_file_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__response_file_id():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,evidence_file,,,,,,\n"
        "3,,,,,,,,,,,,,evidence_file.pdf,,,,,,\n"
        "4,,,,,,,,,,,,,evidence_file.csv,,,,,,\n"
        "5,,,,,,,,,,,,,123dence_file.PdF,,,,,,\n"
        "6,,,,,,,,,,,,,evidence-file.pdf,,,,,,\n"
        "7,,,,,,,,,,,,,evidencefile!.pdf,,,,,,\n"
        "8,,,,,,,,,,,,,file@#4&stuff.pdf,,,,,,\n"
        "9,,,,,,,,,,,,,evidence(234).pdf,,,,,,\n"
        "10,,,,,,,,,,,,,.pdf,,,,,,\n"
        "11,,,,,,,,,,,,,a.pdf,,,,,,\n"
        "12,,,,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [2, 4, 7, 8, 9, 10]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "response_file_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__advertised_download_speed():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,1,,,,\n"
        "3,,,,,,,,,,,,,,,-1,,,,\n"
        "4,,,,,,,,,,,,,,,0.5,,,,\n"
        "5,,,,,,,,,,,,,,,-0.5,,,,\n"
        "6,,,,,,,,,,,,,,,0,,,,\n"
        "7,,,,,,,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,,,,,,101 Mbps,,,,\n"
    )
    invalid_value_rows = [3, 5, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "advertised_download_speed"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__download_speed():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,,1,,,\n"
        "3,,,,,,,,,,,,,,,,-1,,,\n"
        "4,,,,,,,,,,,,,,,,0.5,,,\n"
        "5,,,,,,,,,,,,,,,,-0.5,,,\n"
        "6,,,,,,,,,,,,,,,,0,,,\n"
        "7,,,,,,,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,,,,,,,101 Mbps,,,\n"
    )
    invalid_value_rows = [3, 5, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "download_speed"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__advertised_upload_speed():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,,,1,,\n"
        "3,,,,,,,,,,,,,,,,,-1,,\n"
        "4,,,,,,,,,,,,,,,,,0.5,,\n"
        "5,,,,,,,,,,,,,,,,,-0.5,,\n"
        "6,,,,,,,,,,,,,,,,,0,,\n"
        "7,,,,,,,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,,,,,,,,21 Mbps,,\n"
    )
    invalid_value_rows = [3, 5, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "advertised_upload_speed"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__upload_speed():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,,,,1,\n"
        "3,,,,,,,,,,,,,,,,,,-1,\n"
        "4,,,,,,,,,,,,,,,,,,0.5,\n"
        "5,,,,,,,,,,,,,,,,,,-0.5,\n"
        "6,,,,,,,,,,,,,,,,,,0,\n"
        "7,,,,,,,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,,,,,,,,,21 Mbps,\n"
    )
    invalid_value_rows = [3, 5, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "upload_speed"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_col_content__latency():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,,,,,,,,,,,,,,,,1\n"
        "3,,,,,,,,,,,,,,,,,,,-1\n"
        "4,,,,,,,,,,,,,,,,,,,0.5\n"
        "5,,,,,,,,,,,,,,,,,,,-0.5\n"
        "6,,,,,,,,,,,,,,,,,,,\n"
        "7,,,,,,,,,,,,,,,,,,,21 ms\n"
    )
    invalid_value_rows = [3, 5, 7]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "latency"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_challenges_row_rule__challenger_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,A,,,,,,,,,,,,,,,,,,\n"
        "3,A,001,,,,,,,,,,,,,,,,,\n"
        "4,S,,,,,,,,,,,,,,,,,,\n"
        "5,S,002,,,,,,,,,,,,,,,,,\n"
        "6,L,003,,,,,,,,,,,,,,,,,\n"
        "7,L,,,,,,,,,,,,,,,,,,\n"
        "8,D,,,,,,,,,,,,,,,,,,\n"
        "9,D,004,,,,,,,,,,,,,,,,,\n"
        "10,T,005,,,,,,,,,,,,,,,,,\n"
        "11,T,,,,,,,,,,,,,,,,,,\n"
        "12,B,006,,,,,,,,,,,,,,,,,\n"
        "13,B,,,,,,,,,,,,,,,,,,\n"
        "14,P,,,,,,,,,,,,,,,,,,\n"
        "15,P,007,,,,,,,,,,,,,,,,,\n"
        "16,E,,,,,,,,,,,,,,,,,,\n"
        "17,N,,,,,,,,,,,,,,,,,,\n"
        "18,V,,,,,,,,,,,,,,,,,,\n"
        "19,F,,,,,,,,,,,,,,,,,,\n"
        "20,M,,,,,,,,,,,,,,,,,,\n"
        "21,X,,,,,,,,,,,,,,,,,,\n"
        "22,Y,,,,,,,,,,,,,,,,,,\n"
        "23,Z,,,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [2, 4, 7, 8, 11, 13, 14]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues
        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"]
            == "ChallengesChallengerIdGivenChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__reason_code_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,A,,,,,,,,,,2,,,,,,,,\n"
        "3,A,,,,,,,,,,3,,,,,,,,\n"
        "4,A,,,,,,,,,,4,,,,,,,,\n"
        "5,A,,,,,,,,,,5,,,,,,,,\n"
        "6,A,,,,,,,,,,6,,,,,,,,\n"
        "7,A,,,,,,,,,,7,,,,,,,,\n"
        "8,A,,,,,,,,,,8,,,,,,,,\n"
        "9,A,,,,,,,,,,9,,,,,,,,\n"
        "10,A,,,,,,,,,,1,,,,,,,,\n"
        "11,A,,,,,,,,,,10,,,,,,,,\n"
        "12,A,,,,,,,,,,,,,,,,,,\n"
        "13,B,,,,,,,,,,,,,,,,,,\n"
        "14,S,,,,,,,,,,,,,,,,,,\n"
        "15,P,,,,,,,,,,,,,,,,,,\n"
        "16,E,,,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [7, 11, 12]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesAvailabilityChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__resolution_given_challenge_type__disposition():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,E,,,,,,,,,,,,,,,,,,\n"
        "3,E,,,,,,,,,,,,,Enforceable challenge by X grant; no disp.,,,,,\n"
        "4,E,,,,,I,,,,,,,,Enforceable challenge by X grant; disp I.,,,,,\n"
        "5,E,,,,,N,,,,,,,,Enforceable challenge by X grant; disp N.,,,,,\n"
        "6,E,,,,,A,,,,,,,,Enforceable challenge by X grant; disp A.,,,,,\n"
        "7,E,,,,,S,,,,,,,,Enforceable challenge by X grant; disp S.,,,,,\n"
        "8,E,,,,,R,,,,,,,,Enforceable challenge by X grant; disp R.,,,,,\n"
        "9,E,,,,,M,,,,,,,,Enforceable challenge by X grant; disp M.,,,,,\n"
        "10,S,,,,,I,,,,,,,,Challenge incomplete for reasons.,,,,,\n"
        "11,S,,,,,I,,,,,,,,,,,,,\n"
        "12,B,,,,,N,,,,,,,,No rebuttal.,,,,,\n"
        "13,B,,,,,N,,,,,,,,,,,,,\n"
        "14,T,,,,,A,,,,,,,,ISP agrees with the challenge.,,,,,\n"
        "15,T,,,,,A,,,,,,,,,,,,,\n"
        "16,D,,,,,S,,,,,,,,Rebuttal only showed a 3 MB data cap plan.,,,,,\n"
        "17,D,,,,,S,,,,,,,,,,,,,\n"
        "18,M,,,,,R,,,,,,,,,,,,,\n"
        "19,M,,,,,R,,,,,,,,Rebuttal showed 300 Mbps symmetric tests.,,,,,\n"
        "20,E,,,,,N,,,,,,,,A,,,,,\n"  # Too short
        "21,E,,,,,N,,,,,,,,AB,,,,,\n"  # Too short
        "22,E,,,,,N,,,,,,,,ABC,,,,,\n"  # Min resolution length
        "23,Y,,,,,S,,,,,,,,D,,,,,\n"  # Too short
        "24,L,,,,,S,,,,,,,,DA,,,,,\n"  # Too short
        "25,L,,,,,S,,,,,,,,DAG,,,,,\n"  # Min resolution length
        "26,P,,,,,N,,,,,,,,So,,,,,\n"
        "27,F,,,,,I,,,,,,,,E,,,,,\n"  # Too short
        "28,F,,,,,I,,,,,,,,EG,,,,,\n"  # Too short
        "29,F,,,,,I,,,,,,,,EGG,,,,,\n"  # Min resolution length
        "30,L,,,,,R,,,,,,,,W,,,,,\n"  # Too short
        "31,A,,,,,R,,,,,,,,WI,,,,,\n"  # Too short
        "32,D,,,,,R,,,,,,,,WIG,,,,,\n"  # Min resolution length
    )
    rule_breaking_rows = [2, 11, 17, 18, 20, 21, 23, 24, 27, 28, 30, 31]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesResolutionGivenChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__rebuttal_date_and_file():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,2024-03-15,2024-04-12,,,,,,,,,12345_rebuttal_file.pdf,,,,,,\n"
        "3,,,2024-03-18,2024-04-22,,,,,,,,,,,,,,,\n"
        "4,,,2024-03-15,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues
        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesRebuttalDateAndFileRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__latency_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,S,,,,,,,,,,,,,,,,,,\n"
        "3,M,,,,,,,,,,,,,,,,,,101.9\n"
        "4,M,,,,,,,,,,,,,,,,,,\n"
        "5,L,,,,,,,,,,,,,,,,,,\n"
        "6,L,,,,,,,,,,,,,,,,,,23.1\n"
    )
    rule_breaking_rows = [4, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues
        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesLatencyChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__provider_id_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,P,,,,,,,,,,,,,,,,,,\n"
        "3,P,,,,,,128527,,,,,,,,,,,,\n"
        "4,A,,,,,,990910,,,,,,,,,,,,\n"
        "5,A,,,,,,,,,,,,,,,,,,\n"
        "6,S,,,,,,753191,,,,,,,,,,,,\n"
        "7,S,,,,,,,,,,,,,,,,,,\n"
        "8,L,,,,,,,,,,,,,,,,,,\n"
        "9,L,,,,,,137946,,,,,,,,,,,,\n"
        "10,T,,,,,,987654,,,,,,,,,,,,\n"
        "11,T,,,,,,,,,,,,,,,,,,\n"
        "12,B,,,,,,852963,,,,,,,,,,,,\n"
        "13,B,,,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [5, 7, 8, 11, 13]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues
        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesProviderIdChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__technology_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,N,,,,,,,,,,,,,,,,,,\n"
        "3,N,,,,,,,10,,,,,,,,,,,\n"
        "4,A,,,,,,,40,,,,,,,,,,,\n"
        "5,A,,,,,,,,,,,,,,,,,,\n"
        "6,S,,,,,,,50,,,,,,,,,,,\n"
        "7,S,,,,,,,,,,,,,,,,,,\n"
        "8,Y,,,,,,,60,,,,,,,,,,,\n"
        "9,Y,,,,,,,,,,,,,,,,,,\n"
        "10,T,,,,,,,61,,,,,,,,,,,\n"
        "11,T,,,,,,,,,,,,,,,,,,\n"
        "12,B,,,,,,,,,,,,,,,,,,\n"
        "13,B,,,,,,,70,,,,,,,,,,,\n"
        "14,E,,,,,,,71,,,,,,,,,,,\n"
        "15,E,,,,,,,,,,,,,,,,,,\n"
        "16,M,,,,,,,,,,,,,,,,,,\n"
        "17,M,,,,,,,72,,,,,,,,,,,\n"
        "18,D,,,,,,,,,,,,,,,,,,\n"
        "19,D,,,,,,,23,,,,,,,,,,,\n"
        "20,P,,,,,,,1,,,,,,,,,,,\n"
        "21,P,,,,,,,100,,,,,,,,,,,\n"
        "22,V,,,,,,,45,,,,,,,,,,,\n"
        "23,V,,,,,,,0,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [5, 7, 9, 11, 12, 15, 16, 18, 19, 20, 21, 22]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesTechnologyChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__evidence_file_id_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,P,,,,,,,,,,,evidence_file.pdf,,,,,,,\n"
        "3,P,,,,,,,,,,,,,,,,,,\n"
        "4,E,,,,,,,,,,,,,,,,,,\n"
        "5,E,,,,,,,,,,,evidence_file.pdf,,,,,,,\n"
        "6,S,,,,,,,,,,,my_evidence/file.pdf,,,,,,,\n"
        "7,S,,,,,,,,,,,,,,,,,,\n"
        "8,V,,,,,,,,,,,more_evidence/temp.pdf,,,,,,,\n"
        "9,V,,,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [3, 7]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues
        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesEvidenceFileChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__rebuttal_date_not_before_challenge_date():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,2024-03-18,,,,,,,,,,,,,,,,\n"
        "3,,,2024-03-18,2024-04-12,,,,,,,,,,,,,,,\n"
        "4,,,2024-03-18,2024-03-12,,,,,,,,,,,,,,,\n"
        "5,,,,2024-03-12,,,,,,,,,,,,,,,\n"
        "6,,,,2024-03-12,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [4, 5, 6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesChallengeAndRebuttalDateRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__resolution_date_not_before_challenge_date():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,2024-03-18,,,,,,,,,,,,,,,,\n"
        "3,,,2024-03-18,,2024-04-12,,,,,,,,,,,,,,\n"
        "4,,,2024-03-18,,2024-03-12,,,,,,,,,,,,,,\n"
        "5,,,,,2024-03-12,,,,,,,,,,,,,,\n"
        "6,,,,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [4, 5, 6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesChallengeAndResolutionDateRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__resolution_date_not_before_rebuttal_date():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,,,,2024-03-18,,,,,,,,,,,,,,,\n"
        "3,,,,2024-03-18,2024-04-12,,,,,,,,,,,,,,\n"
        "4,,,,2024-03-18,2024-03-12,,,,,,,,,,,,,,\n"
        "5,,,,,2024-03-12,,,,,,,,,,,,,,\n"
        "6,,,,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [4]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesRebuttalAndResolutionDateRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__advertised_download_speed_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,N,,,,,,,,,,,,,,100,,,,\n"
        "3,N,,,,,,,,,,,,,,,,,,\n"
        "4,A,,,,,,,,,,,,,,1,,,,\n"
        "5,A,,,,,,,,,,,,,,,,,,\n"
        "6,S,,,,,,,,,,,,,,,,,,\n"
        "7,S,,,,,,,,,,,,,,20,,,,\n"
        "8,L,,,,,,,,,,,,,,25,,,,\n"
        "9,L,,,,,,,,,,,,,,,,,,\n"
        "10,D,,,,,,,,,,,,,,10,,,,\n"
        "11,D,,,,,,,,,,,,,,,,,,\n"
        "12,T,,,,,,,,,,,,,,,,,,\n"
        "13,T,,,,,,,,,,,,,,50,,,,\n"
        "14,B,,,,,,,,,,,,,,75,,,,\n"
        "15,B,,,,,,,,,,,,,,,,,,\n"
        "16,P,,,,,,,,,,,,,,120,,,,\n"
        "17,P,,,,,,,,,,,,,,,,,,\n"
        "18,E,,,,,,,,,,,,,,80,,,,\n"
        "19,E,,,,,,,,,,,,,,,,,,\n"
        "20,V,,,,,,,,,,,,,,,,,,\n"
        "21,V,,,,,,,,,,,,,,5,,,,\n"
        "22,F,,,,,,,,,,,,,,12,,,,\n"
        "23,F,,,,,,,,,,,,,,,,,,\n"
        "24,M,,,,,,,,,,,,,,60,,,,\n"
        "25,M,,,,,,,,,,,,,,,,,,\n"
        "26,X,,,,,,,,,,,,,,20,,,,\n"
        "27,X,,,,,,,,,,,,,,,,,,\n"
        "28,Y,,,,,,,,,,,,,,,,,,\n"
        "29,Y,,,,,,,,,,,,,,200,,,,\n"
        "30,Z,,,,,,,,,,,,,,13,,,,\n"
        "31,Z,,,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [5, 6, 9, 11, 12, 15, 17, 19, 20, 23, 25, 27, 28, 31]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"]
            == "ChallengesAdvertisedDownloadSpeedChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__download_speed_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,M,,,,,,,,,,,,,,,123.45,,,\n"
        "3,M,,,,,,,,,,,,,,,,,,\n"
        "4,S,,,,,,,,,,,,,,,84.15,,,\n"
        "5,S,,,,,,,,,,,,,,,,,,\n"
        "6,A,,,,,,,,,,,,,,,,,,\n"
        "7,N,,,,,,,,,,,,,,,,,,\n"
        "8,L,,,,,,,,,,,,,,,,,,\n"
        "9,D,,,,,,,,,,,,,,,,,,\n"
        "10,T,,,,,,,,,,,,,,,,,,\n"
        "11,B,,,,,,,,,,,,,,,,,,\n"
        "12,P,,,,,,,,,,,,,,,,,,\n"
        "13,E,,,,,,,,,,,,,,,,,,\n"
        "14,V,,,,,,,,,,,,,,,,,,\n"
        "15,F,,,,,,,,,,,,,,,,,,\n"
        "16,X,,,,,,,,,,,,,,,,,,\n"
        "17,Y,,,,,,,,,,,,,,,,,,\n"
        "18,Z,,,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [3, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesDownloadSpeedChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__advertised_upload_speed_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,N,,,,,,,,,,,,,,,,100,,\n"
        "3,N,,,,,,,,,,,,,,,,,,\n"
        "4,A,,,,,,,,,,,,,,,,1,,\n"
        "5,A,,,,,,,,,,,,,,,,,,\n"
        "6,S,,,,,,,,,,,,,,,,,,\n"
        "7,S,,,,,,,,,,,,,,,,20,,\n"
        "8,L,,,,,,,,,,,,,,,,25,,\n"
        "9,L,,,,,,,,,,,,,,,,,,\n"
        "10,D,,,,,,,,,,,,,,,,10,,\n"
        "11,D,,,,,,,,,,,,,,,,,,\n"
        "12,T,,,,,,,,,,,,,,,,,,\n"
        "13,T,,,,,,,,,,,,,,,,50,,\n"
        "14,B,,,,,,,,,,,,,,,,75,,\n"
        "15,B,,,,,,,,,,,,,,,,,,\n"
        "16,P,,,,,,,,,,,,,,,,120,,\n"
        "17,P,,,,,,,,,,,,,,,,,,\n"
        "18,E,,,,,,,,,,,,,,,,80,,\n"
        "19,E,,,,,,,,,,,,,,,,,,\n"
        "20,V,,,,,,,,,,,,,,,,,,\n"
        "21,V,,,,,,,,,,,,,,,,5,,\n"
        "22,F,,,,,,,,,,,,,,,,12,,\n"
        "23,F,,,,,,,,,,,,,,,,,,\n"
        "24,M,,,,,,,,,,,,,,,,60,,\n"
        "25,M,,,,,,,,,,,,,,,,,,\n"
        "26,X,,,,,,,,,,,,,,,,20,,\n"
        "27,X,,,,,,,,,,,,,,,,,,\n"
        "28,Y,,,,,,,,,,,,,,,,,,\n"
        "29,Y,,,,,,,,,,,,,,,,200,,\n"
        "30,Z,,,,,,,,,,,,,,,,13,,\n"
        "31,Z,,,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [5, 6, 9, 11, 12, 15, 17, 19, 20, 23, 25, 27, 28, 31]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"]
            == "ChallengesAdvertisedUploadSpeedChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_row_rule__upload_speed_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        "2,M,,,,,,,,,,,,,,,,,123.45,\n"
        "3,M,,,,,,,,,,,,,,,,,,\n"
        "4,S,,,,,,,,,,,,,,,,,84.15,\n"
        "5,S,,,,,,,,,,,,,,,,,,\n"
        "6,A,,,,,,,,,,,,,,,,,,\n"
        "7,N,,,,,,,,,,,,,,,,,,\n"
        "8,L,,,,,,,,,,,,,,,,,,\n"
        "9,D,,,,,,,,,,,,,,,,,,\n"
        "10,T,,,,,,,,,,,,,,,,,,\n"
        "11,B,,,,,,,,,,,,,,,,,,\n"
        "12,P,,,,,,,,,,,,,,,,,,\n"
        "13,E,,,,,,,,,,,,,,,,,,\n"
        "14,V,,,,,,,,,,,,,,,,,,\n"
        "15,F,,,,,,,,,,,,,,,,,,\n"
        "16,X,,,,,,,,,,,,,,,,,,\n"
        "17,Y,,,,,,,,,,,,,,,,,,\n"
        "18,Z,,,,,,,,,,,,,,,,,,\n"
    )
    rule_breaking_rows = [3, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "ChallengesUploadSpeedChallengeTypeRuleValidator"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in rule_breaking_rows)
        assert failing_rows == rule_breaking_rows
        assert all(r in rule_breaking_rows for r in failing_rows)


def test_challenges_column_not_null_validations():
    csv_content = (
        "challenge,challenge_type,challenger,challenge_date,rebuttal_date,"
        "resolution_date,disposition,provider_id,technology,location_id,unit,"
        "reason_code,evidence_file_id,response_file_id,resolution,"
        "advertised_download_speed,download_speed,advertised_upload_speed,"
        "upload_speed,latency\n"
        ",2,,,,,,,,,,,,,,,,,,\n"
        "3,P,,,,,,,,,,,,,,,,,,\n"
        "4,,,2024-03-18,,,,,,,,,,,,,,,,\n"
        "5,,,,,2024-05-02,,,,,,,,,,,,,,\n"
        "6,,,,,,S,,,,,,,,,,,,,\n"
        "7,,,,,,,,,1234567890,,,,,,,,,,\n"
    )
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues
        col_nullness_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "required_column_not_null_validation"
        ]
        null_rows_by_column = {
            id["column"]: id["rows_where_column_is_null"] for id in col_nullness_issues
        }
        assert [r[0] for r in null_rows_by_column["challenge"]] == [
            2
        ], "A row with a null 'challenge' col value wasn't caught"
        assert [r[0] for r in null_rows_by_column["challenge_type"]] == [
            4,
            5,
            6,
            7,
        ], "A row with a null 'challenge_type' col value wasn't caught"
        assert [r[0] for r in null_rows_by_column["challenge_date"]] == [
            2,
            3,
            5,
            6,
            7,
        ], "A row with a null 'challenge_date' col value wasn't caught"
        assert [r[0] for r in null_rows_by_column["resolution_date"]] == [
            2,
            3,
            4,
            6,
            7,
        ], "A row with a null 'resolution_date' col value wasn't caught"
        assert [r[0] for r in null_rows_by_column["disposition"]] == [
            2,
            3,
            4,
            5,
            7,
        ], "A row with a null 'disposition' col value wasn't caught"
        assert [r[0] for r in null_rows_by_column["location_id"]] == [
            2,
            3,
            4,
            5,
            6,
        ], "A row with a null 'location_id' col value wasn't caught"


#########################################################
# ####################### CAIs ######################## #
#########################################################


def test_cai__column_names():
    csv_content = (
        "type,entity_name,latency,entity_number,CMS number,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,provider_id,"
        "need,availability\n"
    )
    missing_column_names = ["frn", "explanation"]
    extra_column_names = ["latency", "provider_id"]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_name_validation"
        ]
        assert len(test_issues) == 1
        assert list(test_issues[0].keys()) == [
            "columns_missing_from_file",
            "extra_columns_in_file",
        ]
        assert set(test_issues[0]["columns_missing_from_file"]) == set(
            missing_column_names
        )
        assert set(test_issues[0]["extra_columns_in_file"]) == set(extra_column_names)


def test_cai__column_order():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "evidence_file_id,city,state,zip_code,latitude,longitude,explanation,"
        "need,availability\n"
    )
    col_numbers_w_wrong_names = [7, 11, 12]
    expected_cols_not_in_expected_place = [
        "latitude",
        "longitude",
        "address_primary",
    ]
    file_col_names_in_wrong_place = [
        "latitude",
        "longitude",
        "evidence_file_id",
    ]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_order_validation"
        ]
        assert len(test_issues) == 1
        cols_out_of_order = test_issues[0]["cols_out_of_order"]
        assert all(
            list(el.keys())
            == ["column_number", "expected_column_name", "column_name_in_file"]
            for el in cols_out_of_order
        )
        missing_expected_cols_w_missings = [
            el["expected_column_name"] for el in cols_out_of_order
        ]
        misordered_expected_col_names = [
            c for c in missing_expected_cols_w_missings if c != "<missing_column>"
        ]
        misordered_col_names_in_file_w_missings = [
            el["column_name_in_file"] for el in cols_out_of_order
        ]
        misordered_col_names_in_file = [
            c
            for c in misordered_col_names_in_file_w_missings
            if c != "<missing_column>"
        ]
        assert set(misordered_expected_col_names) == set(
            expected_cols_not_in_expected_place
        )
        assert set(misordered_col_names_in_file) == set(file_col_names_in_wrong_place)
        assert set(el["column_name_in_file"] for el in cols_out_of_order) == set(
            file_col_names_in_wrong_place
        )
        assert [
            el["column_number"] for el in cols_out_of_order
        ] == col_numbers_w_wrong_names


def test_cai_column_dtypes__entity_number():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,1,,,,,,,,,,,,\n"
        "3,,1.0,,,,,,,,,,,,\n"
        "4,,0xFF,,,,,,,,,,,,\n"
        "5,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 4]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "entity_number"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_column_dtypes__location_id():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,1234567890,,,,,,,,,\n"
        "3,,,,,0x00000000,,,,,,,,,\n"
        "4,,,,,12345.6789,,,,,,,,,\n"
        "5,,,,,abcdefghij,,,,,,,,,\n"
        "6,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 4, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_column_dtypes__need():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,,,41.876356,\n"
        "3,,,,,,,,,,,,,41876356,\n"
        "4,,,,,,,,,,,,,-41,\n"
        "5,,,,,,,,,,,,,41-876356,\n"
        "6,,,,,,,,,,,,,,\n"
        "7,,,,,,,,,,,,,0xABcD,\n"
    )
    invalid_value_rows = [2, 5, 6, 7]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "need"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_column_dtypes__availability():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,,,,41.876356\n"
        "3,,,,,,,,,,,,,,41876356\n"
        "4,,,,,,,,,,,,,,-41\n"
        "5,,,,,,,,,,,,,,41-876356\n"
        "6,,,,,,,,,,,,,,\n"
        "7,,,,,,,,,,,,,,0xABcD\n"
    )
    invalid_value_rows = [2, 5, 7]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "availability"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__type():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "S,2,,,,,,,,,,,,,\n"
        "A,3,,,,,,,,,,,,,\n"
        "L,4,,,,,,,,,,,,,\n"
        "B,5,,,,,,,,,,,,,\n"
        "E,6,,,,,,,,,,,,,\n"
        "G,7,,,,,,,,,,,,,\n"
        "H,8,,,,,,,,,,,,,\n"
        "T,9,,,,,,,,,,,,,\n"
        "F,10,,,,,,,,,,,,,\n"
        "P,11,,,,,,,,,,,,,\n"
        "Q,12,,,,,,,,,,,,,\n"
        "C,13,,,,,,,,,,,,,\n"
        ",14,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 5, 6, 9, 12, 14]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "type"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__entity_name():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,,,,\n"
        "3,Name of this CAI,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [2]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "entity_name"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__cms_number():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,123456,,,,,,,,,,,\n"
        "3,,,,,,,,,,,,,,\n"
        "4,,,12345678,,,,,,,,,,,\n"
        "5,,,1234567890,,,,,,,,,,,\n"
        "6,,,123456789012,,,,,,,,,,,\n"
        "7,,,123ABC,,,,,,,,,,,\n"
        "8,,,123ABCdef0,,,,,,,,,,,\n"
        "9,,,1a,,,,,,,,,,,\n"
    )
    invalid_value_rows = [4, 6, 9]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "cms_number"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__frn():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,0015433808,,,,,,,,,,\n"
        "3,,,,,,,,,,,,,,\n"
        "4,,,,1234567890,,,,,,,,,,\n"
        "5,,,,0000000000,,,,,,,,,,\n"
        "6,,,,9999999999,,,,,,,,,,\n"
        "7,,,,10000000000,,,,,,,,,,\n"
        "8,,,,999999999,,,,,,,,,,\n"
        "9,,,,ABCDEfghij,,,,,,,,,,\n"
        "10,,,,Ab,,,,,,,,,,\n"
        "11,,,,Ab123,,,,,,,,,,\n"
    )
    invalid_value_rows = [7, 8, 9, 10, 11]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "frn"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__location_id():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,1234567890,,,,,,,,,\n"
        "3,,,,,,,,,,,,,,\n"
        "4,,,,,A234567890,,,,,,,,,\n"
        "5,,,,,999999999,,,,,,,,,\n"
        "6,,,,,1000000000,,,,,,,,,\n"
        "7,,,,,9999999999,,,,,,,,,\n"
        "8,,,,,10000000000,,,,,,,,,\n"
        "9,,,,,0100000000,,,,,,,,,\n"
    )
    invalid_value_rows = [4, 5, 8, 9]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__state():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,AL,,,,,,\n"
        "3,,,,,,,,alabama,,,,,,\n"
        "4,,,,,,,,,,,,,,\n"
        "5,,,,,,,,VI,,,,,,\n"
        "6,,,,,,,,PR,,,,,,\n"
        "7,,,,,,,,GU,,,,,,\n"
        "8,,,,,,,,DC,,,,,,\n"
        "9,,,,,,,,dc,,,,,,\n"
        "10,,,,,,,,AS,,,,,,\n"
    )
    invalid_value_rows = [3, 4, 9]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "state"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__zip_code():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,12345,,,,,\n"
        "3,,,,,,,,,,,,,,\n"
        "4,,,,,,,,,60606-5432,,,,,\n"
        "5,,,,,,,,,606VI,,,,,\n"
        "6,,,,,,,,,606,,,,,\n"
        "7,,,,,,,,,312773,,,,,\n"
        "8,,,,,,,,,06060,,,,,\n"
        "9,,,,,,,,,00000,,,,,\n"
    )
    invalid_value_rows = [4, 5, 6, 7]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "zip_code"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__longitude():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,-89.999999,,,,\n"
        "3,,,,,,,,,,-90.000001,,,,\n"
        "4,,,,,,,,,,89.999999,,,,\n"
        "5,,,,,,,,,,90.000001,,,,\n"
        "6,,,,,,,,,,0,,,,\n"
        "7,,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,-87.7176,,,,\n"
        "9,,,,,,,,,,-179.999999,,,,\n"
        "10,,,,,,,,,,-180.000001,,,,\n"
        "11,,,,,,,,,,179.999999,,,,\n"
        "12,,,,,,,,,,180.000001,,,,\n"
        "13,,,,,,,,,,at point 0.000000,,,,\n"
        "14,,,,,,,,,,180.000000,,,,\n"
        "15,,,,,,,,,,-180.000000,,,,\n"
    )
    invalid_value_rows = [6, 8, 10, 12, 13]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "longitude"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__latitude():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,-89.999999,,,\n"
        "3,,,,,,,,,,,-90.000001,,,\n"
        "4,,,,,,,,,,,89.999999,,,\n"
        "5,,,,,,,,,,,90.000001,,,\n"
        "6,,,,,,,,,,,0,,,\n"
        "7,,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,,41.8863,,,\n"
        "9,,,,,,,,,,,179.95,,,\n"
        "10,,,,,,,,,,,-179.95,,,\n"
        "11,,,,,,,,,,,90.000000,,,\n"
        "12,,,,,,,,,,,-90.000000,,,\n"
        "13,,,,,,,,,,,42.000000123,,,\n"
        "14,,,,,,,,,,,-42.000000123,,,\n"
        "15,,,,,,,,,,,42.00000,,,\n"
        "16,,,,,,,,,,,near 42.00000,,,\n"
    )
    invalid_value_rows = [3, 5, 6, 8, 9, 10, 15, 16]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "latitude"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__need():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,,,1000,\n"
        "3,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "need"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_col_content__availability():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,,,,1\n"
        "3,,,,,,,,,,,,,,0\n"
        "4,,,,,,,,,,,,,,-1\n"
    )
    invalid_value_rows = [4]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "availability"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_row_rule__location_possibly_determinable():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,1234567890,,,,,,,,,\n"
        "3,,,,,,123 Fake St,,,,,,,,\n"
        "4,,,,,,123 Fake St,Realtown,,,,,,,\n"
        "5,,,,,,123 Fake St,Realtown,,12345,,,,,\n"
        "6,,,,,1234567890,123 Fake St,Realtown,,12345,,,,,\n"
        "7,,,,,1234567890,123 Fake St,,,12345,,,,,\n"
        "8,,,,,,123 Fake St,,,12345,,,,,\n"
        "9,,,,,,,,,,-87.717600,41.886300,,,\n"
        "10,,,,,,,,,,-87.717600,,,,\n"
        "11,,,,,,,,,,,41.886300,,,\n"
        "12,,,,,9874563210,,,,,-87.717600,,,,\n"
        "13,,,,,,5432 Post Gres,,,,,41.886300,,,\n"
    )
    no_location_combo_rows = [3, 4, 8, 10, 11, 13]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "PostChallengeCaiLocationValidation"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


def test_cai_row_rule__cms_number_given_cai_type():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "H,2,,555444,,,,,,,,,,,\n"
        "H,3,,,,,,,,,,,,,\n"
        "H,4,,a,,,,,,,,,,,\n"
        "S,5,,789321,,,,,,,,,,,\n"
        "S,6,,,,,,,,,,,,,\n"
        "L,7,,3138675309,,,,,,,,,,,\n"
        "L,8,,,,,,,,,,,,,\n"
        "G,9,,,,,,,,,,,,,\n"
        "G,10,,987sdf5545,,,,,,,,,,,\n"
        "F,11,,876000,,,,,,,,,,,\n"
        "F,12,,,,,,,,,,,,,\n"
        "P,13,,,,,,,,,,,,,\n"
        "P,14,,555606,,,,,,,,,,,\n"
        "C,15,,,,,,,,,,,,,\n"
        "C,16,,909606,,,,,,,,,,,\n"
    )
    no_location_combo_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "PostChallengeCaiCMSValidatorGivenCAIType"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in no_location_combo_rows)
        assert failing_rows == no_location_combo_rows
        assert all(r in no_location_combo_rows for r in failing_rows)


def test_cai_row_rule__frn_given_cai_type():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "H,2,,,5554440000,,,,,,,,,,\n"
        "H,3,,,,,,,,,,,,,\n"
        "H,4,,,A119113110,,,,,,,,,,\n"
        "S,5,,,8855220011,,,,,,,,,,\n"
        "S,6,,,,,,,,,,,,,\n"
        "L,7,,,3138675309,,,,,,,,,,\n"
        "L,8,,,,,,,,,,,,,\n"
        "G,9,,,,,,,,,,,,,\n"
        "G,10,,,987sdf5545,,,,,,,,,,\n"
        "F,11,,,8760005505,,,,,,,,,,\n"
        "F,12,,,,,,,,,,,,,\n"
        "P,13,,,,,,,,,,,,,\n"
        "P,14,,,5556061141,,,,,,,,,,\n"
        "C,15,,,,,,,,,,,,,\n"
        "C,16,,,909606abcD,,,,,,,,,,\n"
    )
    no_location_combo_rows = [3, 4, 6, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "PostChallengeCaiFRNValidationGivenCAIType"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


def test_cai_row_rule__explanation_given_cai_type():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "C,2,,,,,,,,,,,Our org teaches digital literacy skills.,,\n"
        "C,3,,,,,,,,,,,,,\n"
        "S,4,,,,,,,,,,,,,\n"
        "L,5,,,,,,,,,,,,,\n"
        "G,6,,,,,,,,,,,,,\n"
        "H,7,,,,,,,,,,,,,\n"
        "F,8,,,,,,,,,,,,,\n"
        "P,9,,,,,,,,,,,,,\n"
    )
    no_location_combo_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "PostChallengeCaiExplanationValidationGivenCAIType"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


########################################################
# ################## CAI Challenges ################## #
########################################################


def test_cai_challenges__column_names():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,"
        "challenge_explanation,entity_name,entity_number,frn,school_id,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
    )
    missing_column_names = ["type", "disposition", "cms_number"]
    extra_column_names = ["school_id"]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_name_validation"
        ]
        assert len(test_issues) == 1
        assert list(test_issues[0].keys()) == [
            "columns_missing_from_file",
            "extra_columns_in_file",
        ]
        assert set(test_issues[0]["columns_missing_from_file"]) == set(
            missing_column_names
        )
        assert set(test_issues[0]["extra_columns_in_file"]) == set(extra_column_names)


def test_cai_challenges__column_order():
    csv_content = (
        "challenge,challenger,category_code,challenge_type,disposition,"
        "explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "challenge_explanation,need,availability\n"
    )
    file_col_names_in_wrong_place = [
        "challenger",
        "category_code",
        "challenge_type",
        "explanation",
        "challenge_explanation",
    ]
    expected_cols_not_in_expected_place = [
        "challenge_type",
        "challenger",
        "category_code",
        "explanation",
        "challenge_explanation",
    ]
    col_numbers_w_wrong_names = [2, 3, 4, 6, 19]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_order_validation"
        ]

        assert len(test_issues) == 1
        cols_out_of_order = test_issues[0]["cols_out_of_order"]
        assert all(
            list(el.keys())
            == ["column_number", "expected_column_name", "column_name_in_file"]
            for el in cols_out_of_order
        )
        missing_expected_cols_w_missings = [
            el["expected_column_name"] for el in cols_out_of_order
        ]
        misordered_expected_col_names = [
            c for c in missing_expected_cols_w_missings if c != "<missing_column>"
        ]
        misordered_col_names_in_file_w_missings = [
            el["column_name_in_file"] for el in cols_out_of_order
        ]
        misordered_col_names_in_file = [
            c
            for c in misordered_col_names_in_file_w_missings
            if c != "<missing_column>"
        ]
        assert set(misordered_expected_col_names) == set(
            expected_cols_not_in_expected_place
        )
        assert set(misordered_col_names_in_file) == set(file_col_names_in_wrong_place)
        assert set(el["column_name_in_file"] for el in cols_out_of_order) == set(
            file_col_names_in_wrong_place
        )
        assert [
            el["column_number"] for el in cols_out_of_order
        ] == col_numbers_w_wrong_names


def test_cai_challenges_column_dtypes__entity_number():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,,,,,,,,1,,,,,,,,,,,,\n"
        "3,,,,,,,,1.0,,,,,,,,,,,,\n"
        "4,,,,,,,,1.1,,,,,,,,,,,,\n"
        "5,,,,,,,,-1,,,,,,,,,,,,\n"
        "6,,,,,,,,0xAB,,,,,,,,,,,,\n"
        "7,,,,,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 4, 6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "entity_number"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_challenges_column_dtypes__location_id():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,,,,,,,,,,,1234567890,,,,,,,,,\n"
        "3,,,,,,,,,,,-123456789,,,,,,,,,\n"
        "4,,,,,,,,,,,12345-6789,,,,,,,,,\n"
        "5,,,,,,,,,,,,,,,,,,,,\n"
        "6,,,,,,,,,,,0xAbCdEf,,,,,,,,,\n"
        "7,,,,,,,,,,,12345.6789,,,,,,,,,\n"
    )
    invalid_value_rows = [4, 6, 7]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_challenges_column_dtypes__need():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,,,,,,,,,,,,,,,,,,,1,\n"
        "3,,,,,,,,,,,,,,,,,,,1.0,\n"
        "4,,,,,,,,,,,,,,,,,,,1.01,\n"
        "5,,,,,,,,,,,,,,,,,,,,\n"
        "6,,,,,,,,,,,,,,,,,,,0x00,\n"
        "7,,,,,,,,,,,,,,,,,,,a,\n"
        "8,,,,,,,,,,,,,,,,,,,-1,\n"
        "9,,,,,,,,,,,,,,,,,,,-1.0,\n"
    )
    invalid_value_rows = [3, 4, 5, 6, 7, 9]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "need"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_challenges_column_dtypes__availability():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,,,,,,,,,,,,,,,,,,,,1\n"
        "3,,,,,,,,,,,,,,,,,,,,1.0\n"
        "4,,,,,,,,,,,,,,,,,,,,1.01\n"
        "5,,,,,,,,,,,,,,,,,,,,\n"
        "6,,,,,,,,,,,,,,,,,,,,0x00\n"
        "7,,,,,,,,,,,,,,,,,,,,a\n"
        "8,,,,,,,,,,,,,,,,,,,,-1\n"
        "9,,,,,,,,,,,,,,,,,,,,-1.0\n"
    )
    invalid_value_rows = [3, 4, 6, 7, 9]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "availability"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_challenges_col_content__challenge():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "eoEYUCTZHR-corE3xwTq5S-LowMQ7QVt8-f7XpDG9dZgm8z3nK,2,,,,,,,,,,,,,,,,,,,\n"
        "Xnow432nXcjgodiDY8F-YipaGRhV24iYQRBPeW6LzoN6piXHFgW,3,,,,,,,,,,,,,,,,,,,\n"
        "a_iDY8F-Yi_V123456789XHFg,4,,,,,,,,,,,,,,,,,,,\n"
        "ABCDEFGHIJKLMNOPQRSTUVWXYabcdefghijklmnopqrstuvwxy,5,,,,,,,,,,,,,,,,,,,\n"
        "a1,6,,,,,,,,,,,,,,,,,,,\n"
        "abcde-12345,7,,,,,,,,,,,,,,,,,,,\n"
        "abcde-12345!,8,,,,,,,,,,,,,,,,,,,\n"
        ",9,,,,,,,,,,,,,,,,,,,\n"
    )
    over_length_rows = [3]
    invalid_char_rows = [4, 8]
    null_char_rows = [9]
    invalid_value_rows = [*over_length_rows, *invalid_char_rows, *null_char_rows]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.ChallengesDataValidator(tf.name)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "challenge"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in over_length_rows)
        assert all(r in failing_rows for r in invalid_char_rows)
        assert all(r in failing_rows for r in null_char_rows)
        assert set(failing_rows) == set(invalid_value_rows)


def test_cai_challenges_col_content__challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,A,,,,,,,,,,,,,,,,,,,\n"
        "3,S,,,,,,,,,,,,,,,,,,,\n"
        "4,L,,,,,,,,,,,,,,,,,,,\n"
        "5,D,,,,,,,,,,,,,,,,,,,\n"
        "6,T,,,,,,,,,,,,,,,,,,,\n"
        "7,B,,,,,,,,,,,,,,,,,,,\n"
        "8,P,,,,,,,,,,,,,,,,,,,\n"
        "9,E,,,,,,,,,,,,,,,,,,,\n"
        "10,N,,,,,,,,,,,,,,,,,,,\n"
        "11,1,,,,,,,,,,,,,,,,,,,\n"
        "12,R,,,,,,,,,,,,,,,,,,,\n"
        "13,G,,,,,,,,,,,,,,,,,,,\n"
        "14,Q,,,,,,,,,,,,,,,,,,,\n"
        "15,V,,,,,,,,,,,,,,,,,,,\n"
        "16,F,,,,,,,,,,,,,,,,,,,\n"
        "17,M,,,,,,,,,,,,,,,,,,,\n"
        "18,X,,,,,,,,,,,,,,,,,,,\n"
        "19,Y,,,,,,,,,,,,,,,,,,,\n"
        "20,Z,,,,,,,,,,,,,,,,,,,\n"
        "21,H,,,,,,,,,,,,,,,,,,,\n"
        "22,I,,,,,,,,,,,,,,,,,,,\n"
        "23,J,,,,,,,,,,,,,,,,,,,\n"
        "24,K,,,,,,,,,,,,,,,,,,,\n"
        "25,C,,,,,,,,,,,,,,,,,,,\n"
        "26,O,,,,,,,,,,,,,,,,,,,\n"
        "27,U,,,,,,,,,,,,,,,,,,,\n"
        "28,W,,,,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        26,
        27,
        28,
    ]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "challenge_type"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_challenges_col_content__longitude():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,,,,,,,,,,,,,,,,-89.999999,,,,\n"
        "3,,,,,,,,,,,,,,,,-90.000001,,,,\n"
        "4,,,,,,,,,,,,,,,,89.999999,,,,\n"
        "5,,,,,,,,,,,,,,,,90.000001,,,,\n"
        "6,,,,,,,,,,,,,,,,0,,,,\n"
        "7,,,,,,,,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,,,,,,,-179.999999,,,,\n"
        "9,,,,,,,,,,,,,,,,179.999999,,,,\n"
        "10,,,,,,,,,,,,,,,,180.000000,,,,\n"
        "11,,,,,,,,,,,,,,,,180.000001,,,,\n"
        "12,,,,,,,,,,,,,,,,-180.000001,,,,\n"
        "13,,,,,,,,,,,,,,,,-180.000000,,,,\n"
        "14,,,,,,,,,,,,,,,,A.000000,,,,\n"
        "15,,,,,,,,,,,,,,,,B,,,,\n"
        "16,,,,,,,,,,,,,,,,123-456,,,,\n"
        "17,,,,,,,,,,,,,,,,180.00000,,,,\n"
        "18,,,,,,,,,,,,,,,,-180.00000,,,,\n"
        "19,,,,,,,,,,,,,,,,179.000001234,,,,\n"
        "20,,,,,,,,,,,,,,,,-179.000001234,,,,\n"
    )
    invalid_value_rows = [6, 11, 12, 14, 15, 16, 17, 18]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "longitude"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_challenges_col_content__latitude():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,,,,,,,,,,,,,,,,,-89.999999,,,\n"
        "3,,,,,,,,,,,,,,,,,-90.000001,,,\n"
        "4,,,,,,,,,,,,,,,,,89.999999,,,\n"
        "5,,,,,,,,,,,,,,,,,90.000001,,,\n"
        "6,,,,,,,,,,,,,,,,,0,,,\n"
        "7,,,,,,,,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,,,,,,,,-179.999999,,,\n"
        "9,,,,,,,,,,,,,,,,,179.999999,,,\n"
        "10,,,,,,,,,,,,,,,,,180.000000,,,\n"
        "11,,,,,,,,,,,,,,,,,180.000001,,,\n"
        "12,,,,,,,,,,,,,,,,,-180.000001,,,\n"
        "13,,,,,,,,,,,,,,,,,-180.000000,,,\n"
        "14,,,,,,,,,,,,,,,,,A.000000,,,\n"
        "15,,,,,,,,,,,,,,,,,B,,,\n"
        "16,,,,,,,,,,,,,,,,,123-456,,,\n"
        "17,,,,,,,,,,,,,,,,,90.000000,,,\n"
        "18,,,,,,,,,,,,,,,,,90.00000,,,\n"
        "19,,,,,,,,,,,,,,,,,-90.00000,,,\n"
        "20,,,,,,,,,,,,,,,,,-90.000000,,,\n"
        "21,,,,,,,,,,,,,,,,,-89.0000001234,,,\n"
        "22,,,,,,,,,,,,,,,,,89.0000001234,,,\n"
    )
    invalid_value_rows = [3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "latitude"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_challenges_row_rule__category_code_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,C,,X,,,,,,,,,,,,,,,,,\n"
        "3,C,,B,,,,,,,,,,,,,,,,,\n"
        "4,C,,R,,,,,,,,,,,,,,,,,\n"
        "5,C,,D,,,,,,,,,,,,,,,,,\n"
        "6,C,,N,,,,,,,,,,,,,,,,,\n"
        "7,C,,I,,,,,,,,,,,,,,,,,\n"
        "8,C,,T,,,,,,,,,,,,,,,,,\n"
        "9,C,,O,,,,,,,,,,,,,,,,,\n"
        "10,G,,,,,,,,,,,,,,,,,,,\n"
        "11,G,,X,,,,,,,,,,,,,,,,,\n"
        "12,Q,,,,,,,,,,,,,,,,,,,\n"
        "13,Q,,I,,,,,,,,,,,,,,,,,\n"
        "14,R,,X,,,,,,,,,,,,,,,,,\n"
        "15,R,,B,,,,,,,,,,,,,,,,,\n"
        "16,R,,R,,,,,,,,,,,,,,,,,\n"
        "17,R,,D,,,,,,,,,,,,,,,,,\n"
        "18,R,,N,,,,,,,,,,,,,,,,,\n"
        "19,R,,I,,,,,,,,,,,,,,,,,\n"
        "20,R,,T,,,,,,,,,,,,,,,,,\n"
        "21,R,,O,,,,,,,,,,,,,,,,,\n"
        "22,R,,1,,,,,,,,,,,,,,,,,\n"
        "23,C,,1,,,,,,,,,,,,,,,,,\n"
        "24,R,,,,,,,,,,,,,,,,,,,\n"
        "25,C,,,,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [2, 3, 4, 10, 18, 19, 20, 22, 23, 24, 25]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "CaiChallengeCategoryCodeConditionalGivenType"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_challenges_row_rule__explanation_given_challenge_type():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,C,,,,,,,,,,,,,,,,,Some Reason.,,\n"
        "3,C,,,,,,,,,,,,,,,,,,,\n"
        """4,R,,,,,,,,,,,,,,,,,"I promise, it's no CAI.",,\n"""
        "5,R,,,,,,,,,,,,,,,,,,,\n"
        "6,G,,,,,,,,,,,,,,,,,The CAI has no fiber options.,,\n"
        "7,G,,,,,,,,,,,,,,,,,,,\n"
        """8,Q,,,,,,,,,,,,,,,,,"Around the CAI, there's fiber.",,\n"""
        "9,Q,,,,,,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "CaiChallengeExplanationConditionalTypeC"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_cai_challenge_row_rule__location_possibly_determinable():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,,,,,,,,,,,1234567890,,,,,,,,,\n"
        "3,,,,,,,,,,,,123 Fake St,,,,,,,,\n"
        "4,,,,,,,,,,,,123 Fake St,Realtown,,,,,,,\n"
        "5,,,,,,,,,,,,123 Fake St,Realtown,,60606,,,,,\n"
        "6,,,,,,,,,,,9879879870,123 Fake St,Realtown,,60606,,,,,\n"
        "7,,,,,,,,,,,9879879870,123 Fake St,,,60606,,,,,\n"
        "8,,,,,,,,,,,,123 Fake St,,,60606,,,,,\n"
        "9,,,,,,,,,,,,,Realtown,,60606,,,,,\n"
        "10,,,,,,,,,,,,,,,,-87.717600,41.886300,,,\n"
        "11,,,,,,,,,,,,,,,,,41.886300,,,\n"
        "12,,,,,,,,,,,,,,,,-87.717600,,,,\n"
        "13,,,,,,,,,,,5554443331,,,,,,41.886300,,,\n"
        "14,,,,,,,,,,,,1060 W Addison,,,,-87.717600,,,,\n"
    )
    no_location_combo_rows = [3, 4, 8, 9, 11, 12, 14]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "CaiChallengeCaiLocationValidationPostChallenge"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


def test_cai_challenge_row_rule__entity_name_given_type():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,,,,,,H,Health Co,,,,,,,,,,,,,\n"
        "3,,,,,,H,,,,,,,,,,,,,,\n"
        "4,,,,,,S,,,,,,,,,,,,,,\n"
        "5,,,,,,S,Edukato,,,,,,,,,,,,,\n"
        "6,,,,,,L,Libre Office,,,,,,,,,,,,,\n"
        "7,,,,,,L,,,,,,,,,,,,,,\n"
        "8,,,,,,G,,,,,,,,,,,,,,\n"
        "9,,,,,,G,Governalia,,,,,,,,,,,,,\n"
        "10,,,,,,P,Unnamed Public Housing Org,,,,,,,,,,,,,\n"
        "11,,,,,,P,,,,,,,,,,,,,,\n"
        "12,,,,,,C,,,,,,,,,,,,,,\n"
        "13,,,,,,C,CAI Co,,,,,,,,,,,,,\n"
        "14,,,,,,F,Cailand PD,,,,,,,,,,,,,\n"
        "15,,,,,,F,,,,,,,,,,,,,,\n"
    )
    no_location_combo_rows = [3, 4, 7, 8, 12, 15]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "CaiChallengeEntityNameConditionalType"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


def test_cai_challenge_row_rule__challenge_explanation_given_type():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,C,,,,This place is a CAI!,,,,,,,,,,,,,,,\n"
        "3,C,,,,,,,,,,,,,,,,,,,\n"
        "4,R,,,,This CAI doesn't exist anymore.,,,,,,,,,,,,,,,\n"
        "5,R,,,,,,,,,,,,,,,,,,,\n"
        "6,Q,,,,This CAI has broadband options.,,,,,,,,,,,,,,,\n"
        "7,Q,,,,,,,,,,,,,,,,,,,\n"
        "9,G,,,,This CAI lacks any broadband options.,,,,,,,,,,,,,,,\n"
        "10,G,,,,,,,,,,,,,,,,,,,\n"
    )
    no_location_combo_rows = [3, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "CaiChallengeChallengeExplanationConditionalTypeC"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


def test_cai_challenge_row_rule__cms_number_given_type():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,,,,,,H,,,654321,,,,,,,,,,,\n"
        "3,,,,,,H,,,,,,,,,,,,,,\n"
        "4,,,,,,H,,,9875558880,,,,,,,,,,,\n"
        "5,,,,,,S,,,111111,,,,,,,,,,,\n"
        "6,,,,,,L,,,222222,,,,,,,,,,,\n"
        "7,,,,,,G,,,333333,,,,,,,,,,,\n"
        "8,,,,,,F,,,444456,,,,,,,,,,,\n"
        "9,,,,,,P,,,55589A,,,,,,,,,,,\n"
        "10,,,,,,C,,,98A5F4,,,,,,,,,,,\n"
        "11,,,,,,C,,,,,,,,,,,,,,\n"
        "12,,,,,,P,,,,,,,,,,,,,,\n"
        "13,,,,,,F,,,,,,,,,,,,,,\n"
        "14,,,,,,G,,,,,,,,,,,,,,\n"
        "15,,,,,,L,,,,,,,,,,,,,,\n"
        "16,,,,,,S,,,,,,,,,,,,,,\n"
    )
    no_location_combo_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "CaiChallengeCMSConditionalTypeH"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


def test_cai_challenge_row_rule__frn_given_type():
    csv_content = (
        "challenge,challenge_type,challenger,category_code,disposition,"
        "challenge_explanation,type,entity_name,entity_number,CMS number,frn,"
        "location_id,address_primary,city,state,zip_code,longitude,latitude,"
        "explanation,need,availability\n"
        "2,,,,,,H,,,,A54321,,,,,,,,,,\n"
        "3,,,,,,H,,,,,,,,,,,,,,\n"
        "4,,,,,,H,,,,9875558880,,,,,,,,,,\n"
        "5,,,,,,S,,,,1111115858,,,,,,,,,,\n"
        "6,,,,,,S,,,,,,,,,,,,,,\n"
        "7,,,,,,L,,,,3333335432,,,,,,,,,,\n"
        "8,,,,,,L,,,,,,,,,,,,,,\n"
        "9,,,,,,P,,,,5554443331,,,,,,,,,,\n"
        "10,,,,,,P,,,,,,,,,,,,,,\n"
        "11,,,,,,C,,,,,,,,,,,,,,\n"
        "12,,,,,,C,,,,7788990011,,,,,,,,,,\n"
        "13,,,,,,F,,,,9985207410,,,,,,,,,,\n"
        "14,,,,,,F,,,,,,,,,,,,,,\n"
        "15,,,,,,G,,,,,,,,,,,,,,\n"
        "16,,,,,,G,,,,1591591590,,,,,,,,,,\n"
    )
    no_location_combo_rows = [2, 3, 6, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.CAIChallengeDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "CaiChallengeFRNGivenType"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


###########################################################
# ############# Post Challenge Locations ################ #
###########################################################


def test_post_challenge_location__column_names():
    csv_content = "location_id,location_class\n"
    missing_column_names = ["classification"]
    extra_column_names = ["location_class"]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeLocationDataValidator(tf.name)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_name_validation"
        ]
        assert len(test_issues) == 1
        assert list(test_issues[0].keys()) == [
            "columns_missing_from_file",
            "extra_columns_in_file",
        ]
        assert set(test_issues[0]["columns_missing_from_file"]) == set(
            missing_column_names
        )
        assert set(test_issues[0]["extra_columns_in_file"]) == set(extra_column_names)


def test_post_challenge_location__column_order():
    csv_content = "index,classification,location_id\n"
    col_numbers_w_wrong_names = [1, 3]
    expected_cols_not_in_expected_place = ["location_id", "<missing_column>"]
    file_col_names_in_wrong_place = [
        "index",
        "location_id",
    ]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeLocationDataValidator(tf.name)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_order_validation"
        ]
        assert len(test_issues) == 1
        cols_out_of_order = test_issues[0]["cols_out_of_order"]
        print(cols_out_of_order)
        assert all(
            list(el.keys())
            == ["column_number", "expected_column_name", "column_name_in_file"]
            for el in cols_out_of_order
        )
        missing_expected_cols_w_missings = [
            el["expected_column_name"] for el in cols_out_of_order
        ]
        misordered_expected_col_names = [
            c for c in missing_expected_cols_w_missings if c != "<missing_column>"
        ]
        misordered_col_names_in_file_w_missings = [
            el["column_name_in_file"] for el in cols_out_of_order
        ]
        misordered_col_names_in_file = [
            c
            for c in misordered_col_names_in_file_w_missings
            if c != "<missing_column>"
        ]
        assert set(misordered_expected_col_names) == set(
            expected_cols_not_in_expected_place
        )
        assert set(misordered_col_names_in_file) == set(file_col_names_in_wrong_place)
        assert set(el["column_name_in_file"] for el in cols_out_of_order) == set(
            file_col_names_in_wrong_place
        )
        assert [
            el["column_number"] for el in cols_out_of_order
        ] == col_numbers_w_wrong_names


def test_post_challenge_location_column_dtypes__location_id():
    csv_content = (
        "location_id,classification\n"
        "1234567890,2\n"
        "12345.6789,3\n"
        "123456789A,4\n"
        "0x12345678,5\n"
        ",6\n"
    )
    invalid_value_rows = [3, 4, 5, 6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeLocationDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_location_column_dtypes__classification():
    csv_content = (
        "location_id,classification\n"
        "2,1\n"
        "3,1.0\n"
        "4,\n"
        "5,0x00\n"
        "6,a\n"
        "7,0\n"
    )
    invalid_value_rows = [3, 4, 5, 6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeLocationDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "classification"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_location_col_content__location_id():
    csv_content = (
        "location_id,classification\n"
        "1234567890,2\n"
        "123456789,3\n"
        "999999999,4\n"
        "1000000000,5\n"
        "9999999999,6\n"
        "10000000000,7\n"
        "10A00X0D0M0,8\n"
        "4060801030,9\n"
    )
    invalid_value_rows = [3, 4, 7, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeLocationDataValidator(tf.name)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_location_col_content__classification():
    csv_content = (
        "location_id,classification\n"
        "2,0\n"
        "3,Unserved\n"
        "4,1\n"
        "5,Underserved\n"
        "6,2\n"
        "7,Served\n"
        "8,3\n"
        "9,Overserved\n"
    )
    invalid_value_rows = [3, 5, 7, 8, 9]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeLocationDataValidator(tf.name)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "classification"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


###########################################################
# ############ Post Challenge CAI Locations ############# #
###########################################################


def test_post_challenge_cai__column_names():
    csv_content = (
        "type,cai_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,crs,"
        "explanation,need,availability\n"
    )
    missing_column_names = ["entity_name"]
    extra_column_names = ["cai_name", "crs"]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_name_validation"
        ]
        assert len(test_issues) == 1
        assert list(test_issues[0].keys()) == [
            "columns_missing_from_file",
            "extra_columns_in_file",
        ]
        assert set(test_issues[0]["columns_missing_from_file"]) == set(
            missing_column_names
        )
        assert set(test_issues[0]["extra_columns_in_file"]) == set(extra_column_names)


def test_post_challenge_cai__column_order():
    csv_content = (
        "type,entity_number,entity_name,location_id,CMS number,frn,"
        "address_primary,city,state,zip_code,latitude,longitude,explanation,"
        "need,availability\n"
    )
    col_numbers_w_wrong_names = [2, 3, 4, 5, 6, 11, 12]
    expected_cols_not_in_expected_place = [
        "entity_name",
        "entity_number",
        "cms_number",
        "frn",
        "location_id",
        "longitude",
        "latitude",
    ]
    file_col_names_in_wrong_place = [
        "entity_number",
        "entity_name",
        "location_id",
        "cms_number",
        "frn",
        "latitude",
        "longitude",
    ]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name)
        issues = _validator.file_validator.issues

        test_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_order_validation"
        ]
        assert len(test_issues) == 1
        cols_out_of_order = test_issues[0]["cols_out_of_order"]
        assert all(
            list(el.keys())
            == ["column_number", "expected_column_name", "column_name_in_file"]
            for el in cols_out_of_order
        )
        missing_expected_cols_w_missings = [
            el["expected_column_name"] for el in cols_out_of_order
        ]
        misordered_expected_col_names = [
            c for c in missing_expected_cols_w_missings if c != "<missing_column>"
        ]
        misordered_col_names_in_file_w_missings = [
            el["column_name_in_file"] for el in cols_out_of_order
        ]
        misordered_col_names_in_file = [
            c
            for c in misordered_col_names_in_file_w_missings
            if c != "<missing_column>"
        ]
        assert set(misordered_expected_col_names) == set(
            expected_cols_not_in_expected_place
        )
        assert set(misordered_col_names_in_file) == set(file_col_names_in_wrong_place)
        assert set(el["column_name_in_file"] for el in cols_out_of_order) == set(
            file_col_names_in_wrong_place
        )
        assert [
            el["column_number"] for el in cols_out_of_order
        ] == col_numbers_w_wrong_names


def test_post_challenge_cai_column_dtypes__entity_number():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,1,,,,,,,,,,,,\n"
        "3,,1.0,,,,,,,,,,,,\n"
        "4,,0xFF,,,,,,,,,,,,\n"
        "5,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 4]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "entity_number"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_column_dtypes__location_id():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,1234567890,,,,,,,,,\n"
        "3,,,,,0x00000000,,,,,,,,,\n"
        "4,,,,,12345.6789,,,,,,,,,\n"
        "5,,,,,abcdefghij,,,,,,,,,\n"
        "6,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 4, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_column_dtypes__need():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,,,41.876356,\n"
        "3,,,,,,,,,,,,,41876356,\n"
        "4,,,,,,,,,,,,,-41,\n"
        "5,,,,,,,,,,,,,41-876356,\n"
        "6,,,,,,,,,,,,,,\n"
        "7,,,,,,,,,,,,,0xABcD,\n"
    )
    invalid_value_rows = [2, 5, 6, 7]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "need"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_column_dtypes__availability():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,,,,41.876356\n"
        "3,,,,,,,,,,,,,,41876356\n"
        "4,,,,,,,,,,,,,,-41\n"
        "5,,,,,,,,,,,,,,41-876356\n"
        "6,,,,,,,,,,,,,,\n"
        "7,,,,,,,,,,,,,,0xABcD\n"
    )
    invalid_value_rows = [2, 5, 7]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_dtype_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_dtype_issues
            if i["column"] == "availability"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__type():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "S,2,,,,,,,,,,,,,\n"
        "A,3,,,,,,,,,,,,,\n"
        "L,4,,,,,,,,,,,,,\n"
        "B,5,,,,,,,,,,,,,\n"
        "E,6,,,,,,,,,,,,,\n"
        "G,7,,,,,,,,,,,,,\n"
        "H,8,,,,,,,,,,,,,\n"
        "T,9,,,,,,,,,,,,,\n"
        "F,10,,,,,,,,,,,,,\n"
        "P,11,,,,,,,,,,,,,\n"
        "Q,12,,,,,,,,,,,,,\n"
        "C,13,,,,,,,,,,,,,\n"
        ",14,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3, 5, 6, 9, 12, 14]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "type"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__entity_name():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,,,,\n"
        "3,Name of this CAI,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [2]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "entity_name"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__cms_number():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,123456,,,,,,,,,,,\n"
        "3,,,,,,,,,,,,,,\n"
        "4,,,12345678,,,,,,,,,,,\n"
        "5,,,1234567890,,,,,,,,,,,\n"
        "6,,,123456789012,,,,,,,,,,,\n"
        "7,,,123ABC,,,,,,,,,,,\n"
        "8,,,123ABCdef0,,,,,,,,,,,\n"
        "9,,,1a,,,,,,,,,,,\n"
    )
    invalid_value_rows = [4, 6, 9]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "cms_number"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__frn():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,0015433808,,,,,,,,,,\n"
        "3,,,,,,,,,,,,,,\n"
        "4,,,,1234567890,,,,,,,,,,\n"
        "5,,,,0000000000,,,,,,,,,,\n"
        "6,,,,9999999999,,,,,,,,,,\n"
        "7,,,,10000000000,,,,,,,,,,\n"
        "8,,,,999999999,,,,,,,,,,\n"
        "9,,,,ABCDEfghij,,,,,,,,,,\n"
        "10,,,,Ab,,,,,,,,,,\n"
        "11,,,,Ab123,,,,,,,,,,\n"
    )
    invalid_value_rows = [7, 8, 9, 10, 11]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "frn"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__location_id():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,1234567890,,,,,,,,,\n"
        "3,,,,,,,,,,,,,,\n"
        "4,,,,,A234567890,,,,,,,,,\n"
        "5,,,,,999999999,,,,,,,,,\n"
        "6,,,,,1000000000,,,,,,,,,\n"
        "7,,,,,9999999999,,,,,,,,,\n"
        "8,,,,,10000000000,,,,,,,,,\n"
        "9,,,,,0100000000,,,,,,,,,\n"
    )
    invalid_value_rows = [4, 5, 8, 9]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__state():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,AL,,,,,,\n"
        "3,,,,,,,,alabama,,,,,,\n"
        "4,,,,,,,,,,,,,,\n"
        "5,,,,,,,,VI,,,,,,\n"
        "6,,,,,,,,PR,,,,,,\n"
        "7,,,,,,,,GU,,,,,,\n"
        "8,,,,,,,,DC,,,,,,\n"
        "9,,,,,,,,dc,,,,,,\n"
        "10,,,,,,,,AS,,,,,,\n"
    )
    invalid_value_rows = [3, 4, 9]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "state"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__zip_code():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,12345,,,,,\n"
        "3,,,,,,,,,,,,,,\n"
        "4,,,,,,,,,60606-5432,,,,,\n"
        "5,,,,,,,,,606VI,,,,,\n"
        "6,,,,,,,,,606,,,,,\n"
        "7,,,,,,,,,312773,,,,,\n"
        "8,,,,,,,,,06060,,,,,\n"
        "9,,,,,,,,,00000,,,,,\n"
    )
    invalid_value_rows = [4, 5, 6, 7]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "zip_code"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__longitude():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,-89.999999,,,,\n"
        "3,,,,,,,,,,-90.000001,,,,\n"
        "4,,,,,,,,,,89.999999,,,,\n"
        "5,,,,,,,,,,90.000001,,,,\n"
        "6,,,,,,,,,,0,,,,\n"
        "7,,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,-87.7176,,,,\n"
        "9,,,,,,,,,,-179.999999,,,,\n"
        "10,,,,,,,,,,-180.000001,,,,\n"
        "11,,,,,,,,,,179.999999,,,,\n"
        "12,,,,,,,,,,180.000001,,,,\n"
        "13,,,,,,,,,,180.000000,,,,\n"
        "14,,,,,,,,,,-180.000000,,,,\n"
        "15,,,,,,,,,,-180.00000,,,,\n"
        "16,,,,,,,,,,-179.000000123,,,,\n"
    )
    invalid_value_rows = [6, 8, 10, 12, 15]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "longitude"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__latitude():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,-89.999999,,,\n"
        "3,,,,,,,,,,,-90.000001,,,\n"
        "4,,,,,,,,,,,89.999999,,,\n"
        "5,,,,,,,,,,,90.000001,,,\n"
        "6,,,,,,,,,,,0,,,\n"
        "7,,,,,,,,,,,,,,\n"
        "8,,,,,,,,,,,41.8863,,,\n"
        "9,,,,,,,,,,,179.95,,,\n"
        "10,,,,,,,,,,,-179.95,,,\n"
        "11,,,,,,,,,,,90.000000,,,\n"
        "12,,,,,,,,,,,-90.000000,,,\n"
        "13,,,,,,,,,,,42.000000123,,,\n"
        "14,,,,,,,,,,,-42.000000123,,,\n"
        "15,,,,,,,,,,,42.00000,,,\n"
        "16,,,,,,,,,,,around 42.00000,,,\n"
    )
    invalid_value_rows = [3, 5, 6, 8, 9, 10, 15, 16]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "latitude"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__need():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,,,1000,\n"
        "3,,,,,,,,,,,,,,\n"
    )
    invalid_value_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "need"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_col_content__availability():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,,,,,,,,,,1\n"
        "3,,,,,,,,,,,,,,0\n"
        "4,,,,,,,,,,,,,,-1\n"
    )
    invalid_value_rows = [4]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "availability"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_post_challenge_cai_row_rule__location_possibly_determinable():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "2,,,,,1234567890,,,,,,,,,\n"
        "3,,,,,,123 Fake St,,,,,,,,\n"
        "4,,,,,,123 Fake St,Realtown,,,,,,,\n"
        "5,,,,,,123 Fake St,Realtown,,12345,,,,,\n"
        "6,,,,,1234567890,123 Fake St,Realtown,,12345,,,,,\n"
        "7,,,,,1234567890,123 Fake St,,,12345,,,,,\n"
        "8,,,,,,123 Fake St,,,12345,,,,,\n"
        "9,,,,,,,,,,-87.717600,41.886300,,,\n"
        "10,,,,,,,,,,-87.717600,,,,\n"
        "11,,,,,,,,,,,41.886300,,,\n"
        "12,,,,,9874563210,,,,,-87.717600,,,,\n"
        "13,,,,,,5432 Post Gres,,,,,41.886300,,,\n"
    )
    no_location_combo_rows = [3, 4, 8, 10, 11, 13]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "PostChallengeCaiLocationValidation"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


def test_post_challenge_cai_row_rule__cms_number_given_type():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "H,2,,555444,,,,,,,,,,,\n"
        "H,3,,,,,,,,,,,,,\n"
        "H,4,,a,,,,,,,,,,,\n"
        "S,5,,789321,,,,,,,,,,,\n"
        "S,6,,,,,,,,,,,,,\n"
        "L,7,,3138675309,,,,,,,,,,,\n"
        "L,8,,,,,,,,,,,,,\n"
        "G,9,,,,,,,,,,,,,\n"
        "G,10,,987sdf5545,,,,,,,,,,,\n"
        "F,11,,876000,,,,,,,,,,,\n"
        "F,12,,,,,,,,,,,,,\n"
        "P,13,,,,,,,,,,,,,\n"
        "P,14,,555606,,,,,,,,,,,\n"
        "C,15,,,,,,,,,,,,,\n"
        "C,16,,909606,,,,,,,,,,,\n"
    )
    no_location_combo_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "PostChallengeCaiCMSValidatorGivenCAIType"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in no_location_combo_rows)
        assert failing_rows == no_location_combo_rows
        assert all(r in no_location_combo_rows for r in failing_rows)


def test_post_challenge_cai_row_rule__frn_given_cai_type():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "H,2,,,5554440000,,,,,,,,,,\n"
        "H,3,,,,,,,,,,,,,\n"
        "H,4,,,A119113110,,,,,,,,,,\n"
        "S,5,,,8855220011,,,,,,,,,,\n"
        "S,6,,,,,,,,,,,,,\n"
        "L,7,,,3138675309,,,,,,,,,,\n"
        "L,8,,,,,,,,,,,,,\n"
        "G,9,,,,,,,,,,,,,\n"
        "G,10,,,987sdf5545,,,,,,,,,,\n"
        "F,11,,,8760005505,,,,,,,,,,\n"
        "F,12,,,,,,,,,,,,,\n"
        "P,13,,,,,,,,,,,,,\n"
        "P,14,,,5556061141,,,,,,,,,,\n"
        "C,15,,,,,,,,,,,,,\n"
        "C,16,,,909606abcD,,,,,,,,,,\n"
    )
    no_location_combo_rows = [3, 4, 6, 8]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "PostChallengeCaiFRNValidationGivenCAIType"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


def test_post_challenge_cai_row_rule__explanation_given_cai_type():
    csv_content = (
        "type,entity_name,entity_number,CMS number,frn,location_id,"
        "address_primary,city,state,zip_code,longitude,latitude,explanation,"
        "need,availability\n"
        "C,2,,,,,,,,,,,Our org teaches digital literacy skills.,,\n"
        "C,3,,,,,,,,,,,,,\n"
        "S,4,,,,,,,,,,,,,\n"
        "L,5,,,,,,,,,,,,,\n"
        "G,6,,,,,,,,,,,,,\n"
        "H,7,,,,,,,,,,,,,\n"
        "F,8,,,,,,,,,,,,,\n"
        "P,9,,,,,,,,,,,,,\n"
    )
    no_location_combo_rows = [3]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.PostChallengeCAIDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        row_rule_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "row_rule_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in row_rule_issues
            if i["validation"] == "PostChallengeCaiExplanationValidationGivenCAIType"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == no_location_combo_rows
        assert all(r in failing_rows for r in no_location_combo_rows)


#########################################################
# ###################### Unserved ##################### #
#########################################################


def test_unserved__column_order():
    csv_content = "1002345678\n2003456789\n"
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.UnservedDataValidator(tf.name, 1000)
        index_col = _validator.file_validator.csv_data_object.index_col
        assert _validator.file_validator.csv_data_object.header == [
            index_col,
            "location_id",
        ]


def test_unserved_rows_missing_columns():
    csv_content = (
        "1234\n"  # 1
        "12.3\n"  # 2
        "0x00\n"  # 3
        "-100\n"  # 4
        "1-11\n"  # 5
        "\n"  # 6
    )
    invalid_value_rows = [6]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.UnservedDataValidator(tf.name)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "enough_columns_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_unserved_column_dtypes__location_id():
    csv_content = (
        "1234\n"  # 1
        "12.3\n"  # 2
        "0x00\n"  # 3
        "-100\n"  # 4
        "1-11\n"  # 5
        "\n"  # 6
    )
    invalid_value_rows = [2, 3, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.UnservedDataValidator(tf.name)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_unserved_col_content__location_id():
    csv_content = (
        "1002345678\n" "2003456789\n" "300345678\n" "40023456789\n" "5002345XII\n"
    )
    invalid_value_rows = [3, 4, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.UnservedDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in invalid_value_rows)


##########################################################
# ##################### Underserved #################### #
##########################################################


def test_underserved__column_order():
    csv_content = "1002345678\n2003456789\n"
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.UnderservedDataValidator(tf.name, 1000)
        index_col = _validator.file_validator.csv_data_object.index_col
        assert _validator.file_validator.csv_data_object.header == [
            index_col,
            "location_id",
        ]


def test_underserved_column_dtypes__location_id():
    csv_content = (
        "1234\n"  # 1
        "12.3\n"  # 2
        "0x00\n"  # 3
        "-100\n"  # 4
        "1-11\n"  # 5
        "\n"  # 6
    )
    invalid_value_rows = [2, 3, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.UnderservedDataValidator(tf.name)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_dtype_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert failing_rows == invalid_value_rows
        assert all(r in failing_rows for r in invalid_value_rows)


def test_underserved_col_content__location_id():
    csv_content = (
        "1002345678\n" "2003456789\n" "300345678\n" "40023456789\n" "5002345XII\n"
    )
    invalid_value_rows = [3, 4, 5]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", newline="") as tf:
        tf.write(csv_content)
        tf.seek(0)
        _validator = validator.UnderservedDataValidator(tf.name, 1000)
        issues = _validator.file_validator.issues

        col_contents_issues = [
            i["issue_details"]
            for i in issues
            if i["issue_type"] == "column_contents_validation"
        ]
        row_fails = [
            i["failing_rows_and_values"]
            for i in col_contents_issues
            if i["column"] == "location_id"
        ]
        assert len(row_fails) == 1
        failing_rows = [row for row, id_col, col in row_fails[0]]
        assert all(r in failing_rows for r in invalid_value_rows)
