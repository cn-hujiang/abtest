#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/11
# @Author : jiang.hu
# @File : ab_test.py 

import numpy as np
from scipy import stats
import statsmodels.stats.weightstats as sw


class ABTest(object):
    def __init__(self):
        pass

    def abtest(self, arr1, arr2, alpha=0.05):
        """
        开始检查，按第一组数据长度选择检查方式
        :param alpha:
        :param arr1:
        :param arr2:
        :return:
        """
        if len(arr1) > 30 or len(arr1) != len(arr2):
            print("使用 Z 检验")
            data = self.z_test(arr1, arr2, alpha)
        else:
            print("使用 T 检验")
            data = self.t_test(arr1, arr2, alpha)

        return data

    @staticmethod
    def t_test(arr1, arr2, alpha=0.0001):
        """
        T检验
        :param arr1: 数组1
        :param arr2: 数组2
        :param alpha: 第一类错误允许值
        :return: t 分数， p 值
        """
        x = np.array(arr1) - np.array(arr2)
        t, p = stats.ttest_1samp(x, 0)
        d = stats.norm.ppf(1 - alpha / 2)
        floor = -d
        ceil = d
        str2 = "p值为 {0}, {1}alpha, 认为 arr1、arr2 均值差异{2}"
        if p > alpha:
            str2 = str2.format(p, "大于", "不显著")
        else:
            str2 = str2.format(p, "小于", "显著")

        data = {
            "test_type": "T-Test",
            "p-value": p,
            "score": t,
            "confidence_interval": [floor, ceil],
            "result_test": str2
        }
        return data

    @staticmethod
    def z_test(arr1, arr2, alpha=0.0001):
        """
        Z检验
        :param arr1: 数组1
        :param arr2: 数组2
        :param alpha: 第一类错误允许值
        :return: z 分数， p 值
        """
        z, p = sw.ztest(arr1, arr2, value=0)

        # arr1_mean, arr1_std, arr2_mean, arr2_std = arr1.mean(), arr1.std(ddof=1), arr2.mean(), arr2.std(ddof=1)
        # z1 = (arr1_mean - arr2_mean) / np.sqrt(arr1_std ** 2 / len(arr1) + arr2_std ** 2 / len(arr2))
        # p1 = 2 * stats.norm.sf(abs(z))

        d = stats.norm.ppf(1 - alpha / 2)
        floor = -d
        ceil = d
        # str0 = "Z分数为：{}".format(z)
        # str1 = "置信区间为 [{}, {}]".format(floor, ceil)
        str2 = "p值为 {0}, {1}alpha, 认为 arr1、arr2 均值差异{2}"
        if p > alpha:
            str2 = str2.format(p, "大于", "不显著")
        else:
            str2 = str2.format(p, "小于", "显著")
        data = {
            "test_type": "Z-Test",
            "p-value": p,
            "score": z,
            "confidence_interval": [floor, ceil],
            "result_test": str2
        }
        return data


if __name__ == '__main__':
    x1 = np.array([1] * 28)
    x2 = np.array([1, 0, 1, 1] * 7)

    # df_x1 = pd.read_excel()
    # df_x2 = pd.read_excel()

    abtest = ABTest()
    abtest.abtest(arr1=x1, arr2=x2)
