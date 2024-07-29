import csv
from pathlib import Path
from typing import List, Optional, Tuple


class EmptyFileError(Exception):
    def __init__(self, file_name: Path, message="File is empty"):
        self.file_name = file_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.filename}: {self.message}"


class CSVData:
    def __init__(self, file_name: Path, header: Optional[List[str]] = None):
        self.file_name = file_name
        if header is None:
            self.header = []
        else:
            self.header = header
        self.data = []
        self.load_file(self.file_name)

    def detect_bom(self, file_name: Path) -> str:
        with open(file_name, "rb") as f:
            raw_bytes = f.read(4)
            if raw_bytes.startswith(b"\xef\xbb\xbf"):
                return "utf-8-sig"
            elif raw_bytes.startswith(b"\xff\xfe\x00\x00"):
                return "utf-32le"
            elif raw_bytes.startswith(b"\x00\x00\xfe\xff"):
                return "utf-32be"
            elif raw_bytes.startswith(b"\xff\xfe"):
                return "utf-16le"
            elif raw_bytes.startswith(b"\xfe\xff"):
                return "utf-16be"
            else:
                return None

    def detect_encoding(
        self,
        file_name: Path,
        encodings: Tuple = (
            "utf-32",
            "utf-16",
            "utf-8",
            "latin1",
            "iso-8859-1",
            "ascii",
            "cp1252",
        ),
    ) -> str:
        bom_encoding = self.detect_bom(file_name)
        if bom_encoding is not None:
            return bom_encoding
        for encoding in encodings:
            try:
                with open(file_name, encoding=encoding) as f:
                    f.read()
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        raise ValueError("Unable to determine encoding")

    def load_file(self, file_name):
        """
        Load the CSV file, extract the header, and load the data with row
          indices.
        """
        encoding = self.detect_encoding(file_name)
        with open(file_name, mode="r", newline="", encoding=encoding) as file:
            csv_reader = csv.reader(file)
            self._set_header(csv_reader)
            try:
                for index, row in enumerate(csv_reader):
                    self.data.append([index] + row)
            except Exception:
                print(
                    f"Encountered an error while tring to read in file\n  {file_name}\n"
                )
                print(f"specifically while reading the line after row number {index}.")
                print(f"row contents: {row}")
                raise

    def _set_header(self, csv_reader) -> None:
        if len(self.header) == 0:
            try:
                self.header = next(csv_reader)
            except StopIteration:
                raise EmptyFileError(
                    self.file_name,
                    f"No data found in file {self.file_name}, and no header "
                    "provided.",
                )
        self._set_index(self.header)
        self.header = [self.index_col] + self.header
        self._standardize_header()

    def _standardize_col_name(self, col_name: str) -> str:
        return "_".join(col_name.lower().strip().split())

    def _standardize_header(self) -> None:
        standardized_header = []
        for col_name in self.header:
            standardized_col_name = self._standardize_col_name(col_name)
            if standardized_col_name in standardized_header:
                raise Exception(
                    f"Standardizing column {col_name} creates a column name"
                    " collision. Please remove the extraneous columns from "
                    f"the {self.file_name} file and then try again."
                )
            standardized_header.append(standardized_col_name)
        if len(standardized_header) == len(self.header):
            self.header = standardized_header
        else:
            raise Exception(
                "Something unexpected happened during column name " "standardization."
            )

    def _set_index(self, header: List[str], _limit: int = 10) -> List[str]:
        """
        Sets the name for a row-index column.
        """
        index_col_name = "index"
        i = 0
        while index_col_name in header:
            # this loop checks for col_name collisions
            index_col_name = f"_{index_col_name}"
            i += 1
            if i > _limit:
                bad_cols = [f"{'_' * i}index" for i in range(0, _limit + 1)]
                raise Exception(
                    f"The given csv has all of these columns: {bad_cols}"
                    "\n\n ... why?"
                )
        self.index_col = index_col_name

    def __getitem__(self, column_name):
        """
        Allow dictionary-like access to columns.
        """
        if column_name not in self.header:
            raise KeyError(f"Column '{column_name}' not found in header.")

        col_index = self.header.index(column_name)
        return [row[col_index] for row in self.data]
