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
import logging, warnings
from math import log2 as log
from utils import getP_C_U, getP_D_C
import pandas as pd

# logger = logging.getLogger(__name__)
# logger.setLevel(10)

# 初始设置
warnings.filterwarnings('ignore')

# print(os.getcwd())
# data = pd.read_csv(filepath_or_buffer='原题.csv', header=None)
data = pd.read_csv(filepath_or_buffer='new-mushroom.csv', header=None)

# 设置属性
# columns = [i for i in range(len(data.columns))]
columns = []
for i in range(len(data.columns)):
    columns.append(chr(97 + i))
columns_C = columns.copy()
columns_C.remove('d')

# 决策集
D = pd.DataFrame(data[len(data.columns) - 1])  # 用DataFrame数据类型来存贮方便后面的循环
# 属性集
C = pd.DataFrame(data.drop(columns=len(data.columns) - 1))
# 属性集的行数(总个数）
U_num = C.shape[0]
# 属性集的列数
property_num = C.shape[1]

# U_D
U_D = []
d_group = D.groupby(by=len(data.columns) - 1).groups  # 按照决策集分类
for i in range(len(d_group)):
    U_D.append(set(list(d_group.values())[i]))  # 分别得到分好类的结果化为集合存贮
# 得到结果格式：
# {{e1,e2,e3},{e4,e5,e6} ······ }

# U_C
U_C = []
c_group = C.groupby(by=[i for i in range(len(C.columns))]).groups  # 分类
for i in range(len(c_group)):
    U_C.append(set(list(c_group.values())[i]))

# p(X_i|Y_j)
p_C_U = getP_C_U(U_C, U_num)
p_D_C = getP_D_C(U_C, U_D)
print(f"个数  U_D: {len(U_D)}, U_C: {len(U_C)},p_C_U: {len(p_C_U)},p_D_C:{len(p_D_C)} ")
print(f"个数 U_D * U_C = P_D_C  {'满足' if len(U_D) * len(U_C) == len(p_D_C) else '不满足'}")
# 熵
H_D_C = 0
for i in range(len(U_C)):
    print('begin')
    inside = 0
    for j in range(len(U_D)):
        if p_D_C[j + i * len(U_D)] == 0:  # 底数为0 无意义跳过
            continue
        else:
            print(p_D_C[j + i * len(U_D)], log(p_D_C[j + i * len(U_D)]))
            inside += p_D_C[j + i * len(U_D)] * log(p_D_C[j + i * len(U_D)])
            print(inside)
            print("\n")
    print(inside, "--")
    H_D_C -= p_C_U[i] * inside
len(p_D_C)


# 子集
def getSubset(items) -> list:
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


allSubset = getSubset(columns_C)


def compare_H(columns_C, H_D_C, C):
    result = []
    for i in range(len(columns_C)):
        temp_set = set(columns_C)
        temp_set.discard(columns_C[i])  # 删除对应元素（列表无不报错的删除，利用set的不报错删除）
        # logger.warning(temp_set)
        temp_set = list(temp_set)  # 转化为列表
        temp_C = C.drop(C.columns[i], axis=1)  # 删除对应列
        temp_C.columns = [i for i in range(len(temp_C.columns))]  # 修改columns为 [0,1,2...]
        temp_U_C = getU_C(temp_C)  # 获取属性集的划分
        temp_P_C_U = getP_C_U(temp_U_C, U_num)  # 获取条件概率
        temp_P_D_C = getP_D_C(temp_U_C, U_D)  #
        temp_H_D_C = H(temp_U_C, U_D, temp_P_C_U, temp_P_D_C)
        same = temp_H_D_C == H_D_C  # 是否相同与原熵相同
        if same:
            result.append(temp_set)
            compare_H(temp_set, temp_H_D_C, temp_C)
    return result


result = compare_H(columns_C, H_D_C, C)


#
# for i in range(len(columns_C)):
#     temp_set = set(columns_C)
#     temp_set.discard(columns_C[i])  # 删除对应元素（列表无不报错的删除，利用set的不报错删除）
#     # logger.warning(temp_set)
#     temp_set = list(temp_set)  # 转化为列表
#     temp_C = C.drop(C.columns[i], axis=1)  # 删除对应列
#     temp_C.columns = [i for i in range(len(temp_C.columns))]  # 修改columns为 [0,1,2...]
#     temp_U_C = getU_C(temp_C)  #
#     temp_P_C_U = getP_C_U(temp_U_C, U_num)
#     temp_P_D_C = getP_D_C(temp_U_C, U_D)
#     temp_H_D_C = H(temp_U_C, U_D, temp_P_C_U, temp_P_D_C)
#     same = temp_H_D_C == H_D_C  # 是否相同与原熵相同
#     # return same, temp_set
#     if same:
#         compare_H(temp_set, temp_H_D_C, temp_C)


def H(U_C, U_D, p_C_U, p_D_C):
    H_D_C = 0
    for i in range(len(U_C)):
        inside = 0
        for j in range(len(U_D)):
            try:
                inside = p_D_C[j + i * property_num] * log(p_D_C[j + i * property_num])
            except ValueError as e:
                pass
        H_D_C -= p_C_U[i] * inside
    return H_D_C


def getU_C(C):
    U_C = []
    C_group = C.groupby(by=[i for i in range(len(C.columns))]).groups  # 分类
    for i in range(len(C_group)):
        U_C.append(set(list(C_group.values())[i]))
    return U_C
