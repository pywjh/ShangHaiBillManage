from matplotlib.font_manager import fontManager
import os

fonts = [font.name for font in fontManager.ttflist if
         os.path.exists(font.fname) and os.stat(font.fname).st_size > 1e6]

# 生成图片展示时的字体包（路径）
FONT = 'C:\Windows\Fonts\simfang.ttf'

# 全局字体设置（此处最好避必输，否则会出现中文无法显示的问题）
# GLOBAL_FONT = fonts[-1] # 可以自己打印出来选一个喜欢的字体
GLOBAL_FONT = ['Microsoft YaHei']

# x轴刻度步长
Y_STEP = 7

# 标题字体大小
TITLE_SIZE = 15

# 轴刻度单位字体大小
LABEL_SIZE = 18 

# x轴字体倾斜角度(0~90)
ROTATION = 30

# 饮食折线统计图线条粗细
EAT_LINEWIDTH = 3

# 总消费折线统计图线条粗细
OTHER_LINEWIDTH = 3

# 全部折线图线条粗细
ALL_LINEWIDTH = 3

# 饮食折线颜色
EAT_LINE_COLOR = 'green'

# 其他折线颜色
OTHER_LINE_COLOR = 'blue'

# 总消费折线颜色
ALL_LINE_COLOR = 'red'

# 辅助线颜色
GRID_COLOR = 'gray'

# 辅助线透明度 0~1
ALPHA_WIDTH = 0.8

# 云词图片宽度
CLOUD_WIDTH = 800

# 云词图片高度
CLOUD_HEIGHT = 500

# 云词背景颜色
BACKGROUND_COLOR = 'black'

# **************************************

# web端消费类别与金额饼状图，饮食类型数量展示限制（最多展示多少个）
NUMBER_WEB_CATEGORY_PIE_EAT = 15

# web端消费类别与金额饼状图，其他类型数量展示限制（最多展示多少个）
NUMBER_WEB_CATEGORY_PIE_OTHER = 10

# 数据新增页面详情表倒序显示的最大数量限制
NUMBER_UPDATE_TABLE = 20

# **************************************

# 是否生成消费折线图
MERGE_PLOT = True

# 是否生成消费类别条形图
CATEGORY_BAR = True

# 是否生成消费类别云图
COST_CLOUDWORD = True

# 是否生成规定形状云图
CLOUDWORD_SHAPE = True

# 是否生成消费对比图
DOUBLE_BAR = True

# 是否生成消费总览对比图
TRIPLE_BAR = True

# 是否生成消费种类饼状图
PIE = True





# plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签