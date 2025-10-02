import pandas as pd
import polars as pl
from backend.db.models.entity.ExpClass import ExpClass
from backend.db.models.entity.Experiment import Experiment  # tortoise 模型
from backend.db.models.entity.Sample import Sample
from backend.db.models.entity.GeneExpressTpm import GeneExpressTpm
from backend.db.models.entity.GeneExpressCounts import GeneExpressCounts
from backend.db.models.entity.GeneExpress import GeneExpress

from backend.db.models.dto.ExpClassDTO import ExpClassDTO


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

    @staticmethod
    def to_gene_express(data: pl.DataFrame) -> list[GeneExpress]:
        # 快速批量转换：Polars 内部一次性生成 list[dict]
        if data.is_empty():
            return []
        return [GeneExpress(**row) for row in data.to_dicts()]

    @staticmethod
    def quick_sort(arr: list[ExpClassDTO]) -> list[ExpClassDTO]:
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2].SampleCounts
        left = [x for x in arr if x.SampleCounts > pivot]
        middle = [x for x in arr if x.SampleCounts == pivot]
        right = [x for x in arr if x.SampleCounts < pivot]
        return Utils.quick_sort(left) + middle + Utils.quick_sort(right)

