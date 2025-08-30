import time
import pandas as pd
from pathlib import Path
from hashlib import md5
import re
from typing import List, Tuple, Dict
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from io import BytesIO
from enum import StrEnum, auto
import modin.pandas as mpd

from backend.api.utils import dataframe_t, dataframe_wide2long


logger = logging.getLogger(__name__)


class FileType(StrEnum):
    xlsx = auto()
    csv = auto()
    parquet = auto()


class GeneDataType(StrEnum):
    tpm = auto()
    counts = auto()


class UploadFileProcessor:
    """
    A class to process uploaded files `sample_sheet`, `gene_expression_tpm`,
    `gene_expression_counts`, `rawdata`.
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not an xlsx file.
        RuntimeError: If there is an error reading or parsing the file.
    """

    def read_file(file: BytesIO, file_type: FileType) -> pd.DataFrame:
        """
        Read file and return a DataFrame.
        Returns:
            pd.DataFrame: The DataFrame containing the file data.
        Raises:
            RuntimeError: If there is an error reading or parsing the file.
        """
        try:
            match file_type:
                case FileType.xlsx:
                    df = pd.read_excel(file, sheet_name="SampleInfo", header=0,
                                       dtype={"CollectionTime": str},
                                       na_values=["", "NA", "null", "None", "999"])
                case FileType.csv:
                    df = pd.read_csv(file, header=0)
                case FileType.parquet:
                    df = pd.read_parquet(file)
            logger.info(
                f"{file_type} file successfully read")
            return df
        except Exception as e:
            logger.error(
                f"Error reading {file_type} file", exc_info=True)
            raise RuntimeError(
                f"Error reading or parsing {file_type} file: {e}"
            )

    def sample_data_validation(name: str, dataframe: pd.DataFrame) -> bool:
        """
        Validate the uploaded file. Checks if the xlsx file is created according to the
        standard list in the 'Explain' sheet.

        Returns:
            bool: True if valid, False otherwise.
        Raises:
            RuntimeError: If there is an error transferring
            collection time or sample age to standard format.
            ValueError: If SampleID contains invalid characters or duplicates.
        """
        try:
            df = dataframe
            # Check if CollectionTime and SampleAge is in the correct format
            df["CollectionTime"] = pd.to_datetime(df["CollectionTime"])
            logger.info(
                "CollectionTime column successfully converted to datetime")
            df["SampleAge"] = pd.to_numeric(df["SampleAge"]).astype("Int64")
            logger.info("SampleAge column successfully converted to numeric")
        except Exception as e:
            logger.error(
                f"Error transfer collection time or sample age to standard format: {name}", exc_info=True)
            raise RuntimeError(
                f"Error parsing file {name}: {e}")

        # Check if SampleID is in the correct format
        invalid_ids_index = df["SampleID"].apply(lambda x: not re.match(
            r"^[A-Za-z][A-Za-z0-9]*-\d{1,2}$", str(x)))
        invalid_ids = df.loc[invalid_ids_index, "SampleID"]
        if not invalid_ids.empty:
            logger.error(
                f"{name} SampleID contains invalid characters: {invalid_ids.to_list()}")
            raise ValueError(
                f"SampleID contains invalid characters: {invalid_ids.tolist()}\n"
                "SampleID must follow the format: start with a letter (A-Z or a-z), "
                "followed by any number of letters or digits, then a hyphen '-', "
                "and end with 1 or 2 digits. Example: 'A-1', 'SBA23-11'.")
        else:
            logger.info(f"{name} SampleID format is valid.")

        duplicated_ids = df.loc[df["SampleID"].duplicated(), "SampleID"]
        if not duplicated_ids.empty:
            logger.error(
                f"{name} SampleID contains duplicate values: {duplicated_ids.tolist()}")
            raise ValueError(
                f"SampleID contains duplicate values: {duplicated_ids.tolist()}\n"
                "Each SampleID must be unique.")
        else:
            logger.info(f"{name} SampleID is unique.")

        return True

    @staticmethod
    def check_md5(file_path: Path, expected_md5: str) -> Tuple[str, bool]:
        if not file_path.exists():
            logger.error(f"file {file_path.name} does not exist.")
            raise FileNotFoundError(
                f"File {file_path.name} does not exist in raw data path.")
        with open(file_path, "rb") as f:
            logger.info(f"{file_path.name} is checking md5 value")
            file_md5 = md5(f.read()).hexdigest()
        return file_path.name, file_md5 == expected_md5

    def gene_ex_validation(sample_sheet: pd.DataFrame, ex: pd.DataFrame) -> bool:
        """
        Validate the gene expression file.
        Args:
            df (pd.DataFrame): The DataFrame containing the gene expression data.
        Returns:
            bool: True if the gene expression file is valid, False otherwise.
        """
        sample_ids = set(sample_sheet["SampleID"].tolist())
        ex_sample_ids = ex.columns.tolist()
        ex_sample_ids.remove("gene_id")

        if sample_ids != set(ex_sample_ids):
            logger.error(
                "Sample IDs in the gene expression file do not match the sample sheet.")
            raise ValueError(
                "Sample IDs in the gene expression file do not match the sample sheet.")
        else:
            logger.info("Gene expression file validation passed.")
            return True

    def rawdata_validation(df: pd.DataFrame, rawdata_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate the md5 of raw data.
        Args:
            df (pd.DataFrame): The DataFrame containing the sample sheet data.
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

        files1 = df[["FileName1", "MD5checksum1"]]
        files2 = df[["FileName2", "MD5checksum2"]]
        files1_dict = dict(zip(files1["FileName1"], files1["MD5checksum1"]))
        files2_dict = dict(zip(files2["FileName2"], files2["MD5checksum2"]))
        files_dict = {**files1_dict, **files2_dict}

        failed_files = []
        max_workers = min(8, os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(UploadFileProcessor.check_md5, rawdata_path / file_name, md5_checksum): file_name
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

        logger.info(
            "Sample sheet converted to snakemake samples format successfully.")

        if to_file:
            sample_sheet.to_csv(output_path, index=False)
            logger.info(f"Sample sheet saved to {output_path} successfully.")
        return sample_sheet


class PutDataBaseWrapper:
    """
    A wrapper class for add data to the database.
    This class provides methods to insert experimental class, experiment,
    sample, gene expression data in TPM and counts format into the database.
    """

    def __init__(self,
                 sample_sheet: pd.DataFrame,
                 gene_expression_tpm: pd.DataFrame,
                 gene_expression_counts: pd.DataFrame):
        self.sample_sheet = sample_sheet
        self.gene_expression_tpm = gene_expression_tpm
        self.gene_expression_counts = gene_expression_counts
        self.sample_sheet_wrapped = self.__database_wrapper()

    def __database_wrapper(self) -> pd.DataFrame:
        """
        Wrap the valid DataFrame with "UniqueID", "UniqueEXID" and "ExpClass" columns
        for database insertion.
        Returns:
            pd.DataFrame: The DataFrame with additional columns.
        """
        try:
            df = self.sample_sheet.copy()
            timestamp_int = int(time.time())
            date_str = format(timestamp_int, "x").zfill(8)

            # Add a unique identifier for each sample
            hex_ids = [format(i+1, "x").zfill(3) for i in range(len(df))]
            df["UniqueID"] = ["LRX" + date_str + hex_id for hex_id in hex_ids]
            logger.info("UniqueID column added to sample sheet.")

            # Add a unique experiment ID
            experiment_groups = df.groupby("Experiment").ngroup() + 1  # 分组编号从1开始
            df["UniqueEXID"] = [
                f"TRCRIE{date_str}{str(idx).zfill(3)}"
                for idx in experiment_groups
            ]
            logger.info("UniqueEXID column added to sample sheet.")
            exp_class_grp = df.groupby("ExperimentCategory").ngroup() + 1
            df["ExpClass"] = [
                f"EXPC{date_str}{str(idx).zfill(3)}" for idx in exp_class_grp]
            logger.info("ExpClass column added to sample sheet.")

        except Exception as e:
            logger.error(f"Error occurred while wrapping sample sheet for database: {e}")

        return df

    def communicate_id_in_db(self) -> list[dict[str, str]]:
        """
        Parsing the experiment class and experiment category from the sample_sheet to communicate
        with the database if the class ID is duplicated.
        Returns:
            list[dict[str, str]]: A list of dictionaries containing the experiment class
            and experiment category.
        """
        sample_sheet_wrapped = self.sample_sheet_wrapped
        exclass = sample_sheet_wrapped[[
            "ExpClass", "ExperimentCategory"]].drop_duplicates().to_dict(orient="records")
        logger.info(
            "Experiment class and category extracted for database communication.")
        return exclass

    def db_insert(self, exclass: tuple[list[bool], List[Dict[str, str]]]) -> Tuple[pd.DataFrame]:
        """
        Parsing exp_sheet and sample_sheet from the sample_sheet_wrapped based on the communicated exclass.

        Args:
            exclass: Tuple[bool, List[Dict[str, str]]]: A tuple containing a boolean indicating
            whether the exclass need to be replaced. True for not to replace and False for replacing,
            and a list of dictionaries containing the experiment class and experiment category.

        Returns:
            Tuple[pd.DataFrame]: A tuple containing two DataFrames:
                exp_sheet: experiment category DataFrame
                sample_sheet: sample sheet DataFrame
        """
        # TODO: CHANGE
        if not all(exclass[0]):
            new_exclass = pd.DataFrame.from_records(exclass[1])
            self.sample_sheet_wrapped = self.sample_sheet_wrapped.drop(columns=["ExpClass"]).merge(
                new_exclass, on="ExperimentCategory", how="left")
            logger.info("Exclass replaced in sample sheet.")

        exp_sheet = self.sample_sheet_wrapped[[
            "ExpClass", "UniqueEXID", "Experiment"]].drop_duplicates()
        logger.info("Experiment sheet extracted from original sample sheet.")
        sample_sheet = self.sample_sheet_wrapped.drop(
            columns=["ExpClass", "ExperimentCategory", "Experiment", "FileName1",
                     "FileName2", "MD5checksum1", "MD5checksum2"])
        sample_sheet["FileName"] = None
        sample_sheet["Sample"] = None
        logger.info("Sample sheet extracted from original sample sheet.")

        return exp_sheet, sample_sheet

    def expression_wrapper(self, sample_sheet: pd.DataFrame) -> mpd.DataFrame:
        """
        Wrap the gene expression DataFrame with "UniqueID" column for database insertion.
        Returns:
            pd.DataFrame: The DataFrame with additional columns.
        """
        tpm_t = dataframe_t(self.gene_expression_tpm)
        counts_t = dataframe_t(self.gene_expression_counts)

        ids = sample_sheet[["SampleID", "UniqueID"]]

        tpm_t_merge = tpm_t.merge(ids, on="SampleID", how="left")
        counts_t_merge = counts_t.merge(ids, on="SampleID", how="left")

        logger.info("UniqueID column added to gene expression data.")

        tpm = dataframe_wide2long(mpd.DataFrame(tpm_t_merge), "Tpm")
        counts = dataframe_wide2long(mpd.DataFrame(counts_t_merge), "Counts")

        logger.info("Gene expression data converted to long format.")

        return tpm, counts
