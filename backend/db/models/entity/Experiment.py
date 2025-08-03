from tortoise.models import Model
from tortoise import fields

class Experiment(Model):
    """实验"""
    UniqueEXID = fields.CharField(
        primary_key=True,
        max_length=100,
        source_field="unique_ex_id",
        description="实验唯一编号"
    )
    ExpClass = fields.CharField(
        max_length=100,
        source_field="exp_class",
        description="实验类别"
    )
    Experiment = fields.CharField(
        max_length=255,
        source_field="experiment",
        description="样本所属实验"
    )

    class Meta:
        table = "experiment"
        unique_together = (("ExpClass", "Experiment"),)  # 等价于 uk_exp