import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker


def read_data(stock_name):
    file_name = '202121130180.xlsx'
    data = pd.read_excel(file_name, sheet_name=stock_name)
    return data
''''起初是用网上的模版，
df = pd.read_excel("202121130180.xlsx")
print(df.head())
#
#
#
class StockGUI:
    def __init__(self, master):
        self.master = master
        master.title("股票展示的GUI")

        #创建GUI
        self.stock_label = tk.Label(master, text="股票选择:")
        self.stock_listbox = tk.Listbox(master, selectmode=tk.MULTIPLE)
        self.stock_listbox.insert(1, "万科A-000002")
        self.stock_listbox.insert(2, "平安银行-000001")
        # self.stock_listbox.insert(3, "MSFT")
        # self.stock_listbox.insert(4, "AMZN")
        #在GUI中创建具体内容
        self.indicator_label = tk.Label(master, text="展示的数据:")
        self.indicator_listbox = tk.Listbox(master, selectmode=tk.MULTIPLE)
        self.indicator_listbox.insert(1, "开盘")
        self.indicator_listbox.insert(2, "收盘")
        self.indicator_listbox.insert(3, "最高")
        self.indicator_listbox.insert(4, "最低")
        #设置按钮
        self.show_button = tk.Button(master, text="展示", command=self.show)
        self.result_label = tk.Label(master, text="")
        
        
'''
# 画出GUI
def plot_indicators(stock_name, indicators):
    data = read_data(stock_name)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(10, 6))
    for indicator in indicators:
        plt.plot(data['日期'], data[indicator], label=indicator)
    #   x 轴作为日期值
    plt.xlabel('日期')
    #   y轴作为指标值
    plt.ylabel('指标值')
    plt.title(stock_name + '指标图表')
    plt.legend()
    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=180))
    plt.show()

# 对股票的信息进行处理
def show_indicators():
    selected_stock = stock_combobox.get()
    selected_indicators = []
    if kdj_var.get():
        selected_indicators.append('kdj_k')
        selected_indicators.append('kdj_d')
        selected_indicators.append('kdj_j')
    if rsi_var.get():
        selected_indicators.append('RSI')

    if selected_stock and selected_indicators:
        plot_indicators(selected_stock, selected_indicators)

# 构造出GUI的基本框架
window = tk.Tk()
window.title("202121130180.xlsx中股票信息展示")
window.geometry("800x400")

# GUI中的股票的选择框
stock_label = tk.Label(window, text="请选择股票：")
stock_label.pack()
stocks = ['万科A-000002-index', '平安银行-000001-index', 'ST国华-000004-index', 'ST星源-000005-index', '深振业A-000006-index', '共创草坪-605099-index', '中国宝安-000009-index', '美丽生态-000010-index', '启明星辰-002439-index', '普莱柯-603566-index']  # 替换为对应的股票名-股票代号
stock_combobox = ttk.Combobox(window, values=stocks)

stock_combobox.pack()

# GUI中的一些基本指标进行选择
indicators_label = tk.Label(window, text="请选择你需要的指标：")
indicators_label.pack()
kdj_var = tk.IntVar()
kdj_checkbox = tk.Checkbutton(window, text="KDJ", variable=kdj_var)
kdj_checkbox.pack()
rsi_var = tk.IntVar()
rsi_checkbox = tk.Checkbutton(window, text="RSI", variable=rsi_var)
rsi_checkbox.pack()

# button的设置
show_button = tk.Button(window, text="展示", command=show_indicators)
show_button.pack()

window.mainloop()
