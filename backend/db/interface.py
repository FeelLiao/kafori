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

    def get_gene_tpm(self, unique_ids: set[str], gene_names: set[str]) -> pd.DataFrame:
        """
        get gene expression tpm data and transform it to DataFrame
        Returns:
            DataFrame of gene expression tpm data
        """
        
        data = self.gene_tpm.model.filter(UniqueID=unique_ids,
                                          GeneID=gene_names).value()
        data_frame = pd.DataFrame(data)

        return


