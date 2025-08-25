# import pytest
# from pathlib import Path
# from backend.analysis.upstream import UpstreamAnalysis
#
# test_path = Path("tests/upstream")
#
#
# @pytest.fixture
# def valid_paths():
#     snakefile = Path("backend/analysis/workflow/Snakefile")
#     work_dir = test_path
#     sample_sheet = test_path / "sample_sheet.csv"
#     genome = Path("tests/upstream/ref/Saccharomyces_cerevisiae.fa")
#     annotation = Path(
#         "tests/upstream/ref/Saccharomyces_cerevisiae.gtf")
#     return snakefile, work_dir, sample_sheet, genome, annotation
#
#
# def test_init_and_config_update(valid_paths):
#     snakefile, work_dir, sample_sheet, genome, annotation = valid_paths
#     analysis = UpstreamAnalysis(
#         snakefile, work_dir, sample_sheet, genome, annotation)
#     assert analysis.snakefile_path == snakefile
#     assert analysis.work_dir == work_dir
#     assert analysis.sample == sample_sheet
#     assert analysis.genome == genome
#     assert analysis.annotation == annotation
#     assert analysis.config["samples"] == sample_sheet.absolute()
#     assert analysis.config["ref"]["genome"] == genome.absolute()
#     assert analysis.config["ref"]["annotation"] == annotation.absolute()
#
#
# @pytest.mark.parametrize("missing", ["snakefile", "work_dir", "sample_sheet", "genome", "annotation"])
# def test_check_paths_missing(tmp_path, missing):
#     snakefile = tmp_path / "Snakefile"
#     work_dir = tmp_path / "work"
#     sample_sheet = tmp_path / "samples.csv"
#     genome = tmp_path / "genome.fa"
#     annotation = tmp_path / "annotation.gtf"
#     # Only create all except one
#     if missing != "snakefile":
#         snakefile.write_text("rule all: input: []")
#     if missing != "work_dir":
#         work_dir.mkdir()
#     if missing != "sample_sheet":
#         sample_sheet.write_text("sample_id")
#     if missing != "genome":
#         genome.write_text(">chr1\nATGC")
#     if missing != "annotation":
#         annotation.write_text("gene_id")
#     kwargs = {
#         "snakefile_path": snakefile,
#         "work_dir": work_dir,
#         "sample_sheet": sample_sheet,
#         "genome": genome,
#         "annotation": annotation
#     }
#     if missing == "work_dir":
#         # Should create work_dir if missing
#         analysis = UpstreamAnalysis(**kwargs)
#         assert analysis.work_dir.exists()
#     else:
#         with pytest.raises(FileNotFoundError):
#             UpstreamAnalysis(**kwargs)
#
#
# def test_run_analysis_success(valid_paths):
#     snakefile, work_dir, sample_sheet, genome, annotation = valid_paths
#     analysis = UpstreamAnalysis(
#         snakefile, work_dir, sample_sheet, genome, annotation)
#
#     result = analysis.run_analysis(dryrun=True, ncores=2, verbose=False)
#     assert result is True
