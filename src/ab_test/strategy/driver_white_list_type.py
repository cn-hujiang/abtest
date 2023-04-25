#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/15
# @Author : jiang.hu
# @File : driver_white_list_type.py
import datetime

from ab_test.util.analytical_param import analytical_parameters
from common.mysql_util import MySqlDbUtil
from conf.config import logger


class DiverWhiteListType(object):
    """
    白名单类型
    """

    def __init__(self, db: MySqlDbUtil):
        self.db = db
        self.extra_type = "white_list_type_extra"

    def create_white_list_type(self, param):
        """
        创建白名单类型
        """
        analytical_parameter_to_wlt = analytical_parameters(param, self.extra_type)
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        analytical_parameter_to_wlt.update({"update_time": update_time})
        self.db.batch_insert("T_ABTEST_WHITE_LIST_TYPE", [analytical_parameter_to_wlt])

    def get_white_list_type_id_by_name(self, name, param_id_info: dict):
        """
        通过白名单类型名称返回白名单类型id
        """
        sql = """
            SELECT id FROM T_ABTEST_WHITE_LIST_TYPE WHERE name='%s' 
        """
        sql = sql % name
        for k, v in param_id_info.items():
            sql += "and "
            sql += " %s=%s " % (k, v)
        white_list_type_id = ''
        try:
            cur = self.db.execute(sql)
            id_result = cur.fetchall()
            if id_result:
                white_list_type_id = id_result[0][0]
        except Exception as e:
            logger.error("查询白名单类型id失败：%s", e)

        return white_list_type_id


if __name__ == '__main__':
    pass
