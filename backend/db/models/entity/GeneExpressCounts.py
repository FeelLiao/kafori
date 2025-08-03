from tortoise.models import Model
from tortoise import fields


class GeneExpressCounts(Model):
    UniqueID = fields.CharField(primary_key=True, max_length=100, source_field="unique_id")
    SampleID = fields.CharField(max_length=255, source_field="sample_id")
    GeneID   = fields.CharField(max_length=10,  source_field="gene_id")
    Counts   = fields.IntField(source_field="counts")

    class Meta:
        table = "gene_express_counts"
        indexes = [("SampleID",)]