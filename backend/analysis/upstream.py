from pathlib import Path
import pandas as pd

from snakemake.api import (
    OutputSettings,
    ResourceSettings,
    SnakemakeApi,
    StorageSettings,
    ConfigSettings,
    DeploymentSettings
)

from snakemake_interface_executor_plugins.settings import DeploymentMethod
from data_analysis import DataAnalysis


class UpstreamAnalysis(DataAnalysis):
    def __init__(self, snakefile_path: Path,
                 config_path: Path,
                 work_dir: Path,
                 sample: Path) -> None:
        
        self.snakefile_path = snakefile_path
        self.config_path = config_path
        self.work_dir = work_dir
        self.sample = sample

    def sample_file(self) -> Path:
        """
        Transform the sample file to a format suitable for the analysis.
        """
        
        sample_df = pd.read_excel(self.sample, sheet_name=["SampleInfo"], 
                                  header=None)
        

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
        config_settings = ConfigSettings(configfiles=[self.config_path])
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
            self.log(f"Upstream analysis failed: {e}")
            return False

        return True
