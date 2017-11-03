import uuid
from django.db import models


# sqoop语句模型,用于复制生成sqoop语句
class SqoopSentence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sqoop_tool = models.CharField(max_length=30, verbose_name="sqoop-tool")
    driver = models.CharField(max_length=100)
    host = models.CharField(max_length=100)
    database = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    table = models.CharField(max_length=200)
    hive_database = models.CharField(max_length=30, verbose_name="hive-database")
    fields_terminated_by = models.CharField(max_length=10, verbose_name="fields-terminated-by")
    hive_overwrite = models.BooleanField(verbose_name="hive-overwrite")
    num_mappers = models.IntegerField(verbose_name="num-mappers")
    remarks = models.CharField(max_length=200)
    

class Job(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    finished_time = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField()
    # 迁移类型: incremental,total
    type = models.CharField(max_length=30)
    migrating_table = models.CharField(max_length=30, verbose_name="migrating-table",
                                       default="", blank=True, null=True)
    finished_table = models.CharField(max_length=200, verbose_name="finished-table",
                                      default="", blank=True, null=True)
    sqoopsentence = models.ForeignKey(SqoopSentence, on_delete=models.CASCADE)
