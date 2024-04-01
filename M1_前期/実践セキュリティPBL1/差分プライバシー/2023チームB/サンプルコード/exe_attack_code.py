import pandas as pd
import os
import Attack as AT

# データセット読み込み(パスは各自で変更)
ano_data = pd.read_csv('./input_file4/team4_anonymized.csv', encoding="shift-jis") # 他チームが匿名化したデータセット
ata_data = pd.read_csv('./test4/dataset_4/team4_candidate.csv', encoding="shift-jis") # 攻撃対象

# -------------------------------------------------------------------------------------
# ファイル出力先とファイル名（必要に応じて変更すること）

out_path = './out_file' # ファイルパス
# 出力先ディレクトリを新規に作る場合は先に作成
if not os.path.isdir(out_path):
    os.makedirs(out_path)

correspond_name = f'{out_path}/team4_attacked.csv' # 対応表ファイル名

# -------------------------------------------------------------------------------------
# 下記のパラメータはサンプル攻撃方法の実行に必須

target_attr = ['年齢', '職業', '最終学歴', '個人ローン', '住宅ローン', "地域", "趣味"] # 攻撃時に参照する属性名一覧

n = 5 # neighbor_att()で抽出する候補の数
dup_flag = False # attack_id()にて対応表のインデックス重複を許容するか否か

# -------------------------------------------------------------------------------------
# 攻撃実行
Dc, Dc_yuclid = AT.neighbor_att(ano_data, ata_data, target_attr, n) # ユークリッド距離が近いn件を抜き出す
correspond = AT.attack_id(Dc, Dc_yuclid, duplication=dup_flag) # 重複ありor無で候補を1対1に絞る

# correspondを2D, pandas化し、匿名データ/攻撃データの対応表として形を整える
correspond_2d = [[i, j] for i, j in enumerate(correspond)]
correspond_df = pd.DataFrame(correspond_2d, columns=['匿名化データ', '攻撃データ'])
print(correspond_df)
# 出力
correspond_df.to_csv(correspond_name, index=False, encoding='shift-jis')
