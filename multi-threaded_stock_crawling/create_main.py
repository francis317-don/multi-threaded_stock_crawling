import json
import os
import time
from multiprocessing.dummy import Pool
import ta
from datetime import datetime
import pandas as pd
import requests
import concurrent.futures

session = requests.session()
def getLinesData(code: str, id: str):
    # beg和end用于调整数据区间
    params = f"fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&" \
             "fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&" \
             "beg=20180101&" \
             "end=20500101&" \
             "ut=fa5fd1943c7b386f172d6893dbfba10b&" \
             "rtntype = 6&" \
             f"secid={code}.{id}&" \
             "klt=101&" \
             "fqt=1&"

    res = session.get("http://push2his.eastmoney.com/api/qt/stock/kline/get", params=params)
    data = json.loads(res.text)
    return data["data"]["klines"]
# 在东方财富中获得数据
def getCompanyData(code: str, id: str):
    area = ''
    if code == "0":
        area = "SZ"
    elif code == "1":
        area = "SH"
    res = session.get(f"https://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/PageAjax?code={area}{id}")
    result = json.loads(res.text)
    cData = result["jbzl"][0]["SECURITY_NAME_ABBR"]
    return cData

def pd_unit(newArr):
    if float(newArr) >= 100000000 or float(newArr) <= -100000000:
        result = format(float(newArr) / 100000000, '.2f') + '亿'
    else:
        result = format(float(newArr) / 10000, '.2f') + '万'
    return result


# 打包为xlsx文件
def getxlsx(code: str, id: str):
    cur_dir = os.path.dirname(__file__)
    res = pd.DataFrame(columns=("股票代码", "股票简称", "日期", "开盘", "收盘", "最高", "最低", "涨跌幅", "涨跌额", "成交量", "成交额", "振幅","换手率"))
    linesData = getLinesData(code, id)
    companyData = getCompanyData(code, id)
    count = 1
    companyName = companyData
    for item in linesData:
        newArr = item.split(',')
        count = count + 1
        res.loc[count] = [id,companyData, newArr[0], newArr[1], newArr[2], newArr[3], newArr[4], newArr[8] + '%',
                          newArr[9], pd_unit(newArr[5]), pd_unit(newArr[6]), newArr[7] + '%', newArr[10] + '%']
    print(companyName + '-' + id + ".xlsx processing")
    res.to_excel(os.path.join(cur_dir, companyName + '-' + id + ".xlsx"), sheet_name='202121130180', index=False)
    print(companyName+"爬取完成")
    return companyName + '-' + id

'''
此处为一开始的代码，不过ta-lib 下载不成功，所以不能运行，但是这样的代码会简单许多
def calculate_indicators(file_path):
    # 读取Excel文件
    df = pd.read_excel(file_path)

    # 计算KDJ指标
    df['kdjk'], df['kdjd'], df['kdjj'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'], window=14)

    # 计算RSI指标
    df['rsi'] = ta.momentum.rsi(df['Close'], window=14)

    # 将计算结果存入Excel文件
    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"{df['Name'][0]}-{df['Code'][0]}-index-{now}.xlsx"
    df.to_excel(output_file, index=False)
'''




def calculate_kdj(name, xlsx, N, M1, M2):

    path = name + xlsx
    data = pd.read_excel(path)

    # 计算前N日最低和最高，缺失值用前n日（n<N)最小值替代
    lowList = data['最高'].rolling(N).min()
    lowList.fillna(value=data['最低'].expanding().min(), inplace=True)
    highList = data['最高'].rolling(N).max()
    highList.fillna(value=data['最高'].expanding().max(), inplace=True)
    # 计算rsi
    rsv = (data['收盘'] - lowList) / (highList - lowList) * 100
    # 计算k,d,j
    data['kdj_k'] = rsv.ewm(alpha=1 / M1, adjust=False).mean()  # ewm是指数加权函数
    data['kdj_d'] = data['kdj_k'].ewm(alpha=1 / M2, adjust=False).mean()
    data['kdj_j'] = 3.0 * data['kdj_k'] - 2.0 * data['kdj_d']

    new_df = pd.DataFrame()
    # new_df['Date']=data['日期']
    new_df['日期'] = data['日期']
    new_df['kdj_k'] = data['kdj_k']
    new_df['kdj_d'] = data['kdj_d']
    new_df['kdj_j'] = data['kdj_j']

    new_df.columns = ['日期','kdj_k', 'kdj_d', 'kdj_j']

    return new_df
    # 计算函数设置周期为12
def calculate_rsi(name, period=12):

    path = name + xlsx
    dataframe = pd.read_excel(path)
    print('rsi excel readed')
    # 计算涨跌幅
    dataframe['change'] = dataframe['涨跌幅'].apply(lambda x: float(x.strip('%')) / 100)

    # 计算上涨和下跌的价格
    dataframe['gain'] = dataframe['change'].apply(lambda x: x if x > 0 else 0)
    dataframe['loss'] = dataframe['change'].apply(lambda x: abs(x) if x < 0 else 0)

    # 计算平均上涨和平均下跌价格
    dataframe['avg_gain'] = dataframe['gain'].rolling(window=period).mean()
    dataframe['avg_loss'] = dataframe['loss'].rolling(window=period).mean()

    # 计算相对强弱指数（RSI）
    dataframe['rs'] = dataframe['avg_gain'] / dataframe['avg_loss']
    dataframe['rsi'] = 100 - (100 / (1 + dataframe['rs']))

    # 删除辅助列
    new_df = pd.DataFrame()

    new_df = dataframe['rsi']
    new_df = new_df.dropna()
    print(new_df)
    return new_df


def process_data(name):
    print('Processing', name)
    kdj = calculate_kdj(name,xlsx ,9, 3, 3)
    print('kdj accomplished')
    rsi = calculate_rsi(name)
    print('rsi accomplished')
    new_df = pd.concat([kdj, rsi], axis=1)
    newPath = name + '-index' + xlsx
    writer = pd.ExcelWriter(newPath)
    new_df.to_excel(writer, sheet_name='202121130180')
    writer.save()
    print(name + 'printing accomplished')
def merge_xlsx_files(output_file):
    file_paths = [file for file in os.listdir() if file.endswith('.xlsx')]
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    for file_path in file_paths:
        sheet_name = os.path.splitext(file_path)[0]
        data = pd.read_excel(file_path)
        data.to_excel(writer, sheet_name=sheet_name, index=False)
        # os.remove(file_path)
    writer.save()
    print("文件合并完成！")


'''
filename = '202121130180' + '.xlsx'
    table_name = companyData[1] + '-' + id
#存在文件则打开不存在则创建
    if os.path.isfile(filename):
        workbook = openpyxl.load_workbook(filename)
    else:
        workbook = openpyxl.Workbook()
#删除原始工作表Sheet
    if "Sheet" in workbook.sheetnames:
        del workbook["Sheet"]
#有同名工作表就删除
    if table_name in workbook.sheetnames:
        del workbook[table_name]
#创建新工作表
    worksheet = workbook.create_sheet(table_name)
    data = res.values.tolist()
    headers = list(res.columns)
#存入标签
    for col_num, header in enumerate(headers, start=1):
        worksheet.cell(row=1, column=col_num, value=header)
#存入数据
    for row_num, row_data in enumerate(data, start=2):
        for col_num, col_data in enumerate(row_data, start=1):
            worksheet.cell(row=row_num, column=col_num, value=col_data)

    workbook.save(filename)
'''


names = ['万科A-000002', '平安银行-000001', 'ST国华-000004', 'ST星源-000005', '深振业A-000006', '共创草坪-605099', '中国宝安-000009','美丽生态-000010', '启明星辰-002439', '普莱柯-603566']
xlsx = '.xlsx'
def main():
    stocks = [['0', '000002'], ['0', '000001'], ['0', '000004'], ['0', '000005'], ['0', '000006'], ['1', '605099'],
['0', '000009'], ['0', '000010'], ['0', '002439'], ['0', '603566']]

    pool = Pool(2)
    start=time.time()
    for stock in stocks:
        try:
            code = stock[0]
            id = stock[1]
            pool.apply_async(getxlsx, args=(code, id))
        except Exception as e:
            print("爬取失败,错误股票代码" + stock[1], e)
            continue
    pool.close()
    pool.join()
    stop = time.time()
    print(f'5线程爬取股票数据，耗时：{stop - start}')
    time.sleep(1)
    # 指定合并后的文件名
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_data, names)
        # 指定合并后的文件名

    output_filename = "202121130180.xlsx"
    if os.path.exists(output_filename):
        os.remove(output_filename)
    try:
        merge_xlsx_files(output_filename)
    except Exception as e:
        print("合并失败")


if __name__ == '__main__':
    main()