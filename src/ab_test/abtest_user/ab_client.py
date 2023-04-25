#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/19
# @Author : jiang.hu
# @File : ab_client.py
import hashlib
from typing import List, Tuple, Dict

from common.mysql_util import MySqlDbUtil
from conf.config import MysqlConf, logger

mysql_db = MySqlDbUtil(**MysqlConf.HADOOP_DB_DICT)
mysql_db.connect()

# 白名单策略，默认id为1
WHITE_LIST = 1


class ABTestClient(object):
    def __init__(self):
        self.exp_info = {}
        self.strategy_info = {}
        self.scene_info = {}
        self.layer_info = {}
        self.bucket_info = {}
        self.bucket_param_info = {}
        self.white_list_type_info = {}
        self.white_list_info = {}

        self.get_exp_info()
        self.get_strategy_conf_info()
        self.get_scene_info()
        self.get_layer_info()
        self.get_bucket_info()
        self.get_bucket_param_info()
        self.get_white_list_type_info()
        self.get_white_list_info()

    def get_bucket_param_by_user_operation(self, param):
        """
        根据用户信息返回参数
        """
        bucket_param_result = []
        user_id, exp_id = self.get_user_param(param)
        # exp_strategy_id_dict = self.get_exp_strategy(exp_id)
        scene_id_list = self.get_scene_id(exp_id)
        if not scene_id_list:
            return
        scene_id_index = self.scene_diversion(user_id, exp_id, len(scene_id_list))
        scene_id = scene_id_list[scene_id_index]

        # layer_info = [(layer_id,diversion_strategy_id)]
        layer_info = self.get_layer_id(exp_id, scene_id)
        if not layer_info:
            return
        for layer_id, layer_strategy_id in layer_info:
            diver_config = self.get_strategy_conf_by_id(layer_strategy_id)
            bucket_param_dic_list = self.bucket_diversion(user_id, exp_id, scene_id, layer_id, diver_config)
            bucket_param_result.append(bucket_param_dic_list)
        return bucket_param_result

    @staticmethod
    def get_user_param(param: dict):
        """
        解析用户传入参数
        param: {user_id:"", exp_id:""}
        """
        user_id = param.get("user_id")
        exp_id = param.get("exp_id")
        return user_id, exp_id

    def get_exp_strategy(self, exp_id):
        """
        根据用户传入实验id，返回实验测策略配置
        """
        strategy_id = self.exp_info.get(exp_id)
        return self.get_strategy_conf_by_id(strategy_id)

    def get_strategy_conf_by_id(self, strategy_id) -> Dict:
        """
        根据用户传入实验id，返回实验测策略配置
        """
        return self.strategy_info.get(strategy_id, {})

    def get_scene_id(self, exp_id) -> List:
        """
        根据实验，返回实验对应的场景id  scene_id
        """
        return self.scene_info.get(exp_id, [])

    def get_layer_id(self, exp_id, scene_id) -> List[Tuple]:
        """
        根据实验id、场景id，获取流量层id及对应的策略id layer_id, strategy_id
        """
        return self.layer_info.get((exp_id, scene_id), [])

    def get_exp_info(self):
        """
        获取所有实验信息
        """
        sql_exp = """
             SELECT id, diversion_strategy_id 
             FROM `hadoop_db_dev`.`t_abtest_experiment` 
             WHERE is_published=1
                AND is_deleted=0
                AND is_locked=0 
        """
        try:
            cur = mysql_db.execute(sql_exp)
            result = cur.fetchall()
            for exp_id, strategy_id in result:
                self.exp_info.setdefault(exp_id, strategy_id)
        except Exception as e:
            logger.error("查询所有实验信息失败：", e)

    def get_strategy_conf_info(self):
        """
        获取所有策略配置
        """
        sql_strategy = """
            SELECT id, diver_config 
             FROM T_ABTEST_DIVERSION_STRATEGY 
             WHERE is_deleted=0
        """
        try:
            cur = mysql_db.execute(sql_strategy)
            result = cur.fetchall()
            for strategy_id, diver_config in result:
                self.strategy_info.setdefault(strategy_id, eval(diver_config))
        except Exception as e:
            logger.error("查询所有策略配置失败：", e)

    def get_scene_info(self):
        """
        获取所有场景
        """
        sql_scene = """
            SELECT id, experiment_id 
             FROM T_ABTEST_SCENE 
             WHERE is_deleted=0
        """
        try:
            cur = mysql_db.execute(sql_scene)
            result = cur.fetchall()
            for scene_id, experiment_id in result:
                self.scene_info.setdefault(experiment_id, []).append(scene_id)
        except Exception as e:
            logger.error("查询所有场景信息失败：", e)

    def get_layer_info(self):
        """
        获取所有流量层
        返回值： {(exp_id,scene_id):[(layer_id,diversion_strategy_id)]}
        """
        sql_layer = """
            SELECT id, diversion_strategy_id, experiment_id, scene_id
             FROM T_ABTEST_LAYER 
             WHERE is_deleted=0
        """
        try:
            cur = mysql_db.execute(sql_layer)
            result = cur.fetchall()
            for layer_id, diversion_strategy_id, experiment_id, scene_id in result:
                self.layer_info.setdefault((experiment_id, scene_id), []).append((layer_id, diversion_strategy_id))
        except Exception as e:
            logger.error("查询所有流量层信息失败：", e)

    def get_bucket_info(self):
        """
        获取所有bucket
        返回值： {(exp_id, scene_id, layer_id, white_list_id):[bucket_id]}
        """
        sql_bucket = """
            SELECT id, layer_id, experiment_id, scene_id, white_list_id, name
             FROM T_ABTEST_BUCKET 
             WHERE is_deleted=0
        """
        try:
            cur = mysql_db.execute(sql_bucket)
            result = cur.fetchall()
            for bucket_id, layer_id, experiment_id, scene_id, white_list_id, bucket_name in result:
                self.bucket_info.setdefault((experiment_id, scene_id, layer_id, white_list_id), []).append(
                    {bucket_id: bucket_name})
        except Exception as e:
            logger.error("查询所有bucket信息失败：", e)

    def get_bucket_param_info(self):
        """
        获取所有bucket_param
        返回值： {bucket_id:[{param_name: param_value}]}
        """
        sql_bucket_param = """
            SELECT name, value, bucket_id
             FROM T_ABTEST_BUCKET_PARAMS 
             WHERE is_deleted=0
        """
        try:
            cur = mysql_db.execute(sql_bucket_param)
            result = cur.fetchall()
            for param_name, param_value, bucket_id in result:
                self.bucket_param_info.setdefault(bucket_id, []).append({param_name: param_value})
        except Exception as e:
            logger.error("查询所有bucket param信息失败：", e)

    def get_white_list_type_info(self):
        """
        获取所有白名单类型信息
        返回值： {(experiment_id, scene_id, layer_id):[white_list_type_id]}
        """
        sql_white_list_type = """
            SELECT id, experiment_id, scene_id, layer_id
             FROM T_ABTEST_WHITE_LIST_TYPE 
             WHERE is_deleted=0
        """
        try:
            cur = mysql_db.execute(sql_white_list_type)
            result = cur.fetchall()
            for white_list_type_id, experiment_id, scene_id, layer_id in result:
                self.white_list_type_info.setdefault((experiment_id, scene_id, layer_id), []).append(white_list_type_id)
        except Exception as e:
            logger.error("查询所有 white_list_type 信息失败：", e)

    def get_white_list_info(self):
        """
        获取所有白名单信息
        返回值： {white_list_id:[user_id]}
        """
        sql_white_list_type = """
            SELECT user_id, white_list_id
             FROM T_ABTEST_USER_WHITE_LIST 
             WHERE is_deleted=0
        """
        try:
            cur = mysql_db.execute(sql_white_list_type)
            result = cur.fetchall()
            for user_id, white_list_id in result:
                self.white_list_info.setdefault(int(white_list_id), []).append(user_id)
        except Exception as e:
            logger.error("查询所有 white_list_type 信息失败：", e)

    def scene_diversion(self, user_id, exp_id, N):
        """
        根据实验分流策略，对用户进行分流，到不同的场景
        N:一个实验下有多少个场景
        """
        if N == 0:
            return
        user_info = {"user_id": user_id, "exp_id": exp_id}
        index = self.generate_diversion_strategy_by_user(user_info, N)
        return index

    def bucket_diversion(self, user_id, exp_id, scene_id, layer_id, diver_config: dict):
        """
        根据layer层的分流策略，对用户进行分流到不同的bucket
        如果是白名单分流，直接返回bucket_param
        """
        bucket_param_dic_list = []
        # 排序优先级
        diversions_priorities = sorted(diver_config.keys())

        # 根据优先级循环策略
        for diversion_priority in diversions_priorities:
            if diver_config.get(diversion_priority) == WHITE_LIST:
                white_list_types = self.white_list_type_info.get((exp_id, scene_id, layer_id))
                if not white_list_types:
                    continue

                for white_list_type in white_list_types:
                    user_id_list = self.white_list_info.get(white_list_type)
                    if user_id not in user_id_list:
                        continue
                    bucket_info_list = self.bucket_info.get((exp_id, scene_id, layer_id, white_list_type), [])
                    if not bucket_info_list:
                        continue
                    self.get_bucket_param_list(bucket_info_list[0], bucket_param_dic_list)
                if not bucket_param_dic_list:
                    continue
                return bucket_param_dic_list

            else:
                user_info = {"user_id": user_id, "exp_id": exp_id, "scene_id": scene_id, "layer_id": layer_id}
                key = (exp_id, scene_id, layer_id, 0)
                bucket_info_list = self.bucket_info.get(key, [])
                if not bucket_info_list:
                    continue
                #
                layer_id_index = self.generate_diversion_strategy_by_user(user_info, len(bucket_info_list))

                self.get_bucket_param_list(bucket_info_list[layer_id_index], bucket_param_dic_list)
                if not bucket_param_dic_list:
                    continue
                return bucket_param_dic_list

        return bucket_param_dic_list

    def get_bucket_param_list(self, bucket_info_dic, bucket_param_dic_list):
        """
        解析bucket_param
        """
        bucket_param_dict = {}
        for bucket_id, bucket_name in bucket_info_dic.items():
            bucket_param_list = self.bucket_param_info.get(bucket_id)
            if not bucket_param_list:
                continue
            bucket_param_dict.update({"bucket_id": bucket_id, "bucket_name": bucket_name})
            for bucket_param_info in bucket_param_list:
                bucket_param_dict.update(bucket_param_info)
            bucket_param_dic_list.append(bucket_param_dict)

    @staticmethod
    def generate_diversion_strategy_by_user(user_info: dict, N):
        """
        根据用户信息及传入的其他信息作hash取值
        :param user_info:根据传入 N 取模,， 默认2
        :param N:根据传入 N 取模,， 默认2
        """
        hash_str = str(user_info.get("user_id", "")) + str(user_info.get("exp_id", "")) + str(
            user_info.get("layer_id", ""))
        hash_value = hashlib.md5(str(hash_str).encode(encoding="utf8"))
        index = int(hash_value.hexdigest(), 16) % N
        return index


if __name__ == '__main__':
    parameter = {"user_id": "000007", "exp_id": 1}
    ac_c = ABTestClient()
    # ac_c.get_bucket_param_info()
    lst = ac_c.get_bucket_param_by_user_operation(parameter)
    print(lst)
    pass
