#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/14
# @Author : jiang.hu
# @File : bucket_param.py
import datetime

from ab_test.util.analytical_param import analytical_parameters
from common.mysql_util import MySqlDbUtil
from conf.config import MysqlConf, logger


class BucketParam(object):
    """
    查询bucket，返回对应参数
    """

    def __init__(self, db: MySqlDbUtil):
        self.db = db
        self.extra_type = "bucket_param_extra"

    def create_and_update_bucket_param(self, param_list):
        """
        创建桶bucket,存入数据库表
        :param param_list:待存入的参数列表
        """
        bucket_list = []
        for param in param_list:
            analytical_parameter_to_bp = analytical_parameters(param, self.extra_type)
            update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            analytical_parameter_to_bp.update({"update_time": update_time})
            bucket_list.append(analytical_parameter_to_bp)
        self.db.batch_insert("T_ABTEST_BUCKET_PARAMS", bucket_list)

    def get_bucket_param(self, bucket_id):
        """
        根据bucket_id查询对应的参数
        """
        sql = """
            SELECT name, value FROM T_ABTEST_BUCKET_PARAMS WHERE bucket_id=%s
        """
        sql = sql % bucket_id
        bucket_param_dic = {}
        try:
            cur = self.db.execute(sql)
            result = cur.fetchall()
            bucket_param_dic = {tup: value for tup, value in result}
        except Exception as e:
            logger.error("查询bucket参数失败：%s", e)

        return bucket_param_dic


if __name__ == '__main__':
    mysql_db1 = MySqlDbUtil(**MysqlConf.HADOOP_DB_DICT)
    bp = BucketParam(mysql_db1)
    bp.get_bucket_param(1)
