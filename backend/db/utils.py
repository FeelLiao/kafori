import pandas as pd
from backend.db.models.entity.Experiment import Experiment  # tortoise 模型
from backend.db.models.entity.Sample import Sample
from backend.db.models.entity.GeneExpressTpm import GeneExpressTpm
from backend.db.models.entity.GeneExpressCounts import GeneExpressCounts


class Utils:
    @staticmethod
    def to_experiment(data: pd.DataFrame) -> Experiment:
        #  DataFrame → Model 列表
        result = [
            Experiment(
                UniqueEXID=row['UniqueEXID'],
                ExpClass=row['ExpClass'],
                Experiment=row['Experiment'],
            )
            for _, row in data.iterrows()
        ]
        return result

    @staticmethod
    def to_sample(data: pd.DataFrame) -> Sample:
        #  DataFrame → Model 列表
        result = [
            Sample(
                SampleID=row['SampleID'],
                CollectionTime=row['CollectionTime'],
                SampleAge=row['SampleAge'],
                CollectionPart=row['CollectionPart'],
                SampleDetail=row['SampleDetail'],
                DepositDatabase=row['DepositDatabase'],
                Accession=row['Accession'],
                Origin=row['Origin'],
                UniqueID=row['UniqueID'],
                UniqueEXID=row['UniqueEXID'],
                FileName=row['FileName'],
                Sample=row['Sample']
            )
            for _, row in data.iterrows()
        ]
        return result

    @staticmethod
    def to_gene_tpm(data: pd.DataFrame) -> GeneExpressTpm:
        #  DataFrame → Model 列表
        result = [
            GeneExpressTpm(
                UniqueID=row['UniqueID'],
                SampleID=row['SampleID'],
                GeneID=row['GeneID'],
                Tpm=row['Tpm']
            )
            for _, row in data.iterrows()
        ]
        return result

    @staticmethod
    def to_gene_counts(data: pd.DataFrame) -> GeneExpressCounts:
        #  DataFrame → Model 列表
        result = [
            GeneExpressCounts(
                UniqueID=row['UniqueID'],
                SampleID=row['SampleID'],
                GeneID=row['GeneID'],
                Counts=row['Counts']
            )
            for _, row in data.iterrows()
        ]
        return result
