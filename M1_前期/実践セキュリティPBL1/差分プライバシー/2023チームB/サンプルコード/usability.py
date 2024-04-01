import pandas as pd
import math

# カルバックライブラー情報量を求める
def get_KL_divergence(p,q):
    if p == 0 or q == 0:
        return 0
    else:
        return p * math.log2(p/q)

# D1:生データセット，D2:匿名化データセット
def get_KL_divergence_DB(D1, D2, dtype):
    KL_div = 0.0
    for column in D1.columns:
        # columnがカテゴリ型の場合
        if dtype[column] == 1:
            for att in D1[column].unique():
                D1_att_cnt = D1[column].value_counts()[att]
                if att in D2[column].unique():
                    D2_att_cnt = D2[column].value_counts()[att]
                else:
                    D2_att_cnt = 0
                KL_div += get_KL_divergence(D1_att_cnt/len(D1[column]), D2_att_cnt/len(D2[column]))
        # columnが数値型の場合
        else:
            # D1の階級幅を分類する（std/2づつで分類）
            D1_class_value = [min(D1[column])]
            D1_std = D1[column].std()
            v = min(D1[column])
            while v + D1_std / 2 <= max(D1[column]):
                v += D1_std / 2
                D1_class_value.append(v)
            D1_class_value.append(max(D1[column]))

            #各階級に属するデータにたいして差分を計算
            D1_class_cnt = D1[D1[column] < D1_class_value[0]].count()[column]
            D2_class_cnt = D2[D2[column] < D1_class_value[0]].count()[column]
            KL_div += get_KL_divergence(D1_class_cnt/len(D1[column]), D2_class_cnt/len(D2[column]))
            for i in range(len(D1_class_value)-1):
                D1_class_cnt = D1[(D1[column] >= D1_class_value[i]) & (D1[column] < D1_class_value[i+1])].count()[column]
                D2_class_cnt = D2[(D2[column] >= D1_class_value[i]) & (D2[column] < D1_class_value[i+1])].count()[column]
                KL_div += get_KL_divergence(D1_class_cnt/len(D1[column]), D2_class_cnt/len(D2[column]))
            D1_class_cnt = D1[D1[column] >= D1_class_value[-1]].count()[column]
            D2_class_cnt = D2[D2[column] >= D1_class_value[-1]].count()[column]
            KL_div += get_KL_divergence(D1_class_cnt/len(D1[column]), D2_class_cnt/len(D2[column]))

    return KL_div

# 二つのデータセットの差分を求める．
def get_diffs(D1, D2, dtype):
    diffs = []
    for column in D1.columns:
        diffs_column = []
        # columnがカテゴリ型の場合
        if dtype[column] == 1:
            for att in D1[column].unique():
                D1_att_cnt = D1[column].value_counts()[att]
                if att in D2[column].unique():
                    D2_att_cnt = D2[column].value_counts()[att]
                else:
                    D2_att_cnt = 0
                diffs_column.append(abs(D1_att_cnt - D2_att_cnt))
            diffs.append(diffs_column)

        # columnが数値型の場合
        else:
            # D1の階級幅を分類する（std/2づつで分類）
            D1_class_value = [min(D1[column])]
            D1_std = D1[column].std()
            v = min(D1[column])
            while v + D1_std / 2 <= max(D1[column]):
                v += D1_std / 2
                D1_class_value.append(v)
            D1_class_value.append(max(D1[column]))

            #各階級に属するデータにたいして差分を計算
            D1_class_cnt = D1[D1[column] < D1_class_value[0]].count()[column]
            D2_class_cnt = D2[D2[column] < D1_class_value[0]].count()[column]
            diffs_column.append(abs(D1_class_cnt - D2_class_cnt))
            for i in range(len(D1_class_value)-1):
                D1_class_cnt = D1[(D1[column] >= D1_class_value[i]) & (D1[column] < D1_class_value[i+1])].count()[column]
                D2_class_cnt = D2[(D2[column] >= D1_class_value[i]) & (D2[column] < D1_class_value[i+1])].count()[column]
                diffs_column.append(abs(D1_class_cnt - D2_class_cnt))
            D1_class_cnt = D1[D1[column] >= D1_class_value[-1]].count()[column]
            D2_class_cnt = D2[D2[column] >= D1_class_value[-1]].count()[column]
            diffs_column.append(abs(D1_class_cnt - D2_class_cnt))
            diffs.append(diffs_column)

    return diffs

def get_diffs_sum(diffs):
    diffs_sum_lst = sum(diffs, [])
    return sum(diffs_sum_lst)

# 実行例（自分の環境に応じて'filename1'，'filename2'を変更してください）
def main():
    # データセットの読み込み
    filename1 = 'teamB_original.csv'
    filename2 = 'teamB_noised.csv'
    D1 = pd.read_csv(filename1, encoding='shift-jis')
    D2 = pd.read_csv(filename2, encoding='shift-jis')

    # 各列のデータ型のリスト
    d_type_lst = [0,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1]    # 0:数値型，1:カテゴリ型
    # データ型の辞書（列の名前：データ型の対応）
    d_type = dict()
    for column in D1.columns:
        d_type[column] = d_type_lst.pop(0)

    # カルバックライブラー情報量を計算
    print("KL_divergence =" ,get_KL_divergence_DB(D1, D2, d_type))
    # 差分を計算
    diffs = get_diffs(D1, D2, d_type)
    print("diffs =", diffs)
    print("diffs_sum =", get_diffs_sum(diffs))

if __name__ == '__main__':
    main()