import subprocess
from pathlib import Path

import datapane as dp
import pandas as pd
import plotly.express as px
from anovos.data_analyzer.association_evaluator import (
    correlation_matrix,
    variable_clustering,
    IV_calculation,
    IG_calculation,
)
from anovos.data_analyzer.quality_checker import (
    duplicate_detection,
    nullRows_detection,
    nullColumns_detection,
    outlier_detection,
    IDness_detection,
    biasedness_detection,
    invalidEntries_detection,
)
from anovos.data_analyzer.stats_generator import (
    global_summary,
    measures_of_counts,
    measures_of_centralTendency,
    measures_of_cardinality,
    measures_of_dispersion,
    measures_of_percentiles,
    measures_of_shape,
)
from anovos.shared.utils import ends_with

global_theme = px.colors.sequential.Plasma
global_theme_r = px.colors.sequential.Plasma_r
global_plot_bg_color = "rgba(0,0,0,0)"
global_paper_bg_color = "rgba(0,0,0,0)"

default_template = dp.HTML(
    '<html><img src="https://mobilewalla-anovos.s3.amazonaws.com/anovos.png" style="height:100px;display:flex;margin:auto;float:right"></img></html>'
), dp.Text("# ML-Anovos Report")


def stats_args(path, func):
    output = {}
    mainfunc_to_args = {
        "biasedness_detection": ["stats_mode"],
        "IDness_detection": ["stats_unique"],
        "outlier_detection": ["stats_unique"],
        "correlation_matrix": ["stats_unique"],
        "nullColumns_detection": ["stats_unique", "stats_mode", "stats_missing"],
        "variable_clustering": ["stats_unique", "stats_mode"],
    }
    args_to_statsfunc = {
        "stats_unique": "measures_of_cardinality",
        "stats_mode": "measures_of_centralTendency",
        "stats_missing": "measures_of_counts",
    }

    for arg in mainfunc_to_args.get(func, []):
        output[arg] = {
            "file_path": (ends_with(path) + args_to_statsfunc[arg] + ".csv"),
            "file_type": "csv",
            "file_configs": {"header": True, "inferSchema": True},
        }

    return output


def anovos_basic_report(
    spark,
    idf,
    id_col="",
    label_col="",
    event_label="",
    output_path=".",
    local_or_emr="local",
    print_impact=True,
):
    """
    :param spark: Spark Session
    :param idf: Input Dataframe
    :param id_col: ID column
    :param label_col: Label/Target column
    :param event_label: Value of (positive) event (i.e label 1)
    :param output_path: File Path for saving metrics and basic report
    :param local_or_emr: "local" (default), "emr"
                         "emr" if the files are read from or written in AWS s3
    """
    global num_cols
    global cat_cols

    SG_funcs = [
        global_summary,
        measures_of_counts,
        measures_of_centralTendency,
        measures_of_cardinality,
        measures_of_dispersion,
        measures_of_percentiles,
        measures_of_shape,
    ]
    QC_rows_funcs = [duplicate_detection, nullRows_detection]
    QC_cols_funcs = [
        nullColumns_detection,
        outlier_detection,
        IDness_detection,
        biasedness_detection,
        invalidEntries_detection,
    ]
    AA_funcs = [correlation_matrix, variable_clustering]
    AT_funcs = [IV_calculation, IG_calculation]
    all_funcs = SG_funcs + QC_rows_funcs + QC_cols_funcs + AA_funcs + AT_funcs

    if local_or_emr == "local":
        local_path = output_path
    else:
        local_path = "report_stats"
    Path(local_path).mkdir(parents=True, exist_ok=True)

    for func in all_funcs:
        if func in SG_funcs:
            stats = func(spark, idf)
        elif func in (QC_rows_funcs + QC_cols_funcs):
            extra_args = stats_args(output_path, func.__name__)
            stats = func(spark, idf, **extra_args)[1]
        elif func in AA_funcs:
            extra_args = stats_args(output_path, func.__name__)
            stats = func(spark, idf, drop_cols=id_col, **extra_args)
        elif label_col:
            if func in AT_funcs:
                stats = func(spark, idf, label_col=label_col, event_label=event_label)
        else:
            continue

        stats.toPandas().to_csv(
            ends_with(local_path) + func.__name__ + ".csv", index=False
        )

        if local_or_emr == "emr":
            bash_cmd = (
                "aws s3 cp "
                + ends_with(local_path)
                + func.__name__
                + ".csv "
                + ends_with(output_path)
            )
            output = subprocess.check_output(["bash", "-c", bash_cmd])

        if print_impact:
            print(func.__name__, ":\n")
            stats = spark.read.csv(
                ends_with(output_path) + func.__name__ + ".csv",
                header=True,
                inferSchema=True,
            )
            stats.show()

    def remove_u_score(col):
        col_ = col.split("_")
        bl = []

        for i in col_:
            if i == "nullColumns" or i == "nullRows":
                bl.append("Null")
            else:
                bl.append(i[0].upper() + i[1:])

        return " ".join(bl)

    global_summary_df = pd.read_csv(ends_with(local_path) + "global_summary.csv")
    rows_count = int(
        global_summary_df[global_summary_df.metric.values == "rows_count"].value.values[
            0
        ]
    )
    catcols_count = int(
        global_summary_df[
            global_summary_df.metric.values == "catcols_count"
        ].value.values[0]
    )
    numcols_count = int(
        global_summary_df[
            global_summary_df.metric.values == "numcols_count"
        ].value.values[0]
    )
    columns_count = int(
        global_summary_df[
            global_summary_df.metric.values == "columns_count"
        ].value.values[0]
    )
    catcols_name = ",".join(
        list(
            global_summary_df[
                global_summary_df.metric.values == "catcols_name"
            ].value.values
        )
    )
    numcols_name = ",".join(
        list(
            global_summary_df[
                global_summary_df.metric.values == "numcols_name"
            ].value.values
        )
    )

    l1 = dp.Group(
        dp.Text("# "),
        dp.Text("*This section summarizes the dataset with key statistical metrics.*"),
        dp.Text("# "),
        dp.Text("# "),
        dp.Text("### Global Summary"),
        dp.Group(
            dp.Text(" Total Number of Records: **" + str(f"{rows_count:,d}") + "**"),
            dp.Text(" Total Number of Attributes: **" + str(columns_count) + "**"),
            dp.Text(" Number of Numerical Attributes : **" + str(numcols_count) + "**"),
            dp.Text(" Numerical Attributes Name : **" + str(numcols_name) + "**"),
            dp.Text(
                " Number of Categorical Attributes : **" + str(catcols_count) + "**"
            ),
            dp.Text(" Categorical Attributes Name : **" + str(catcols_name) + "**"),
            rows=6,
        ),
        rows=8,
    )

    l2 = dp.Text("### Statistics by Metric Type")

    SG_content = []
    for i in SG_funcs:
        if i.__name__ != "global_summary":
            SG_content.append(
                dp.DataTable(
                    pd.read_csv(ends_with(local_path) + str(i.__name__) + ".csv").round(
                        3
                    ),
                    label=remove_u_score(i.__name__),
                )
            )
    l3 = dp.Group(dp.Select(blocks=SG_content, type=dp.SelectType.TABS), dp.Text("# "))

    tab1 = dp.Group(
        l1,
        dp.Text("# "),
        l2,
        l3,
        dp.Text("# "),
        dp.Text("# "),
        dp.Text("# "),
        label="Descriptive Statistics",
    )

    QCcol_content = []
    for i in QC_cols_funcs:
        QCcol_content.append(
            [
                dp.Text("### " + str(remove_u_score(i.__name__))),
                dp.DataTable(
                    pd.read_csv(ends_with(local_path) + str(i.__name__) + ".csv").round(
                        3
                    )
                ),
                dp.Text("#"),
                dp.Text("#"),
            ]
        )
    QCrow_content = []
    for i in QC_rows_funcs:
        if i.__name__ == "duplicate_detection":
            stats = pd.read_csv(ends_with(local_path) + str(i.__name__) + ".csv").round(
                3
            )
            unique_rows_count = (
                " No. Of Unique Rows: **"
                + str(
                    format(
                        int(stats[stats["metric"] == "unique_rows_count"].value.values),
                        ",",
                    )
                )
                + "**"
            )
            total_rows_count = (
                " No. of Rows: **"
                + str(
                    format(
                        int(stats[stats["metric"] == "rows_count"].value.values), ","
                    )
                )
                + "**"
            )
            duplicate_rows_count = (
                " No. of Duplicate Rows: **"
                + str(
                    format(
                        int(stats[stats["metric"] == "duplicate_rows"].value.values),
                        ",",
                    )
                )
                + "**"
            )
            duplicate_rows_pct = (
                " Percentage of Duplicate Rows: **"
                + str(
                    float(
                        stats[stats["metric"] == "duplicate_pct"].value.values * 100.0
                    )
                )
                + " %"
                + "**"
            )
            QCrow_content.append(
                [
                    dp.Text("### " + str(remove_u_score(i.__name__))),
                    dp.Group(
                        dp.Text(total_rows_count),
                        dp.Text(unique_rows_count),
                        dp.Text(duplicate_rows_count),
                        dp.Text(duplicate_rows_pct),
                        rows=4,
                    ),
                    dp.Text("#"),
                    dp.Text("#"),
                ]
            )
        else:
            QCrow_content.append(
                [
                    dp.Text("### " + str(remove_u_score(i.__name__))),
                    dp.DataTable(
                        pd.read_csv(
                            ends_with(local_path) + str(i.__name__) + ".csv"
                        ).round(3)
                    ),
                    dp.Text("#"),
                    dp.Text("#"),
                ]
            )
    QCcol_content = [item for sublist in QCcol_content for item in sublist]
    QCrow_content = [item for sublist in QCrow_content for item in sublist]

    tab2 = dp.Group(
        dp.Text("# "),
        dp.Text(
            "*This section identifies the data quality issues at both row and column level.*"
        ),
        dp.Text("# "),
        dp.Text("# "),
        dp.Select(
            blocks=[
                dp.Group(
                    dp.Text("# "),
                    dp.Group(*QCcol_content),
                    rows=2,
                    label="Column Level",
                ),
                dp.Group(
                    dp.Text("# "), dp.Group(*QCrow_content), rows=2, label="Row Level"
                ),
            ],
            type=dp.SelectType.TABS,
        ),
        dp.Text("# "),
        dp.Text("# "),
        label="Quality Check",
    )

    AA_content = []
    for i in AA_funcs + AT_funcs:
        if i.__name__ == "correlation_matrix":
            stats = pd.read_csv(ends_with(local_path) + str(i.__name__) + ".csv").round(
                3
            )
            feats_order = list(stats["attribute"].values)
            stats = stats.round(3)
            fig = px.imshow(
                stats[feats_order],
                y=feats_order,
                color_continuous_scale=global_theme,
                aspect="auto",
            )
            fig.layout.plot_bgcolor = global_plot_bg_color
            fig.layout.paper_bgcolor = global_paper_bg_color
            AA_content.append(
                dp.Group(
                    dp.Text("##"),
                    dp.DataTable(stats[["attribute"] + feats_order]),
                    dp.Plot(fig),
                    rows=3,
                    label=remove_u_score(i.__name__),
                )
            )

        elif i.__name__ == "variable_clustering":
            stats = (
                pd.read_csv(ends_with(local_path) + str(i.__name__) + ".csv")
                .round(3)
                .sort_values(by=["Cluster"], ascending=True)
            )
            fig = px.sunburst(
                stats,
                path=["Cluster", "Attribute"],
                values="RS_Ratio",
                color_discrete_sequence=global_theme,
            )
            fig.layout.plot_bgcolor = global_plot_bg_color
            fig.layout.paper_bgcolor = global_paper_bg_color
            fig.layout.autosize = True
            AA_content.append(
                dp.Group(
                    dp.Text("##"),
                    dp.DataTable(stats),
                    dp.Plot(fig),
                    rows=3,
                    label=remove_u_score(i.__name__),
                )
            )

        else:
            if label_col:
                stats = pd.read_csv(
                    ends_with(local_path) + str(i.__name__) + ".csv"
                ).round(3)
                col_nm = [x for x in list(stats.columns) if "attribute" not in x]
                stats = stats.sort_values(col_nm[0], ascending=True)
                fig = px.bar(
                    stats,
                    x=col_nm[0],
                    y="attribute",
                    orientation="h",
                    color_discrete_sequence=global_theme,
                )
                fig.layout.plot_bgcolor = global_plot_bg_color
                fig.layout.paper_bgcolor = global_paper_bg_color
                fig.layout.autosize = True
                AA_content.append(
                    dp.Group(
                        dp.Text("##"),
                        dp.DataTable(stats),
                        dp.Plot(fig),
                        label=remove_u_score(i.__name__),
                        rows=3,
                    )
                )

    tab3 = dp.Group(
        dp.Text("# "),
        dp.Text(
            "*This section analyzes the interaction between different attributes and/or the relationship between an attribute & the binary target variable.*"
        ),
        dp.Text("# "),
        dp.Text("# "),
        dp.Text("### Association Matrix & Plot"),
        dp.Select(blocks=AA_content, type=dp.SelectType.DROPDOWN),
        dp.Text("### "),
        dp.Text("## "),
        dp.Text("## "),
        dp.Text("## "),
        label="Attribute Associations",
    )

    basic_report = dp.Report(
        default_template[0],
        default_template[1],
        dp.Select(blocks=[tab1, tab2, tab3], type=dp.SelectType.TABS),
    ).save(ends_with(local_path) + "basic_report.html", open=True)

    if local_or_emr == "emr":
        bash_cmd = (
            "aws s3 cp "
            + ends_with(local_path)
            + "basic_report.html "
            + ends_with(output_path)
        )
        output = subprocess.check_output(["bash", "-c", bash_cmd])
