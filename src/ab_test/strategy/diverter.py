#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/14
# @Author : jiang.hu
# @File : diverter.py
import datetime

from ab_test.util.analytical_param import analytical_parameters
from common.mysql_util import MySqlDbUtil
from conf.config import MysqlConf, logger


class Diverted(object):
    """
    分流器类型
    """

    def __init__(self, db: MySqlDbUtil):
        self.db = db
        self.extra_type = "diver_extra"
        # self.create_diver()

    def create_diver(self, param_list):
        """
        创建分流器
        系统初始化时执行
        """
        data_list = []
        for param in param_list:
            analytical_parameter_to_cd = analytical_parameters(param, self.extra_type)
            update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            analytical_parameter_to_cd.update({"update_time": update_time})
            data_list.append(analytical_parameter_to_cd)
        self.db.batch_insert("T_ABTEST_DIVERSION", data_list)

    def get_diver_id_by_name(self, name):
        """
        通过分流器名字返回分流器id
        """
        sql = """
            SELECT id FROM T_ABTEST_DIVERSION WHERE name='%s'
        """
        sql = sql % str(name)
        diver_id = ''
        try:
            cur = self.db.execute(sql)
            id_result = cur.fetchall()
            if id_result:
                diver_id = id_result[0][0]
        except Exception as e:
            logger.error("查询分流器id失败：%s", e)

        return diver_id

    def user_diver(self):
        pass


if __name__ == '__main__':
    para = [{"name": "白名单分流", "is_deleted": 0}, {"name": "用户信息分流", "is_deleted": 0}]
    mysql_db = MySqlDbUtil(**MysqlConf.HADOOP_DB_DICT)
    mysql_db.connect()
    dd = Diverted(mysql_db)
    dd.create_diver(para)
    driver_id_list = dd.get_diver_id_by_name("白名单分流")
    print(driver_id_list)
