from datetime import datetime
from flask import Flask, render_template, url_for, request
from werkzeug.utils import redirect

from api.bill_manage import MouthCost
from cost_record import *
from api import draw

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    status, columns = record.to_table()
    return render_template("index.html",
                           chart_url=url_for('get_current_month_bar'),
                           usage_chart=url_for("get_month_usage"),
                           data=status, columns=columns)


@app.route("/current_month")
def get_current_month_bar():
    """
    首页条形统计图
    :return: Bar
    """
    x, y = record.web_index_bar()
    bar = draw.draw_balance_bar(xaxis=x, yaxis=y)
    return bar.dump_options()


@app.route("/current_usage")
def get_month_usage():
    """
    首页饼状图
    :return: Pie
    """
    pie = record.web_index_pie()
    return pie.dump_options()


@app.route("/details", methods=['GET', 'POST'])
def details():
    name = 'select_month'
    if request.method == 'GET':
        t = datetime.now()
    else:
        month = request.form.get(name)
        try:
            t: datetime = datetime.strptime(month, '%Y-%m')
        except ValueError:
            t = datetime.now()

    return redirect(url_for('get_details', year=t.year, month=t.month))


@app.route("/details/year=<year>&month=<month>")
def get_details(year, month):
    name = 'select_month'
    year = int(year)
    month = int(month)
    data, columns = api.get_balance_details_in_month(year, month)

    return render_template("details.html",
                           chart_url=url_for('get_bar_chart', year=year, month=month),
                           data=data, columns=columns, name=name)


if __name__ == "__main__":
    record = MouthCost(
        eat_month=eat_month_20_4,
        other_month=other_month_20_4
    )
    app.run(debug=True, port=8000)
