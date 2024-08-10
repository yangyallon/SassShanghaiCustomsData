
import os 
import sys 
current_path = os.getcwd()
parent_path = os.path.abspath(os.path.dirname(os.getcwd()))
sys.path.append(parent_path)

update_month = '6月'

product=["机电产品",
        '农产品',
        '食品',
        '高新技术产品',
        '金属矿及矿砂',
        "高新技术产品",
        '医药材及药品',
        '计量检测分析自控仪器及器具',
        '医疗仪器及器械',
        "集成电路",
        '汽车包括底盘',
        "汽车零配件",
        '电动载人汽车',
        "自动数据处理设备及其部件",
        "自动数据处理设备及其零部件",
        "笔记本电脑",
        "手机",
        "锂离子蓄电池",
        "太阳能电池",
        "生命科学技术",
        '美容化妆品及洗护用品',
        '乘用车']