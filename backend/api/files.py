import pandas as pd
from pathlib import Path
from datetime import datetime
from hashlib import md5
import re
from typing import List, Tuple
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

logger = logging.getLogger(__name__)


class UploadFileProcessor:
    """
    A class to process uploaded xlsx files.
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not an xlsx file.
        RuntimeError: If there is an error reading or parsing the file.
    """

    def __init__(self, file: str | Path):
        """
        Initialize the UploadFileProcessor with a file path.
        Args:
            file (str | Path): The path to the xlsx file.
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
            logger.error("uploaded sample sheet does not exist")
            raise FileNotFoundError(f"File {self.file.name} does not exist.")
        if self.file.suffix.lower() != ".xlsx":
            logger.error("sample sheet file must be xlsx format")
            raise ValueError("File must be an xlsx file.")

        # Read the "SampleInfo" sheet.
        try:
            df = pd.read_excel(self.file, sheet_name="SampleInfo", header=0,
                               dtype={"CollectionTime": str},
                               na_values=["", "NA", "null", "None", "999"])
            logger.info(f"sample sheet file successfully read: {self.file.name}")
            # Check if CollectionTime and SampleAge is in the correct format
            df["CollectionTime"] = pd.to_datetime(df["CollectionTime"])
            logger.info("CollectionTime column successfully converted to datetime")
            df["SampleAge"] = pd.to_numeric(df["SampleAge"]).astype("Int64")
            logger.info("SampleAge column successfully converted to numeric")
        except Exception as e:
            logger.error(f"Error reading sample sheet file: {self.file.name}")
            raise RuntimeError(
                f"Error reading or parsing file {self.file.name}: {e}"
            ) from e

        # Check if SampleID is in the correct format
        invalid_ids_index = df["SampleID"].apply(lambda x: not re.match(
            r"^[A-Za-z][A-Za-z0-9]*-\d{1,2}$", str(x)))
        invalid_ids = df.loc[invalid_ids_index, "SampleID"]
        if not invalid_ids.empty:
            logger.error(f"{self.file.name} SampleID contains invalid characters: {invalid_ids.to_list()}")
            raise ValueError(
                f"SampleID contains invalid characters: {invalid_ids.tolist()}\n"
                "SampleID must follow the format: start with a letter (A-Z or a-z), "
                "followed by any number of letters or digits, then a hyphen '-', "
                "and end with 1 or 2 digits. Example: 'A-1', 'SBA23-11'.")

        duplicated_ids = df.loc[df["SampleID"].duplicated(), "SampleID"]
        if not duplicated_ids.empty:
            logger.error(f"{self.file} SampleID contains duplicate values: {duplicated_ids.tolist()}")
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

    @staticmethod
    def check_md5(file_path: Path, expected_md5: str) -> Tuple[str, bool]:
        if not file_path.exists():
            logger.error(f"file {file_path.name} does not exist.")
            raise FileNotFoundError(f"File {file_path.name} does not exist in raw data path.")
        with open(file_path, "rb") as f:
            logger.info(f"{file_path.name} is checking md5 value")
            file_md5 = md5(f.read()).hexdigest()
        return file_path.name, file_md5 == expected_md5

    def rawdata_validation(self, rawdata_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate the md5 of raw data.
        Args:
            rawdata_path (Path): The path to the raw data directory.
        Returns:
            Tuple[bool, List[str]]: A tuple containing a boolean indicating
            whether the validation passed and a list of failed files.
        Raises:
            FileNotFoundError: If the raw data path does not exist.
        """
        if not rawdata_path.exists():
            logger.error(f"Rawdata path {rawdata_path} does not exist.")
            raise FileNotFoundError(
                f"Raw data path {rawdata_path} does not exist.")

        files1 = self.valid_dataframe[["FileName1", "MD5checksum1"]]
        files2 = self.valid_dataframe[["FileName2", "MD5checksum2"]]
        files1_dict = dict(zip(files1["FileName1"], files1["MD5checksum1"]))
        files2_dict = dict(zip(files2["FileName2"], files2["MD5checksum2"]))
        files_dict = {**files1_dict, **files2_dict}

        failed_files = []
        max_workers = min(8, os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.check_md5, rawdata_path / file_name, md5_checksum): file_name
                for file_name, md5_checksum in files_dict.items()
            }
            for future in as_completed(futures):
                try:
                    file_name, is_valid = future.result()
                    if not is_valid:
                        logger.error(f"{file_name} md5 value check failed")
                        failed_files.append(file_name)
                except Exception as e:
                    logger.error(f"Error checking {futures[future]}: {e}")
                    failed_files.append(futures[future])

        if not failed_files:
            return True, []
        else:
            return False, failed_files

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
        experiment_groups = df.groupby("Experiment").ngroup() + 1  # 分组编号从1开始
        df["UniqueEXID"] = [
            f"TRCRIE{date_str}{str(idx).zfill(3)}"
            for idx in experiment_groups
        ]

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
        sample_sheet["sample"] = dataframe["FileName1"].apply(
            lambda x: str(x).split("_")[0])
        sample_sheet["sample_id"] = dataframe["UniqueID"]
        sample_sheet["read1"] = dataframe["FileName1"].apply(
            lambda x: str(Path(rawdata_path, x).absolute()))
        sample_sheet["read2"] = dataframe["FileName2"].apply(
            lambda x: str(Path(rawdata_path, x).absolute()))

        if to_file:
            sample_sheet.to_csv(output_path, index=False)
        return sample_sheet
