#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/13
# @Author : jiang.hu
# @File : mysql_util.py
from typing import List, Dict, Union

import pandas as pd
from pymysql import cursors, Connect
from sqlalchemy import create_engine
from conf.config import logger, MysqlConf
from config.create_db_sql import *


def gen_insert_sql(tb_name, docs: List[Dict], upsert=True):
    """
    生成插入 Mysql 语句，注意每个dic中的键数量必须保持一致
    Args:
        tb_name:    表明
        docs:       插入的数据
        upsert:     键重复时更新
        Examples:
            INSERT INTO TABLE
                p_tags(t_id, t_type, t_type_cn, t_name, t_name_cn, t_weight)
            VALUES
                ("A_00000001","pay_type","支付方式","wx","微信支付", 0.0),
                ("A_00000002","pay_type","支付方式","alipay","支付宝", 0.0),
                ("A_00000003","pay_type","支付方式","upacp","银联支付", 0.0);
    """

    def gen_insert_pattern(count):
        # (%s, %s, %s)
        return '(' + ', '.join('%s' for i in range(count)) + ')'

    def gen_update_pattern(count):
        # %%s=VALUES(%s), %s=VALUES(%s)
        return tuple('%s=VALUES(%s)' for i in range(count))

    if not docs:
        return
    columns = docs[0].keys()
    col_cnt = len(columns)

    # 构造插入语句
    i_pattern = gen_insert_pattern(col_cnt)
    sql = f'INSERT INTO {tb_name}' + i_pattern + '\nVALUES '
    sql = sql % tuple(columns)  # INSERT INTO TABLE (1, 2, 3)
    values = []
    for cnt, doc in enumerate(docs):
        v_list = []
        for v in doc.values():
            if isinstance(v, str):
                v = '"%s"' % v
            else:
                v = str(v)
            v_list.append(v)
        values.append(i_pattern % tuple(v_list))  # (1, 2, "3")
    sql += ',\n'.join(values)

    # 构造更新语句(重复键)
    if upsert:
        sql += '\nON DUPLICATE KEY UPDATE\n'
        u_patter = gen_update_pattern(col_cnt)
        columns_dup = tuple((k, k) for k in columns)
        sql += ', '.join(u % c for u, c in zip(u_patter, columns_dup))

    return sql + ';'


class PandasDbUtil(object):

    def __init__(self, url: str):
        self.url = url
        self.engine = create_engine(self.url, encoding='utf8',
                                    pool_size=20, max_overflow=100)

    def read_sql(self, sql: str,
                 chunk_size: Union[None, int] = 5000) -> pd.DataFrame:
        """
        通过 pandas API 读取数据库表(按块读取)
        Args:
            sql:        查询语句
            chunk_size: 批大小
        Returns:
        """
        if isinstance(chunk_size, int):
            chunks = []
            for chunk in pd.read_sql(sql, con=self.engine, chunksize=chunk_size):
                chunks.append(chunk)
            if len(chunks) == 0:
                return pd.DataFrame()
            return pd.concat(chunks)
        else:
            return pd.read_sql(sql, con=self.engine)

    def to_sql(self, df: pd.DataFrame, tb_name, dtype=None, if_exists='append',
               chunk_size: Union[None, int] = 10000, **kwargs) -> bool:
        """
        通过 pandas API 存储到数据库表
        Args:
            df:         数据表
            tb_name:    表名
            chunk_size: 批大小
            dtype:      数据类型
            if_exists:  {'fail', 'replace', 'append'}, default 'fail'
                        How to behave if the table already exists.
        Returns:
        """
        df.to_sql(tb_name, con=self.engine, dtype=dtype, if_exists=if_exists,
                  chunksize=chunk_size, **kwargs)
        return True


class MySqlDbUtil(object):

    def __init__(self, **kwargs):
        self.config = kwargs
        self.conn = None

    def execute(self, sql: str) -> cursors.DictCursor:
        """
        通过 MySqlDB API 读取数据库表
        Args:
            sql:            查询语句
        Returns:
        """
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
        except Exception as e:
            logger.error("sql read database error: %s", e)
        return cur

    def batch_insert(self, tb_name, docs: List[Dict], chunk_size: int = 1000, upsert=True) -> int:
        """
        批量插入MySQL
        Args:
            tb_name:        表名
            docs:           待写入的数据
            chunk_size:     批大小
            upsert:         键重复时是否更新
        Returns:

        """
        cur = self.conn.cursor()
        try:
            rows = 0
            _rows = 0
            length = len(docs)
            while rows < length:
                sql = gen_insert_sql(tb_name, docs[rows:rows + chunk_size], upsert=upsert)
                _rows += cur.execute(sql)
                rows += chunk_size

                self.conn.commit()
                logger.info('[MySQL-%s][写]: 有效行数/总行数 = %s/%s', tb_name, _rows, length)
            return _rows
        except Exception as e:
            logger.error("[MySQL-%s][写]: sql read database error: %s", tb_name, e)

    def delete(self, tb_name: str):
        """
        删除某个表的所有数据
        Args:
            tb_name: 表名
        """
        cur = self.conn.cursor()
        try:
            sql = 'DELETE FROM %s;' % tb_name
            _rows = cur.execute(sql)

            self.conn.commit()
            logger.info('[MySQL-%s][删]: 影响行数 = %s', tb_name, _rows)
            return _rows
        except Exception as e:
            logger.error("sql read database error: %s", e)

    def connect(self):
        self.conn = Connect(**self.config)
        return self.conn

    def create_table(self, sql):
        self.execute(sql)
        self.conn.commit()

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    mysql_db = MySqlDbUtil(**MysqlConf.HADOOP_DB_DICT)
    mysql_db.connect()
    mysql_db.create_table(CREATE_T_ABTEST_BUCKET_PARAMS)
    mysql_db.create_table(CREATE_T_ABTEST_LAYER)
    mysql_db.create_table(CREATE_T_ABTEST_SCENE)
    mysql_db.create_table(CREATE_T_ABTEST_BUCKET)
    mysql_db.create_table(CREATE_T_ABTEST_EXPERIMENT)
    mysql_db.create_table(CREATE_T_ABTEST_DIVERSION_STRATEGY)
    mysql_db.create_table(CREATE_T_ABTEST_USER_WHITE_LIST)
    mysql_db.create_table(CREATE_T_ABTEST_DIVERSION)
    mysql_db.create_table(CREATE_T_ABTEST_WHITE_LIST_TYPE)
