#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/14
# @Author : jiang.hu
# @File : scene_operation.py
import datetime

from ab_test.util.analytical_param import analytical_parameters
from common.mysql_util import MySqlDbUtil
from conf.config import logger


class SceneOperation:
    """
        创建场景
    """

    def __init__(self, db: MySqlDbUtil):
        self.db = db
        self.extra_type = "scene_extra"

    def create_and_update_scene(self, param_list):
        """
        创建场景,存入数据库表
        """
        scene_param_list = []
        for param in param_list:
            analytical_parameter_to_cs = analytical_parameters(param, self.extra_type)
            update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            analytical_parameter_to_cs.update({"update_time": update_time})
            scene_param_list.append(analytical_parameter_to_cs)
        self.db.batch_insert("T_ABTEST_SCENE", scene_param_list)

    def get_scene_id_by_name(self, name, exp_id):
        """
        通过创建的场景名字返回实验id
        """
        sql = """
            SELECT id FROM T_ABTEST_SCENE WHERE name='%s' and is_deleted=0 and experiment_id=%s
        """
        sql = sql % (name, exp_id)
        scene_id = None
        try:
            cur = self.db.execute(sql)
            id_result = cur.fetchall()
            if id_result:
                scene_id = id_result[0][0]
        except Exception as e:
            logger.error("查询场景scene_id失败：%s", e)

        return scene_id


if __name__ == '__main__':
    pass
