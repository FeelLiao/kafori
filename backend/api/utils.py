import pandas as pd
from pathlib import Path
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import json
import shutil
import modin.pandas as mpd
import time

logger = logging.getLogger(__name__)


# Utility function to safely search for metrics in HISAT2 log files
def extract_hisat2_metrics(hisat2_log: Path) -> dict[str, int]:
    """Extract metrics from a HISAT2 log file.
    Args:
        hisat2_log (Path): Path to the HISAT2 log file.
    Returns:
        dict: A dictionary containing total reads, mapped reads, and unique mapping.
    Raises:
        RuntimeError: If the expected patterns are not found in the log file.
    """

    metrics = {"total_reads": 0, "mapped_reads": 0, "unique_mapping": 0}
    try:
        hisat2_file = hisat2_log.read_text(encoding="utf-8")

        def safe_search(pattern, text=hisat2_file):
            m = re.search(pattern, text)
            return int(m.group(1))

        # Extract useful statistics from hisat2 run log using regex
        total_reads = safe_search(r"(\d+) reads;")
        al_con_e_1 = safe_search(
            r"(\d+)\s*\([^)]*\) aligned concordantly exactly 1 time")
        al_con_g_1 = safe_search(
            r"(\d+)\s*\([^)]*\) aligned concordantly >1 times")
        al_dis_1 = safe_search(
            r"(\d+)\s*\([^)]*\) aligned discordantly 1 time")
        al_ex_1 = safe_search(r"(\d+)\s*\([^)]*\) aligned exactly 1 time")
        al_g_1 = safe_search(r"(\d+)\s*\([^)]*\) aligned >1 times")

        # Calculate total, mapped, and unique reads
        total = total_reads * 2
        mapped = al_con_e_1*2 + al_con_g_1*2 + al_dis_1*2 + al_ex_1 + al_g_1
        unq_map = al_con_e_1*2 + al_dis_1*2 + al_ex_1

        # Update metrics dictionary
        metrics["total_reads"] = total
        metrics["mapped_reads"] = mapped
        metrics["unique_mapping"] = unq_map

    except Exception as e:
        logger.error(
            f"Error extracting HISAT2 metrics from {hisat2_log.name}: {e} "
            "This may indicate that the expected patterns were not found in the log file.", exc_info=True)
        raise RuntimeError(
            f"Failed to extract metrics from {hisat2_log}") from e
    return metrics


# process the HISAT2 log report
# Format percentage safely
def format_rate(numerator: int, denominator: int) -> str:
    try:
        rate = numerator / denominator * 100
        return f"{rate:.2f}%"
    except ZeroDivisionError:
        return "0.00%"


# Main function to process a directory of HISAT2 logs
def align_report(hisat2_log_dir: Path) -> tuple[bool, pd.DataFrame, list[str]]:
    """
    Process HISAT2 log files in a directory and return a DataFrame with alignment statistics.
    Args:
        hisat2_log_dir (Path): Directory containing HISAT2 log files.
    Returns:
        tuple: A tuple containing:
            - bool: True if processing was successful, False if at least one log were error.
            - pd.DataFrame: DataFrame with alignment statistics.
            - list[str]: List of log files that failed to process.
    Raises:
        RuntimeError: If no valid HISAT2 log files were processed successfully.
    """
    hisat2_logs = list(hisat2_log_dir.glob("*.log"))
    alignment_results: dict[str, dict[str, int]] = {}
    failed_logs: list[str] = []

    def process_log(log_file: Path) -> tuple[str, dict[str, int]]:
        try:
            sample = log_file.stem
            metrics = extract_hisat2_metrics(log_file)
            return sample, metrics
        except Exception:
            return None

    max_workers = min(8, os.cpu_count() or 1)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_log, log_file): log_file.name for log_file in hisat2_logs}
        for future in as_completed(futures):
            results = future.result()
            if results is not None:
                sample, metrics = results
                alignment_results[sample] = metrics
            else:
                log_name = futures[future]
                failed_logs.append(log_name)

    if not alignment_results:
        raise RuntimeError(
            "No valid HISAT2 log files were processed successfully.")

    # Construct DataFrame
    df = pd.DataFrame.from_dict(alignment_results, orient='index')
    df.index.name = "Sample"
    df.reset_index(inplace=True)

    # Add formatted rate columns
    df["Mapped Rate"] = df.apply(lambda x: format_rate(
        x["mapped_reads"], x["total_reads"]), axis=1)
    df["Unique Mapped Rate"] = df.apply(lambda x: format_rate(
        x["unique_mapping"], x["total_reads"]), axis=1)

    # Rename columns for clarity
    df = df.rename(columns={
        "total_reads": "Total Reads",
        "mapped_reads": "Reads Mapped",
        "unique_mapping": "Unique Mapped"
    })

    # Define final column order
    final_columns = [
        "Sample", "Total Reads", "Reads Mapped", "Mapped Rate",
        "Unique Mapped", "Unique Mapped Rate"
    ]
    df = df[[col for col in final_columns if col in df.columns]]
    df = df.sort_values(by="Sample")
    if failed_logs:
        logger.warning(
            f"Some logs failed to process: {', '.join(failed_logs)}. "
            "Check the logs for more details.")
        return False, df, failed_logs

    return True, df, failed_logs


def trim_report(fastp_json_dir: Path) -> tuple[bool, pd.DataFrame, list[str]]:
    """
    Parse a list of fastp JSON report files and return a summary DataFrame (multi-threaded).
    Args:
        fastp_json_dir (Path): Directory containing fastp JSON files.
    Returns:
        tuple: A tuple containing:
            - bool: True if processing was successful, False if at least one file failed.
            - pd.DataFrame: DataFrame with summary statistics.
            - list[str]: List of JSON files that failed to process.
    Raises:
        RuntimeError: If no valid fastp JSON files were processed successfully.
    """
    report_json_files = list(fastp_json_dir.glob("*.json"))
    report_all: dict[str, dict[str, int | str]] = {}
    report_errors: list[str] = []

    def process_json(report: Path):
        try:
            with open(report, 'r') as f:
                data = json.load(f)
                before = data["summary"]["before_filtering"]
                after = data["summary"]["after_filtering"]
                data_out = {
                    "total_reads": before["total_reads"],
                    "after_filtering": after["total_reads"],
                    "GC_content": after["gc_content"]
                }
                sample = report.stem
                return sample, data_out
        except Exception as e:
            logger.error(f"Error processing {report}: {e}", exc_info=True)
            return None

    max_workers = min(8, os.cpu_count() or 1)
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(
            process_json, log_file): log_file.name for log_file in report_json_files}
        for future in as_completed(futures):
            results = future.result()
            if results is not None:
                sample, data = results
                report_all[sample] = data
            else:
                log_name = futures[future]
                report_errors.append(log_name)

    if not report_all:
        raise RuntimeError(
            "No valid fastp json files were processed successfully.")

    trim_report = pd.DataFrame.from_dict(report_all, orient='index')
    trim_report.index.name = "Sample"
    trim_report.reset_index(inplace=True)

    trim_report["PassRate"] = trim_report["after_filtering"] / \
        trim_report["total_reads"] * 100
    trim_report["PassRate"] = trim_report["PassRate"].round(2)
    trim_report["GC_content"] = trim_report["GC_content"].round(2)
    trim_report["PassRate"] = trim_report["PassRate"].astype(str) + "%"
    trim_report["GC_content"] = trim_report["GC_content"].astype(str) + "%"

    trim_report = trim_report.rename(
        columns={
            "total_reads": "Total Reads",
            "after_filtering": "After Filtering",
            "GC_content": "GC Content",
            "PassRate": "Pass Rate"
        }
    )

    trim_report = trim_report.sort_values(by=["Sample"], ascending=True)
    if report_errors:
        logger.warning(
            f"Some fastp JSON files failed to process: {', '.join(report_errors)}. "
            "Check the logs for more details.")
        return False, trim_report, report_errors
    return True, trim_report, report_errors


def cleanup_directories(directories: list[Path]) -> None:
    """
    Clean up specified directories by removing them if they exist.

    Args:
        directories (list[Path]): List of Path objects representing directories to clean up.
    """
    for dir_path in directories:
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                logger.info(f"Removed directory: {dir_path}")
            except Exception as e:
                logger.error(
                    f"Error removing directory {dir_path}: {e}", exc_info=True)
        else:
            logger.warning(f"Directory does not exist: {dir_path}")


def dataframe_t(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transpose the DataFrame and set the first row as the header.

    Returns:
        pd.DataFrame: The transposed DataFrame.
    """
    data_T = df.T
    data_T.columns = data_T.iloc[0]      # 第一行作为新的列名
    data_T = data_T.iloc[1:]             # 去掉第一行
    data = data_T.reset_index(inplace=False)      # 把原来的 index 变成一列
    results = data.rename(columns={'index': 'SampleID'}, inplace=False)
    return results


def dataframe_wide2long(df: mpd.DataFrame, type: str) -> mpd.DataFrame:
    """
        Wrap the DataFrame from wide to long format.
        Args:
            df (mpd.DataFrame): The DataFrame to reshape.
            type (str): The name of the value column ("Counts" or "Tpm").
        Returns:
            pd.DataFrame: The DataFrame with additional columns.
    """
    timestamp_int = int(time.time())
    date_str = format(timestamp_int, "x").zfill(8)
    df_long = mpd.melt(
        df, id_vars=['SampleID', "SampleRealID"], var_name='GeneID', value_name=type)
    hex_ids = [format(i+1, "x").zfill(8) for i in range(len(df_long))]
    df_long["UniqueID"] = ["GEXP" + date_str + hex_id for hex_id in hex_ids]

    return df_long
