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


def table1_output():
    ## 表1-近五年上海进出口额及占全国比重变化
    table_01 = pd.read_excel(parent_path + r"\output\2.1结果.xlsx")

    table_1_1 = (
        pd.pivot_table(table_01, index="出口or进口", columns="年份", values="金额")
        .reset_index()
        .replace({"出口": "上海出口额", "进口": "上海进口额", "进出口": "上海进出口额"})
        .rename(columns={"出口or进口": "金额/占比"})
    )

    table_1_2 = (
        pd.pivot_table(table_01, index="出口or进口", columns="年份", values="同比")
        .reset_index()
        .replace({"出口": "出口同比", "进口": "进口同比", "进出口": "进出口同比"})
        .rename(columns={"出口or进口": "金额/占比"})
    )

    table_1_3 = (
        pd.pivot_table(
            table_01, index="出口or进口", columns="年份", values="上海占比全国"
        )
        .reset_index()
        .replace(
            {
                "出口": "出口占全国比重",
                "进口": "进口占全国比重",
                "进出口": "进出口占全国比重",
            }
        )
        .rename(columns={"出口or进口": "金额/占比"})
    )

    res_table = pd.concat(
        [table_1_1, table_1_2, table_1_3], axis=0, ignore_index=True
    ).round(2)
    res_table.to_excel(
        f"..//result/{update_month}/表1-近五年上海进出口额及占全国比重变化.xlsx",
        index=False,
    )

    return res_table


def table2_output():

    ## 表2-近五年上海重点产品出口金额及增长情况

    table_2 = pd.read_excel(r"..\output\2.2结果.xlsx")
    table_export_num = pd.pivot_table(
        data=table_2[table_2["进口or出口"] == "出口"],
        index=["商品"],
        columns=["年份"],
        values=["上海进出口该商品金额", "上海同比"],
    )
    export_product = [
        "机电产品",
        "高新技术产品",
        "集成电路",
        "电动载人汽车",
        "汽车零配件",
        "自动数据处理设备及其零部件",
        "笔记本电脑",
        "手机",
        "锂离子蓄电池",
        "太阳能电池",
        "生命科学技术",
    ]

    table_export_num[table_export_num.index.isin(export_product)].round(2).to_excel(
        f"../result/{update_month}/表2-近五年上海重点产品出口金额及增长情况.xlsx"
    )
    return table_export_num[table_export_num.index.isin(export_product)].round(2)


def table3_output():
    ## 表3-近五年上海重点产品出口占上海及全国比重变化(%)
    table_2 = pd.read_excel(r"..\output\2.2结果.xlsx")
    table_export_ratio = pd.pivot_table(
        data=table_2[table_2["进口or出口"] == "出口"],
        index=["商品"],
        columns=["年份"],
        values=["占上海比重", "上海占全国比重"],
    )
    export_product = [
        "机电产品",
        "高新技术产品",
        "集成电路",
        "电动载人汽车",
        "汽车零配件",
        "自动数据处理设备及其零部件",
        "笔记本电脑",
        "手机",
        "锂离子蓄电池",
        "太阳能电池",
        "生命科学技术",
    ]

    table_export_ratio[table_export_ratio.index.isin(export_product)].round(1).to_excel(
        f"../result/{update_month}/表3-近五年上海重点产品出口占上海及全国比重变化(%).xlsx"
    )

    return table_export_ratio[table_export_ratio.index.isin(export_product)].round(1)


def table4_output():
    # 表4-2019-2024年上海电动载人汽车出口目的地金额及占比（亿元）
    df_2023 = pd.read_excel(f"../output/2023与2024年1到{update_month}.xlsx")
    df_2023.rename(columns={"贸易伙伴名称": "贸易伙伴"}, inplace=True)
    df_2023[f"2024年1-{update_month}同比"] = (
        df_2023[f"2024年1-{update_month}金额"] - df_2023["人民币"]
    ) / df_2023["人民币"]

    table_v4_history = pd.read_excel(
        r"..\data\表4历史数据.xlsx",
        usecols=[
            "贸易伙伴",
            "2019年金额",
            "2019年占比",
            "2020年金额",
            "2020年占比",
            "2021年金额",
            "2021年占比",
            "2022年金额",
            "2022年占比",
            "2023年金额",
            "2023年占比",
        ],
    )

    table_v4_history = table_v4_history.merge(
        df_2023[
            [
                "贸易伙伴",
                f"2024年1-{update_month}金额",
                f"2024年1-{update_month}占比",
                f"2024年1-{update_month}同比",
            ]
        ],
        on="贸易伙伴",
        how="left",
    )

    for ratio in [
        "2019年占比",
        "2020年占比",
        "2021年占比",
        "2022年占比",
       "2023年占比",
        f"2024年1-{update_month}占比",
        f"2024年1-{update_month}同比",
    ]:
        # 将'values'列转换为百分比
        table_v4_history[ratio] = table_v4_history[ratio] * 100
        table_v4_history[ratio] = table_v4_history[ratio].apply(lambda x: f"{x:.2f}%")

        table_v4_history.to_excel(
            f"../result/{update_month}/表4-2019-2024年上海电动载人汽车出口目的地金额及占比（亿元）.xlsx",
            index=False,
        )

    return table_v4_history


def table5_output():
    table_5 = pd.read_excel(
        r"../output//锂离子蓄电池出口.xlsx",
    )
    table_v5_history = pd.read_excel(
        r"..\data\表5历史数据.xlsx",
        usecols=[
            "贸易伙伴名称",
            "2019年金额",
            "2019年占比",
            "2022年金额",
            "2022年占比",
            "2023年金额",
            "2023年占比",
        ],
    )

    table_v5_history = table_v5_history.merge(
        table_5[
            [
                "贸易伙伴名称",
                f"2024年1-{update_month}金额",
                f"2024年1-{update_month}占比",
            ]
        ],
        on="贸易伙伴名称",
        how="left",
    )
    for ratio in [
        "2019年占比",
        "2022年占比",
        "2023年占比",
        f"2024年1-{update_month}占比",
    ]:
        # 将'values'列转换为百分比
        table_v5_history[ratio] = table_v5_history[ratio] * 100
        table_v5_history[ratio] = table_v5_history[ratio].apply(lambda x: f"{x:.2f}%")

        table_v5_history.to_excel(
            f"../result/{update_month}/表5-2019-2024年上海锂离子蓄电池出口目的地金额及占比（亿元）.xlsx",
            index=False,
        )

    return table_v5_history


def table6_output():
    table_6 = pd.read_excel(
        r"../output//笔记本电脑出口.xlsx",
    )
    table_v6_history = pd.read_excel(
        r"..\data\表6历史数据.xlsx",
        usecols=[
            "贸易伙伴名称",
            "2019年金额",
            "2019年占比",
            "2022年金额",
            "2022年占比",
            "2023年金额",
            "2023年占比",
        ],
    )

    table_v6_history = table_v6_history.merge(
        table_6[
            [
                "贸易伙伴名称",
                f"2024年1-{update_month}金额",
                f"2024年1-{update_month}占比",
            ]
        ],
        on="贸易伙伴名称",
        how="left",
    )
    for ratio in [
        "2019年占比",
        "2022年占比",
        "2023年占比",
        f"2024年1-{update_month}占比",
    ]:
        # 将'values'列转换为百分比
        table_v6_history[ratio] = table_v6_history[ratio] * 100
        table_v6_history[ratio] = table_v6_history[ratio].apply(lambda x: f"{x:.2f}%")

        table_v6_history.to_excel(
            f"../result/{update_month}/表6-2019-2024年上海笔记本电脑出口目的地金额及占比（亿元）.xlsx",
            index=False,
        )

    return table_v6_history


def table7_output():
    table_7 = pd.read_excel(r"..\output\2.2结果.xlsx")
    table_import_num = pd.pivot_table(
        data=table_7[table_7["进口or出口"] == "进口"],
        index=["商品"],
        columns=["年份"],
        values=["上海进出口该商品金额", "上海同比"],
    )
    import_product = [
        "机电产品",
        "高新技术产品",
        "集成电路",
        "农产品",
        "食品",
        "美容化妆品及洗护用品",
        "金属矿及矿砂",
        "生命科学技术",
        "计量检测分析自控仪器器具",
        "医疗仪器器械",
        "乘用车"
    ]
    print(table_import_num.index)

    table_import_num[table_import_num.index.isin(import_product)].round(2).to_excel(
        f"../result/{update_month}/表7-近五年上海重点产品进口金额及增长情况 （亿元，%）.xlsx"
    )

    return table_import_num[table_import_num.index.isin(import_product)].round(2)


def table8_output():
    table_8 = pd.read_excel(r"..\output\2.2结果.xlsx")
    table_import_num = pd.pivot_table(
        data=table_8[table_8["进口or出口"] == "进口"],
        index=["商品"],
        columns=["年份"],
        values=["占上海比重", "上海占全国比重"],
    )
    import_product = [
        "机电产品",
        "高新技术产品",
        "集成电路",
        "农产品",
        "食品",
        "美容化妆品及洗护用品",
        "金属矿及矿砂",
        "生命科学技术",
        "计量检测分析自控仪器器具",
        "医疗仪器器械",
        "乘用车"
    ]

    table_import_num[table_import_num.index.isin(import_product)].round(2).to_excel(
        f"../result/{update_month}/表8-近五年上海重点产品进口占上海及全国比重变化（亿元）.xlsx"
    )


def table9_output():
    table_9 = pd.read_excel(
        r"../data/上海海关分国别/2024上海进出口分国别.xls",
    )
    table_9 = table_9[
        [
            f"本市2：2024年1至{update_month}进出口商品国别（地区）总值表（人民币值）",
            "Unnamed: 3",
            "Unnamed: 4",
            "Unnamed: 7",
            "Unnamed: 8",
            "Unnamed: 11",
            "Unnamed: 12",
        ]
    ]
    table_9.columns = [
        "2024贸易伙伴",
        "2024进出口金额",
        "2024进出口同比",
        "2024出口金额",
        "2024出口同比",
        "2024进口金额",
        "2024进口同比",
    ]
    table_9 = table_9.loc[3:, :]
    table_9["2024进出口占比"] = (
        table_9["2024进出口金额"]
        / table_9.loc[table_9["2024贸易伙伴"] == "总值", "2024进出口金额"].values[0]
    )
    table_9["2024出口占比"] = (
        table_9["2024出口金额"]
        / table_9.loc[table_9["2024贸易伙伴"] == "总值", "2024出口金额"].values[0]
    )
    table_9["2024进口占比"] = (
        table_9["2024进口金额"]
        / table_9.loc[table_9["2024贸易伙伴"] == "总值", "2024进口金额"].values[0]
    )
    table_9_history = pd.read_excel(
        r"../data/表9历史数据.xlsx",
        usecols=[
            "序号",
            "2019贸易伙伴",
            "2019进出口",
            "2019占比",
            "2023贸易伙伴",
            "2023进出口",
            "2023占比",
            "2024贸易伙伴",
        ],
    )
    table_9_9 = table_9[
        table_9["2024贸易伙伴"].isin(table_9_history["2024贸易伙伴"])
    ].reset_index(drop=True)
    table_9_history = table_9_history.merge(table_9_9, on="2024贸易伙伴", how="left")
    table_9_history[
        [
            "序号",
            "2019贸易伙伴",
            "2019进出口",
            "2019占比",
            "2023贸易伙伴",
            "2023进出口",
            "2023占比",
            "2024贸易伙伴",
            "2024进出口金额",
            "2024进出口占比",
        ]
    ].to_excel(
        f"../result/{update_month}/表9-上海进出口贸易伙伴占比变化（2019-2024）.xlsx",
        index=False,
    )

    table_10_history = pd.read_excel(
        r"../data/表10历史数据.xlsx",usecols=['排序', '2019出口目的地', '2019出口占比', '2023出口目的地', '2023出口占比', '2024出口目的地',
            '2019进口来源地', '2019进口占比', '2023进口来源地', '2023进口占比',
        '2024进口来源地',])
    table_10_history['2024进口来源地'] = table_10_history['2024进口来源地'].str.strip()
    table_10_history['2024出口目的地'] = table_10_history['2024出口目的地'].str.strip()
    table_9['2024贸易伙伴'] = table_9['2024贸易伙伴'].str.strip()
    table_10_history = table_10_history.merge(table_9[['2024贸易伙伴','2024进口占比']],left_on=['2024进口来源地'],right_on=['2024贸易伙伴'],how='left')
    table_10_history = table_10_history.merge(table_9[['2024贸易伙伴','2024出口占比']],left_on=['2024出口目的地'],right_on=['2024贸易伙伴'],how='left')
    table_10_history[['排序', '2019出口目的地', '2019出口占比', '2023出口目的地', '2023出口占比', '2024出口目的地','2024出口占比',
        '2019进口来源地', '2019进口占比', '2023进口来源地', '2023进口占比', '2024进口来源地',
        '2024进口占比', ]].to_excel(
        f"../result/{update_month}/表10-上海出口和进口贸易伙伴占比变化（2019-2024）.xlsx",
        index=False,
    )

    return table_9_history,table_10_history


def table_output():
    table1_output()
    table2_output()
    table3_output()
    table4_output()
    table5_output()
    table6_output()
    table7_output()
    table8_output()
    table9_output()
