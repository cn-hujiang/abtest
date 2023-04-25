#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/14
# @Author : jiang.hu
# @File : bucket_operation.py 

import datetime

from ab_test.util.analytical_param import analytical_parameters
from common.mysql_util import MySqlDbUtil
from conf.config import logger


class BucketOperation(object):
    """
        创建桶bucket
    """

    def __init__(self, db: MySqlDbUtil):
        self.db = db
        self.extra_type = "bucket_extra"

    def create_and_update_bucket(self, param, is_white_list=0):
        """
        创建桶bucket,存入数据库表
        :param param:待存入的参数
        :param is_white_list:是否是白名单参数
        """
        analytical_parameter_to_cb = analytical_parameters(param, self.extra_type)
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        analytical_parameter_to_cb.update({"update_time": update_time})
        analytical_parameter_to_cb.update({"white_list_id": is_white_list})
        self.db.batch_insert("T_ABTEST_BUCKET", [analytical_parameter_to_cb])

    def get_bucket_id_by_name(self, name: str, process_ids: dict, is_white_list):
        """
        通过分流器名字返回分流器id
        """
        sql = """
            SELECT id FROM T_ABTEST_BUCKET WHERE name='%s' and white_list_id=%s and is_deleted=0
        """
        sql = sql % (name, is_white_list)
        for k, v in process_ids.items():
            sql += " and "
            sql += "%s=%s" % (k, v)
        bucket_id = None
        try:
            cur = self.db.execute(sql)
            id_result = cur.fetchall()
            if id_result:
                bucket_id = id_result[0][0]
        except Exception as e:
            logger.error("查询bucket_id失败：%s", e)

        return bucket_id


if __name__ == '__main__':
    pass
