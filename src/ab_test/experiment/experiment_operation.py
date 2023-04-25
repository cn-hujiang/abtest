#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/13
# @Author : jiang.hu
# @File : experiment_operation.py
# @description : 新建实验
import datetime

from ab_test.util.analytical_param import analytical_parameters
from common.mysql_util import MySqlDbUtil
from conf.config import MysqlConf, logger


class ExperimentalOperation:
    """
        创建实验
    """

    def __init__(self, db: MySqlDbUtil):
        self.db = db
        self.extra_type = "experiment_extra"

    def create_and_update_experiment(self, param):
        """
        创建实验,存入数据库表
        """
        analytical_parameters_to_ce = analytical_parameters(param, self.extra_type)
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        analytical_parameters_to_ce.update({"update_time": update_time})
        self.db.batch_insert("T_ABTEST_EXPERIMENT", [analytical_parameters_to_ce])

    def get_experiment_id_by_name(self, name):
        """
        通过创建的实验名字返回实验id
        """
        sql = """
            SELECT id FROM T_ABTEST_EXPERIMENT WHERE name='%s' and is_locked=0 and is_published=1
        """
        sql = sql % name
        experiment_id = None
        try:
            cur = self.db.execute(sql)
            id_result = cur.fetchall()
            if id_result:
                experiment_id = id_result[0][0]
        except Exception as e:
            logger.error("查询实验id失败：%s", e)

        return experiment_id

    def update_diversion_strategy_id_field(self, field_value: dict, update_id):
        """
        更新实验策略
        """
        sql = """
            UPDATE T_ABTEST_EXPERIMENT SET
        """
        for k, v in field_value.items():
            sql += "%s=%s" % (k, v)
        sql += " WHERE id=%s" % update_id

        try:
            self.db.execute(sql)
            self.db.conn.commit()
        except Exception as e:
            logger.error("更新实验策略id失败：%s", e)

    @staticmethod
    def analytical_parameters_to_ds(param: dict):
        """
        解析用户传入的参数,供分流策略计算
        """
        user_id = param.get("user_id", '')
        exp_id = param.get("exp_id", '')
        layer_id = param.get("layer_id", '')

        if not exp_id:
            return {}
        ana_param_dic = {"user_id": user_id, "exp_id": exp_id, "layer_id": layer_id}
        return ana_param_dic

    # def get_exp_id_and_layer_id(self):
    #     """
    #     获取表数据中最大实验id和流量层id
    #     由于表id为自增id，用户传入的
    #     """
    #     sql1 = """
    #         SELECT id FROM T_ABTEST_EXPERIMENT ORDER BY id DESC LIMIT 1;
    #     """
    #     sql2 = """
    #         SELECT id FROM T_ABTEST_LAYER ORDER BY id DESC LIMIT 1;
    #     """
    #     cur = self.db.execute(sql1)
    #     experiment_result = cur.fetchall()
    #     self.exp_id_max = experiment_result[0][0] if experiment_result else ""
    #     cur = self.db.execute(sql2)
    #     layer_result = cur.fetchall()
    #     self.layer_id_max = layer_result[0][0] if layer_result else ""
    #     pass


if __name__ == '__main__':
    mysql_db1 = MySqlDbUtil(**MysqlConf.HADOOP_DB_DICT)
    # mysql_db.connect()
    eop = ExperimentalOperation(mysql_db1)
