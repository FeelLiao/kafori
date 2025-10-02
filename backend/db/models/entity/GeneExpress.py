from tortoise.models import Model
from tortoise import fields


class GeneExpress(Model):
    UniqueID = fields.CharField(primary_key=True, max_length=100, source_field="unique_id")
    SampleID = fields.CharField(max_length=100, source_field="sample_id")
    TPMBlob = fields.BinaryField(source_field="tpm_blob")
    CountsBlob = fields.BinaryField(source_field="counts_blob")

    class Meta:
        table = "gene_express"