from pathlib import Path

import pandas as pd

from Tests.TestHelpers import get_jmeter_result_path


def print_result_infos(df):
    df["RealLatency"] = df["elapsed"] - df["Connect"]
    print("Max Latency:", df["RealLatency"].max())
    print("Min Latency: ", df["RealLatency"].min())
    print("Avg Latency:", df["RealLatency"].mean())
    print("Std Latency", df["RealLatency"].std())
    print("10th percentile: ", df["RealLatency"].quantile(0.1))
    print("90th percentile: ", df["RealLatency"].quantile(0.9))
    print(
        "% of Success",
        len(df[df["responseCode"] == 200]) / df["RealLatency"].count() * 100,
    )
    print(
        "% of Failure",
        len(df[df["responseCode"] != 200]) / df["RealLatency"].count() * 100,
    )
    print("Number executions", df["RealLatency"].count())


def plot_real_latency(color: str, label: str, ax, test_name: str, file_name: str):
    jmeter_file = get_jmeter_result_path(test_name) + "/" + file_name
    df = pd.read_csv(jmeter_file)

    print_result_infos(df)
    plot_data_frame(df.reset_index(), "RealLatency", "index", color, label, ax)


def plot_data_frame(data_frame, y, x, color, label, ax):
    data_frame.plot(
        marker="o",
        kind="line",
        y=y,
        x=x,
        color=color,
        label=label,
        ax=ax,
    )


def save_fig(plt, result_path: str, serverless_provider: str, ts: float):
    fig = plt.gcf()
    plt.show()
    Path(result_path).mkdir(parents=True, exist_ok=True)
    fig.savefig(
        "{0}/{1}-{2}.png".format(result_path, serverless_provider, str(ts)),
        transparent=False,
    )
    fig.savefig(
        "{0}/{1}-{2}.pdf".format(result_path, serverless_provider, str(ts)),
        transparent=False,
    )
