from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie


def draw_balance_bar(xaxis, yaxis, title="消费统计", markline=None, width=2000) -> Bar:
    bar = Bar()
    bar.add_xaxis(xaxis)
    for name, axis in yaxis:
        bar.add_yaxis(name, axis, category_gap="20%", gap="0%")
    bar.set_global_opts(title_opts=opts.TitleOpts(title=title, ),
                        datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100),
                                       opts.DataZoomOpts(type_="inside")],
                        tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='shadow'))
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    return bar


def draw_usage_pie(payout, budget, title) -> Pie:
    pie = Pie()
    pie.add(series_name=title,
          data_pair=budget,
          radius=["0%", "30%"],
          label_opts=opts.LabelOpts(position="inner"),
          )
    pie.add(series_name=title,
          radius=["30%", "40%"],
          data_pair=payout,
          label_opts=opts.LabelOpts(position="outside",
                                    formatter="{b}:\n{c}({d}%)",
                                    border_width=1,
                                    border_radius=4,
                                    ),
          )

    return pie