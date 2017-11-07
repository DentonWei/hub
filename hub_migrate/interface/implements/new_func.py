import datetime
import subprocess


def gen_sqoop_str_list(connect_dict, sqoop_tool):
    """
    根据传入字典生成sqoop_str_list,并返回
    """
    # print(sqoop_tool)
    if sqoop_tool == "import":
        connect_dict["hive-import"] = True
    connect_dict["driver"] = "com.ibm.as400.access.AS400JDBCDriver"
    sqoop_str_list = ["/home/why/app/sqoop-1.4.6/bin/sqoop", sqoop_tool]
    sqoop_str_list += ["--connect", "jdbc:as400://" + connect_dict["host"] + "/" + connect_dict["database"]]
    
    for key, value in connect_dict.items():
        if key == "remarks":
            if value is not None:
                pass
        # elif key == "num-mappers":
        #     sqoop_str_list += (["--" + key, "'" + value +"'"])
        elif key == "fields-terminated-by":
            sqoop_str_list += (["--" + key, "'" + value +"'"])
        elif key not in ["connect", "host", "database", "table", "fields-terminated-by"]:
            if value is not True:
                sqoop_str_list += (["--" + key, value])
            else:
                sqoop_str_list += (["--" + key])
    # print(sqoop_str_list)
    return sqoop_str_list


def analyse_dict(sqoop_str_list, test=True):
    """
    在终端执行输入的sqoop语句,进行历史数据迁移
    :param test: True表示test,False表示submit
    :return 返回终端的output
    """
    # 在后台执行sqoop命令
    print("正在查询数据库")
    as400_tables = subprocess.run(sqoop_str_list,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    result_dict = {}
    # 当连接不成功时,返回后台错误代码
    if as400_tables.stderr is not None and as400_tables.stdout is None:
        print("连接错误")
        result_dict["errors"] = str(as400_tables.stderr, encoding="utf-8")
        return result_dict
    else:
        # 测试成功时,返回{"success": 1}
        if test:
            print("连接as400成功")
            result_dict["success"] = 1
            return result_dict
        # 当提交成功时,返回查询获得的数据库表名
        else:
            result_dict["stdout"] = str(as400_tables.stdout, encoding="utf-8").split()
            return result_dict


def create_job(connect_dict, sqoop_tool, job):
    # 生成sqoop语句 sqoop_str_list, 不包含 --table
    sqoop_str_list = gen_sqoop_str_list(connect_dict, sqoop_tool)
    stdout_str = []
    finished_table_temp = ""
    # print(connect_dict["table"][:-1])
    # 遍历table存储的表,依次迁移数据
    for table in connect_dict["table"][:-1].split(','):
        print(sqoop_str_list + (["--table", table]))
        # 开始进行迁移任务,将当前进行任务写入job.migrating
        job.migrating_table = table
        job.save()
        # 在后台执行sqoop命令,进行数据迁移
        hive_import = subprocess.run(sqoop_str_list + (["--table", table]),
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        # 迁移任务进行失败时,更新job状态为3
        if hive_import.returncode != 0:
            job.status = 3
            job.migrating_table = "failed"
            job.finished_time = datetime.datetime.now()
            job.save()
            print(str(hive_import.stderr, encoding="utf-8"))
            print("表{}导入hive失败".format(table))
            return 0
        # 单个迁移任务完成时,将完成任务表名写入数据库
        else:
            stdout_str += str(hive_import.stdout, encoding="utf-8")
            finished_table_temp += (table + ",")
            job.finished_table = finished_table_temp[:-1]
            job.save()
            print(job.finished_table)
            print("表{}导入hive成功".format(table))
    # 当所有迁移任务完成时,更新Job状态为4
    job.status = 4
    job.finished_time = datetime.datetime.now()
    job.migrating_table = ""
    job.save()
    return stdout_str
