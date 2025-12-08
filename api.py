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

# Use non-interactive backend
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


# ------------------------- Helper -------------------------

def fig_to_base64(fig):
    """Convert Matplotlib figure to base64 PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def apply_plot_styling(ax):
    """Apply black background and tick reduction."""
    ax.set_facecolor("black")
    ax.xaxis.set_major_locator(MaxNLocator(6))
    ax.grid(True, color="gray", alpha=0.3)


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

    titles_units = [
        ("Lift (N)", result["L"]),
        ("Drag (N)", result["D"]),
        ("Power (W)", result["P"]),
        ("Efficiency (η)", result["eta"]),
        ("Pitch Angle (deg)", result["theta_deg"]),
        ("Stroke Position (m)", result["x_pos"])
    ]

    for ax, (title, data), color in zip(
        axs.flat, titles_units, LINE_COLORS
    ):
        ax.plot(result["t"], data, color=color, linewidth=1.8)
        ax.set_title(title, color="white")
        ax.set_xlabel("Time (s)", color="white")
        ax.tick_params(colors="white")
        apply_plot_styling(ax)

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
        elif req.sweep_type == "frequency":
            params["pitch_amp"] = np.deg2rad(req.pitch_deg)
            params["f"] = val
        else:
            return {"error": "sweep_type must be 'pitch' or 'frequency'"}

        r = quasi_steady_flap(params)
        color = LINE_COLORS[idx]

        axs[0, 0].plot(r["t"], r["L"], color=color, label=f"{val}")
        axs[0, 1].plot(r["t"], r["D"], color=color)
        axs[1, 0].plot(r["t"], r["P"], color=color)
        axs[1, 1].plot(r["t"], r["eta"], color=color)
        axs[2, 0].plot(r["t"], r["theta_deg"], color=color)
        axs[2, 1].plot(r["t"], r["x_pos"], color=color)

    titles = [
        "Lift (N)", "Drag (N)",
        "Power (W)", "Efficiency (η)",
        "Pitch Angle (deg)", "Stroke Position (m)"
    ]

    for ax, title in zip(axs.flat, titles):
        ax.set_title(title, color="white")
        ax.set_xlabel("Time (s)", color="white")
        ax.tick_params(colors="white")
        apply_plot_styling(ax)

    # Legend centered at top
    fig.legend(
        title=f"{req.sweep_type.capitalize()} Sweep",
        title_fontsize=12,
        fontsize=10,
        loc="upper center",
        ncol=5,
        frameon=False,
        labelcolor="white"
    )

    fig.subplots_adjust(
        hspace=0.38,
        wspace=0.30,
        top=0.90  # Leaves room for legend
    )

    return {"plot_base64": fig_to_base64(fig)}
