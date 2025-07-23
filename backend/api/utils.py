import pandas as pd
from pathlib import Path
from datetime import datetime
from hashlib import md5
import re
from typing import List, Tuple


class UploadFileProcessor:
    """
    A class to process uploaded xlsx files.
    """

    def __init__(self, file: str | Path):
        """
        Initialize the UploadFileProcessor with a file path.
        Args:
            file (str | Path): The path to the xlsx file.
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not an xlsx file.
            RuntimeError: If there is an error reading or parsing the file.
        """
        if isinstance(file, str):
            file = Path(file)
        self.file = file
        self.valid_dataframe = self.__file_validation()
        self.modified_timestamp = self.file.stat().st_mtime
        self.modified_time = self.__timestamp_to_str(self.modified_timestamp)
        self.experiment_categories = self.__experiment_category()
        self.experiments = self.__experiment()
        self.collection_parts = self.__collection_part()

    def __timestamp_to_str(self, timestamp: float) -> str:
        """
        Convert a timestamp to a formatted string.
        Args:
            timestamp (float): The timestamp to convert.
        Returns:
            str: The formatted date string.
        """
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def __file_validation(self) -> pd.DataFrame:
        """
        Validate the uploaded file.
        Checks if the xlsx file is created according to
        the standard list in the "Explain" sheet.
        Returns:
            bool: True if valid, False otherwise.
        """

        # Check if the file exists and is an xlsx file
        if not self.file.exists():
            raise FileNotFoundError(f"File {self.file} does not exist.")
        if self.file.suffix.lower() != ".xlsx":
            raise ValueError("File must be an xlsx file.")

        # Read the "SampleInfo" sheet.
        try:
            df = pd.read_excel(self.file, sheet_name="SampleInfo", header=0,
                               dtype={"CollectionTime": str},
                               na_values=["", "NA", "null", "None", "999"])

            # Check if CollectionTime and SampleAge is in the correct format
            df["CollectionTime"] = pd.to_datetime(df["CollectionTime"])
            df["SampleAge"] = pd.to_numeric(df["SampleAge"]).astype("Int64")
        except Exception as e:
            raise RuntimeError(
                f"Error reading or parsing file {self.file}: {e}"
            ) from e

        # Check if SampleID is in the correct format
        invalid_ids_index = df["SampleID"].apply(lambda x: not re.match(
            r"^[A-Za-z][A-Za-z0-9]*-\d{1,2}$", str(x)))
        invalid_ids = df.loc[invalid_ids_index, "SampleID"]
        if not invalid_ids.empty:
            raise ValueError(
                f"SampleID contains invalid characters: {invalid_ids.tolist()}\n"
                "SampleID must follow the format: start with a letter (A-Z or a-z), "
                "followed by any number of letters or digits, then a hyphen '-', "
                "and end with 1 or 2 digits. Example: 'A-1', 'SBA23-11'.")

        duplicated_ids = df.loc[df["SampleID"].duplicated(), "SampleID"]
        if not duplicated_ids.empty:
            raise ValueError(
                f"SampleID contains duplicate values: {duplicated_ids.tolist()}\n"
                "Each SampleID must be unique.")

        return df

    def __experiment_category(self) -> List:
        """
        Get the unique experiment categories from the DataFrame.
        Returns:
            List: A list of unique experiment categories.
        """
        return self.valid_dataframe["ExperimentCategory"].unique().tolist()

    def __experiment(self) -> List:
        """
        Get the unique experiments from the DataFrame.
        Returns:
            List: A list of unique experiments.
        """
        return self.valid_dataframe["Experiment"].unique().tolist()

    def __collection_part(self) -> List:
        """
        Get the unique collection parts from the DataFrame.
        Returns:
            List: A list of unique collection parts.
        """
        return self.valid_dataframe["CollectionPart"].unique().tolist()

    def rawdata_validation(self, rawdata_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate the md5 of raw data.
        Args:
            rawdata_path (Path): The path to the raw data directory.
        Returns:
            bool: True if valid, False otherwise.
        """
        if not rawdata_path.exists():
            raise FileNotFoundError(
                f"Raw data path {rawdata_path} does not exist.")

        files1 = self.valid_dataframe[["FileName1", "MD5checksum1"]]
        files2 = self.valid_dataframe[["FileName2", "MD5checksum2"]]
        files1_dict = dict(zip(files1["FileName1"], files1["MD5checksum1"]))
        files2_dict = dict(zip(files2["FileName2"], files2["MD5checksum2"]))
        files_dict = {**files1_dict, **files2_dict}
        md5_result = {}
        for file_name, md5_checksum in files_dict.items():
            file_path = rawdata_path / file_name
            if not file_path.exists():
                raise FileNotFoundError(f"File {file_name} does not exist in "
                                        f"raw data path {rawdata_path}.")

            with open(file_path, "rb") as f:
                file_md5 = md5(f.read()).hexdigest()

            if file_md5 != md5_checksum:
                md5_result[file_name] = False

        if not md5_result:
            return True, []
        else:
            return False, list(md5_result.keys())

    def database_wrapper(self) -> pd.DataFrame:
        """
        Wrap the valid DataFrame with "UniqueID" and "UniqueEXID" columns
        for database insertion.
        Returns:
            pd.DataFrame: The DataFrame with additional columns.
        """
        df = self.valid_dataframe.copy()
        timestamp_int = int(self.modified_timestamp)
        date_str = format(timestamp_int, "x").zfill(8)

        # Add a unique identifier for each sample
        hex_ids = [format(i+1, "x").zfill(3) for i in range(len(df))]
        df["UniqueID"] = ["LRX" + date_str + hex_id for hex_id in hex_ids]

        # Add a unique experiment ID
        df["UniqueEXID"] = ["TRCRIE" + date_str]

        return df

    @staticmethod
    def trans_to_smk_samples(dataframe: pd.DataFrame,
                             rawdata_path: Path,
                             to_file: bool = False,
                             output_path: Path | None = None) -> pd.DataFrame:
        """
        Convert the DataFrame to snakemake samples format.
        Args:
            dataframe (pd.DataFrame): The DataFrame to convert. The dataframe
                should be the processed dataframe from the UploadFileProcessor
                class (the dataframe to write into mysql).
            rawdata_path (Path): The path to the raw data directory.
            to_file (bool): Whether to save the converted DataFrame to a file.
            output_path (Path | None): The path to save the converted DataFrame.
                If None, the DataFrame will not be saved to a file.
        Returns:
            pd.DataFrame: The converted DataFrame.
        """

        sample_sheet = pd.DataFrame()
        sample_sheet["sample"] = dataframe["FileName"].apply
