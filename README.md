# ShangHaiBillManage

web == flask database == csv

写在前面：
- 账单记录用的csv表格
- web端搭建基本完成
- 内容大体上根据`Doublex69`的[Xbill](https://github.com/DoubleX69/Xbill)改造

#### 功能介绍
1. 首页
2. 账单明细表
3. 账单报表
4. 年度收支
5. 统计
6. 数据录入


#### 记账
根目录下新建cost_record文件夹
```txt
cost_record
    └───2020
        └───2020_1.csv
        ├───2020_2.csv
        ├───2020_3.csv
        ├───2020_4.csv
        ├───.....
        ├───2020_12.csv
    └───2021
        └───2021_1.csv
        ├───2021_2.csv
        ├───2021_3.csv
        ├───2021_4.csv
        ├───.....
        ├───2021_12.csv
    └───other_record.csv
```
其中，日记账：
```csv
date,name,payment,type,note
日期（月_日），名称，金额，类型（eat,other），备注
```
其他记账：
```csv
date,salary,save,budget,rent,salary_day,note
日期（年_月），工资，月存储，预算，房租，发工资日期，备注
```

`auto_create_cost_record.py`文件：
可以自动生成一年的账单文件也可以手动做，看个人喜好

#### 运行
安装好对应的python库，在`app.py`文件运行代码就可以了

#### 设置
配置文件`setting.py`写的还算清楚，就不多介绍了

#### 环境
```cmd
pip install -r requirements.txt
```
`wordcloud`云词安装不能直接pip

[点击](https://www.cnblogs.com/pywjh/p/9372652.html)查看安装教程