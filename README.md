# ShangHaiBillManage

web == flask database == py -> dict

写在前面：
账单记录还比较low（py文件字典记录），web端搭建ing...

#### 记账
ShangHai_life_consumpyion_record.py文件，需要自己生成
```python
eat_month_20_4 = {
    '4_16': {
        '午餐': 45,
        '甜点': 35,    
    },
    '4_17': {
        '午餐': 19,
        '买菜': 55.6,
    },# .......
}
other_month_20_4 = {
    '4_15': {
        '上衣': 150,
        '短袖': 110,
        '口红': 399,
    },
    '4_16': {
        '挂钩': 15,
    }, # .....
}
```
#### 运行
在`run.py`文件里面填上对应维护的`eat_month`和`other_month`就可以了

#### 设置
配置文件`setting.py`写的还算清楚，就不多介绍了

#### 环境
```cmd
pip3 install numpy
pip3 install matplotlib
pip3 install pywin32
pip3 install Pillow
```
`wordcloud`云词安装不能直接pip

[点击](https://www.cnblogs.com/pywjh/p/9372652.html)查看安装教程