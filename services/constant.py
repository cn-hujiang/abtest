#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author: zhengchubin
# @time: 2021/6/21 16:36
# @function:
from copy import deepcopy

# 状态码定义
SUCCESS_1 = {
    "code": 0,          # 返回状态码
    "data": [],         # 返回数据
    "msg": "成功",       # 返回信息
    "status": 0,        # 返回状态
    "success": True     # 时是否成功
}

ERROR_0 = {
    "code": -1,
    "data": [],
    "msg": "未知错误",
    "status": 0,
    "success": False
}
