from tortoise.models import Model
from tortoise import fields


class GeneExpress(Model):
    # Python 里字段名 = 你要在代码里访问/创建/过滤用的名字
    # source_field = 数据库真实列名（已经存在的表：unique_id, sample_id, tpm_blob, counts_blob）
    UniqueID = fields.CharField(
        primary_key=True,
        max_length=100,
        source_field="unique_id",
        description="sample 的 unique_id"
    )
    SampleID = fields.CharField(
        max_length=100,
        source_field="sample_id"
    )
    TPMBlob = fields.BinaryField(
        null=True,
        source_field="tpm_blob",
        description="TPM MediumBLOB"
    )
    CountsBlob = fields.BinaryField(
        null=True,
        source_field="counts_blob",
        description="Counts MediumBLOB"
    )

    class Meta:
        table = "gene_express"   # 与你现有表一致
        # 可选：添加索引
        # indexes = ("SampleID",)