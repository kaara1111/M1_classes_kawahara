from __future__ import annotations

import pandas as pd
import numpy as np
import math
import json
import copy
import random
import itertools

# カテゴリ属性の集合attの値について、階層lの値に置換する
# 入力
# data: データセット（pandas.DataFrame想定）
# attr: 属性名（columns）リスト
# l_before: 現時点の階層
# l_after: 変更後の階層
# 出力
# pandas.DataFrame (置換後のデータ)
def generalization(data: pd.DataFrame, attr: list[str], l_before: int, l_after: int) -> pd.DataFrame:

    # 階層の情報は同ディレクトリの'attr_depth.json'にあらかじめ記録
    f_json = open('./attr_depth.json', 'r', encoding='utf-8')
    info_depth = json.load(f_json)
    f_json.close()

    for a in attr:
        a_info_depth = info_depth[a]
        if a_info_depth['type'] == 'category':
            parameter_dic = a_info_depth['definition']
            value_variation = [a[f'depth_{l_before}'] for a in parameter_dic]# 現在の階層で取り得るパラメータ全パターン
            value_variation = list(set(value_variation)) # 重複部削除
            # 置換の設定
            for param in value_variation:
                hit_index = data[data[a] == param] # とある値をもつ行を抜き出す
                if len(hit_index) == 0:
                    continue
                hit_val = [d[f'depth_{l_after}'] for d in parameter_dic if d[f'depth_{l_before}'] == param] # 置換後の値候補
                print(hit_val)
                new_col = random.choices(hit_val, k=len(hit_index))
                for i, num_index in enumerate(hit_index.index):
                    data.at[num_index, a] = new_col[i]


        elif a_info_depth['type'] == 'numeric':
            # 逆変換の場合は数値はいじらない
            if l_before >= l_after:
                continue

            # 該当する階層に設定されている閾値を取得
            # 閾値は区切り文字'/'で一つの文字列に列挙
            threshold_list = a_info_depth[f'threshold_{l_after}'].split('/')
            for i, th in enumerate(threshold_list):
                # 条件別に条件式を生成
                if i == 0:
                    condition = f'{a} < {th}'
                else:
                    condition = f'{a} >= {th_pre} & {a} < {th}'
                # 中央値計算、該当行列の値を中央値に置換
                tmp_df = data.query(condition)
                medium = int(tmp_df[a].median())
                for idtmp in tmp_df.index:
                    data.loc[idtmp, a] = medium
                th_pre = th
            # 最後の閾値以上の範囲について処理
            condition = f'{a} >= {th}'
            tmp_df = data.query(condition)
            medium = int(tmp_df[a].median())
            for idtmp in tmp_df.index:
                data.loc[idtmp, a] = medium


    return data



# k-匿名性のないレコードをdataから削除
# 入力
# data: データセット（pandas.DataFrame想定）
# attr: 属性名（columns）リスト
# k: attrの同じレコードがk件以下のものを削除
# 出力
# 1. pandas.DataFrame(レコード削除後のデータセット)
# 2. list[int]: 削除したレコードのインデックスリスト
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


# ラプラスノイズ付加
# 入力
# x: 単データ（スカラー）
# value_range: 同じ属性の値リスト、または[最大値, 最小値]のリスト
# epsilon: ノイズパラメータ
# 出力
# float(ノイズ付加後の単データ)
def differential_l(x: float, value_range: list[float], epsilon: float) -> float:
    delta_L = max(value_range) - min(value_range) # データの取り得る範囲
    generator = np.random.default_rng()
    noise = generator.laplace(0, delta_L/epsilon) # ラプラス分布の乱数
    # print(noise)
    return x + noise


# 指数ノイズ付加
# 入力
# x: 単データ（文字列）
# variation: 同じ属性のカテゴリリスト、または取り得る値の一覧
# epsilon: ノイズパラメータ
# 出力
# float(ノイズ付加後の単データ)
def differential_e(x: str, variation: list[str], epsilon: float) -> str:
    variation = list(set(variation)) # カテゴリの重複を除いた一覧
    exp_ep = math.exp(epsilon)
    threshold = exp_ep / (len(variation) - 1 + exp_ep)
    r = random.random()

    # 閾値と乱数の大小関係によって分岐
    if r <= threshold:
        return x
    else:
        # x以外の要素からランダムに1件抽出
        variation.remove(x)
        return random.choice(variation)
