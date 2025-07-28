from pathlib import Path
import copy

from snakemake.api import (
    OutputSettings,
    ResourceSettings,
    SnakemakeApi,
    StorageSettings,
    ConfigSettings,
    DeploymentSettings
)

from snakemake_interface_executor_plugins.settings import DeploymentMethod
from backend.analysis.analysis_base import DataAnalysis


class UpstreamAnalysis(DataAnalysis):
    """Class for performing upstream analysis in RNA-Seq data processing.
    This class is responsible for configuring and running the upstream analysis
    workflow using Snakemake.
    Attributes:
        snakefile_path (Path): Path to the Snakemake workflow file.
        work_dir (Path): Working directory for the analysis.
        sample (Path): Path to the sample sheet containing metadata for samples.
        genome (Path): Path to the reference genome file.
        annotation (Path): Path to the reference annotation file.
    """

    base_config = {
        "samples": "path/to/sample_sheet.csv",
        "ref": {
            "genome": "path/to/genome.fa",
            "annotation": "path/to/annotation.gtf"
        },
        "featureCounts": {
            "attribute_type": "gene_id",
            "feature_type": "exon"
        }
    }

    def __init__(self, snakefile_path: Path,
                 work_dir: Path,
                 sample_sheet: Path,
                 genome: Path,
                 annotation: Path) -> None:

        self.snakefile_path = snakefile_path
        self.work_dir = work_dir
        self.sample = sample_sheet
        self.genome = genome
        self.annotation = annotation

        self.config = copy.deepcopy(self.base_config)
        self.__update_config()
        self.__check_paths()

    def __check_paths(self) -> None:
        """
        Check if the provided paths for sample, genome, and annotation exist.
        Raises:
            FileNotFoundError: If any of the paths do not exist.
        """
        if not self.snakefile_path.exists():
            raise FileNotFoundError(
                f"Snakefile not found: {self.snakefile_path}")
        if not self.work_dir.exists():
            Path.mkdir(self.work_dir, parents=False, exist_ok=False)
        if not self.sample.exists():
            raise FileNotFoundError(f"Sample sheet not found: {self.sample}")
        if not self.genome.exists():
            raise FileNotFoundError(f"Genome file not found: {self.genome}")
        if not self.annotation.exists():
            raise FileNotFoundError(
                f"Annotation file not found: {self.annotation}")

    def __update_config(self) -> None:
        """
        Update the configuration according to instance property.
        """
        self.config["samples"] = self.sample
        self.config["ref"]["genome"] = self.genome
        self.config["ref"]["annotation"] = self.annotation

    def run_analysis(self,
                     dryrun: bool = True,
                     ncores: int = 1,
                     verbose: bool = False) -> bool:

        output_settings = OutputSettings(
            verbose=verbose,
            show_failed_logs=True,
            dryrun=dryrun,
            stdout=dryrun)

        deployment_method = set()
        deployment_method.add(DeploymentMethod.CONDA)

        storage_settings = StorageSettings()
        resource_settings = ResourceSettings(cores=ncores)
        config_settings = ConfigSettings(config=self.config)
        deployment_settings = DeploymentSettings(
            deployment_method=deployment_method,
        )

        if dryrun:
            executor_mode = "dryrun"
        else:
            executor_mode = "local"

        try:
            with SnakemakeApi(output_settings) as snakemake_api:
                workflow = snakemake_api.workflow(
                    storage_settings=storage_settings,
                    deployment_settings=deployment_settings,
                    resource_settings=resource_settings,
                    config_settings=config_settings,
                    snakefile=self.snakefile_path,
                    workdir=self.work_dir
                )
                workflow.dag().execute_workflow(executor=executor_mode)

        except Exception as e:
            print(f"Upstream analysis failed: {e}")
            return False

        return True

    def post_process(self) -> None:
        """
        Post-process the results of the upstream analysis.
        """
        
