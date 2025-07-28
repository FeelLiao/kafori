import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from backend.analysis.upstream import UpstreamAnalysis

test_path = Path("tests/upstream")


@pytest.fixture
def valid_paths():
    snakefile = Path("backend/analysis/workflow/Snakefile").absolute()
    work_dir = test_path.absolute()
    sample_sheet = (test_path / "sample_sheet.csv").absolute()
    genome = Path("tests/upstream/ref/Saccharomyces_cerevisiae.fa").absolute()
    annotation = Path("tests/upstream/ref/Saccharomyces_cerevisiae.gtf").absolute()
    return snakefile, work_dir, sample_sheet, genome, annotation


def test_init_and_config_update(valid_paths):
    snakefile, work_dir, sample_sheet, genome, annotation = valid_paths
    analysis = UpstreamAnalysis(
        snakefile, work_dir, sample_sheet, genome, annotation)
    assert analysis.snakefile_path == snakefile
    assert analysis.work_dir == work_dir
    assert analysis.sample == sample_sheet
    assert analysis.genome == genome
    assert analysis.annotation == annotation
    assert analysis.config["samples"] == sample_sheet
    assert analysis.config["ref"]["genome"] == genome
    assert analysis.config["ref"]["annotation"] == annotation


@pytest.mark.parametrize("missing", ["snakefile", "work_dir", "sample_sheet", "genome", "annotation"])
def test_check_paths_missing(tmp_path, missing):
    snakefile = tmp_path / "Snakefile"
    work_dir = tmp_path / "work"
    sample_sheet = tmp_path / "samples.csv"
    genome = tmp_path / "genome.fa"
    annotation = tmp_path / "annotation.gtf"
    # Only create all except one
    if missing != "snakefile":
        snakefile.write_text("rule all: input: []")
    if missing != "work_dir":
        work_dir.mkdir()
    if missing != "sample_sheet":
        sample_sheet.write_text("sample_id")
    if missing != "genome":
        genome.write_text(">chr1\nATGC")
    if missing != "annotation":
        annotation.write_text("gene_id")
    kwargs = {
        "snakefile_path": snakefile,
        "work_dir": work_dir,
        "sample_sheet": sample_sheet,
        "genome": genome,
        "annotation": annotation
    }
    if missing == "work_dir":
        # Should create work_dir if missing
        analysis = UpstreamAnalysis(**kwargs)
        assert work_dir.exists()
    else:
        with pytest.raises(FileNotFoundError):
            UpstreamAnalysis(**kwargs)


def test_run_analysis_success(valid_paths):
    snakefile, work_dir, sample_sheet, genome, annotation = valid_paths
    analysis = UpstreamAnalysis(
        snakefile, work_dir, sample_sheet, genome, annotation)

    result = analysis.run_analysis(dryrun=False , ncores=2, verbose=False)
    assert result is True


@patch("backend.analysis.upstream.SnakemakeApi")
def test_run_analysis_failure(mock_api, valid_paths):
    snakefile, work_dir, sample_sheet, genome, annotation = valid_paths
    analysis = UpstreamAnalysis(
        snakefile, work_dir, sample_sheet, genome, annotation)
    mock_api.return_value.__enter__.side_effect = Exception("API error")
    with pytest.raises(RuntimeError):
        analysis.run_analysis()


@patch("backend.analysis.upstream.align_report")
@patch("backend.analysis.upstream.trim_report")
@patch("backend.analysis.upstream.cleanup_directories")
def test_post_process_success(mock_cleanup, mock_trim, mock_align, valid_paths):
    snakefile, work_dir, sample_sheet, genome, annotation = valid_paths
    analysis = UpstreamAnalysis(
        snakefile, work_dir, sample_sheet, genome, annotation)
    mock_align.return_value = (True, "alignment_df", [])
    mock_trim.return_value = ("trim_df", [])
    analysis.post_process()
    mock_align.assert_called_once()
    mock_trim.assert_called_once()
    mock_cleanup.assert_called_once_with(work_dir)


@patch("backend.analysis.upstream.align_report")
@patch("backend.analysis.upstream.trim_report")
@patch("backend.analysis.upstream.cleanup_directories")
def test_post_process_failed_logs(mock_cleanup, mock_trim, mock_align, valid_paths, capsys):
    snakefile, work_dir, sample_sheet, genome, annotation = valid_paths
    analysis = UpstreamAnalysis(
        snakefile, work_dir, sample_sheet, genome, annotation)
    mock_align.return_value = (False, None, ["log1"])
    mock_trim.return_value = ("trim_df", ["trim_log1"])
    analysis.post_process()
    captured = capsys.readouterr()
    assert "Failed to process some HISAT2 logs: ['log1']" in captured.out
    assert "Failed to process some trimming logs: ['trim_log1']" in captured.out
    mock_cleanup.assert_called_once_with(work_dir)
