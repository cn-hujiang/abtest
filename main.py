#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/8
# @Author : jiang.hu
# @File : main.py

import numpy as np
from flask import Blueprint, request, jsonify

from services.constant import SUCCESS_1, ERROR_0
from views.ab_test import ABTest

blueprint = Blueprint(
    'abtest',
    __name__,
    url_prefix='/abtest'
)

abtest = ABTest()


@blueprint.route('/1.0.0.0', methods=['GET', 'POST'])
def v_1_0_0_0():
    """
    abtest接口
    ---
    tags:
      - abtest接口
    description:
        abtest接口
    parameters:
      - name: first_data
        in: query
        type: List
        required: true
        description: 第一组数据
      - name: second_data
        in: query
        type: List
        required: true
        description: 第二组数据
      - name: alpha
        in: query
        type: number
        required: false
        description: alpha

    responses:
      500:
        description: Error Fail
      200:
        description: 请求成功
        schema:
          id: abtest
          properties:
            code:
              type: integer
              description: 状态码, 0成功,-1失败
            msg:
              type: string
              description: 状态信息
            status:
              type: integer
              description: 暂定0
            success:
              type: boolean
              description: 是否成功
            data:
              type: array
              description: abtest
              items:
                type: object
                properties:
                    test_type:
                      type: string
                      description: 检验类型
                    confidence_interval:
                      type: List
                      description: 置信区间
                    p-value:
                      type: number
                      description: p值结果
                    score:
                      type: number
                      description: 检验得分
                    result_test:
                      type: string
                      description: 检验结论
    """

    try:
        params = request.args.to_dict()
        if request.method == "POST":
            params = request.get_json()
        # print('请求参数[原始]：%s', json.dumps(params, ensure_ascii=False))
        first_data = params.get("first_data", [])
        second_data = params.get("second_data", [])
        alpha = np.array(params.get("alpha", 0.05))
        data = abtest.abtest(arr1=first_data, arr2=second_data, alpha=alpha)
        result = SUCCESS_1
        result.update({"data": data})
        return jsonify(result)
    except Exception as err:
        print(err)
        return jsonify(ERROR_0)


if __name__ == '__main__':
    x1 = np.array([1] * 28)
    x2 = np.array([1, 0, 1, 1] * 7)
    abtest.abtest(arr1=x1, arr2=x2)
