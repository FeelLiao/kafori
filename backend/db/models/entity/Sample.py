from tortoise.models import Model
from tortoise import fields

class Sample(Model):
    """样本"""
    UniqueID = fields.CharField(
        primary_key=True,
        max_length=100,
        source_field="unique_id",
        description="唯一主键段1"
    )
    UniqueEXID = fields.CharField(
        max_length=100,
        unique=True,
        source_field="unique_ex_id",
        description="实验编号"
    )
    FileName = fields.CharField(max_length=255, null=True, source_field="filename")
    SampleID = fields.CharField(
        max_length=255,
        source_field="sample_id",
        description="样本 id"
    )
    Sample = fields.CharField(
        max_length=255,
        null=True,
        source_field="sample",
        description="由 sample_id 计算得到的样本名"
    )
    CollectionTime = fields.DateField(
        source_field="collection_time",
        description="采集时间"
    )
    SampleAge = fields.SmallIntField(
        null=True,
        source_field="sample_age",
        description="样本年龄"
    )
    CollectionPart = fields.CharField(
        max_length=100,
        source_field="collection_part",
        description="采集部位"
    )
    SampleDetail = fields.TextField(
        null=True,
        source_field="sample_detail"
    )
    DepositDatabase = fields.CharField(
        max_length=100,
        null=True,
        source_field="deposit_database"
    )
    Accession = fields.CharField(
        max_length=100,
        null=True,
        source_field="accession"
    )
    Origin = fields.CharField(
        max_length=100,
        null=True,
        source_field="origin"
    )
    created_at = fields.DatetimeField(
        auto_now_add=True,
        source_field="created_at"
    )
    updated_at = fields.DatetimeField(
        auto_now=True,
        source_field="updated_at"
    )

    class Meta:
        table = "sample"
        unique_together = (("UniqueID", "CollectionTime"),)   # 使用真实列名
        indexes = [
            ("UniqueEXID",),
            ("SampleID",),
            ("SampleID", "CollectionTime"),
            ("CollectionTime", "CollectionPart"),
            ("UniqueEXID", "CollectionTime"),
        ]