from __future__ import annotations

import pandas as pd
import numpy as np

# 匿名化データと攻撃データを比較
# 1件の匿名化データに対し、距離が近い攻撃データのレコードn件をリストアップする対応表Dcを作成
# 入力
# ano_data: 匿名化データセット
# ata_data: 攻撃用データセット
# original_ano_len: remove_record前の匿名化データのレコード数
# ata_len: remove_record前の攻撃データのレコード数
# att: 比較を行う属性の名前リスト
# n: Dcに挙げる1データあたりのレコード数
# 出力
# 1. list[int]: 攻撃データのインデックスリスト
# 2. list[float]: 攻撃データのユークリッド距離リスト(インデックスリストと対応)
def neighbor_att(ano_data: pd.DataFrame, ata_data: pd.DataFrame, att: list[str], n: int):
    # 対象の属性の列取得
    ano_att = ano_data[att]
    ata_att = ata_data[att]

    # 匿名化データの欠損値のみの行（Anonymize_sample.remove_record()で削除された行）削除
    ano_att = ano_att.dropna(how='all')
    print(ano_att)

    # 属性が連続値か離散値か判定、連続値は最大・最小を測定し、正規化のパラメータ算出
    dict_normal = {} # 連続値の値の範囲を記録するディクショナリ
    for a in att:
        col = ano_att[a]
        if col.dtype != 'object':
            max_val = np.amax(col.values)
            min_val = np.amin(col.values)
            dict_normal[a] = max_val - min_val
    # 各要素のユークリッド距離計算、Dc作成
    Dc = [[-1] * n for i in range(len(ano_data))] # Dc初期化（-1で初期化）
    Dc_yuclid = [[float('inf')] * n for i in range(len(ano_data))] # Dc_yuclid初期化（初期値無限大）

    for i, row_ano in ano_att.iterrows():
        yuclid_np = np.full(len(ata_data), float('inf')) # ユークリッド距離のリスト(初期値無限大)

        for j, row_ata in ata_att.iterrows():
            yuclid = 0.0
            for a in att:
                ano_side = row_ano[a]
                ata_side = row_ata[a]
                if a in dict_normal.keys():
                    # 連続値属性の場合、距離を[0, 1]の範囲に正規化
                    differ = abs(ano_side - ata_side)
                    differ_normal = float(differ) / dict_normal[a]
                    yuclid += differ_normal ** 2
                else:
                    # 離散値の場合、一致は距離0（計算無し）, 不一致は距離1とする
                    if ano_side != ata_side:
                        yuclid += 1
            yuclid_np[j] = np.sqrt(yuclid) # ユークリッド距離追加

        # ユークリッド距離のリストから小さい順にn件のインデックスを取得しDcに追加
        min_sort_index = yuclid_np.argsort().tolist()
        min_n = min_sort_index[:n]
        min_yuclid_val = [yuclid_np[y] for y in min_n]

        Dc[i] = min_n
        Dc_yuclid[i] = min_yuclid_val


    return Dc, Dc_yuclid


# neighbor_attで作成したリストDc, Dc_yuclidを使用
# optionで指定した評価手法で対応を1対1に絞る
# 入力
# Dc: 攻撃データのインデックスリスト
# Dc_yuclid: 攻撃データのユークリッド距離リスト(インデックスリストと対応)
# drop_ano: remove_recordで削除した匿名化データレコードのインデックスリスト
# duplication: True(デフォルト)ならば、各匿名化データとDcの先頭要素を対応させる。重複は許す
#         　　 Falseならば、ユークリッド距離が短い要素から重複しないようにマッチングさせる。対応データなしとする場合もあり
# 出力
# list[int] (匿名化データと攻撃データの対応リスト)
def attack_id(Dc: list[list[int]], Dc_yuclid: list[list[float]], duplication=True) -> list[int]:
    correspond = [-1] * len(Dc) # 対応表(初期値はDcのインデックス外)
    not_matching_index = list(range(len(Dc)))
    flag_end = False
    if duplication:
        # 重複込みで対応を決定
        correspond = [Dc[i][0] for i in not_matching_index]
    else:
        while flag_end == False:
            # ユークリッド距離が小さい順に匿名データ・攻撃データの対応を決定する
            yuclid_list = [Dc_yuclid[i][0] for i in not_matching_index] # 各匿名データに最も近い要素のユークリッド距離
            min_ = yuclid_list.index(min(yuclid_list))
            # print(min_)
            # 削除されたレコードが最小（=無限大が最小）とされた場合はそこで離脱
            if min_ == float('inf'):
                break
            match_index = not_matching_index[min_]

            # print(f'match {match_index} vs {Dc[match_index][0]}')
            correspond[match_index] = Dc[match_index][0]

            # マッチングしたインデックス（レコード番号）は次回以降の操作から除外
            del not_matching_index[min_]

            # 既にペアが決まった攻撃データのインデックスとユークリッド距離をDc, Dc_yuclidから削除
            delete_index_list = [] # 本処理中にnot_matching_indexから除外すべきインデックスが出たとき、
                                    # ここに記録し後からnot_matching_index上から削除
            for j in not_matching_index:
                current_Dc = Dc[j]
                if correspond[match_index] in current_Dc:
                    delete_index = current_Dc.index(correspond[match_index])
                    del Dc[j][delete_index]
                    del Dc_yuclid[j][delete_index]
                    # Dc_yuclidが空になる場合、対応する候補なし(インデックスは-1)として登録。not_matching_indexからも除外
                    if len(Dc[j]) == 0:
                        correspond[j] = -1
                        delete_index_list.append(j)

            not_matching_index = [k for k in not_matching_index if k not in delete_index_list]
            # print(len(not_matching_index))
            # 全ての匿名化データのペアが決定次第、whileを離脱
            if len(not_matching_index) == 0:
                flag_end = True


    return correspond
