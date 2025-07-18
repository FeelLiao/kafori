import os
import shutil
import pytest
from backend.analysis.upstream import UpstreamAnalysis

# 清理输出目录
def setup_function():
    if os.path.exists("tests/output"):
        shutil.rmtree("tests/output")

def test_upstream_success():
    analysis = TranscriptomeUpstreamAnalysis(
        input_path="tests/dummy_data/input",
        output_dir="tests/output",
        config={
            "snakefile": "tests/dummy_data/Snakefile",
            "configfile": "tests/dummy_data/config.yaml",
            "cores": 1
        }
    )
    analysis.run()

    # 检查输出目录是否创建
    assert os.path.exists("tests/output")

    # 检查日志文件是否存在
    assert os.path.exists("logs/project_analysis.log")

def test_input_path_error():
    with pytest.raises(FileNotFoundError):
        TranscriptomeUpstreamAnalysis(
            input_path="nonexistent_path",
            output_dir="tests/output",
            config={}
        )

def test_snakemake_fail(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            returncode = 1
            stderr = "Snakemake failed"
        return Result()
    
    from subprocess import run
    monkeypatch.setattr("subprocess.run", fake_run)

    analysis = TranscriptomeUpstreamAnalysis(
        input_path="tests/dummy_data/input",
        output_dir="tests/output",
        config={"snakefile": "tests/dummy_data/Snakefile"}
    )

    with pytest.raises(RuntimeError):
        analysis.run()


run_snakemake_workflow(
    snakefile_path=Path(
        "backend/dataAnalysis/rnaSeqUpstream/workflow/Snakefile"),
    config_path=Path("backend/dataAnalysis/rnaSeqUpstream/config/config.yaml"),
    work_dir=Path.cwd(),
    dryrun=True,
    ncores=4
)
            