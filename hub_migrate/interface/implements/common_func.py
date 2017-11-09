import datetime
import subprocess


class SqoopCommand(object):
    def __init__(self, json_str, sqoop_tool):
        """
        存储sqoop语句参数
        :param json_str: 类型为字典,键为sqoop-tool 参数,
        :param sqoop_tool: sqoop语句类型
        """
        self.conn = json_str["conn"]
        self.sqoop_tool = sqoop_tool
        self.conn["driver"] = "com.ibm.as400.access.AS400JDBCDriver"
        
        if self.sqoop_tool == "import":
            self.conn["hive-import"] = True
            # 处理table,原始数据为List,转换为String
            table_str = ""
            print(json_str["conn"]["table"])
            for table in json_str["conn"]["table"]:
                if table != "":
                    table_str += (str(table) + ',')
            self.conn["table"] = table_str[:-1]
    
    @property
    def get_sqoop_str_seq(self):
        """
        获取sqoop语句对应的程序参数序列(sequence of program arguments)
        """
        # print(sqoop_tool)
        if self.sqoop_tool == "import":
            self.conn["hive-import"] = True
        self.conn["driver"] = "com.ibm.as400.access.AS400JDBCDriver"
        sqoop_str_seq = ["/home/why/app/sqoop-1.4.6/bin/sqoop", self.sqoop_tool]
        sqoop_str_seq += ["--connect", "jdbc:as400://" + self.conn["host"] + "/" + self.conn["database"]]
        
        for key, value in self.conn.items():
            if key == "remarks":
                if value is not None:
                    pass
            elif key == "fields-terminated-by":
                sqoop_str_seq += (["--" + key, "'" + value + "'"])
            elif key not in ["connect", "host", "database", "table", "fields-terminated-by"]:
                if value is not True:
                    sqoop_str_seq += (["--" + key, value])
                else:
                    sqoop_str_seq += (["--" + key])
        # print(sqoop_str_seq)
        return sqoop_str_seq

    def conn_as400(self, test=True):
        """
        在终端执行输入的sqoop list-tables语句
        :param test: True表示test,False表示submit
        :return 返回as400指定数据库中的table
        """
        # 在后台执行sqoop命令
        print("正在查询数据库")
        as400_tables = subprocess.run(self.get_sqoop_str_seq,
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
                print("获取table成功")
                result_dict["stdout"] = str(as400_tables.stdout, encoding="utf-8").split()
                return result_dict


    def create_job(self, job):
        """
        创建sqoop 迁移Job
        :param job: 迁移Job对象
        :return:
        """
        stdout_str = []
        finished_table_temp = ""
        
        # 遍历table存储的表,依次迁移数据
        for table in self.conn["table"].split(','):
            print("开始迁移表{}".format(table))
            # 开始进行迁移任务,将当前进行任务写入job.migrating_table
            job.migrating_table = table
            job.save()
            
            # 在后台执行sqoop命令,进行数据迁移
            hive_import = subprocess.run(self.get_sqoop_str_seq + (["--table", table]),
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
            
            # 迁移任务进行失败时,更新job
            if hive_import.returncode != 0:
                job.status = "Failed"
                job.migrating_table = "failed"
                job.finished_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                print("表{}导入hive成功".format(table))
                
        # 当所有迁移任务完成时,更新Job
        job.status = "Finished"
        job.finished_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        job.migrating_table = ""
        job.save()
        print("所有迁移任务完成")
        # return stdout_str
