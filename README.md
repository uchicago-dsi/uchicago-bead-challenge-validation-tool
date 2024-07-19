<br/><br/>
<p align="center">
<img src="./images/DSILogo.png" alt="UChicago Logo" width="600"/>
</p>
<br/><br/>

# BEAD INSPECTOR


Welcome to the BEAD Inspector, presented by the [University of Chicago's Data Science Institute](https://datascience.uchicago.edu/).

As part of the NTIA BEAD Challenge process, eligible entities are required to submit a specific set of data deliverables to the NTIA. The purpose of this package is to validate NTIA BEAD challenge process data (against the [official specification](https://www.ntia.gov/sites/default/files/2023-11/bead_challenge_process_policy_notice.pdf#page=23) and Notices of Changes to Process) and provide feedback that helps Eligible Entities identify errors in their submittable CSVs.

More information on the BEAD Challenge process can be found:

1. [Video Link](https://www.youtube.com/watch?v=p3pOUUDEGVo)
2. [Detailed BEAD Description](https://broadbandusa.ntia.gov/technical-assistance/BEAD_Challenge_Process_Data_Submission)
3. [Challenge Submission Templates](https://broadbandusa.ntia.doc.gov/technical-assistance/BEAD_Challenge_Results_Submission_Templates)
4. [Link to challenge notice](https://www.internetforall.gov/bead-challenge-process-policy)

Importantly, this is not an official package supported by the NTIA. The authors of this package present this without any warranty or guarantees.

## Who should use this package

This package requires knowledge of the command line and a computer installed with Python and pip. The code has been tested on both Windows PCs and Macs.

## What this package checks

This package focuses on a set of data quality issues that are easy to overlook when submitting your challenge results. This package will check the following files for the following issues

<table>

<tr>
<th>

| File Name |
| --- |
| cai.csv |
| challengers.csv |
| challenges.csv |
| cai_challenges.csv |
| post_challenge_locations.csv |
| post_challenge_cai.csv
</th>

<!-- There are three specific types of errors that it will identify: -->
<th>

**Quality Checks**

1. **Column based data quality issues:** Errors related to data types present in each column. Examples of this include making sure that numeric and text fields are properly typed.
2. **Row based data quality issues:** The BEAD data deliverable specification contains a number of row-level conditional logic. Examples of this include fields that need to be present conditional on the challenge type.
3. **Multi-file internal consistency:** Errors related to cross-file consistency, such as making sure that every challenger in the `challenges.csv` file exist in the `challengers.csv` file.
</th>
</tr>
</table>

## What this package does _not_ check

1. **Availability / Fabric Validation:** This package does not check locations against the Fabric or FCC Availability Data.
2. **Correctness of open text fields:** There are a number of open text fields (such as `resolution` in the `challenges.csv` file. BEAD INSPECTOR checks to make sure that these fields are not empty, but does not check to verify the correctness of the content.

## Using BEAD Inspector

This python package is installed via `pip` and can be used directly from the command line following the instructions below. Refer to the [advanced usage section](#advanced-usage) for non-command line use.

#### Pre-requisites

Make sure that you computer has access to Python and Pip. You can do this by going to the command line and typing `pip --version` and `python --version`. Both of these should return version numbers. The Python version needs to be greater than 3.7. As with all third part packages, we recommend using a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) when using, but it is not required.

#### Installation

This package can be installed via python's package manager, pip, by typing `pip install bead_inspector` at the command line.

#### Creating a Report

1. Put all files that you wish to have checked in a single directory, noting the location. _Make sure that all filenames conform to the NTIA standard filenames._ If you wish to only check a subset of the files then put that subset inside the directory. Bead Inspector will only analyze those files that it finds in the specified location.
2. Once files are copied, enter the following at the command line, making sure to put a full path location.

    `> bead_inspector /path_to_files`

3. Note that running the command may take a few minutes, depending on the size of the files.
4. Once the command is complete two files will be generated:
    1. `path_to_files/reports/validation_issue_logs_{DATE}_{TIME}.html`
    2. `path_to_files/logs/validation_issue_logs_{DATE}_{TIME}.json`

The `html` file in the `reports` subdirectory is a human readable version of the report. For most users this is the file that should be used to evaluate the quality of the reports. The `json` file is presented in case you wish to programatically interpret the resulting files.

## Understanding the Report

TODO

## FAQ

| What if I only want to have _some_ of the files to check? |
| --- | 
| BEAD Inspector only checks the files which are present in the target directory that following the NTIA file naming conventions. If a file is missing a warning will be issued, but the tool will check all present files |

| There is a rule that I think BEAD Inspector should check that it is not checking. | 
| --- | 
| Please add an issue to the [issue page](https://github.com/uchicago-dsi/uchicago-bead-challenge-validation-tool/issues). | 

| I found a bug! | 
| --- | 
| Please file an issue using the [issue page](https://github.com/uchicago-dsi/uchicago-bead-challenge-validation-tool/issues). We will do our best to fix it as soon as we have time. If you are more technically skilled and know how to fix the issue please put in a pull request.| 

## Development

If you find a bug or wish to highlight an issue, please use the github tools above.  If you wish to help with development of this project, please submit a pull request which describes the code changes that you are making and why.

**Note** This repo uses [pre-commit](https://pre-commit.com/) hook, please install by typing `pre-commit install`.

## Advanced Usage

You can programmatically access BEAD inspector by importing the package and passing it a directory containing the files.

```python
from pathlib import Path
import bead_inspector

bcdv = bead_inspector.validator.BEADChallengeDataValidator(
    data_directory=Path("path/to/dir/containing/csvs"),
    single_error_log_limit=5,
)
```

You can also generate a report from an existing log file, such as in the example below.

```python
from pathlib import Path
import bead_inspector

issues_file_path=Path("path/to/logs_dir/validation_issue_logs_date_time.json")
reporter = bead_inspector.reporting.ReportGenerator(issues_file_path)
```

This will output a report file (HTML) to the `/reports/` directory parallel to `/logs/` directory containing the .json file of issues.

The directory of CSVs (`/output_csv/` in the above example) should look like this now (with a new .json file and .html file being added each time `BEADChallengeDataValidator()` is run).

```console
$ cd output_csv/
$ tree
.
├── logs
│   └── validation_issue_logs_20240714_113216.json
├── reports
│   └── validation_issue_logs_20240714_113216.html
├── cai_challenges.csv
├── cai.csv
├── challengers.csv
├── challenges.csv
├── post_challenge_cai.csv
├── post_challenge_locations.csv
├── underserved.csv
└── unserved.csv
```