import pandas as pd
import Anonymize_sample as anonymize
import random
import numpy as np
import usability
import copy

def anonymize_all(origD, eps_list, def_dom, prev_campaign_scale):
    for column in eps_list.keys():
        if column == "年齢":
            for i in range(len(origD[column])):
                # print(origD)
                # print(origD.loc[i, column])
                origD.loc[i, column] = anonymize.differential_l(origD[column][i], def_dom[column], eps_list[column])
                if origD.loc[i, column] < 20:
                    origD.loc[i, column] = 20
                elif origD.loc[i, column] >= 80:
                    origD.loc[i, column] = 80
                # print(origD.loc[i, column])
                origD.loc[i, column] = generalize_age(origD[column][i], column)
                origD.loc[i, column] = random.randint(origD[column][i], origD[column][i] + 9)
        elif column == "地域":
            for i in range(len(origD[column])):
                removed_value = set(["静岡", "神奈川"])
                if origD[column][i] in removed_value:
                    origD.loc[i, column] = random.choice(list(def_dom[column] - removed_value))
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column] - removed_value, eps_list[column])
        elif column == "趣味":
            for i in range(len(origD[column])):
                removed_value = set(["ゲーム", "旅行"])
                if origD[column][i] in removed_value:
                    origD.loc[i, column] = random.choice(list(def_dom[column] - removed_value))
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column] - removed_value, eps_list[column])
        elif column == "職業":
            removed_value = set(["学生", "起業家", "自営業", "失業中", "家政婦"])
            for i in range(len(origD[column])):
                if origD[column][i] in removed_value:
                    origD.loc[i, column] = random.choice(list(def_dom[column] - removed_value))
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column] - removed_value, eps_list[column])
        elif column == "結婚":
            removed_value = set(["離婚または死別"])
            for i in range(len(origD[column])):
                if origD[column][i] in removed_value:
                    origD.loc[i, column] = random.choice(list(def_dom[column] - removed_value))
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column] - removed_value, eps_list[column])
        elif column == "最終学歴":
            removed_value = set(["不明"])
            for i in range(len(origD[column])):
                if origD[column][i] in removed_value:
                    origD.loc[i, column] = random.choice(list(def_dom[column] - removed_value))
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column] - removed_value, eps_list[column])
        elif column == "債務不履行":
            removed_value = set(["あり"])
            for i in range(len(origD[column])):
                if origD[column][i] in removed_value:
                    origD.loc[i, column] = random.choice(list(def_dom[column] - removed_value))
        elif column == "残高":      
            for i in range(len(origD[column])):
                origD.loc[i, column] = anonymize.differential_l(origD[column][i], def_dom[column], eps_list[column])
            origD = generalize_and_return(origD, column)
        elif column == "住宅ローン":
            for i in range(len(origD[column])):
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column], eps_list[column])
        elif column == "個人ローン":
            for i in range(len(origD[column])):
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column], eps_list[column])
        elif column == "連絡手段":
            removed_value = set(["固定電話"])
            for i in range(len(origD[column])):
                if origD[column][i] in removed_value:
                    origD.loc[i, column] = random.choice(list(def_dom[column] - removed_value))
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column] - removed_value, eps_list[column])
        elif column == "最近の連絡日（日）":
            for i in range(len(origD[column])):
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column], eps_list[column])
        elif column == "最近の連絡日（月）":
            removed_value = set(["1月", "12月"])
            for i in range(len(origD[column])):
                if origD[column][i] in removed_value:
                    origD.loc[i, column] = random.choice(list(def_dom[column] - removed_value))
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column] - removed_value, eps_list[column])
        elif column == "通話時間（秒）":
            for i in range(len(origD[column])):
                origD.loc[i, column] = int(anonymize.differential_l(origD[column][i], def_dom[column], eps_list[column]))
            origD = generalize_and_return(origD, column)
        elif column == "キャンペーン連絡回数":
            removed_value = set(["13", "15", "19"])
            for i in range(len(origD[column])):
                if origD[column][i] in removed_value:
                    origD.loc[i, column] = random.choice(list(def_dom[column] - removed_value))
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column] - removed_value, eps_list[column])
        elif column == "前回のキャンペーン連絡からの経過日数":
            removed_value = set(["8", "52", "87", "97", "98", "127", "155", "181", "182", "183", "185", "195", "197", "256", "297", "346", "359", "680", "842"])
            for i in range(len(origD[column])):
                origD.loc[i, column] = -1
            rep_idx_list = random.sample(range(100), 19)
            for idx in rep_idx_list:
                # origD.loc[idx, column] = int(abs(np.random.normal(loc=0.0, scale=passing_days_scale, size=1)[0]))
                origD.loc[idx, column] = int(abs(anonymize.differential_l(origD.loc[idx, column], def_dom[column], eps_list[column])))
        elif column == "キャンペーン前の連絡回数":
            removed_value = set(["1", "2", "3", "4", "5", "6"])
            for i in range(len(origD[column])):
                origD.loc[i, column] = 0
            rep_idx_list = random.sample(range(100), 19)
            for idx in rep_idx_list:
                origD.loc[idx, column] = int(abs(anonymize.differential_l(origD.loc[idx, column], def_dom[column], eps_list[column])))
        elif column == "前回キャンペーンの成果":
            removed_value = set(["成功", "失敗", "その他"])
            for i in range(len(origD[column])):
                    origD.loc[i, column] = "不明"
            rep_idx_list = random.sample(range(100), 19)
            for idx in rep_idx_list:
                origD.loc[idx, column] = int(np.random.normal(loc=0.5, scale=prev_campaign_scale, size=1)[0])
                if origD.loc[idx, column] == -1:
                    origD.loc[idx, column] = "成功"
                elif origD.loc[idx, column] == 0:
                    origD.loc[idx, column] = "失敗"
                elif origD.loc[idx, column] == 1:
                    origD.loc[idx, column] = "その他"
                else:
                    origD.loc[idx, column] = "失敗"
        elif column == "新キャンペーンの成果":
            for i in range(len(origD[column])):
                origD.loc[i, column] = anonymize.differential_e(origD[column][i], def_dom[column], eps_list[column])
        
    return origD




def generalize_age(data, column):
    if column == "年齢":
        data = 10 * (data // 10)
        return data

def generalize_and_return(origD, column):
    origD_class_value = [min(origD[column])]
    origD_std = origD[column].std()
    v = min(origD[column])
    while v + origD_std / 2 <= max(origD[column]):
        v += origD_std / 2
        origD_class_value.append(v)
    origD_class_value.append(max(origD[column]))

    for i in range(len(origD[column])):
        for j in range(len(origD_class_value) - 1):
            if origD_class_value[j] <= origD[column][i] < origD_class_value[j + 1]:
                origD.loc[i, column] = int(random.uniform(origD_class_value[j], origD_class_value[j + 1]))
                break
    return origD

def main():
    filename = "teamB_original.csv"
    origD = pd.read_csv(filename, encoding='shift-jis')
    origD_copy = copy.deepcopy(origD)
    
    def_dom = dict()
    for column in origD.columns:
        def_dom[column] = set(origD[column])

    # passing_days_scale = 100.0
    # calling_times_scale = 1.0
    prev_campaign_scale = 1.0
    eps_list = {
    "年齢": 20.0,
    "地域": 5.0,
    "趣味": 5.0,
    "職業": 7.0,
    "結婚": 1.0,
    "最終学歴": 2.0,
    "債務不履行": 1.0,
    "残高": 30.0,
    "住宅ローン": 2.0,
    "個人ローン": 10.0,
    "連絡手段": 5.0,
    "最近の連絡日（日）": 5.0,
    "最近の連絡日（月）": 5.0,
    "通話時間（秒）": 30.0,
    "キャンペーン連絡回数": 10.0,
    "前回のキャンペーン連絡からの経過日数": 3.0,
    "キャンペーン前の連絡回数": 10.0,
    "前回キャンペーンの成果": 1.0,
    "新キャンペーンの成果": 2.0
    }

    noisedD = anonymize_all(origD, eps_list, def_dom, prev_campaign_scale)
    noisedD.to_csv("teamB_noised.csv", index=False, encoding='shift-jis')

    eps_df = pd.DataFrame(eps_list, index=[0])
    eps_df.to_csv("eps_list.csv", index=False, encoding='shift-jis')

    # 各列のデータ型のリスト
    d_type_lst = [0,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1]    # 0:数値型，1:カテゴリ型
    # データ型の辞書（列の名前：データ型の対応）
    d_type = dict()
    for column in origD_copy.columns:
        d_type[column] = d_type_lst.pop(0)

    # カルバックライブラー情報量を計算
    print("origD =", origD)
    print("noisedD =", noisedD)
    print("KL_divergence =" ,usability.get_KL_divergence_DB(origD_copy, noisedD, d_type))
    # 差分を計算
    diffs = usability.get_diffs(origD_copy, noisedD, d_type)
    print("diffs =", diffs)
    diffs_column = dict()
    for column, idx in zip(origD_copy.columns, range(len(origD_copy.columns))):
        diffs_column[column] = sum(diffs[idx])
    print("diffs_column =", diffs_column)
    print("diffs_sum =", usability.get_diffs_sum(diffs))

if __name__=="__main__":
    main()