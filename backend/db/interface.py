from abc import ABC
from dataclasses import dataclass
from datetime import date
from typing import List, Tuple, Dict
import pandas as pd

from backend.db.repositories.impl.ExpClassRepositoryImpl import ExpClassRepositoryImpl
from backend.db.repositories.impl.ExperimentRepositoryImpl import ExperimentRepositoryImpl
from backend.db.repositories.impl.SampleRepositoryImpl import SampleRepositoryImpl
from backend.db.repositories.impl.GeneExpressTpmRepositoryImpl import GeneExpressTpmRepositoryImpl
from backend.db.repositories.impl.GeneExpressCountsRepositoryImpl import GeneExpressCountsRepositoryImpl


class DataBase:
    """统一入口，所有表的操作封装在这里"""

    def __init__(self):
        self.exp_class = ExpClassRepositoryImpl()
        self.experiment = ExperimentRepositoryImpl()
        self.sample = SampleRepositoryImpl()
        self.gene_tpm = GeneExpressTpmRepositoryImpl()
        self.gene_counts = GeneExpressCountsRepositoryImpl()


db = DataBase()


@dataclass
class CollectionDate:
    starttime: date
    endtime: date


class GetDataBaseInterface(ABC):
    """
    Database interface for all get repository operations.
    """

    @staticmethod
    async def get_exp_class() -> pd.DataFrame:
        """
        Get experimental class data.

        Returns:
            pd.DataFrame: containing all experimental class data. The DataFrame should have the following columns:
                ExpClass: Unique identifier for the experimental class.
                ExperimentCategory: Name of the experimental class.
        """
        data = await db.exp_class.getExpClass()
        return pd.DataFrame(data)

    @staticmethod
    async def get_experiment(exp_class: tuple) -> pd.DataFrame:
        """
        Get experiment data for a specific experimental class.

        Args:
            exp_class (tuple): A tuple of experimental class identifiers.

        Returns:
            pd.DataFrame: containing all experiment data for the specified experimental class. 
            The DataFrame should have the following columns:
                UniqueEXID: Unique identifier for the experiment.
                ExpClass: Experimental class identifier.
                Experiment: Name of the experiment.
        """
        data = []
        for exp in exp_class:
            data += await db.experiment.model.filter(ExpClass=exp).values()
        return pd.DataFrame(data)

    @staticmethod
    async def get_sample(unique_ex_id: tuple[str],
                         collection_time: CollectionDate = None,
                         collection_part: tuple[str] = None) -> pd.DataFrame:
        """
        Get sample data for a specific filter. `unique_ex_id` is required and should be first implemented,
        while `collection_time` and `collection_part` are optional and should be further discussed.

        Args:
            unique_ex_id (tuple): A tuple of unique experiment identifiers.
            collection_time (CollectionDate, optional): A CollectionDate object with starttime and endtime attributes.
                Defaults to None.
            collection_part (tuple, optional): A tuple of collection parts. Defaults to None.

        Returns:
            pd.DataFrame: containing all sample data for the specified experiment.
            The DataFrame should have the following columns:
                UniqueID: Unique identifier for the sample.
                SampleID: Name of the sample.
                SampleAge: Age of the sample.
                SampleDetail: Additional details about the sample.
                CollectionTime: Time when the sample was collected.
                DepositDatabase: Database where the sample is stored.
                Accession: Accession number for the sample.
                Origin: Origin of the sample.
        """

        res = await db.sample.get_sample_by_unique_ex_id_and_part_time(unique_ex_id=unique_ex_id, collection_part=collection_part, start_time=collection_time.starttime, end_time=collection_time.endtime)
        return pd.DataFrame(res)

    @staticmethod
    async def get_gene_tpm(gene_id: tuple[str], unique_id: tuple[str]) -> pd.DataFrame:
        """
        Get gene expression data in TPM (Transcripts Per Million) format. This method should implement the filtering
        based on `gene_id` and `unique_id`.
        Args:
            gene_id (tuple[str]): A tuple of gene identifiers.
            unique_id (tuple[str]): A tuple of unique sample identifiers.
        Returns:
            pd.DataFrame: containing gene expression data in TPM format.
            The DataFrame should have the following columns:
                UniqueID: Unique identifier for the sample.
                SampleID: Name of the sample.
                GeneID: Name of the gene.
                GeneTPM: Expression level of the gene in TPM.
        """
        data = await db.gene_tpm.model.filter(SampleID__in=unique_id, GeneID__in=gene_id).values()
        return pd.DataFrame(data)

    @staticmethod
    async def get_gene_counts(gene_id: tuple[str], unique_id: tuple[str]) -> pd.DataFrame:
        """
        Get gene expression data in counts format. This method should implement the filtering
        based on `gene_id` and `unique_id`.

        Args:
            gene_id (tuple[str]): A tuple of gene identifiers.
            unique_id (tuple[str]): A tuple of unique sample identifiers.

        Returns:
            pd.DataFrame: containing gene expression data in counts format.
            The DataFrame should have the following columns:
                UniqueID: Unique identifier for the sample.
                SampleID: Name of the sample.
                GeneID: Name of the gene.
                GeneCounts: Expression level of the gene in counts.
        """
        data = await db.gene_counts.model.filter(SampleID__in=unique_id, GeneID__in=gene_id).values()
        return pd.DataFrame(data)


class PutDataBaseInterface(ABC):
    """
    Database interface for all put repository operations.
    """

    @staticmethod
    def put_exp_class(data: pd.DataFrame) -> bool:
        """
        Insert experimental class data into the database.

        Args:
            data (pd.DataFrame): DataFrame containing experimental class data.
            The DataFrame should have the following columns:
                ExpClass: Unique identifier for the experimental class.
                ExperimentCategory: Name of the experimental class.
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        pass

    @staticmethod
    def put_experiment(data: pd.DataFrame) -> bool:
        """
        Insert experiment data into the database.

        Args:
            data (pd.DataFrame): DataFrame containing experiment data. 
            The DataFrame should have the following columns:
                UniqueEXID: Unique identifier for the experiment.
                ExpClass: Experimental class identifier.
                Experiment: Name of the experiment.
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        pass

    @staticmethod
    def put_sample(data: pd.DataFrame) -> bool:
        """
        Insert sample data into the database.

        Args:
            data (pd.DataFrame): DataFrame containing sample data.
            The DataFrame should have the following columns:
                UniqueID: Unique identifier for the sample.
                SampleID: Name of the sample.
                SampleAge: Age of the sample.
                SampleDetail: Additional details about the sample.
                CollectionTime: Time when the sample was collected.
                DepositDatabase: Database where the sample is stored.
                Accession: Accession number for the sample.
                Origin: Origin of the sample.
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        pass

    @staticmethod
    def put_gene_tpm(data: pd.DataFrame) -> bool:
        """
        Insert gene expression data in TPM (Transcripts Per Million) format into the database.

        Args:
            data (pd.DataFrame): DataFrame containing gene expression data in TPM format.
            The DataFrame should have the following columns:
                UniqueID: Unique identifier for the sample.
                SampleID: Name of the sample.
                GeneID: Name of the gene.
                GeneTPM: Expression level of the gene in TPM.
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        pass

    @staticmethod
    def put_gene_counts(data: pd.DataFrame) -> bool:
        """
        Insert gene expression data in counts format into the database.

        Args:
            data (pd.DataFrame): DataFrame containing gene expression data in counts format.
            The DataFrame should have the following columns:
                UniqueID: Unique identifier for the sample.
                SampleID: Name of the sample.
                GeneID: Name of the gene.
                GeneCounts: Expression level of the gene in counts.
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        pass

    @staticmethod
    def exclass_processing(
            exclass: list[dict[str, str]]) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Process experimental class data for database insertion. This method should convert a list of dictionaries

        Args:
            exclass (list[dict[str, str]]): List of dictionaries containing experimental class data.
                Each dictionary should have the keys 'ExpClass' and 'ExperimentCategory'.

        Returns:
            Tuple[bool, List[Dict[str, str]]]: A tuple where the first element is a boolean indicating
            whether the experiment category already exists in the database, True for new (direct insertion)
            and False for existing (the database do not need to be inserted again),
            and the second element is a list of dictionaries with processed experimental class data.
            Each dictionary should have the keys 'ExpClass' and 'ExperimentCategory'.
        """
        pass
