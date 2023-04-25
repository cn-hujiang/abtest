#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/13
# @Author : jiang.hu
# @File : diversion_strategy.py
import datetime

from ab_test.util.analytical_param import analytical_parameters
from common.mysql_util import MySqlDbUtil
from conf.config import logger
import hashlib


class DiversionStrategy(object):
    """
    分流策略
    """

    def __init__(self, db: MySqlDbUtil):
        self.db = db
        self.extra_type = "strategy_extra"

    def create_diver_strategy(self, param):
        """
        创建分流策略
        """
        analytical_parameter_to_cds = analytical_parameters(param, self.extra_type)
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        analytical_parameter_to_cds.update({"update_time": update_time})
        self.db.batch_insert("T_ABTEST_DIVERSION_STRATEGY", [analytical_parameter_to_cds])

    def get_diver_strategy_id_by_name(self, name, process_ids: dict):
        """
        通过分流策略名字返回分流策略id
        """
        sql = """
            SELECT id FROM T_ABTEST_DIVERSION_STRATEGY WHERE name='%s' and is_deleted=0 
        """
        sql = sql % name
        for k, v in process_ids.items():
            sql += " and %s=%s" % (k, v)
        diver_strategy_id = None
        try:
            cur = self.db.execute(sql)
            id_result = cur.fetchall()
            if id_result:
                diver_strategy_id = id_result[0][0]
        except Exception as e:
            logger.error("通过策略名查询策略id失败：%s", e)

        return diver_strategy_id

    @staticmethod
    def generate_diversion_strategy_by_white_list(user_info, white_list_set):
        """
        白名单策略，默认白名单直接进入bucket_id=1的桶
        判断传入用户是否在白名单，是则返回1
        """
        if user_info.get("user_id") in white_list_set:
            return 1
        return

    def get_diversion_strategy_info(self, config):
        """
        根据用户分流类型返回分流策略id
        """
        sql = """
            SELECT id, name FROM T_ABTEST_DIVERSION_STRATEGY WHERE is_deleted=0 and config=%s;
        """
        sql = sql % config
        cur = self.db.execute(sql)
        result = cur.fetchall()
        diversion_strategy_id = result[0][0]
        return diversion_strategy_id


if __name__ == '__main__':
    import hashlib

    hash_v = hashlib.md5("123".encode(encoding="utf8"))
    a = int(hash_v.hexdigest(), 16)
    print(a)
