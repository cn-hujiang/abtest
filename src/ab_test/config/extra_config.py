#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/14
# @Author : jiang.hu
# @File : extra_config.py
import json
import os
from pathlib import Path

from conf import ConfigWrapper

BASE_DIR = Path(os.path.realpath(__file__)).parent.parent.parent.parent
# print(BASE_DIR)
RC_CONFIG_FILE = BASE_DIR.joinpath('config', 'extra.conf').__str__()
PARAM_CONFIG_FILE = BASE_DIR.joinpath('config', 'parameter.json').__str__()
# print(RC_CONFIG_FILE)
RC_CONFIG = ConfigWrapper(RC_CONFIG_FILE)

if __name__ == '__main__':
    with open(PARAM_CONFIG_FILE, encoding='utf8') as f:
        data = f.read()
    print(json.loads(data)["experiment"])
