#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/15
# @Author : jiang.hu
# @File : white_list_info.py 
import datetime

from ab_test.util.analytical_param import analytical_parameters
from common.mysql_util import MySqlDbUtil


class WhiteListInfo(object):
    """
    白名单类型
    """

    def __init__(self, db: MySqlDbUtil):
        self.db = db
        self.extra_type = "white_list_extra"

    def create_white_list(self, param_list: list):
        """
        创建白名单用户
        """
        white_list_user = []
        for param in param_list:
            analytical_parameter_to_wlt = analytical_parameters(param, self.extra_type)
            update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            analytical_parameter_to_wlt.update({"update_time": update_time})
            white_list_user.append(analytical_parameter_to_wlt)
        self.db.batch_insert("T_ABTEST_USER_WHITE_LIST", white_list_user)


if __name__ == '__main__':
    pass
