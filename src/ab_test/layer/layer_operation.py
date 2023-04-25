#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/14
# @Author : jiang.hu
# @File : layer_operation.py
import datetime

from ab_test.util.analytical_param import analytical_parameters
from common.mysql_util import MySqlDbUtil
from conf.config import logger


class LayerOperation:
    """
        创建流量层
    """

    def __init__(self, db: MySqlDbUtil):
        self.db = db
        self.extra_type = "layer_extra"

    def create_and_update_later(self, param):
        """
        创建流量层,存入数据库表
        """
        analytical_parameter_to_cl = analytical_parameters(param, self.extra_type)
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        analytical_parameter_to_cl.update({"update_time": update_time})
        self.db.batch_insert("T_ABTEST_LAYER", [analytical_parameter_to_cl])

    def get_layer_id_by_name(self, name, exp_id, scene_id):
        """
        通过创建的实验名字返回实验id
        """
        sql = """
            SELECT id FROM T_ABTEST_LAYER WHERE name='%s' and experiment_id='%s' and scene_id='%s' and is_deleted=0
        """
        sql = sql % (name, exp_id, scene_id)
        layer_id = None
        try:
            cur = self.db.execute(sql)
            id_result = cur.fetchall()
            if id_result:
                layer_id = id_result[0][0]
        except Exception as e:
            logger.error("查询流量层layer_id参数失败：%s", e)

        return layer_id

    def update_diversion_strategy_id_field(self, field_value: dict, update_id):
        """
        更新l流量层策略
        """
        sql = """
            UPDATE T_ABTEST_LAYER SET
        """
        for k, v in field_value.items():
            sql += "%s=%s" % (k, v)

        sql += " WHERE id=%s" % update_id

        try:
            self.db.execute(sql)
            self.db.conn.commit()
        except Exception as e:
            logger.error("更新流量层策略id失败：%s", e)


if __name__ == '__main__':
    pass
