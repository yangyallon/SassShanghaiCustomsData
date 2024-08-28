import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")
import os
import sys
import config
import re

current_path = os.getcwd()
parent_path = os.path.abspath(os.path.dirname(os.getcwd()))
product = config.product
update_month = config.update_month


# 匹配中文字符
def findcn(name):
    res = re.findall("[\u4e00-\u9fa5]*", name)
    for pro in res:
        if len(pro) > 0:
            break
        else:
            pass
    return pro


# 将带逗号的数转化成数值，如果本身是数值，则不变
def str_to_num(x):
    try:
        return float(x.replace(",", ""))
    except:
        return x


def int_trans(digit):
    x = filter(str.isdigit, digit)
    x = float("".join(list(x)))
    x = x / 100000000
    x = round(x, 2)
    return x


# 处理全国海关进出口数据
def get_custom_all(parent_path):

    year, imoex, value = [], [], []

    for y in [2019, 2020, 2021, 2022, 2023, 2024]:
        data = pd.read_excel(f"{parent_path}\\data\\全国海关数据\\{y}.xls")
        ex = data.loc[2, "Unnamed: 2"]
        im = data.loc[2, "Unnamed: 4"]
        exvalue = round(data.loc[4, "Unnamed: 3"] / 10000, 2)
        imvalue = round(data.loc[4, "Unnamed: 5"] / 10000, 2)

        year.append(y)
        year.append(y)
        imoex.append(im)
        imoex.append(ex)
        value.append(imvalue)
        value.append(exvalue)

    df_all = pd.DataFrame({"年份": year, "出口or进口": imoex, "全国总额": value})
    df_all_pt = pd.pivot_table(
        df_all, index=["年份"], values="全国总额", aggfunc=np.sum
    )
    df_all_pt["出口or进口"] = "进出口"
    df_all_pt = df_all_pt.reset_index()
    df_all = pd.concat([df_all, df_all_pt], axis=0, ignore_index=True)

    return df_all


# 处理上海海关进出口数据
def get_custom_sh(parent_path, df_all):

    year, imex, value, percent = [], [], [], []

    dir_list = os.listdir(parent_path + "\\data\\上海海关分贸易方式")
    for dirname in dir_list:
        data = pd.read_excel(parent_path + "\\data\\上海海关分贸易方式\\" + dirname)
        y = dirname[0:4]
        year += [y] * 3
        imex = imex + ["进出口", "出口", "进口"]

        if y in ["2021", "2022", "2023", "2024"]:
            percent.append(round(data.loc[3, "Unnamed: 4"], 2))
            percent.append(round(data.loc[3, "Unnamed: 8"], 2))
            percent.append(round(data.loc[3, "Unnamed: 12"], 2))

            value.append(round(data.loc[3, "Unnamed: 3"], 2))
            value.append(round(data.loc[3, "Unnamed: 7"], 2))
            value.append(round(data.loc[3, "Unnamed: 11"], 2))

        else:
            percent.append(round(data.loc[3, "Unnamed: 2"], 2))
            percent.append(round(data.loc[3, "Unnamed: 6"], 2))
            percent.append(round(data.loc[3, "Unnamed: 10"], 2))

            value.append(round(data.loc[3, "Unnamed: 1"], 2))
            value.append(round(data.loc[3, "Unnamed: 5"], 2))
            value.append(round(data.loc[3, "Unnamed: 9"], 2))

    df_trade = pd.DataFrame(
        {"年份": year, "进口or出口": imex, "金额": value, "同比": percent}
    )
    df_all["年份"] = df_all["年份"].astype("str")
    res = df_all.merge(
        df_trade,
        left_on=["出口or进口", "年份"],
        right_on=["进口or出口", "年份"],
        how="left",
    )
    res["金额"] = round(res["金额"], 2)
    res.loc[res["金额"] > 10000000, "金额"] = (
        res.loc[res["金额"] > 10000000, "金额"] / 10000
    )
    res["上海占比全国"] = res["金额"] / res.全国总额 * 100
    res.sort_values(by=["出口or进口"], ascending=[True], inplace=True)
    res.drop("进口or出口", axis=1, inplace=True)
    return res


# 处理上海重点商品数据
def get_product_sh(parent_path):
    dir_list = os.listdir(parent_path + "\data\上海海关数据")
    df_product_sh = pd.DataFrame()
    for dirname in dir_list:
        data = pd.read_excel(parent_path + "\data\上海海关数据/" + dirname, header=3)
        data.商品编码8位 = data.商品编码8位.apply(lambda x: x.strip())
        data["商品"] = data.商品编码8位.apply(lambda x: findcn(x))
        data = data[data["商品"].isin(product)]
        data = data[["商品", "人民币(万).1", "人民币同比(%).1"]]
        data.index = range(len(data))
        data.columns = ["商品", "金额", "同比"]
        data["金额"] = data["金额"] / 10000
        data["进口or出口"] = dirname[7:9]
        data["年份"] = dirname[0:4]
        df_product_sh = pd.concat([df_product_sh, data], axis=0, ignore_index=True)

    df_sh = pd.read_excel(r"../output/2.1结果.xlsx")
    df_sh["进口or出口"] = df_sh["出口or进口"]
    df_sh["上海金额"] = df_sh["金额"]
    df_sh.年份 = df_sh.年份.astype("str")
    df_product_sh = df_product_sh.merge(
        df_sh[["年份", "进口or出口", "上海金额"]], on=["年份", "进口or出口"], how="left"
    )
    df_product_sh["占上海比重"] = df_product_sh["金额"] / df_product_sh["上海金额"]

    return df_product_sh


# 处理全国重点商品数据
def get_product_all(parent_path):

    df_product_all = pd.DataFrame()
    dir_list = os.listdir(parent_path + "\data\全国海关数据")
    for dirname in dir_list:
        if len(dirname) < 10:
            pass
        else:
            data = pd.read_excel(
                parent_path + "\data\全国海关数据/" + dirname, header=3
            )
            data.商品名称 = data.商品名称.astype("str")
            data["商品"] = data.商品名称.apply(lambda x: findcn(x))
            data = data[data["商品"].isin(product)]
            data = data[["商品", "Unnamed: 6", "Unnamed: 10"]]
            data.index = range(len(data))
            data.columns = ["商品", "金额", "同比"]
            data["金额"] = data["金额"].apply(lambda x: str_to_num(x))
            data["金额"] = data["金额"].astype("int")
            data["金额"] = data["金额"] / 10000
            data["进口or出口"] = dirname[6:8]
            data["年份"] = dirname[0:4]
            df_product_all = pd.concat([df_product_all, data], axis=0)
    df_product_all.rename(
        columns={"金额": "全国金额", "同比": "全国同比"}, inplace=True
    )
    return df_product_all


# 拼接上海和全国重点商品数据
def get_res_product(df_product_sh, df_product_all):
    res = df_product_sh.merge(
        df_product_all, on=["商品", "进口or出口", "年份"], how="left"
    )
    res["上海占全国比重"] = res["金额"] / res["全国金额"]
    res.drop_duplicates(inplace=True)
    res.rename(
        columns={
            "金额": "上海进出口该商品金额",
            "同比": "上海同比",
            "上海金额": "上海进出口商品总额",
            "全国金额": "全国进出口该商品金额",
        },
        inplace=True,
    )
    res["年份"] = res["年份"].astype("int")
    res["商品"].replace(
        "自动数据处理设备及其部件", "自动数据处理设备及其零部件", inplace=True
    )
    res["占上海比重"] = res["占上海比重"] * 100
    res["上海占全国比重"] = res["上海占全国比重"] * 100
    return res


# 处理上海海关分贸易方式的数据
def get_data_trade(parent_path):
    dirlist = os.listdir(parent_path + "\data\上海海关分贸易方式")
    data_trade = pd.DataFrame()
    for dirname in dirlist:
        data = pd.read_excel(parent_path + "\data\上海海关分贸易方式/" + dirname)
        data.columns = [
            "Unnamed: 0",
            "Unnamed: 1",
            "Unnamed: 2",
            "Unnamed: 3",
            "Unnamed: 4",
            "Unnamed: 5",
            "Unnamed: 6",
            "Unnamed: 7",
            "Unnamed: 8",
            "Unnamed: 9",
            "Unnamed: 10",
            "Unnamed: 11",
            "Unnamed: 12",
        ]
        data = data.loc[[3, 4, 7, 17], ["Unnamed: 0", "Unnamed: 5", "Unnamed: 9"]]
        data.columns = ["贸易方式", "出口", "进口"]
        data_new = pd.melt(
            data,
            id_vars=["贸易方式"],
            value_vars=["出口", "进口"],
            var_name="进出口",
            value_name="金额",
        )
        data_new["年份"] = dirname[0:4]
        data_trade = pd.concat([data_new, data_trade], axis=0, ignore_index=True)
    return data_trade


# 处理上海重点进出口商品
def important_product(parent_path):

    country_name = pd.read_excel(parent_path+r"\data\country_name.xlsx")
    # 去除字符串中的空格
    country_name["中文名称"] = country_name["中文名称"].str.replace(" ", "")
    country_name_map = dict(zip(country_name["中文名称"], country_name["大洲"]))

    for product in ["集成电路", "笔记本电脑", "锂离子蓄电池", "电动载人汽车"]:
        if product == "集成电路":
            eximlist = ["进口", "出口"]
        else:
            eximlist = ["出口"]
        for exim in eximlist:
            df_product = pd.DataFrame()
            for year in ["2019", "2022", "2023", "2024"]:
                df = pd.read_csv(
                    parent_path
                    + r"\data\上海重点进出口商品/"
                    + r"%s%s%s.csv" % (year, product, exim),
                    encoding="gbk",
                )
                df["人民币"] = df["人民币"].apply(lambda x: int_trans(x))
                df_pt = pd.pivot_table(
                    df[["贸易伙伴名称", "人民币"]],
                    index="贸易伙伴名称",
                    values="人民币",
                    aggfunc=np.sum,
                ).reset_index()
                df_pt["年份"] = year
                df_product = pd.concat([df_pt, df_product], axis=0, ignore_index=True)

            print(product + exim)
            df_2019 = df_product[df_product["年份"] == "2019"]
            # df_2020 = df_product[df_product["年份"] == "2020"]
            # df_2021 = df_product[df_product["年份"] == "2021"]
            df_2022 = df_product[df_product["年份"] == "2022"]
            df_2023 = df_product[df_product["年份"] == "2023"]
            df_2024 = df_product[df_product["年份"] == "2024"]

            df_2019["2019年占比"] = df_2019["人民币"] / df_2019["人民币"].sum()
            # df_2020["2020年占比"] = df_2020["人民币"] / df_2020["人民币"].sum()
            # df_2021["2021年占比"] = df_2021["人民币"] / df_2021["人民币"].sum()
            df_2022["2022年占比"] = df_2022["人民币"] / df_2022["人民币"].sum()
            df_2023["2023年1-11月占比"] = df_2023["人民币"] / df_2023["人民币"].sum()
            df_2024[f"2024年1-{update_month}占比"] = (
                df_2024["人民币"] / df_2024["人民币"].sum()
            )

            df_2019.rename(columns={"人民币": "2019年金额"}, inplace=True)
            # df_2020.rename(columns={"人民币": "2020年金额"}, inplace=True)
            # df_2021.rename(columns={"人民币": "2021年金额"}, inplace=True)
            df_2022.rename(columns={"人民币": "2022年金额"}, inplace=True)
            df_2023.rename(columns={"人民币": "2023年1-11月金额"}, inplace=True)
            df_2024.rename(
                columns={"人民币": f"2024年1-{update_month}金额"}, inplace=True
            )

            # res = df_2019.merge(df_2020, on="贸易伙伴名称", how="outer")
            # res = res.merge(df_2021, on="贸易伙伴名称", how="outer")
            res = df_2019.merge(df_2022, on="贸易伙伴名称", how="outer")
            res = res.merge(df_2023, on="贸易伙伴名称", how="outer")
            res = res.merge(
                df_2024, on="贸易伙伴名称", how="outer", suffixes=["_dd", "_ss"]
            )
            res = res[
                [
                    "贸易伙伴名称",
                    "2019年金额",
                    "2019年占比",
                    # "2020年金额",
                    # "2020年占比",
                    # "2021年金额",
                    # "2021年占比",
                    "2022年金额",
                    "2022年占比",
                    # "2023年占比",
                    "2023年1-11月金额",
                    "2023年1-11月占比",
                    f"2024年1-{update_month}金额",
                    f"2024年1-{update_month}占比",
                ]
            ]
            res = res.fillna(0)
            res.sort_values(by="2023年1-11月占比", ascending=False, inplace=True)
            res["大洲"] = res["贸易伙伴名称"].map(country_name_map)

            res.to_excel(r"../output/%s%s.xlsx" % (product, exim), index=False)

        df_2023_ = pd.read_csv(
            parent_path
            + f"\data\上海重点进出口商品/"
            + f"2023年1-{update_month}电动载人汽车出口.csv",
            encoding="gbk",
        )
        df_2023_["人民币"] = df_2023_["人民币"].apply(lambda x: int_trans(x))
        df_pt = pd.pivot_table(
            df_2023_[["贸易伙伴名称", "人民币"]],
            index="贸易伙伴名称",
            values="人民币",
            aggfunc=np.sum,
        ).reset_index()
        df_pt[f"2023年1-{update_month}占比"] = df_pt["人民币"] / df_pt["人民币"].sum()
        df_pt.merge(
            df_2024,
            on="贸易伙伴名称",
            how="outer",
        ).to_excel(f"..//output/2023与2024年1到{update_month}.xlsx", index=False)



