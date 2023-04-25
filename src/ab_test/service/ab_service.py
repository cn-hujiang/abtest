"""
ab test service 相关内容
"""
# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2021/10/19
# @Author : jiang.hu
# @File : __init__.py.py

# pylint: disable=E0401
import datetime
import hashlib
import json

from ab_test.abtest_user.ab_client import ABTestClient
from ab_test.bucket.bucket_operation import BucketOperation
from ab_test.bucket.bucket_param import BucketParam
from ab_test.config.extra_config import PARAM_CONFIG_FILE
from ab_test.experiment.experiment_operation import ExperimentalOperation
from ab_test.layer.layer_operation import LayerOperation
from ab_test.scene.scene_operation import SceneOperation
from ab_test.strategy.diversion_strategy import DiversionStrategy
from ab_test.strategy.diverter import Diverted
from ab_test.strategy.driver_white_list_type import DiverWhiteListType
from ab_test.strategy.white_list_info import WhiteListInfo
from ab_test.util.resolve_input_parameters import resolve_params
from common import Singleton
from common.mysql_util import MySqlDbUtil

from common.name_template import gen_ab_name, gen_recall_group_stra_name, gen_fusion_stra_name

# pylint: disable=R0903,R0205
from conf.config import MysqlConf, logger
from infoflow.config import ChannelInfoConfig

mysql_db = MySqlDbUtil(**MysqlConf.HADOOP_DB_DICT)
mysql_db.connect()

# 白名单策略，默认id为1
WHITE_LIST = 1


# @Singleton
class ABService(object):
    """
    ab test service
    """

    def __init__(self):
        self.eop = ExperimentalOperation(mysql_db)
        self.sop = SceneOperation(mysql_db)
        self.lop = LayerOperation(mysql_db)
        self.bop = BucketOperation(mysql_db)
        self.ds = DiversionStrategy(mysql_db)
        self.bp = BucketParam(mysql_db)
        self.dwlt = DiverWhiteListType(mysql_db)
        self.wli = WhiteListInfo(mysql_db)

    # pylint: disable=R0201,W0613
    def abtest(self, params: dict) -> dict:
        """
        :param params:
        :return:
        """
        # user_id = params["user_id"]
        # bucket = int(hashlib.sha1(str(user_id).encode("utf8")).hexdigest(), 16) % 100
        ab_config = {
            "name": gen_ab_name("test", "1.0.0.0")
        }
        if True:
            ab_config.update({
                "9999": {
                    "use_rs": True,
                    "recall_stra": gen_recall_group_stra_name(
                        ChannelInfoConfig.recommender_channel_id, "1.0.0.0"),
                    "fusion_stra": gen_fusion_stra_name(
                        ChannelInfoConfig.recommender_channel_id, "1.0.0.0"),
                    "rank_stra": "RS:R:ARL:1.0.0.0",
                    "rerank_stra": "RS:RR:CRL:1.0.0.0",
                    "use_cache":  False,
                    "cache_stra": "RS:CC:RI:1.0.1.0"
                },
                ChannelInfoConfig.ipr_channel_id: {
                    "use_rs": True,
                    "recall_stra": gen_recall_group_stra_name(
                        ChannelInfoConfig.ipr_channel_id, "1.0.0.0"),
                    "fusion_stra": gen_fusion_stra_name(
                        ChannelInfoConfig.ipr_channel_id, "1.0.0.0"),
                    "rank_stra": "RS:R:ARL:1.0.0.0",
                    "rerank_stra": "RS:RR:CRL:1.0.0.0",
                    "use_cache":  False,
                    "cache_stra": "RS:CC:RI:1.0.1.0"
                },
                ChannelInfoConfig.publicy_subsidy_channel_id: {
                    "use_rs": True,
                    "recall_stra": gen_recall_group_stra_name(
                        ChannelInfoConfig.publicy_subsidy_channel_id, "1.0.0.0"),
                    "fusion_stra": gen_fusion_stra_name(
                        ChannelInfoConfig.publicy_subsidy_channel_id, "1.0.0.0"),
                    "rank_stra": "RS:R:ARL:1.0.0.0",
                    "rerank_stra": "RS:RR:CRL:1.0.0.0",
                    "use_cache":  False,
                    "cache_stra": "RS:CC:RI:1.0.1.0"
                },
                ChannelInfoConfig.other_channel_id: {
                    "use_rs": True,
                    "recall_stra": gen_recall_group_stra_name(
                        ChannelInfoConfig.other_channel_id, "1.0.0.0"),
                    "fusion_stra": gen_fusion_stra_name(
                        ChannelInfoConfig.other_channel_id, "1.0.0.0"),
                    "rank_stra": "RS:R:ARL:1.0.0.0",
                    "rerank_stra": "RS:RR:CRL:1.0.0.0",
                    "use_cache":  False,
                    "cache_stra": "RS:CC:RI:1.0.1.0"
                },
                ChannelInfoConfig.pc_channel_id: {
                    "use_rs": True,
                    "recall_stra": gen_recall_group_stra_name(
                        ChannelInfoConfig.pc_channel_id, "1.0.0.0"),
                    "fusion_stra": gen_fusion_stra_name(
                        ChannelInfoConfig.pc_channel_id, "1.0.0.0"),
                    "rank_stra": "RS:R:ARL:1.0.0.0",
                    "rerank_stra": "RS:RR:CRL:1.0.1.0",
                    "use_cache":  False,
                    "cache_stra": "RS:CC:RI:1.0.1.0"
                }
            })

        return ab_config

    def create_and_insert_db_abtest(self, filepath):
        """
        根据配置创建 新 abtest 并存入数据库
        """
        experiment_info = resolve_params(filepath)

        # 创建实验，如果实验名为空，则程序退出
        experiment_name = experiment_info.get("experiment_name")
        if not experiment_name:
            return
        # 创建实验，根据实验名返回实验id
        self.eop.create_and_update_experiment({"name": experiment_name})
        exp_id = self.eop.get_experiment_id_by_name(experiment_name)

        # 创建实验后创建策略，返回策略id
        # 创建策略的同时判断是否包含白名单策略并建立对应的白名单
        exp_diversion_strategy = experiment_info.get("exp_diversion_strategy")
        if not exp_diversion_strategy:
            return
        exp_diversion_strategy_id = self.create_and_resolve_strategy_param(exp_diversion_strategy,
                                                                           {"experiment_id": exp_id})
        # 更新实验策略id
        self.eop.update_diversion_strategy_id_field({"diversion_strategy_id": exp_diversion_strategy_id}, exp_id)

        # 创建场景
        scene_info = experiment_info.get("scene_info", [])
        for scene in scene_info:
            scene_name = scene.get("scene_name")
            if not scene_name:
                logger.info("没有配置场景名")
                continue

            # 创建场景并根据场景返回scene_id
            self.sop.create_and_update_scene(
                [{"name": scene_name, "experiment_id": exp_id, "allocation_ratio": 1}])
            scene_id = self.sop.get_scene_id_by_name(scene_name, exp_id)

            # 创建流量层
            layer_info = scene.get("layer_info")
            for layer in layer_info:
                layer_name = layer.get("layer_name")
                if not layer_name:
                    logger.info("没有配置流量层名称")
                    continue

                # 创建layer并返回layer_id
                self.lop.create_and_update_later({"name": layer_name, "experiment_id": exp_id, "scene_id": scene_id})
                layer_id = self.lop.get_layer_id_by_name(layer_name, exp_id, scene_id)

                # 获取并创建用户配置的 layer -> bucket 分流策略,返回策略id
                layer_diversion_strategy = layer.get("layer_diversion_strategy", {})
                if not layer_diversion_strategy:
                    logger.info("没有配置分流策略")
                    continue
                _process_ids = {"experiment_id": exp_id, "scene_id": scene_id, "layer_id": layer_id}

                # 返回策略id
                layer_diversion_strategy_id = self.create_and_resolve_strategy_param(layer_diversion_strategy,
                                                                                     _process_ids)

                # 更新流量层分流策略id
                self.lop.update_diversion_strategy_id_field({"diversion_strategy_id": layer_diversion_strategy_id},
                                                            layer_id)

                # 创建非白名单bucket
                bucket_info = layer.get("bucket_info", [])
                self.create_and_update_bucket_util(_process_ids, bucket_info, is_white_list=0)

    def create_and_update_bucket_util(self, process_ids, bucket_info, is_white_list=0):
        """
        创建bucket
        创建bucket_param
        """
        for bucket_dic in bucket_info:
            bucket_name = bucket_dic.get("bucket_name")
            if not bucket_name:
                continue
            param_info = {"name": bucket_name}
            param_info.update(process_ids)
            self.bop.create_and_update_bucket(param_info, is_white_list=is_white_list)
            bucket_id = self.bop.get_bucket_id_by_name(bucket_name, process_ids, is_white_list)
            bucket_param = bucket_dic.get("bucket_param")
            bucket_param_list = []
            for param_name, param_value in bucket_param.items():
                bucket_param_list.append(
                    {"name": param_name, "value": param_value, "bucket_id": bucket_id})
            self.bp.create_and_update_bucket_param(bucket_param_list)

    def create_and_resolve_strategy_param(self, diversion_strategy, process_ids: dict):
        """
        解析数据
        创建分流策略
        如果有白名单策略，则创建白名单
        返回策略id
        """
        if not diversion_strategy:
            logger.info("没有配置分流策略")
            return
        diversion_strategy_name = diversion_strategy.get("diversion_strategy_name")
        diversions = diversion_strategy.get("diversions")

        # 策略类型 当前支持两种：白名单、用户信息
        diversion_type = diversions.get("diversion_type")

        # 优先级
        diversions_priority = diversions.get("diversions_priority")
        # 创建策略并返回策略id
        param_info = {"name": diversion_strategy_name,
                      "diver_config": str(dict(zip(diversions_priority, diversion_type)))}
        param_info.update(process_ids)
        self.ds.create_diver_strategy(param_info)
        diver_id = self.ds.get_diver_strategy_id_by_name(diversion_strategy_name, process_ids)

        # 判断策略是否选择白名单策略并创建白名单
        # exp --> scene 白名单
        # layer --> bucket白名单
        if WHITE_LIST in diversion_type:
            white_list_info = diversions.get("white_list_info", [])
            self.create_white_list(white_list_info, process_ids)
        return diver_id

    def create_white_list(self, white_list_info: list, process_ids: dict):
        """
        创建 scene 和 bucket 白名单
        """
        for dic in white_list_info:
            white_list_type_name = dic.get("white_list_type_name")
            if not white_list_type_name:
                continue
            param_info = {"name": white_list_type_name}
            param_info.update(process_ids)
            # 新建白名单类型并返回类型id
            self.dwlt.create_white_list_type(param_info)
            white_list_type_id = self.dwlt.get_white_list_type_id_by_name(white_list_type_name, process_ids)

            white_list_users = dic.get("white_list")
            white_lists = []
            for user in white_list_users:
                white_lists.append({"user_id": user, "white_list_id": white_list_type_id})
            # 创建并存入白名单用户
            self.wli.create_white_list(white_lists)

            white_list_bucket_info = dic.get("white_list_bucket_info", {})
            # 创建白名单策略bucket及参数 bucket_param
            self.create_and_update_bucket_util(process_ids, [white_list_bucket_info], is_white_list=white_list_type_id)


if __name__ == '__main__':
    logger.info("开始创建实验...")
    logger.info("请上传实验配置文件...")
    path = ''
    ab = ABService()
    logger.info("正在创建实验...")
    ab.create_and_insert_db_abtest(path)
    ac_c = ABTestClient()
    logger.info("实验创建完成...")
    logger.info("请导入用户信息...")
    parameter = {"user_id": "000007", "exp_id": 1}
    # ac_c.get_bucket_param_info()
    lst = ac_c.get_bucket_param_by_user_operation(parameter)
    print(lst)
