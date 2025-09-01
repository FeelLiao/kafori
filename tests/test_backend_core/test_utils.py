import pytest
from backend.api import utils
import pandas as pd
import modin.pandas as mpd

hisat2_log_content = (
    """
      14832983 reads; of these:
        14832983 (100.00%) were paired; of these:
          1131460 (7.63%) aligned concordantly 0 times
          7155488 (48.24%) aligned concordantly exactly 1 time
          6546035 (44.13%) aligned concordantly >1 times
          ----
          1131460 pairs aligned concordantly 0 times; of these:
            99429 (8.79%) aligned discordantly 1 time
          ----
          1032031 pairs aligned 0 times concordantly or discordantly; of these:
            2064062 mates make up the pairs; of these:
              627387 (30.40%) aligned 0 times
              582845 (28.24%) aligned exactly 1 time
              853830 (41.37%) aligned >1 times
      97.89% overall alignment rate
      [bam_sort_core] merging from 2 files and 8 in-memory blocks...
"""
)

fastp_json_content = (
    """
{
    "summary": {
        "fastp_version": "0.23.4",
        "sequencing": "paired end (151 cycles + 151 cycles)",
        "before_filtering": {
            "total_reads":30550358,
            "total_bases":4575072545,
            "q20_bases":4456108328,
            "q30_bases":4258564656,
            "q20_rate":0.973997,
            "q30_rate":0.930819,
            "read1_mean_length":149,
            "read2_mean_length":149,
            "gc_content":0.521848
        },
        "after_filtering": {
            "total_reads":29665966,
            "total_bases":4441892767,
            "q20_bases":4345773040,
            "q30_bases":4158820875,
            "q20_rate":0.978361,
            "q30_rate":0.936272,
            "read1_mean_length":149,
            "read2_mean_length":149,
            "gc_content":0.521226
        }
    }
}
    """
)

tpmdata_path = "tests/upstream/samples_merged_tpm.csv"

@pytest.fixture
def dataframe_trans_data(tpm = tpmdata_path):
    return tpm


@pytest.fixture
def hisat2_log_path(tmp_path, content=hisat2_log_content):
    names = [f"sample{i+1}.log" for i in range(100)]
    log_path1 = tmp_path / "hisat2_logs1"
    log_path1.mkdir(parents=True, exist_ok=True)
    for name in names:
        log = log_path1 / name
        log.write_text(content, encoding="utf-8")

    log_path0 = tmp_path / "hisat2_logs0"
    log_path0.mkdir(parents=True, exist_ok=True)
    for name in names:
        log = log_path0 / name
        log.write_text(content, encoding="utf-8")
    hisat2_error = log_path0 / "hisat2_error.log"
    hisat2_error.write_text("test for error!!", encoding="utf-8")
    return log_path0, log_path1


@pytest.fixture
def fastp_json_path(tmp_path, content=fastp_json_content):
    names = [f"sample{i+1}.json" for i in range(100)]
    log_path1 = tmp_path / "fastp_json1"
    log_path1.mkdir(parents=True, exist_ok=True)
    for name in names:
        log = log_path1 / name
        log.write_text(content, encoding="utf-8")

    log_path0 = tmp_path / "fastp_json0"
    log_path0.mkdir(parents=True, exist_ok=True)
    for name in names:
        log = log_path0 / name
        log.write_text(content, encoding="utf-8")
    hisat2_error = log_path0 / "fastp_json_error.json"
    hisat2_error.write_text("test for error!!", encoding="utf-8")
    return log_path0, log_path1


def test_extract_hisat2_metrics_success(hisat2_log_path):
    log_path = hisat2_log_path[1] / "sample1.log"
    metrics = utils.extract_hisat2_metrics(log_path)
    assert metrics["total_reads"] == 29665966
    assert metrics["mapped_reads"] == 29038579
    assert metrics["unique_mapping"] == 15092679


def test_extract_hisat2_metrics_missing_pattern(hisat2_log_path, caplog):
    log_path = hisat2_log_path[0] / "hisat2_error.log"
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError):
            utils.extract_hisat2_metrics(log_path)
    assert "Error extracting HISAT2 metrics" in caplog.text


@pytest.mark.parametrize("numerator,denominator,expected", [
    (50, 100, "50.00%"),
    (0, 100, "0.00%"),
    (1, 3, "33.33%"),
    (0, 0, "0.00%"),
])
def test_format_rate(numerator, denominator, expected):
    assert utils.format_rate(numerator, denominator) == expected


def test_align_report(hisat2_log_path):
    status, df, failed_logs = utils.align_report(hisat2_log_path[1])
    assert status is True
    assert not failed_logs
    assert not df.empty
    assert set(df["Sample"]) == set([
        name.stem for name in list(hisat2_log_path[1].glob("*.log"))])
    assert all(df["Mapped Rate"] == "97.89%")
    assert all(df["Unique Mapped Rate"] == "50.88%")
    assert all(df["Total Reads"] == 29665966)
    assert all(df["Reads Mapped"] == 29038579)
    assert all(df["Unique Mapped"] == 15092679)


def test_align_report_error_files(hisat2_log_path, caplog):
    with caplog.at_level("WARNING"):
        status, df, failed_logs = utils.align_report(hisat2_log_path[0])

    assert "Some logs failed to process" in caplog.text
    assert "Error extracting HISAT2 metrics from" in caplog.text
    assert status is False
    assert failed_logs == ["hisat2_error.log"]
    assert not df.empty
    assert set(df["Sample"]) == set([
        name.stem for name in list(hisat2_log_path[1].glob("*.log"))])
    assert all(df["Mapped Rate"] == "97.89%")
    assert all(df["Unique Mapped Rate"] == "50.88%")
    assert all(df["Total Reads"] == 29665966)
    assert all(df["Reads Mapped"] == 29038579)
    assert all(df["Unique Mapped"] == 15092679)


def test_align_report_no_logs(tmp_path):
    with pytest.raises(RuntimeError):
        utils.align_report(tmp_path)


def test_trim_report(fastp_json_path):
    status, df, failed_logs = utils.trim_report(fastp_json_path[1])
    assert status is True
    assert not failed_logs
    assert not df.empty
    assert set(df["Sample"]) == set([
        name.stem for name in list(fastp_json_path[1].glob("*.json"))])
    assert all(df["Total Reads"] == 30550358)
    assert all(df["After Filtering"] == 29665966)
    assert all(df["Pass Rate"] == "97.11%")
    assert all(df["GC Content"] == "0.52%")


def test_trim_report_error_files(fastp_json_path, caplog):
    with caplog.at_level("WARNING"):
        status, df, failed_logs = utils.trim_report(fastp_json_path[0])

    assert "Some fastp JSON files failed to process" in caplog.text
    assert "Error processing" in caplog.text
    assert status is False
    assert failed_logs == ["fastp_json_error.json"]
    assert not df.empty
    assert set(df["Sample"]) == set([
        name.stem for name in list(fastp_json_path[1].glob("*.json"))])
    assert all(df["Total Reads"] == 30550358)
    assert all(df["After Filtering"] == 29665966)
    assert all(df["Pass Rate"] == "97.11%")
    assert all(df["GC Content"] == "0.52%")


def test_trim_report_empty(tmp_path):
    with pytest.raises(RuntimeError):
        utils.trim_report(tmp_path)


def test_cleanup_directories(tmp_path, caplog):
    d1 = tmp_path / "dir1"
    d2 = tmp_path / "dir2"
    d1.mkdir()
    d2.mkdir()
    file1 = d1 / "file.txt"
    file1.write_text("test")
    utils.cleanup_directories([d1, d2])
    assert not d1.exists()
    assert not d2.exists()
    # Test non-existent directory
    with caplog.at_level("WARNING"):
        utils.cleanup_directories([d1])
    assert "Directory does not exist" in caplog.text


def test_dataframe_trans(dataframe_trans_data):
    df = pd.read_csv(dataframe_trans_data)
    df_t = utils.dataframe_t(df)
    df_t["SampleRealID"] = None
    df_long = utils.dataframe_wide2long(mpd.DataFrame(df_t), "Tpm")

    df_wide = utils.dataframe_long2wide(df_long._to_pandas())

    assert df_wide.shape == df.shape
    assert set(df_wide.columns.to_list()) == set(df.columns.to_list())
