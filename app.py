import os
import json
from datetime import datetime
from werkzeug.utils import redirect
from flask import Flask, render_template, url_for, request, jsonify

from api import draw
from api import get_bill_record
from api.bill_manage import MouthCost
from api.get_bill_record import data_aggregation

from setting import *

app = Flask(__name__)

other_record = MouthCost.read_other_record(os.path.dirname(__file__))


@app.route("/")
@app.route("/index")
def index():
    record, year, month = data_aggregation(default=True)
    record = MouthCost(record, year, month)
    status, columns = record.to_table()
    paid_limit = list(filter(lambda d: d['name'] == '日付上限', status))[0]['balance']
    return render_template(
        "index.html",
        chart_url=url_for('get_current_month_bar'),
        usage_chart=url_for("get_month_usage"),
        data=status,
        columns=columns,
        paid_limit=paid_limit
    )


@app.route("/current_month")
def get_current_month_bar():
    """
    首页条形统计图
    :return: Bar
    """
    record, year, month = data_aggregation(default=True)
    record = MouthCost(record, year, month)
    x, y = record.web_index_bar()
    status, columns = record.to_table()
    markline = list(filter(lambda d: d['name'] == '日付上限', status))[0]['balance']
    bar = draw.draw_balance_bar(xaxis=x, yaxis=y, markline=markline)
    return bar.dump_options()


@app.route("/current_usage")
def get_month_usage():
    """
    首页饼状图
    :return: Pie
    """
    budget = float(MouthCost.current_fix_data(other_record)['budget'])
    record, year, month = data_aggregation(default=True)
    record = MouthCost(record, year, month)
    data = record.web_index_pie()
    pie =  draw.draw_usage_pie(payout=data, budget=[('预算', budget)], title="本月结余")
    return pie.dump_options()


@app.route("/details", methods=['GET', 'POST'])
def details():
    name = 'select_month'
    if request.method == 'GET':
        year = 'null'
        month = 'null'
    else:
        month = request.form.get(name) # 获取界面选择的日期
        try:
            t: datetime = datetime.strptime(month, '%Y-%m')
        except ValueError:
            t = datetime.now()
        finally:
            year = t.year
            month = t.month

    return redirect(url_for('get_details', year=year, month=month))


@app.route("/details/year=<year>&month=<month>")
def get_details(year, month):
    name = 'select_month'
    record, year, month = data_aggregation(year, month)
    record = MouthCost(record, year, month)
    data, columns = [], []
    if record:
        data, columns = record.to_detail_table()
    return render_template("details.html",
                           chart_url=url_for('get_bar_chart', year=year, month=month),
                           name=name, data=data, columns=columns)


@app.route("/barChart/year=<year>&month=<month>")
def get_bar_chart(year, month):
    record, year, month = data_aggregation(year, month)
    record = MouthCost(record, year, month)
    title = '消费统计'
    if record:
        x, y = record.web_index_bar()
        title = '消费合计：{}元'.format(round(sum([float(i) for i in y[2][1]]), 2))
    else:
        x = ['无数据']
        y = []
    line = draw.draw_balance_line(xaxis=x, yaxis=y, title=title)
    return line.dump_options()


@app.route("/update", methods=['GET', 'POST'])
def update():
    name = 'select_month'
    if request.method == 'GET':
        year = 'null'
        month = 'null'
    else:
        month = request.form.get(name) # 获取界面选择的日期
        try:
            t: datetime = datetime.strptime(month, '%Y-%m')
        except ValueError:
            t = datetime.now()
        finally:
            year = t.year
            month = t.month
    return redirect(url_for('get_update', year=year, month=month))


@app.route("/update/year=<year>&month=<month>")
def get_update(year, month):
    name = 'select_month'
    record, year, month = data_aggregation(year, month)
    record = MouthCost(record, year, month)
    data, columns = [], []
    if record:
        data, columns = record.to_detail_table(update=True)
    return render_template("update.html",date_f=(year, month),
        year=year,month=month,name=name,data=data,columns=columns,dt=datetime.now())


@app.route('/add', methods=['POST'])
def add_bill():
    params = json.loads(request.data)
    code, message = get_bill_record.add_record(params)
    return jsonify({'code': code, 'message': message})


@app.route("/category_statistics", methods=['GET', 'POST'])
def category_statistics():
    name = 'select_month'
    if request.method == 'GET':
        year = 'null'
        month = 'null'
    else:
        month = request.form.get(name) # 获取界面选择的日期
        try:
            t: datetime = datetime.strptime(month, '%Y-%m')
        except ValueError:
            t = datetime.now()
        finally:
            year = t.year
            month = t.month
    return redirect(url_for('get_category', year=year, month=month))


@app.route("/category_statistics/year=<year>&month=<month>")
def get_category(year, month):
    name = 'select_month'
    record, year, month = data_aggregation(year, month)
    record = MouthCost(record, year, month)
    data, columns = record.to_table(category=True)
    return render_template(
        "category.html",
        usage_chart=url_for('get_category_pie', year=year, month=month),
        name=name,
        data=data,
        columns=columns)


@app.route("/PieChart/Category/year=<year>&month=<month>")
def get_category_pie(year, month):
    record, year, month = data_aggregation(year, month)
    record = MouthCost(record, year, month)
    eat, other = record.web_category_pie()
    if year == 'null' or month == 'null':
        year = str(datetime.now().year)
        month = str(datetime.now().month)
    pie = draw.draw_category_pie(
        inner=eat[:NUMBER_WEB_CATEGORY_PIE_EAT],
        outside=other[:NUMBER_WEB_CATEGORY_PIE_OTHER],
        inner_title=f'{year}年{month}饮食报表',
        outer_title=f'{year}年{month}其他报表')
    return pie.dump_options()


@app.route('/annual', methods=['GET', 'POST'])
def annual():
    name = 'select_year'
    if request.method == 'GET':
        year = datetime.now().year
    else:
        year = request.form.get(name) # 获取界面选择的日期
        year = int(year)

    return redirect(url_for('annual_with_year', year=year))


@app.route('/annual/year=<year>')
def annual_with_year(year):
    name = 'select_year'

    status, columns = get_bill_record.get_data_columns(year=year)

    return render_template("annual.html", name=name,
                           chart_url=url_for('get_annual_bar', year=year),
                           pie_url=url_for('get_annual_pie', year=year),
                           data=status, columns=columns
                           )


@app.route("/pieChart/year=<year>")
def get_annual_pie(year):
    eat_list, other_list = get_bill_record.get_all_eat_other_record(year)
    eat, other = get_bill_record.get_all_eat_other_sum_amount(
        eat_list,
        other_list
    )
    pie = draw.draw_category_pie(
        inner=eat[: NUMBER_WEB_CATEGORY_PIE_EAT],
        outside=other[: NUMBER_WEB_CATEGORY_PIE_OTHER],
        inner_title=f'{year}年饮食报表',
        outer_title=f'{year}年其他报表')
    return pie.dump_options()


@app.route("/barChart/year=<year>")
def get_annual_bar(year):
    record, year, month = data_aggregation(year=year)
    record = MouthCost(record, year, month)

    x, y = record.web_annual_bar(year)
    bar = draw.draw_balance_bar(x, y, title='年度收支', markline=1700+1700)
    return bar.dump_options()


@app.route("/statistics")
def annual_statistics():
    balance = get_bill_record.account_from_start_to_now()
    return render_template(
        "statistics.html",
        bar_chart_url=url_for('get_annual_statistics_bar'),
        line_chart_url=url_for('get_annual_statistics_line'),
        balance=balance
       )


@app.route('/barChart/annual_statistics')
def get_annual_statistics_bar():
    x, y = get_bill_record.web_statistical_bar()
    bar = draw.draw_balance_bar(x, y, title='年度收支')
    return bar.dump_options()


@app.route('/lineChart/annual_statistics')
def get_annual_statistics_line():
    x, y = get_bill_record.web_statistical_line()
    line = draw.draw_balance_line(x, y, title='年度结余')
    return line.dump_options()


@app.route('/search', methods=['GET', 'POST'])
def search():
    today_year = datetime.today().year
    select_year = 'select_year'
    total = False
    word = 'word'
    search_year = ''
    if request.method == 'GET':
        data = [{'name': '请选择'}]
        columns = []
    else:
        search_year = request.form.get(select_year) if request.form.get('type') == 'year' else None
        word = request.form.get('word', '')
        data, columns = get_bill_record.search_key(
            word=word,
            year=search_year
        )
        if data:
            total = round(sum([float(i['payment']) for i in data]), 4)
    return render_template(
        "tools.html",
        search_line=url_for('search_line', word='null' if not word else word, year='null' if not search_year else search_year),
        word=word,
        today_year=today_year,
        select_year=select_year,
        data=data,
        columns=columns,
        total=total,
    )


@app.route('/search/search_line/word=<word>&year=<year>')
def search_line(word, year):
    if word == 'null':
        word = ''
    data, columns = get_bill_record.search_key(
        word=word,
        year=request.form.get(year) if request.form.get('time') == 'year' else None
    )
    x = [d['date'] for d in data]
    y = [(word, [d['payment'] for d in data])]
    line = draw.draw_balance_line(xaxis=x, yaxis=y)
    return line.dump_options()



if __name__ == "__main__":
    app.config["JSON_AS_ASCII"] = False
    app.run(debug=True, port=8000)
