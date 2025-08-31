from tortoise.models import Model
from tortoise import fields


class GeneExpressTpm(Model):
    UniqueID = fields.CharField(primary_key=True, max_length=100, source_field="unique_id")
    SampleID = fields.CharField(max_length=255, source_field="sample_id")
    SampleRealID = fields.CharField(max_length=255, source_field="sample_real_id")
    GeneID = fields.CharField(max_length=10, source_field="gene_id")
    Tpm = fields.FloatField(source_field="tpm")

    class Meta:
        table = "gene_express_tpm"

        indexes = [
            ("SampleID","SampleRealID")
        ]