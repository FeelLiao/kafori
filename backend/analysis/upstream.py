from pathlib import Path
import copy
import logging
import pandas as pd
from typing import Dict, List, Any
import io
import contextlib

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
from backend.api.utils import align_report, trim_report, cleanup_directories

logger = logging.getLogger(__name__)


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
        self.config["samples"] = self.sample.absolute()
        self.config["ref"]["genome"] = self.genome.absolute()
        self.config["ref"]["annotation"] = self.annotation.absolute()
        logger.info(f"Config updated: {self.config}")

    # Sankemake workflow execution log can be captured by the SankemakeApi
    def run_analysis(self,
                     dryrun: bool = True,
                     ncores: int = 1,
                     verbose: bool = False) -> bool:
        """
        Run the upstream analysis workflow using Snakemake.
        The workflow running log will be captured by the default logger through
        `contextlib.redirect_stdout`.
        Args:
            dryrun (bool): If True, perform a dry run without executing the workflow.
            ncores (int): Number of cores to use for the analysis.
            verbose (bool): If True, enable verbose logging.
        Returns:
            bool: True if the analysis was successful, False otherwise.
        Raises:
            RuntimeError: If there is an error during the analysis execution.
        """

        output_settings = OutputSettings(
            verbose=verbose,
            show_failed_logs=True,
            dryrun=dryrun,
            stdout=dryrun)

        deployment_method = set()
        deployment_method.add(DeploymentMethod.CONDA)

        storage_settings = StorageSettings()
        resource_settings = ResourceSettings(cores=ncores)
        config_settings = ConfigSettings(config=self.config,
                                         replace_workflow_config=True)
        deployment_settings = DeploymentSettings(
            deployment_method=deployment_method,
        )

        if dryrun:
            executor_mode = "dryrun"
        else:
            executor_mode = "local"

        run_status = True

        try:
            # Redirect stdout to a string buffer
            std_out_buffer = io.StringIO()
            with contextlib.redirect_stdout(std_out_buffer):
                with SnakemakeApi(output_settings) as snakemake_api:
                    workflow = snakemake_api.workflow(
                        storage_settings=storage_settings,
                        deployment_settings=deployment_settings,
                        resource_settings=resource_settings,
                        config_settings=config_settings,
                        snakefile=self.snakefile_path,
                        workdir=self.work_dir
                    )
                    logger.info("Running upstream workflow")
                    workflow.dag().execute_workflow(executor=executor_mode)

                # Log the output from the buffers
                logger.info("Snakemake execution output: \n" + std_out_buffer.getvalue())

        except Exception as e:
            logger.error(f"Upstream analysis failed: {e}", exc_info=True)
            run_status = False
            raise RuntimeError(
                f"Upstream analysis failed: {e}") from e

        return run_status

    def post_process(self, clean: bool = False) -> Dict[str, List[Any]]:
        """
        Post-process the results of the upstream analysis.
        Args:
            clean (bool): Whether to clean up the working directory after processing.
        Returns:
            Dict: A dictionary containing processed results,
            including quantification data, alignment reports, and fastp reports.
            The dictionary has the following structure:
            - "quantification": List containing TPM and counts DataFrames.
            - "align_report": List containing success status, alignment DataFrame,
              and list of failed HISAT2 logs.
            - "fastp_report": List containing success status, fastp DataFrame,
              and list of failed fastp logs.
        Raises:
            RuntimeError: If there is an error processing the reports.
        """
        output_dir = self.work_dir / "out"
        hisat2_log_dir = output_dir/"logs"/"hisat2_align"
        fastp_json_dir = output_dir/"reports"/"json"
        tpm = output_dir/"quantification"/"samples_merged_tpm.csv"
        counts = output_dir/"quantification"/"samples_merged_counts.csv"

        logger.info("Post-processing upstream analysis results")
        tpm_df = pd.read_csv(tpm)
        counts_df = pd.read_csv(counts)

        # Process HISAT2 alignment reports
        try:
            success_align, alignment_df, failed_his_logs = align_report(
                hisat2_log_dir)
            if not success_align:
                logger.warning(
                    "Not all alignment report processing success, Please check log for more information.")
            else:
                logger.info("Alignment report processed successfully.")
        except Exception as e:
            logger.error(f"Error processing alignment reports: {e}")
            success_align = False
            alignment_df = pd.DataFrame()
            failed_his_logs = []
            raise RuntimeError(
                f"Error processing alignment reports: {e}") from e
        # Process fastp reports
        try:
            success_fastp, fastp_df, failed_fastp_logs = trim_report(
                fastp_json_dir)
            if not success_fastp:
                logger.warning(
                    "Not all fastp report processing success, Please check log for more information.")
            else:
                logger.info("Fastp report processed successfully.")
        except Exception as e:
            logger.error(f"Error processing fastp reports: {e}")
            success_fastp = False
            fastp_df = pd.DataFrame()
            failed_fastp_logs = []
            raise RuntimeError(
                f"Error processing fastp reports: {e}") from e
        # Cleanup directories
        if clean:
            cleanup_directories(self.work_dir)

        return {"quantification": [tpm_df, counts_df],
                "align_report": [success_align, alignment_df, failed_his_logs],
                "fastp_report": [success_fastp, fastp_df, failed_fastp_logs]
                }
