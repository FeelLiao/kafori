from pathlib import Path
from snakemake.api import (
    OutputSettings,
    ResourceSettings,
    SnakemakeApi,
    StorageSettings,
    ConfigSettings
)


def run_snakemake_workflow(snakefile_path: Path,
                           config_path: Path,
                           work_dir: Path,
                           dry_run: bool = True,
                           ncores: int = 1):
    if dry_run:
        output_settings = OutputSettings(
            verbose=True,
            show_failed_logs=True,
            dry_run=True)
    else:
        output_settings = OutputSettings(
            verbose=True,
            show_failed_logs=True,
            dry_run=False)

    storage_settings = StorageSettings()
    resource_settings = ResourceSettings(cores=ncores)
    config_settings = ConfigSettings(configfiles=[config_path])
    with SnakemakeApi(output_settings) as snakemake_api:
        workflow = snakemake_api.workflow(
            storage_settings=storage_settings,
            resource_settings=resource_settings,
            config_settings=config_settings,
            snakefile=snakefile_path,
            workdir=work_dir
        )
        workflow.dag().execute_workflow(executor="local")
