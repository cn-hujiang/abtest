#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/12
# @Author : jiang.hu
# @File : palindrome.py
def is_palindrome(str1):
    """
    判断字符串是否是回文字符串
    :param str1:
    :return:
    """
    if len(str1) < 2:
        return True
    if str1[0] != str1[-1]:
        return False

    return is_palindrome(str1[1:-1])


if __name__ == '__main__':
    s = "1233321"
    print(is_palindrome(s))
