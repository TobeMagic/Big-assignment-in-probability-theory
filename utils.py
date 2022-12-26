#!/user/bin/env python
# -*- coding: utf-8 -*- #
"""
# File name: script
# Created: 2022/12/4
# Author: Magician
# Version: 1.0
# Description: 启发式算法
# style: .import black
# other: 小数统一 float
"""
import pandas as pd
import numpy as np
from math import log2 as log
import logging, time

logger = logging.getLogger(__name__)
logger.setLevel(10)


class matrix(object):
    """
    this is a different matrix

    matrix class is the parent class of all matrix,this class contains
    general attributes of matrix and some functions of matrix,such as get
    P_D_C,P_C_U,H et

    Attributes:
        matrix: A dataframe from original matrix
        columns: A list contains attribute sets and division sets
        columns_C： A list contains attribute sets and division sets except division
        D: A dataframe about division set
        C: A dataframe about attribute set
        U_num: A integer about number of U
        property_num:  A integer number of columns
        U_D: A List about Division of division sets in discussion domain
        U_C: A List about Attribute of division sets in discussion domain
        p_C_U: A List about attribute sets about discussion sets conditional probability
        p_D_C: A List about division sets about attribute sets conditional probability
        H_D_C: A com entropy about attribute sets and division sets
        condition_reduction: A list  about condition_reduction of matrix
    """

    def __init__(self, filename_or_buffer):
        begin_time = time.time()
        self.matrix = pd.read_csv(filepath_or_buffer=filename_or_buffer, header=None)
        self.columns = self.getColumns()
        self.columns_C = self.getColumns_C()
        self.D = pd.DataFrame(self.matrix[len(self.matrix.columns) - 1])
        self.C = pd.DataFrame(self.matrix.drop(columns=len(self.matrix.columns) - 1))
        self.U_num = self.C.shape[0]
        self.property_num = self.C.shape[1]
        self.U_D = self.getU_D()
        self.U_C = self.getU_C()
        self.p_C_U = getP_C_U(self.U_C, self.U_num)
        self.p_D_C = getP_D_C(self.U_C, self.U_D)
        self.H_D_C = self.getH_D_C()
        self.condition_reduction = self.compare_H(self.columns_C, self.H_D_C, self.C)
        logger.warning(f"initialize duration: {time.time() - begin_time}")

    def __str__(self):
        return f"columns: {self.columns} ,H_D_C: {self.H_D_C}, condition_reduction: {self.condition_reduction}"

    def __repr__(self):  # report the class for developer
        return f"<matrix  columns: {self.columns} U_num: {self.U_num}>"

    # def __format__(self, format_spec):
    #     return "".format()

    def getColumns(self):
        columns = []
        for i in range(len(self.matrix.columns)):
            columns.append(chr(97 + i))
        return columns

    def getColumns_C(self):
        columns_C = self.columns.copy()
        columns_C.remove('d')
        return columns_C

    def getU_D(self):
        U_D = []
        d_group = self.D.groupby(by=len(self.matrix.columns) - 1).groups  # 按照决策集分类
        for i in range(len(d_group)):
            U_D.append(set(list(d_group.values())[i]))  # 分别得到分好类的结果化为集合存贮
        return U_D

    def getU_C(self):
        U_C = []
        c_group = self.C.groupby(by=[i for i in range(len(self.C.columns))]).groups  # 分类
        for i in range(len(c_group)):
            U_C.append(set(list(c_group.values())[i]))
        return U_C

    def getH_D_C(self):
        """总熵"""
        logger.warning(
            f"个数  U_D: {len(self.U_D)}, U_C: {len(self.U_C)},p_C_U: {len(self.p_C_U)},p_D_C:{len(self.p_D_C)} ")
        if len(self.U_D) * len(self.U_C) == len(self.p_D_C):
            logger.warning(f"个数 U_D * U_C = P_D_C 满足")
        else:
            logger.warning(f"个数 U_D * U_C = P_D_C 不满足")
            return np.nan
        H_D_C = 0
        for i in range(len(self.U_C)):
            inside = 0
            for j in range(len(self.U_D)):
                if self.p_D_C[j + i * len(self.U_D)] == 0:  # 底数为0 无意义跳过
                    continue
                else:
                    inside += self.p_D_C[j + i * len(self.U_D)] * log(self.p_D_C[j + i * len(self.U_D)])
            H_D_C -= self.p_C_U[i] * inside
        return H_D_C

    def condition_reduction(self):
        for i in range(len(self.columns_C)):
            temp_set = set(self.columns_C)
            temp_set.discard(self.columns_C[i])  # 列表无不报错的删除，利用set的不报错删除
            logger.info(temp_set)
        temp_set = list(temp_set)

    def compare_H(self, columns_C, H_D_C, C):
        result = []
        for i in range(len(columns_C)):
            temp_set = set(columns_C)
            temp_set.discard(columns_C[i])  # 删除对应元素（列表无不报错的删除，利用set的不报错删除）
            # logger.warning(temp_set)
            temp_set = list(temp_set)  # 转化为列表
            temp_C = C.drop(C.columns[i], axis=1)  # 删除对应列
            temp_C.columns = [i for i in range(len(temp_C.columns))]  # 修改columns为 [0,1,2...]
            temp_U_C = getU_C(temp_C)  # 获取属性集的划分
            temp_P_C_U = getP_C_U(temp_U_C, self.U_num)  # 获取条件概率
            temp_P_D_C = getP_D_C(temp_U_C, self.U_D)  #
            temp_H_D_C = self.H(temp_U_C, self.U_D, temp_P_C_U, temp_P_D_C)
            same = temp_H_D_C == H_D_C  # 是否相同与原熵相同
            if same:
                result.append(temp_set)
                self.compare_H(temp_set, temp_H_D_C, temp_C)
        # result = set(result)
        # result = list(result)
        temp = [item for item in result if result.count(item) == 1]  # 去重
        return temp

    def H(self, U_C, U_D, p_C_U, p_D_C):
        """熵"""
        H_D_C = 0
        for i in range(len(U_C)):
            inside = 0
            for j in range(len(U_D)):
                if p_D_C[j + i * len(U_D)] == 0:  # 底数为0 无意义跳过
                    continue
                else:
                    inside += p_D_C[j + i * len(U_D)] * log(p_D_C[j + i * len(U_D)])
            H_D_C -= p_C_U[i] * inside
        return H_D_C


def getU_C(C):
    U_C = []
    C_group = C.groupby(by=[i for i in range(len(C.columns))]).groups  # 分类
    for i in range(len(C_group)):
        U_C.append(set(list(C_group.values())[i]))
    return U_C


def getP_C_U(U_C, U_num) -> list:
    """
    :param U_C: 属性划分
    :param U_num: 论域个数
    :return: p_C_U 百分比 （i=1,2...)
    """
    p_C_U = []
    for i in U_C:
        p_C_U.append(float(len(i) / U_num))
    return p_C_U


def getP_D_C(U_C, U_D) -> list:
    """
    :param U_C: 属性划分
    :param U_D: 决策划分
    :return: p_D_C  [i, j (j = 1,2,...)] (i = 1,2...)
    """
    p_D_C = []
    for i in U_C:
        for j in U_D:
            p_D_C.append(len(j & i) / len(i))  # j & i = j.intersection(i)
    return p_D_C


# 子集
def getSubset(items, columns_C) -> list:
    """
    :param items: A list about set
    :param columns_C:  A list about attributes
    :return:
    """
    all_subset = []
    N = len(items)
    for i in range(2 ** N):  # 子集个数，每循环一次一个子集
        combo = []
        for j in range(N):  # 用来判断二进制下标为j的位置数是否为1
            if (i >> j) % 2:
                combo.append(items[j])
        all_subset.append(combo)
    all_subset.sort(key=len)  # 排序
    all_subset.remove([])  # 去空集
    all_subset.remove(columns_C)  # 去属性集
    return all_subset


# 子集
def getSubset(items, columns_C) -> list:
    all_subset = []
    N = len(items)
    for i in range(2 ** N):  # 子集个数，每循环一次一个子集
        combo = []
        for j in range(N):  # 用来判断二进制下标为j的位置数是否为1
            if (i >> j) % 2:
                combo.append(items[j])
        all_subset.append(combo)
    all_subset.sort(key=len)  # 排序
    all_subset.remove([])  # 去空集
    all_subset.remove(columns_C)  # 去属性集母集本身
    return all_subset
