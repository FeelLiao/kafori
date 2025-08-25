from tortoise.models import Model
from tortoise import fields

class ExpClass(Model):
    """实验类别"""
    ExpClass = fields.CharField(primary_key=True, max_length=100, source_field="exp_class")
    ExperimentCategory = fields.CharField(max_length=255, unique=True, source_field="experiment_category")

    class Meta:
        table = "exp_class"
        indexes = [("ExperimentCategory",)]   # 等价于 idx_name