from flask import Flask, render_template, url_for

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


if __name__ == "__main__":
    record = MouthCost(
        eat_month=eat_month_20_4,
        other_month=other_month_20_4
    )
    app.run(debug=True, port=8000)
