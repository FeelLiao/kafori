import pandas as pd
from backend.db.models.entity.ExpClass import ExpClass
from backend.db.models.entity.Experiment import Experiment  # tortoise 模型
from backend.db.models.entity.Sample import Sample
from backend.db.models.entity.GeneExpressTpm import GeneExpressTpm
from backend.db.models.entity.GeneExpressCounts import GeneExpressCounts


class Utils:
    @staticmethod
    def to_exp_class(data: pd.DataFrame) -> list[ExpClass]:
        #  DataFrame → Model 列表
        return [
            ExpClass(**row)
            for row in data.to_dict('records')
        ]

    @staticmethod
    def to_experiment(data: pd.DataFrame) -> list[Experiment]:
        #  DataFrame → Model 列表
        return [
            Experiment(**row)
            for row in data.to_dict('records')
        ]

    @staticmethod
    def to_sample(data: pd.DataFrame) -> list[Sample]:
        #  DataFrame → Model 列表
        return [
            Sample(**row)
            for row in data.to_dict('records')
        ]

    @staticmethod
    def to_gene_tpm(data: pd.DataFrame) -> list[GeneExpressTpm]:
        #  DataFrame → Model 列表
        return [
            GeneExpressTpm(**row)
            for row in data.to_dict('records')
        ]

    @staticmethod
    def to_gene_counts(data: pd.DataFrame) -> list[GeneExpressCounts]:
        #  DataFrame → Model 列表
        return [
            GeneExpressCounts(**row)
            for row in data.to_dict('records')
        ]
