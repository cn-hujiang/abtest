#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.conf import get_logger, ConfigWrapper

# @Author : jiang.hu
# @File : config.py.py
path = ""

parser = ConfigWrapper(path)

log_path = "/data/logs"
log_level = "debug"

logger = get_logger(log_path, log_level)


class MysqlConf:
    def __int__(self):
        pass
