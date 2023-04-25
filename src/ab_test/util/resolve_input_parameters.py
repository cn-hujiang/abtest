#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/16
# @Author : jiang.hu
# @File : resolve_input_parameters.py
import json

from ab_test.config.extra_config import PARAM_CONFIG_FILE


def resolve_params(filepath) -> dict:
    if not filepath:
        filepath = PARAM_CONFIG_FILE
    with open(filepath, encoding='utf8') as f:
        param_data = f.read()

    param = json.loads(param_data)
    return param["experiment"]


if __name__ == '__main__':
    path = ''
    print(resolve_params(path)["scene_info"])
