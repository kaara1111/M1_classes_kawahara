from __future__ import annotations

import pandas as pd
import numpy as np
import math
import json
import copy
import random
import itertools
print(np.__version__)
def remove_record(data: pd.DataFrame, attr: list[str], k: int):

    # attrの各属性がもつ値の組み合わせを列挙
    attr_pattern = ()
    pre_attr = ()
    for a in attr:
        pattern = data[a].unique()
        # 各属性の直積を作成
        if len(pre_attr) != 0:
            attr_pattern = []
            for x, y in itertools.product(pre_attr, pattern):
                a_pattern = []
                if type(x) is tuple:
                    a_pattern = [t for t in x]
                else:
                    a_pattern = [x]
                a_pattern.append(y)
                attr_pattern.append(tuple(a_pattern))

            pre_attr = tuple(attr_pattern)
        else:
            pre_attr = tuple(pattern)


    # attrの全属性がある値のとき、合致するレコードを取得
    # k件以下であれば削除する
    delete_index = []
    for p in attr_pattern:
        data_reduce = copy.deepcopy(data)
        for attr_name, parameter in zip(attr, p):
            data_reduce = data_reduce[data_reduce[attr_name] == parameter]
            hit_index = data_reduce.index
        if len(hit_index) <= k:
            delete_index.extend(hit_index)

    # hitしたインデックスのデータを無くす
    if len(delete_index) != 0:
        delete_index = list(set(delete_index)) # 重複部分を削除
        all_columns = data.columns
        data.loc[delete_index, all_columns] = None # 削除対象のデータを一括して欠損値にする

    return data

data = pd.DataFrame({'a': [1, 1, 2, 2, 3, 3, 4, 4],
                    'b': [1, 1, 1, 1, 2, 2, 2, 2],
                    'c': [1, 1, 1, 1, 1, 1, 1, 1],
                    })

print(set(data['a']))
data = remove_record(data, ['a', 'b'], 2)
