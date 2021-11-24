import glob
import locale
import pandas as pd
import tabula
from tqdm import tqdm

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def read_and_reshape_salary(filepath):
    # pandas_options={'header': None}でデータが列名になるのを防いで列名揃える
    dfs = tabula.io.read_pdf(
        filepath, lattice=True, pages='all',
        pandas_options={'header': None}, silent=True)
    key_list = [x for x in range(len(dfs))]

    # 列名揃えたんでdfは縦に積む
    df = pd.concat(dfs, axis=0, keys=key_list)

    # 縦に積んだとはいえ4列になっているのでさらに2列に積みなおす
    df_salary = {}
    for i in range(int(len(df.columns) / 2)):
        if i == 0:
            df_salary = df.iloc[:, [0, 1]]
        else:
            df_salary = pd.concat(
                [df_salary,
                 df.iloc[:, [2 * i, 2 * i + 1]].rename(
                     columns={2 * i: 0, 2 * i + 1: 1})],
                axis=0)

    # 空白行削除
    df_salary = df_salary.dropna(how='any').sort_index()
    df_salary = df_salary.reset_index(
        level=1, drop=True).set_index(0, append=True)

    # 横に並べ替える
    df_salary_t = df_salary.transpose().reset_index()
    df_salary_t.columns = [
        '_'.join(map(str, col)) for col in df_salary_t.columns]
    df_salary_t = df_salary_t.drop(columns='_index')
    return df_salary_t


#  main code ------------------------------------------

if __name__ == '__main__':
    salary_dir = "data"
    files = glob.glob(salary_dir + r'*\**\*.pdf', recursive=True)
    li = []
    for file in tqdm(files):
        li.append(read_and_reshape_salary(file))
    df_summary = pd.concat(li, axis=0)
    df_summary = df_summary.drop_duplicates(
        subset=['0_支給年月日', '5_控除後支給額'],
        keep='first')
    df_summary = df_summary.set_index('0_支給年月日').sort_index()
    df_summary = df_summary[sorted(df_summary.columns)]
    df_summary.to_csv('salary.csv', encoding="shift jis")
    print(df_summary)
    pass
