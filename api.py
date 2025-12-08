import io
import base64
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from physics import quasi_steady_flap
from run_simulation import base_params

plt.switch_backend("Agg")


# ------------------------- FastAPI Setup -------------------------

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ------------------------- Data Models -------------------------

class SimRequest(BaseModel):
    f: float
    stroke_amp: float
    pitch_amp: float
    t_end: float


class SweepStepsRequest(BaseModel):
    sweep_type: str
    base: float
    freq_hz: float
    pitch_deg: float
    step: float
    stroke_amp: float
    t_end: float


# ------------------------- Helper Functions -------------------------

def fig_to_base64(fig):
    """Convert Matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def apply_axes_style(ax):
    """Standardize styling for dark plots."""
    ax.set_facecolor("black")
    ax.xaxis.set_major_locator(MaxNLocator(6))
    ax.grid(True, color="gray", alpha=0.3)
    ax.tick_params(colors="white")


LINE_COLORS = ["lime", "orange", "yellow", "cyan", "violet"]


# ------------------------- Endpoints -------------------------

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


@app.post("/simulate_plot")
def simulate_plot(req: SimRequest):
    params = base_params.copy()
    params["f"] = req.f
    params["stroke_amp"] = req.stroke_amp
    params["pitch_amp"] = req.pitch_amp
    params["t_end"] = req.t_end

    result = quasi_steady_flap(params)

    fig, axs = plt.subplots(3, 2, figsize=(11, 10), dpi=100)
    fig.patch.set_facecolor("black")

    titles = [
        "Lift vs Time", "Drag vs Time",
        "Power vs Time", "Efficiency vs Time",
        "Pitch Angle vs Time", "Stroke Position vs Time"
    ]

    ylabels = [
        "Lift (N)", "Drag (N)",
        "Power (W)", "Efficiency (η)",
        "Pitch (deg)", "Stroke (m)"
    ]

    data_series = [
        result["L"], result["D"],
        result["P"], result["eta"],
        result["theta_deg"], result["x_pos"]
    ]

    for ax, title, ylab, data, color in zip(
        axs.flat, titles, ylabels, data_series, LINE_COLORS
    ):
        ax.plot(result["t"], data, color=color, linewidth=1.8)
        ax.set_title(title, color="white")
        ax.set_ylabel(ylab, color="white")
        ax.set_xlabel("Time (s)", color="white")
        apply_axes_style(ax)

    fig.subplots_adjust(hspace=0.38, wspace=0.30)

    return {"plot_base64": fig_to_base64(fig)}


@app.post("/sweep_steps")
def sweep_steps(req: SweepStepsRequest):
    values = [
        req.base - 2 * req.step,
        req.base - req.step,
        req.base,
        req.base + req.step,
        req.base + 2 * req.step
    ]

    fig, axs = plt.subplots(3, 2, figsize=(11, 10), dpi=100)
    fig.patch.set_facecolor("black")

    for idx, val in enumerate(values):
        params = base_params.copy()
        params["stroke_amp"] = req.stroke_amp
        params["t_end"] = req.t_end

        if req.sweep_type == "pitch":
            params["pitch_amp"] = np.deg2rad(val)
            params["f"] = req.freq_hz
            label_val = f"{val}°"
            legend_unit = "(deg)"
        else:
            params["pitch_amp"] = np.deg2rad(req.pitch_deg)
            params["f"] = val
            label_val = f"{val} Hz"
            legend_unit = "(Hz)"

        r = quasi_steady_flap(params)
        color = LINE_COLORS[idx]

        axs[0, 0].plot(r["t"], r["L"], color=color, label=label_val)
        axs[0, 1].plot(r["t"], r["D"], color=color)
        axs[1, 0].plot(r["t"], r["P"], color=color)
        axs[1, 1].plot(r["t"], r["eta"], color=color)
        axs[2, 0].plot(r["t"], r["theta_deg"], color=color)
        axs[2, 1].plot(r["t"], r["x_pos"], color=color)

    titles = [
        "Lift vs Time", "Drag vs Time",
        "Power vs Time", "Efficiency vs Time",
        "Pitch Angle vs Time", "Stroke Position vs Time"
    ]

    ylabels = [
        "Lift (N)", "Drag (N)",
        "Power (W)", "Efficiency (η)",
        "Pitch (deg)", "Stroke (m)"
    ]

    for ax, title, ylab in zip(axs.flat, titles, ylabels):
        ax.set_title(title, color="white")
        ax.set_ylabel(ylab, color="white")
        ax.set_xlabel("Time (s)", color="white")
        apply_axes_style(ax)

    fig.legend(
        title=f"{req.sweep_type.capitalize()} Sweep {legend_unit}",
        loc="upper center",
        fontsize=10,
        title_fontsize=12,
        ncol=5,
        frameon=False,
        labelcolor="white"
    )

    fig.subplots_adjust(
        hspace=0.38,
        wspace=0.30,
        top=0.90
    )

    return {"plot_base64": fig_to_base64(fig)}
