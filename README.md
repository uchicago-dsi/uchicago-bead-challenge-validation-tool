<br/><br/>
<p align="center">
<img src="https://raw.githubusercontent.com/uchicago-dsi/uchicago-bead-challenge-validation-tool/main/images/DSILogo.png" alt="UChicago Logo" width="600"/>
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

This package focuses on a set of data quality issues that are easy to overlook when submitting your challenge results. This package will check the following files for the following issues:

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

1. **Availability / Fabric Validation:** This package does not check locations against the FCC Fabric or FCC Availability Data.
2. **Correctness of open text fields:** There are a number of open text fields (such as `resolution` in the `challenges.csv` file. BEAD INSPECTOR checks to make sure that these fields are not empty, but does not check to verify the correctness of the content.

## Using BEAD Inspector

This python package is installed via `pip` and can be used directly from the command line following the instructions below. Refer to the [advanced usage section](#advanced-usage) for non-command line use.

#### Pre-requisites

Make sure that you computer has access to Python and Pip. You can do this by going to the command line and typing `pip --version` and `python --version`. Both of these should return version numbers. The Python version needs to be greater than 3.7. As with all third party packages, we recommend using a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/), but it is not required.

#### Installation

This package can be installed via python's package manager, pip, by typing `pip install bead_inspector` at the command line.

#### Creating a Report

1. Put all files that you wish to have checked in a single directory, noting the location. _Make sure that all filenames conform to the NTIA standard filenames._ If you wish to only check a subset of the files, put that subset inside the directory. Bead Inspector will only analyze files that it finds in the specified location. [See here for NTIA standards](https://broadbandusa.ntia.gov/sites/default/files/2024-03/BEAD_Challenge_Process_Data_Submission_-_Data_Quality_File_Formats_and_Common_Issues.pdf)
2. Once files are copied, enter the following at the command line, making sure to put a full path location.

    `> bead_inspector /path_to_files`

3. Note that running the command may take a few minutes, depending on the size of the files.
4. Once the command is complete two files will be generated:
    1. `path_to_files/reports/BEAD_Data_Validation_Report_{DATE}_{TIME}.html`
    2. `path_to_files/logs/validation_issue_logs_{DATE}_{TIME}.json`

The `html` file in the `reports` subdirectory is a human readable version of the report. For most users this is the file that should be used to evaluate the quality of the reports. The `json` file is presented in case you wish to programatically interpret the resulting files.

## Understanding the Report

Within our report we denote two different levels of checks:

1. **Errors**: Checks which are errors are extremely likely to need to be fixed before submission. Examples of this would include required fields missing, etc.
2. **Info**: Our Info level are checks which may or may not need to be fixed, depending on the circumstances of your submissions. For example if an eligible entity has submitted area challenges then, per NOTCP 07/002, the `challenger` field in the `challenges.csv` file should be left empty, which is in contrast to the original policy notice. As such we generate an "Info" level issue as this _may_ need to be fixed depending on the specific challenge requirements for your state.

When a report is generated there are three sections:

1. The [Header](#header)
2. The [Table of Contents](#table-of-contents)
3. [Specific Issue list](#specific-issue-list)

### Header

<table>
<tr>
<td>
<p>
<img src="https://raw.githubusercontent.com/uchicago-dsi/uchicago-bead-challenge-validation-tool/main/images/Header.png" alt="Header Example" width="2400"/>
</p>
</td>
<td>
<p>The header material consists of a Title, which states the date that the report was run and summary information.</p>

<p>The summary information is broken out by Errors and Info level issues. The first column is the data format, which is the name of the CSV that is being analyzed. The second column specifies the level of the issue. The third column specifies the number of issues of this level found in the file.</p>

<p>Finally the last column in the table specifies the total number of rows found in that file.</p>
</td>
</tr>
<table>

### Table of Contents

<table>
<tr>
<td>
<p>
<img src="https://raw.githubusercontent.com/uchicago-dsi/uchicago-bead-challenge-validation-tool/main/images/TableOfContents.png" alt="TOC Example" width="2400"/>
</p>
</td>
<td>
<p>The Table of Contents contains a list with links to specific issues found, organized by the level of the issue found (Info / Error). They are numbered, in order, starting from one and the issue name is of the format:</p>

<p>{File where issue was found} :: Name of Issue :: [Optional: Type of Issue]</p>

</td>
</tr>
<table>


### Specific Issue List


<table>
<tr>
<td>
<p>
<img src="https://raw.githubusercontent.com/uchicago-dsi/uchicago-bead-challenge-validation-tool/main/images/OneIssue.png" alt="Issue Example" width="2400"/>
</p>
</td>
<td>
<p>Detailed information regarding the specific issue can be found in this section. There are a few new fields that were not previously discussed:</p>
<ul>
<li><b>Description:</b> This lists a description of the problem encountered.</li>
<li><b>Column:</b> Displays the specific column in the CSV where this issue applies.</li>
<li><b>Failing Rows:</b> Lists the failed values by row.</li>
<li><b>Total Rows with Invalid Values:</b> Identifies the total number of rows with failing values.</li>
<li><b>All Rows Shown:</b> BEAD Inspector displays the first few invalid values. In the case where there are many broken values this will indicate if all failures are shown or not.</li>
</ul>
</td>
</tr>
<table>

## FAQ

| Where does the report go? Does the NTIA see this? What about UChicago? |
| --- | 
| NOPE! You can look at the code in this repository and see that nothing is reported to NTIA or the University of Chicago. This is simply a tool to identify potential problems. What you do with the report is up to you! | 

| Some of the issues seem to duplicate, why? |
| --- | 
| Some of the checks that we have in place do overlap with other issues. Missing and nulls, for example, can run afoul of multiple NTIA rules.

| What if I only want to have _some_ of the files to check? |
| --- | 
| BEAD Inspector only checks the files which 1) are present in the target directory that 2) follow the NTIA file naming conventions. If a file is missing, a warning will be issued, but the tool will check all files present in the target directory |

| There is a rule that I think BEAD Inspector should check that it is not checking. | 
| --- | 
| Please add an issue to the [issue page](https://github.com/uchicago-dsi/uchicago-bead-challenge-validation-tool/issues). | 

| I found a bug! | 
| --- | 
| Please file an issue using the [issue page](https://github.com/uchicago-dsi/uchicago-bead-challenge-validation-tool/issues). We will do our best to fix it as soon as we have time. If you are more technically skilled and know how to fix the issue please put in a pull request.| 

## Development

If you find a bug or wish to highlight an issue, please use the github tools above.  If you wish to help with development of this project, please submit a pull request which describes the code changes that you are making and why.

<!-- I also put together notes for building, testing, and publishing code. I'll find somewhere better for them tomorrow.
# Dev notes:
## Making a testing, dev, and packaging env
python -m venv .venv
conda deactivate
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
python -m pip install build
python -m pip install twine
python -m pip install "setuptools>=61.0"
python -m pip install "setuptools-scm"
python -m pip install wheel
## Building the package
rm -rf dist/ *.egg-info
python -m build
### Testing a build
deactivate
python -m venv .testenv
source .testenv/bin/activate
python -m pip install --upgrade pip
python -m pip install dist/bead_inspector-0.0.post1-py3-none-any.whl
# then try running the code with the built version
bead_inspector ../path/to/csv_dir
if all good, you can deactivate and delete the env
deactivate
rm -r .testenv
And just make a new one next time you need one (it only takes a minute or two).
## Tagging a release
git checkout -b my_feature_branch
git add src/stuff.py tests/test_stuff.py
git commit -m "Prepare for 0.1.0 release"
git push feature_branch
# do the PR + merge step on GitHub
git checkout main
git pull
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0\
then build the package again
rm -r dist
python -m build
you can install and test the build if you like (as shown above), and when you're content, you, well, Matt Triano can push it up to PyPI via this command
twine upload dist/*
(an API key is required hence it being a Matt Triano thing ATM, but we can sort that out)

**Note** This repo uses [pre-commit](https://pre-commit.com/) hook, please install by typing `pre-commit install`. -->

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
