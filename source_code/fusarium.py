import seaborn as sns
import pandas as pd
import matplotlib.transforms as mtransforms
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from source_code.general_functions import select_time_range


def equation_fusarium(t: float):
    tmin = 5
    tmax = 30
    if t <= tmin:
        return 0
    if t >= tmax:
        return 0
    b, c = 17.2, 10.5
    teq = (t - tmin) / (tmax - tmin)
    y = (teq**b) * ((1 - teq) ** c)
    return y * 98294267.23029275 / 1.0218637974743057


# ð=ð**(100âRH)/(1+ð ** (ðâðÃð¡))


def equation_fusarium_rh(rh: float) -> float:
    # a = 1
    # b = 2
    if rh > 100:
        rh = 100
    c = 0.850
    y = c ** (100 - rh)
    return y * 1 / 0.85


def plot_risk_fusarium(
    df_airtemp: pd.DataFrame,
    df_moisture,
    temp_min: float,
    temp_max: float,
    hist_start: float,
    hist_end: float,
    start_dd_mm: str,
    end_dd_mm: str,
    moving_average: int,
):

    # Step 1: create the time intervals from the input "dd.mm"
    df_airtemp = select_time_range(
        df_airtemp, start_dd_mm=start_dd_mm, end_dd_mm=end_dd_mm
    )
    df_moisture = select_time_range(
        df_moisture, start_dd_mm=start_dd_mm, end_dd_mm=end_dd_mm
    )
    # Step 2: apply the function for the model

    # Step 2.1: the model for temperature
    df_airtemp["useful_t"] = df_airtemp.TT_TU.apply(equation_fusarium)

    # Step 2.2: the model for moisutre
    df_moisture["rh_risk"] = df_moisture.RF_STD.apply(equation_fusarium_rh)

    # Step 3: process and prepare for plotting
    # Step 3.1: for temperature
    df_airtemp = df_airtemp.groupby(["year"]).mean()
    avg_hist = df_airtemp[
        (df_airtemp.index <= hist_end) & (df_airtemp.index >= hist_start)  # type: ignore
    ]["useful_t"].mean()
    max_hist = df_airtemp[
        (df_airtemp.index <= hist_end) & (df_airtemp.index >= hist_start)  # type: ignore
    ]["useful_t"].max()
    min_hist = df_airtemp[
        (df_airtemp.index <= hist_end) & (df_airtemp.index >= hist_start)  # type: ignore
    ]["useful_t"].min()
    df_airtemp[f"{moving_average}years_average"] = df_airtemp.useful_t.rolling(7).mean()

    # Step 3.2: for moisture
    df_moisture = df_moisture.groupby(["year"]).mean()
    avg_hist_m = df_moisture[
        (df_moisture.index <= hist_end) & (df_moisture.index >= hist_start)
    ]["rh_risk"].mean()
    # max_hist = df_airtemp[(df_airtemp.index <= hist_end)&(df_airtemp.index >= hist_start)]["useful_t"].max()
    # min_hist = df_airtemp[(df_airtemp.index <= hist_end)&(df_airtemp.index >= hist_start)]["useful_t"].min()
    df_moisture[f"{moving_average}years_average"] = df_moisture.rh_risk.rolling(
        7
    ).mean()

    # Step 4: plot
    # Step 4.1: Make a grid
    gs = gridspec.GridSpec(10, 10)
    fig = plt.figure(figsize=(15, 8))

    # Step 4.2: Plot in different spaces of the grid
    # Step 4.2.1: Left upper corner
    ax1 = fig.add_subplot(gs[0:2, 0:5])
    degr = [equation_fusarium(i / 100) for i in range(500, 3000, 1)]
    sns.lineplot(x=[i / 100 for i in range(500, 3000, 1)], y=degr, ax=ax1)
    ax1.set_xlabel("Temperature ($^\circ$C)")
    ax1.set_ylabel("Development of Fusarium")

    # Step 4.2.2: Right upper corner
    ax2 = fig.add_subplot(gs[0:2, 5:10], sharey=ax1)
    degr = [equation_fusarium_rh(i) for i in range(65, 101)]
    sns.lineplot(x=[i for i in range(65, 101)], y=degr, ax=ax2)
    ax2.set_xlabel("RH (%)")
    plt.setp(ax2.get_yticklabels(), visible=False)

    # Step 4.2.3: Middle center
    ax3 = fig.add_subplot(gs[3:7, :])
    sns.lineplot(
        x="year",
        y="useful_t",
        data=df_airtemp,
        label="yearly temperature risk",
        ax=ax3,
        alpha=0.55,
    )
    sns.lineplot(
        x="year",
        y=f"{moving_average}years_average",
        ax=ax3,
        data=df_airtemp,
        label=f"{moving_average} years average",
    )
    # sns.lineplot(x = df_airtemp.index, y = min_hist,linestyle="dashed",ax=ax3, label=f"minimum in the historical period ({hist_start}-{hist_end})")
    sns.lineplot(
        x=df_airtemp.index,
        y=avg_hist,
        linestyle="dashed",
        ax=ax3,
        label=f"historic temperature risk ({hist_start}-{hist_end})",
    )
    # sns.lineplot(x = df_airtemp.index, y = max_hist, linestyle="dashed",ax=ax3, label=f"maximum period in the historical period ({hist_start}-{hist_end})")
    # plt.ylabel("% of hours with optimal temperature")
    # plt.plot([hist_end,hist_end], [-0.00,0.05], lw=2, color = "0.65", label = "historical period (left)")
    ax3.set_xlabel("")
    ax3.set_ylabel("risk from temperature")

    # Step 4.2.4: Bottom center
    ax4 = fig.add_subplot(gs[7:11, :], sharex=ax3)  # row 1, span all columns
    ax4.sharex(ax3)
    sns.lineplot(
        x="year",
        y="rh_risk",
        data=df_moisture,
        label="yearly rh risk",
        ax=ax4,
        alpha=0.55,
    )
    sns.lineplot(
        x="year",
        y=f"{moving_average}years_average",
        ax=ax4,
        data=df_moisture,
        label=f"{moving_average} years average",
    )
    sns.lineplot(
        x=df_moisture.index,
        y=avg_hist_m,
        linestyle="dashed",
        ax=ax4,
        label=f"historic rh risk ({hist_start}-{hist_end})",
    )
    ax4.set_ylabel("risk from RH")

    plt.setp(ax3.get_xticklabels(), visible=False)

    # Step 4.3: Add suptitles, labels, ticks
    fig.suptitle(
        "Evolution of parameters associated with disease development of \n Fusarium graminearum in Maize",
        fontsize=16,
    )
    for ax, label in zip([ax1, ax2, ax3, ax4], ["a", "b", "c", "d"]):
        trans = mtransforms.ScaledTranslation(10 / 72, -5 / 72, fig.dpi_scale_trans)
        ax.text(
            0,
            1,
            label,
            transform=ax.transAxes + trans,
            fontsize="medium",
            verticalalignment="top",
            fontfamily="serif",
            bbox=dict(facecolor="0.7", edgecolor="none", pad=3.0),
        )

    plt.figtext(
        0.1,
        0.00,
        "Figure 4. Evolution of environmental factors asociated with development of Perithecia in $\it{Fusarium }$  $\it{graminearum}$ in the time period of 1950 - 2020 in 20 weather stations in Germany. \n (a)(b) $\it{Fusarium }$  $\it{graminearum}$ development at different temperatures and RH, where 1 on y axis correspods to the optimal temperature / humidity. \n (c)(d) Evolution of the disease risk corresponding to the given parameter, calculated yearly as a mean of hourly risk, on the months of June August.",
    )
    plt.show()
