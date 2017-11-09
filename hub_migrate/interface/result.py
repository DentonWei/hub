import json
import os

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from lxml import etree
from pyspark.sql import SparkSession

from hub_migrate.models import Job

DATADETAIL = None
DATACOLUMNS = None
PAGETEMP = None
PAGE = None

# 获取hive默认路径
HIVE_HOME = os.getenv("HIVE_HOME")


@csrf_exempt
def init_result(request):
    """
    初始化result.html页面显示,
    :return: hive数据库路径,以及该Job迁移的所有table
    """
    # 获取Job中的所有table
    job = Job.objects.get(pk=int(request.body.decode("utf-8")))
    tables = job.sqoopsentence.table
    table_list = tables.split(',')

    database = job.sqoopsentence.hive_database
    # 获取hive配置文件路径
    hive_conf = os.path.join(HIVE_HOME, "conf/hive-site.xml")
    # 生成hive配置文件的解析器,并解析文件
    parser = etree.XMLParser()
    xml = etree.parse(hive_conf, parser)
    parse_str = "/configuration/property[name='hive.metastore.warehouse.dir']/value"
    hive_database_dir = xml.xpath(parse_str)[0].text + "/" + database + ".db"
    
    return JsonResponse({"tables": table_list,
                         "hive_path": hive_database_dir})


@csrf_exempt
def get_table_info(request):
    # initialize parameter
    global DATADETAIL, PAGETEMP, PAGE, DATACOLUMNS

    # print(request.POST)
    jsonTemp = json.loads(request.body.decode("utf-8"))
    id = jsonTemp["id"]
    tableName = jsonTemp["tableName"]
    dataColumnNameList = []
    dataDetailDicList = []

    # 获取请求Job对象
    job = Job.objects.get(pk=id)

    if tableName:
        # get hive database name
        dataBaseName = job.sqoopsentence.hive_database

        # set spark configuration
        spark = SparkSession.builder \
            .appName("getHiveData") \
            .master("local") \
            .config("spark.some.cofig.option", "some-value") \
            .enableHiveSupport() \
            .getOrCreate()

        # set hive database
        spark.sql("use " + "default")

        # get the table data
        dataFrame = spark.table(tableName)
        DATACOLUMNS = dataFrame.columns
        dataColumnNameList = DATACOLUMNS
        dataDetail = dataFrame.select('*').collect()

        # initialize global parameter
        DATADETAIL = [dataTemp.asDict() for dataTemp in dataDetail]
        PAGETEMP = Paginator(DATADETAIL, 20)

        # return data
        PAGE = 1
        dataDetailDicList = PAGETEMP.page(PAGE).object_list

    # return column name, first 20 rows data and table list of the job
    a = {"success": 1, "column": dataColumnNameList, "dataList": dataDetailDicList}

    return JsonResponse(a)


@csrf_exempt
def get_nextPage_info(request):
    global DATADETAIL, PAGETEMP, PAGE

    if PAGETEMP.page(PAGE).has_next() == True:
        PAGE += 1
    else:
        PAGE = PAGETEMP.num_pages

    dataDetailDicList = PAGETEMP.page(PAGE).object_list
    dataColumnNameList = DATACOLUMNS

    a = {"column": dataColumnNameList, "dataList": dataDetailDicList}

    return JsonResponse(a)


@csrf_exempt
def get_previousPage_info(request):
    global DATADETAIL, PAGETEMP, PAGE

    if PAGETEMP.page(PAGE).has_previous() == True:
        PAGE -= 1
    else:
        PAGE = 1

    dataDetailDicList = PAGETEMP.page(PAGE).object_list
    dataColumnNameList = DATACOLUMNS

    a = {"column": dataColumnNameList, "dataList": dataDetailDicList}

    return JsonResponse(a)
