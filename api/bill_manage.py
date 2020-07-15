import setting

import os
import csv
import calendar
import datetime as dt
import numpy as np

# from matplotlib import pyplot as plt
# from matplotlib import font_manager
from collections import Counter
from win32api import GetSystemMetrics
from PIL import Image
from datetime import datetime
from dateutil.relativedelta import relativedelta


if setting.CLOUDWORD_SHAPE or setting.COST_CLOUDWORD:
    from wordcloud import WordCloud


class MouthCost(object):
    """
        每天的消费情况统计
        每天的饮食消费必须记录，统计图日期以饮食日期为主，其他消费可以为空

        能得到每个月吃饭消费的总数:              eat_total 
        能得到每个月一共消费的总数:              all_total
        将饮食和总消费做成一张折线图             merge_plot
        将一个月的消费类别做成条形图             category_bar
        生成消费类别的云图                               
    """
    def __init__(self, record, year, month, *args, **kwargs):
        self.base_dir = os.path.dirname(__file__)
        self.eat_month, self.other_month = self.split_record(record)
        self.record = record
        self.other_record = MouthCost.read_other_record(self.base_dir[:-4])
        self.font = setting.FONT # 云图所使用的字体
        self.year = str(dt.date.today().year) if not year or year=='null' else year
        # self.my_font = font_manager.FontProperties(fname=self.font) # 统计图所使用的字体包
        self.bar_width = GetSystemMetrics(0) / 100  # 折线图宽
        self.bar_height = GetSystemMetrics(1) / 100  # 折线图高
        self.bar_dpi = 200  # 图片分辨率
        self.month_number = str(dt.date.today().month) if not month or month=='null' else month
        self.current_fix_data = MouthCost.current_fix_data(year=self.year,
                                                           month=self.month_number,
                                                           other_record=self.other_record)
        # 当前统计的月份
        # self.y_step = setting.Y_STEP # x轴刻度步长
        # self.title_size = setting.TITLE_SIZE # 标题字体大小
        # self.label_size = setting.LABEL_SIZE # 轴刻度单位字体大小
        # self.rotation = setting.TOTATION # 刻度名称旋转角度
        # self.eat_linewidth = setting.EAT_LINEWIDTH # 饮食折线图线条粗细
        # self.other_linewidth = setting.OTHER_LINEWIDTH # 其他折线图线条粗细
        # self.all_linewidth = setting.ALL_LINEWIDTH # 全部折线图线条粗细
        # self.eat_line_color = setting.EAT_LINE_COLOR # 饮食折线颜色
        # self.other_line_color = setting.OTHER_LINE_COLOR # 其他折线颜色
        # self.all_line_color = setting.ALL_LINE_COLOR # 总消费折线颜色
        # self.grid_color = setting.GRID_COLOR # 辅助线颜色
        # self.alpha_width = setting.ALPHA_WIDTH # 辅助线透明度 0~1
        # self.cloud_width = setting.CLOUD_WIDTH  # 云词图片宽度
        # self.cloud_height = setting.CLOUD_HEIGHT # 云词图片高度

        # self.background_color = setting.BACKGROUND_COLOR # 云词背景颜色
        if setting.CLOUDWORD_SHAPE:
            self.mark = np.array(Image.open(r'.\mask\mark.png'))
        # plt.rcParams['font.sans-serif'] = setting.GLOBAL_FONT

    def __call__(self, *args, **kwargs):
        other_total = round(self.all_total() - self.eat_total(), 2)
        print("{}年{}月，饮食月消费总数：".format(self.year, self.month_number), self.eat_total())
        print("{}年{}月，其他月消费总数：".format(self.year, self.month_number), other_total)
        print("{}年{}月，全部消费总数：".format(self.year, self.month_number), self.all_total())
        self.file_manage()
        if setting.MERGE_PLOT: # 生成消费折线图
            print('正在生成折线图...')
            self.merge_plot()
        if setting.CATEGORY_BAR: # 生成消费类别条形图
            print('正在生成条形图...')
            self.category_bar()
        if setting.COST_CLOUDWORD: # 生成消费类别云图
            print('正在生成云图...')
            self.cost_cloudword()
        if setting.DOUBLE_BAR: # 生成消费对比图
            print('正在生成消费对比图...')
            self.double_bar()
        if setting.TRIPLE_BAR: # 消费总览对比图
            print('正在生成消费总览对比图...')
            self.triple_bar()
        if setting.PIE: # 消费种类饼状图
            print('正在生成消费种类饼状图...')
            self.pie()

    @classmethod
    def get_special_date(cls, year='null', month='null',day=None, default=None):
        """根据发工资时间，判断月份是否往前一个月"""
        if not day:
            day = dt.date.today().day
        day = int(day)

        base_dir = os.path.dirname(__file__)

        other_record = MouthCost.read_other_record(base_dir[:-4])

        year = dt.date.today().year if year in ('null', None) else year

        month = dt.date.today().month if month in ('null', None) else month

        current_fix_data = MouthCost.current_fix_data(other_record, year=year, month=month)

        if default:

            if current_fix_data and day < int(current_fix_data['salary_day']):
                month = str((dt.date(dt.date.today().year, int(month), day) - relativedelta(months=1)).month)
            else:
                month = str(month)

        return year, month

    @classmethod
    def _read_csv(cls, path, encoding_list=('GBK', 'UTF-8')):
        for encoding in encoding_list:
            try:
                with open(path, encoding=encoding) as csv_file:

                    reader = csv.DictReader(csv_file)
                    return [row for row in reader if row]

            except UnicodeDecodeError:
                raise ValueError("文件格式有误！")
            except FileNotFoundError:
                raise ValueError('未找到账单文件：{}'.format(path))
            except Exception as e:
                raise ValueError(e)
        return None

    @classmethod
    def current_fix_data(cls, other_record, year=dt.date.today().year,month=dt.date.today().month):
        """获取对应时间的固定信息表
        因为发工资时间存在了表里
        查询指定时间发工资时间就会递归
        这里采取的方法就是查询对应的指定时间，不存在就取上一个月的"""
        res = list(filter(lambda li: li['date'] == f"{year}_{month}", other_record))
        if not res:
            month = str((dt.date(
                int(year), int(month),1
            ) - relativedelta(months=1)).month)
        res = list(
            filter(lambda li: li['date'] == f"{year}_{month}", other_record))
        if len(res) == 1:
            return res[0]

    @classmethod
    def read_other_record(cls, base_dir):
        """读取其他数据记录表"""
        path = '{}/cost_record/other_record.csv'.format(base_dir)
        return MouthCost._read_csv(path)

    def current_rest_day(self):
        """当月目前所剩下的天数，基于发工资日"""
        day = datetime.now().day
        if day >= int(self.current_fix_data['salary_day']):
            rest_date = calendar.monthrange(
                year=int(self.year),
                month=int(self.month_number)
            )[1] - int(self.x_axis_num()[-1].split('_')[-1]) + 15
        else:
            rest_date = 15 - day
        return rest_date

    def split_record(self, record):
        """
        将账单按type分成两个列表
        :param record: csv文件读取的数据 -> list(dict)
        :return: eat_month_data -> list(dict),
                 other_month_data -> list(dict)
        """
        eat_month_data = other_month_data = []
        if record:
            eat_month_data = list(filter(lambda li: li['type'] == 'eat', record))
            other_month_data = list(
                filter(lambda li: li['type'] == 'other', record))
        return eat_month_data, other_month_data

    def get_weekday(self, no_format_date):
        """
        为对应的日期添加周几的信息
        :param no_format_date: date -> str
        :return: str
        """
        weekday_dict = {
            1: '一',
            2: '二',
            3: '三',
            4: '四',
            5: '五',
            6: '六',
            7: '天'
        }
        month = int(no_format_date.split("_")[0])
        day = int(no_format_date.split("_")[1])
        date = datetime(int(self.year), month, day)
        weekday = date.isoweekday()
        return weekday_dict.get(weekday)

    def format_date(self, no_format_date):
        result = "{month}月{day}日({weekday})".format(
            month=no_format_date.split("_")[0],
            day=no_format_date.split("_")[-1],
            weekday=self.get_weekday(no_format_date))
        return result

    def get_title_code(self):
        """
        获取csv文件的标题，实现界面数据高度灵活性
        :return: title -> list
        """
        data = self.record and self.record[0] or []
        if data:
            return data.keys()

    def details_bill(self):
        """
        整理详细的账单内容，方便界面展示
        :return: list(dict, dict)
        """
        bills = []
        record = self.record or []
        for rec in record:
            bills.append({
                'date': self.year + '年' + self.format_date(rec.get('date', '')),
                'name': rec.get('name', ''),
                'payment': rec.get('payment', '-'),
                'note': rec.get('note', ''),
                'type': rec.get('type', 'none')
            })
        return bills

    def file_manage(self):
        file_name = self.year + '年' + self.month_number + '月' + '账单记录'
        if not os.path.exists(file_name):
            os.mkdir(file_name)  # 创建文件夹
            os.chdir(file_name)  # 进入文件夹
        else:
            os.chdir(file_name)  # 进入文件夹

    def x_axis_num(self):
        date_list = list(
            set(
                [date.get('date') for date in self.eat_month] +
                [date.get('date') for date in self.other_month]
            )
        )
        date_list.sort(
            key=lambda date: datetime(
                year=int(self.year),
                month=int(date.split('_')[0]),
                day=int(date.split('_')[-1])
            ))
        return date_list

    def x_axis_zh(self):
        date_list = self.x_axis_num()
        date_list = [self.format_date(i) for i in date_list]
        return date_list

    def eat_sum(self):
        """
            饮食上一个月的总消费额，{日期: 日结算}
            return: eat_dict
        """
        date_list = self.x_axis_num()
        eat_dict = {}
        for date in date_list:
            eat_dict[date] = round(sum(
                [float(eat.get('payment', 0)) for eat in filter(
                    lambda li: li['date'] == date, self.eat_month)]), 2)
        return eat_dict

    def other_sum(self):
        """
            其他消费，一个月的总消费额，{日期: 日结算}
            return: other_dict
        """
        date_list = self.x_axis_num()
        other_dict = {}
        for date in date_list:
            other_dict[date] = round(sum(
                [float(other.get('payment', 0)) for other in filter(
                    lambda li: li['date']==date, self.other_month)]), 2)
        return other_dict

    def get_eat_y(self):
        x = self.x_axis_num()
        y = []
        for month in x:
            y.append(round(self.eat_sum().get(month, 0), 2))
        return y

    def get_other_y(self):
        x = self.x_axis_num()
        y = []
        for month in x:
            y.append(round(self.other_sum().get(month, 0), 2))
        return y

    def get_all_y(self):
        x = self.x_axis_num()
        y = []
        for month in x:
            y.append(round(self.other_sum().get(month, 0) + self.eat_sum().get(month, 0), 2))
        return y

    def all_total(self):
        """
            得到每个月一共消费的总数
            return: all_total_num
        """
        all_list = self.get_all_y()
        all_total_num = round(sum([i for i in all_list]), 2)
        return all_total_num

    def eat_total(self):
        """
            得到每个月吃饭消费的总数
            return : eat_total_num
        """
        eat_list = self.get_eat_y()
        eat_total_num = round(sum([i for i in eat_list]), 2)
        return eat_total_num

    def merge_plot(self):
        """
            通过折现图展示一个月每天的总消费情况和一个月饮食消费情况
            return: 月消费折线图.png
        """
        other_total = round(self.all_total() - self.eat_total(), 2)
        x_axis = self.x_axis_zh()
        y_axis_eat = [i for i in self.get_eat_y()]
        y_axis_other = [i for i in self.get_other_y()]
        y_axis_all = [i for i in self.get_all_y()]
        # 设置画布
        plt.figure(figsize=(self.bar_width, self.bar_height), dpi=self.bar_dpi)
        # 开始绘制折线图
        plt.plot(x_axis, y_axis_eat,
                 color=setting.EAT_LINE_COLOR,
                 linewidth=setting.EAT_LINEWIDTH,
                 label="饮食总和：{}".format(self.eat_total())) # 条形图:bar;折线图:plot
        plt.plot(x_axis, y_axis_other,
                 color=setting.OTHER_LINE_COLOR,
                 linewidth=setting.OTHER_LINEWIDTH,
                 label="其他总和：{}".format(other_total)) # 条形图:bar;折线图:plot
        plt.plot(x_axis, y_axis_all,
                 color=setting.ALL_LINE_COLOR,
                 linewidth=setting.ALL_LINEWIDTH,
                 label="消费总和：{}".format(self.all_total()),
                 linestyle='--')
        # 设置x，y轴刻度
        plt.xticks(range(len(x_axis)), x_axis,
                   fontproperties=self.my_font,
                   rotation=setting.ROTATION)
        plt.yticks(range(int(min(y_axis_eat)), int(max(y_axis_all)+1), setting.Y_STEP))
        # 设置刻度名称和标题
        plt.xlabel('日期（单位：日）',
                   fontproperties=self.my_font,
                   size=setting.LABEL_SIZE)
        plt.ylabel('消费额（单位：元）',
                   fontproperties=self.my_font,
                   size=setting.LABEL_SIZE)

        # 设置数字标签
        for x, y in zip(x_axis, y_axis_eat):
            plt.text(x, y, y, ha='center', va='bottom', fontsize=10)
        for x, y in zip(x_axis, y_axis_other):
            plt.text(x, y, y, ha='center', va='bottom', fontsize=10)
        for x, y in zip(x_axis, y_axis_all):
            plt.text(x, y, y, ha='center', va='bottom', fontsize=10)


        plt.title('{}年{}月消费统计'.format(self.year, self.month_number),
                  fontproperties=self.my_font,
                  size=setting.TITLE_SIZE)
        plt.legend(prop=self.my_font) # 设置折线类别
        plt.grid(alpha=setting.ALPHA_WIDTH, color=setting.GRID_COLOR) # 设置辅助线
        plt.savefig("./{}年{}月消费统计图".format(self.year, self.month_number)) # 保存图片

    def category_list(self):
        """
            将所有消费类别,金额做成一个列表
            return: category_list
        """
        category_list = []
        for record in self.record:
            category_list.append((record.get('name'), record.get('payment')))
        return category_list

    def category_bar(self):
        """
            将一个月的消费类别做成条形图  
            return: 消费类别条形图.png
        """
        category_list = self.category_list()
        counter = Counter()
        for category in category_list:
            counter[category] += 1 # 没有默认返回0
        counter = counter.most_common()
        x_axis = [i for i, j in counter]
        y_axis = [j for i, j in counter]
        # 设置画布
        plt.figure(figsize=(self.bar_width, self.bar_height), dpi=self.bar_dpi)
        # 绘制条形图
        plt.bar(x_axis, y_axis, color=setting.OTHER_LINE_COLOR)
        # 设置x，y轴刻度
        plt.xticks(range(len(x_axis)), x_axis,
                   fontproperties=self.my_font,
                   rotation=setting.ROTATION) #
        plt.yticks(range(int(min(y_axis)), int(max(y_axis)+1)))
        # 设置刻度名称和标题
        plt.xlabel('消费类别', fontproperties=self.my_font, size=setting.LABEL_SIZE)
        plt.ylabel('出现次数（单位：次）', fontproperties=self.my_font, size=setting.LABEL_SIZE)
        plt.title('{}年{}月消费统计'.format(self.year, self.month_number),
                  fontproperties=self.my_font, size=setting.TITLE_SIZE)
        plt.grid(alpha=setting.ALPHA_WIDTH, color=setting.GRID_COLOR)
        plt.savefig("./{}年{}月消费类别统计".format(self.year, self.month_number))

    def cost_cloudword(self):
        """
            生成消费类别的云图s
        """
        category_list = self.category_list()
        text = ' '.join(category_list)
        wd = WordCloud(
            font_path=self.font,
            width=setting.CLOUD_WIDTH,
            height=setting.CLOUD_HEIGHT,
            background_color=setting.BACKGROUND_COLOR,
            margin=1,  # 字体之间宽度
            # mask=self.mark,  # 以该参数值作图绘制词云，
        ).generate(text)
        plt.figure()
        plt.axis('off')  # 去掉x，y轴
        plt.imshow(wd)
        # plt.show()
        wd.to_file("./{}年{}月消费类别云图.png".format(self.year, self.month_number))
        if setting.CLOUDWORD_SHAPE:
            wd2 = WordCloud(
                font_path=self.font,
                width=setting.CLOUD_WIDTH,
                height=setting.CLOUD_HEIGHT,
                background_color=setting.BACKGROUND_COLOR,
                margin=1,  # 字体之间宽度
                mask=self.mark,  # 以该参数值作图绘制词云，
            ).generate(text)
            plt.figure()
            plt.axis('off')  # 去掉x，y轴
            plt.imshow(wd2)
            wd2.to_file("./{}年{}月消费类别mask云图.png".format(self.year, self.month_number))

    def double_bar(self):
        labels = self.x_axis_num()
        eat_y = self.get_eat_y()
        other_y = self.get_other_y()

        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots(squeeze=True)
        rects1 = ax.bar(x - width / 2, eat_y, width, label='饮食')
        rects2 = ax.bar(x + width / 2, other_y, width, label='其他')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('金额')
        ax.set_title('日消费对比图')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)
        fig.tight_layout()
        # plt.show()
        plt.savefig("./{}年{}月消费对比图".format(self.year, self.month_number))

    def triple_bar(self):
        category_names = ['总消费', '其他消费', '饮食消费']
        results = {}
        for time, all, other, eat in zip(self.x_axis_zh(), self.get_all_y(),
                                         self.get_other_y(), self.get_eat_y()):
            results.update({
                time: [all, other, eat]
            })

        def survey(results, category_names):
            """
            Parameters
            ----------
            results : dict
                A mapping from question labels to a list of answers per category.
                It is assumed all lists contain the same number of entries and that
                it matches the length of *category_names*.
            category_names : list of str
                The category labels.
            """
            labels = list(results.keys())
            data = np.array(list(results.values()))
            data_cum = data.cumsum(axis=1)
            category_colors = plt.get_cmap('RdYlGn')(
                np.linspace(0.15, 0.85, data.shape[1]))

            fig, ax = plt.subplots(figsize=(9.2, 5))
            ax.invert_yaxis()
            ax.xaxis.set_visible(False)
            ax.set_xlim(0, np.sum(data, axis=1).max())

            for i, (colname, color) in enumerate(
                    zip(category_names, category_colors)):
                widths = data[:, i]
                starts = data_cum[:, i] - widths
                ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)
                xcenters = starts + widths / 2

                r, g, b, _ = color
                text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
                for y, (x, c) in enumerate(zip(xcenters, widths)):
                    ax.text(x, y, str(int(c)), ha='center', va='center',
                            color=text_color)
            ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
                      loc='lower left', fontsize='small')

            return fig, ax

        survey(results, category_names)
        # plt.show()
        plt.savefig("./{}年{}月消费总览对比图".format(self.year, self.month_number))

    def pie(self):
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

        # recipe = ["375 g flour",
        #         "75 g sugar",
        #         "250 g butter",
        #         "300 g berries"]

        category_list = self.category_list()
        counter = Counter()
        for category in category_list:
            counter[category] += 1  # 没有默认返回0
        counter = counter.most_common()
        recipe = []
        for kind, num in counter:
            recipe.append(str(num) + ' ' + str(kind))
        # print(recipe)

        data = [float(x.split()[0]) for x in recipe]
        ingredients = [x.split()[-1] for x in recipe]

        def func(pct, allvals):
            absolute = int(pct / 100. * np.sum(allvals))
            return "{:.1f}%\n({:d})".format(pct, absolute)

        wedges, texts, autotexts = ax.pie(data,
                                          autopct=lambda pct: func(pct, data),
                                          textprops=dict(color="w"))

        ax.legend(wedges, ingredients,
                  title="消费品类",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))

        plt.setp(autotexts, size=8, weight="bold")

        ax.set_title("消费种类饼状图")

        # plt.show()
        plt.savefig("./{}年{}月消费种类饼状图".format(self.year, self.month_number))

    def get_rent(self, date):
        """获取指定时间的月份的房租"""
        if list(filter(lambda l: l['date']==date, self.other_record)):
            rent = list(filter(lambda l: l['date']==date, self.other_record))[0]['rent']
            return float(rent)
        return 0

    def web_index_bar(self):
        """
        网页首页的条形数据准备
        :return:
            x = [月_日, 月_日, 月_日, ....]
            y = [(title1, [num1, num2, num3, num4, ...]), (title2, [num1, num2, num3, num4, ...])]
        """
        x = self.x_axis_zh()
        eat_y = self.get_eat_y()
        other_y = self.get_other_y()
        all_y = self.get_all_y()
        y = []
        y.append(('饮食消费', eat_y))
        y.append(('其他消费', other_y))
        y.append(('合计消费', all_y))
        return (x, y)

    def web_index_pie(self):
        """
        网站首页饼状图
        :return:
            data -> list [(title1, num1), (title2, num2)]
        """
        payout = self.all_total()
        surplus = round(float(self.current_fix_data['budget']) - payout)
        if surplus < 0:
            surplus = 0

        data = [('结余', surplus), ('支出', payout)]
        return data

    def web_category_pie(self):
        """
        账单报表页的饼状图
        :return: Pie
        """
        eat_cost = []
        other_cost = []
        if self.record:
            names = list(set([record['name'] for record in self.record]))
            # 同名消费汇总
            for name in names:
                if name in [i['name'] for i in self.eat_month]:
                    eat_cost.append((
                        name, round(sum([float(i['payment']) for i in list(
                            filter(lambda li: li['name'] == name, self.eat_month)
                        )]), 2))
                    )
                if name in [i['name'] for i in self.other_month]:
                    other_cost.append(
                        (name, round(sum([float(i['payment']) for i in list(
                            filter(lambda li: li['name']==name, self.other_month)
                        )]), 2))
                    )
            # 限制数量(价格降序排列前30条数据)
            eat_cost = sorted(eat_cost, key=lambda t: t[1], reverse=True)
            other_cost = sorted(other_cost, key=lambda t: t[1], reverse=True)
        return (eat_cost, other_cost)

    def to_table(self, category=False):
        '''
        首页账单概览
        :return: ([{name1: balance1}, {name2: balance2}],  [{columns}])
        '''
        current_month_payment = self.all_total()
        current_salary = '0'
        rent = 0
        budget = 0
        save = 0
        rest_date = 1
        # 当月工资数据
        record = self.current_fix_data
        if record:
            current_salary = record['salary'] # 当月工资
            rent = float(record['rent']) # 当月房租
            budget = float(record['budget']) # 当月预算
            save = float(record['save']) # 当月存储
            # 这个月剩余的天数
            rest_date = self.current_rest_day()
        status = [
            {'name': '本月收入','balance': current_salary},
            {'name': '本月支出','balance': current_month_payment},
            {'name': '本月房租','balance': rent},
            {'name': '本月预算','balance': budget},
            {'name': '预算结余','balance': round((budget - current_month_payment), 2)},
            {'name': '日付上限','balance': round(((budget - current_month_payment) / rest_date), 2)},
            {'name': '月储金额','balance': float(save)},
            {'name': '本月结余','balance': round((eval(current_salary)-current_month_payment-rent), 2)},
        ]
        if category:
            status.insert(
                1, {'name': '饮食支出','balance': self.eat_total()}
            )
            status.insert(
                2, {'name': '其他支出', 'balance': round(self.all_total()-self.eat_total(), 2)}
            )
        columns = [
            {
                "field": "name",  # which is the field's name of data key
                "title": "名称",  # display as the table header's name
                "sortable": False,
            },
            {
                "field": "balance",
                "title": "金额 (元)",
                "sortable": False,
            },
        ]
        return status, columns

    def to_detail_table(self, update=False):
        """
        账单详情表
        :return:  details_bill, columns   -> list(dict, dict)
        """
        details_bill = self.details_bill() # -> list(dict, dict)
        columns = [
            {
                "field": "date",  # which is the field's name of data key
                "title": "日期",  # display as the table header's name
                "sortable": False,
            },
            {
                "field": "name",
                "title": "用途",
                "sortable": False,
            },
            {
                "field": "payment",
                "title": "金额（元）",
                "sortable": False,
            },
            {
                "field": "note",
                "title": "备注",
                "sortable": False,
            },
        ]
        # 如果是新增数据页面
        if update:
            columns.insert(3, {
                "field": "type",
                "title": "类型",
                "sortable": False,
            })
            return details_bill[::-1][:setting.NUMBER_UPDATE_TABLE], columns

        return details_bill, columns

    def web_annual_bar(self, year):
        """
        年度统计数据汇总
        :return x_date x轴  y轴工资  cost_list 总消费列表
            x = [年_月, 年_月, 年_月, ....]
            y = [(title1, num1), (title2, num2)]
        """
        x_date = []
        y_amount = [('支出', []), ('收入', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])]

        annual_payment_path = f'{self.base_dir[:-4]}/cost_record/{year}'

        if os.path.exists(annual_payment_path):

            annual_payment_list = sorted(os.listdir(annual_payment_path), key=lambda file: datetime(
                    year=int(file.split('.')[0].split('_')[0]),
                    month=int(file.split('.')[0].split('_')[-1]),
                    day=1
                ))

            x_date = [f"{month.split('.')[0]}" for month in annual_payment_list]

            for month in annual_payment_list:
                path = annual_payment_path + f'/{month}'
                data = MouthCost._read_csv(path)
                # 此月份开销 + 房租
                payment_amount = round(sum([float(i['payment']) for i in data]) + self.get_rent(
                    month.split('.')[0]), 2)
                y_amount[0][1].append(payment_amount)

            for other in self.other_record:
                if other['date'] in x_date:
                    month_name = other['date'] # year_month
                    month_index = int(month_name.split('_')[-1]) - 1
                    if other.get('salary'):
                        y_amount[1][1].pop(month_index)
                        y_amount[1][1].insert(month_index, eval(other.get('salary')))

        return [f"{date.split('_')[0]}年{date.split('_')[-1]}月" for date in x_date], y_amount








if __name__ == '__main__':
    MouthCost.test([1,2,3], '2020', '5')


