import os
import copy
import pandas as pd
import Anonymize_sample as AS

# データ読み込み
# 最初のパスは各自のDataset_anonymize.csvのパスに合わせること
ano_data = pd.read_csv('./test4/dataset_4/team4_original.csv', encoding="shift-jis")

# -------------------------------------------------------------------------------------
# ファイル出力先とファイル名（必要に応じて変更すること）

out_path = './out_file' # ファイルパス
# 出力先ディレクトリを新規に作る場合は先に作成
if not os.path.isdir(out_path):
    os.makedirs(out_path)

dataset_name = f'{out_path}/team4_anonymized.csv' # データセットファイル名

# -------------------------------------------------------------------------------------

# 下記パラメータはAnonymize_sample使用時に必須のもの
# 自作する場合は使用する必要なし

generate_attr = ['職業', '年齢', '残高', "地域", "趣味"] # generalization()にかける属性名一覧（attr_depth.jsonに記載のあるもののみ指定）
k_anonymize_attr = ['職業', '年齢', '残高', "地域", "趣味"] # remove_record()で対象にする属性名一覧
numeric = ['年齢', '残高'] # 匿名化する数値属性一覧
category = ['職業', '結婚', '最終学歴', '債務不履行', '個人ローン', '住宅ローン', "地域", "趣味"] # 匿名化するカテゴリ属性一覧

epsilon = 10 # ε（プライバシーパラメータ）
k = 0 # k-匿名性のライン（同じ属性の組み合わせがk件以上あるレコードだけ使う）
first_depth = 1 # 階層（変更前）
convert_depth = 2 # 階層（変更後）
# -------------------------------------------------------------------------------------

# 一般化実行
gen_ano = AS.generalization(ano_data, generate_attr, first_depth, convert_depth)

# k-匿名性を守るようにレコード削除
rem_ano = AS.remove_record(gen_ano, k_anonymize_attr, k)

# 匿名化
copy_ano = copy.deepcopy(rem_ano) # コピー
copy_ano = copy_ano.dropna(how='all') # コピーしたデータセットから削除したレコードを引く
# 数値属性の匿名化
for n in numeric:
    values_col = copy_ano[n] # 1属性（列）を取得
    range_list = values_col.values.tolist() # 値だけリスト化
    # 匿名化はひとつの値ごとに行う
    # 匿名化した値はコピー元データに代入
    for i, val in enumerate(values_col):
        rem_ano.at[copy_ano.index[i], n] = AS.differential_l(val, range_list, epsilon) # 匿名化実行

# カテゴリ属性の匿名化（流れは数値と同じ）
for c in category:
    values_col = copy_ano[c]
    range_list = values_col.values.tolist()
    for i, val in enumerate(values_col):
        rem_ano.at[copy_ano.index[i], c] = AS.differential_e(val, range_list, epsilon) # 匿名化実行

# 出力前に値を元の階層に戻す
repro_ano = AS.generalization(rem_ano, generate_attr, convert_depth, first_depth)
# 匿名化後データセットの出力
# インデックスを削除、shift-jisエンコードで出力する
repro_ano.to_csv(dataset_name, index=False, encoding='shift-jis')
