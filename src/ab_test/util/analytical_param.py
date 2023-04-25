#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/15
# @Author : jiang.hu
# @File : analytical_param.py
from ab_test.config.extra_config import RC_CONFIG


def analytical_parameters(param: dict, extra_type):
    """
    解析传入的参数,
    """
    ana_param_to_dic = {}
    extra_list = RC_CONFIG.get_list("mysqldb-table_extra", extra_type)
    # print(extra_list)
    for extra in extra_list:
        if extra in param:
            ana_param_to_dic.update({"{}".format(extra): param.get(extra)})
    # print(ana_param_to_dic)
    return ana_param_to_dic


if __name__ == '__main__':
    result = analytical_parameters({}, "experiment_extra")
    print(result)
