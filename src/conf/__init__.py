#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/20
# @Author : jiang.hu
# @File : __init__.py.py 

import os
import sys
import logging
from logging import Formatter, StreamHandler
from logging.handlers import TimedRotatingFileHandler, WatchedFileHandler
from configparser import ConfigParser


class ConfigWrapper(ConfigParser):  # pylint: disable=R0901
    """
    配置解析包装类
    """

    def __init__(self, path: str):
        ConfigParser.__init__(self)
        self.path = path
        self.read(self.path, encoding="utf-8")

    def parse_to_mysql_url(self, section: str) -> str:
        """
        配置转 MySqlUrl
        Args:
            section:数据库标识
        Returns:
            mysql url (str)
        """
        return "mysql+pymysql://{}:{}@{}:{}/{}".format(
            self.get(section, 'username'), self.get(section, 'password'),
            self.get(section, 'password'), self.get(section, 'port'),
            self.get(section, 'database'))

    def parse_to_es_dict(self, section: str, index: str) -> dict:
        """
        配置转 ES 字典
        Args:
            section:数据库标识
            index:  ES索引
        """
        return {
            'host': self.get(section, 'esHost'), 'port': int(self.get(section, 'esPort')),
            'http_auth': (self.get(section, 'esUser'), self.get(section, 'esPass')),
            'index': index
        }

    def parse_to_redis_dict(self, section: str) -> dict:
        """
        配置转 Redis 字典
        Args:
            section:数据库标识
        """
        return {
            'host': self.get(section, 'host'), 'port': int(self.get(section, 'port')),
            'password': self.get(section, 'password'), 'db': int(self.get(section, 'database')),
            'decode_responses': True
        }

    def parse_to_dict(self, section: str) -> dict:
        """
        配置转字典
        Args:
            section:数据库标识
        Returns:
            dict
        """
        kv = {}  # pylint: disable=C0103
        for option in self.options(section):
            value = self.get(section, option)
            if ',' in value:
                value = tuple(value.strip().split(','))
            if option.lower() == 'port':
                value = int(value)
            if option.lower().startswith('user'):
                option = 'user'
            kv[option] = value
        return kv

    def get_conf(self, section, option):
        """获取某一个配置"""
        return self.get(section, option)

    def get_list(self, section, option, separator=','):
        """ 获取列表配置 """

        def str2list(_str):
            return [i.strip() for i in _str.strip().split(separator) if i] if _str else []

        if option not in self.options(section):
            return None
        return str2list(self.get(section, option))


logging_name_to_Level = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}


def get_logger(log_path, log_level: str, name='mylogger'):
    """
    获取日志实例
    Args:
        log_path:    日志目录
        log_level:   日志级别
        name:        日志记录器的名字
    Returns:
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging_name_to_Level.get(log_level.upper(), logging.INFO))

    # 可以将日志写到任意位置(handlers)
    default_handlers = {
        WatchedFileHandler(os.path.join(log_path, 'all.log')): logging.INFO,  # 所有日志
        WatchedFileHandler(os.path.join(log_path, 'err.log')): logging.ERROR,  # 错误日志
        StreamHandler(sys.stdout): logging.DEBUG  # 控制台
    }

    # 日志格式：[时间] [文件名-行号] [类型] [信息]
    # _format = '%(asctime)s - %(filename)s[:%(lineno)d] - %(levelname)s - %(message)s'
    # _format = "%(asctime)s - %(levelname)s - %(message)s"
    _format = '%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] %(message)s'

    # 添加多个位置
    for handler, level in default_handlers.items():
        handler.setFormatter(Formatter(_format))
        if level is not None:
            handler.setLevel(level)
        logger.addHandler(handler)
    return logger


if __name__ == '__main__':
    pass
