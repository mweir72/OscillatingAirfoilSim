"""
Flapping-wing simulation FastAPI backend (fixed & cleaned).
"""

from run_simulation import base_params
from physics import quasi_steady_flap
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import matplotlib
matplotlib.use("Agg")


# ------------------------- FastAPI Setup -------------------------

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# ------------------------- Data Models -------------------------

class SimRequest(BaseModel):
    f: float
    pitch_amp: float   # radians
    t_end: float


class SweepStepsRequest(BaseModel):
    sweep_type: str
    base: float
    freq_hz: float
    pitch_deg: float
    step: float
    t_end: float


# ------------------------- Helper -------------------------

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=80)
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return img


# ------------------------- Endpoints -------------------------

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


# ------------------- SINGLE SIMULATION -------------------

@app.post("/simulate_plot")
def simulate_plot(req: SimRequest):

    params = base_params.copy()
    params["f"] = req.f
    params["pitch_amp"] = req.pitch_amp
    params["t_end"] = req.t_end

    result = quasi_steady_flap(params)

    plt.style.use("dark_background")
    fig, axs = plt.subplots(3, 2, figsize=(10, 12))
    fig.tight_layout(pad=3.0)
    plt.subplots_adjust(hspace=0.6)

    plots = [
        ("Lift (N)", result["L"]),
        ("Drag (N)", result["D"]),
        ("Power (W)", result["P"]),
        ("Efficiency", result["eta"]),
        ("Pitch Angle (deg)", result["theta_deg"]),
        ("Stroke Position (m)", result["x_pos"])
    ]

    for ax, (title, data) in zip(axs.flat, plots):
        ax.plot(result["t"], data, color="#00ff88")
        ax.set_title(title)
        ax.set_xlabel("Time (s)")
        ax.grid(True, alpha=0.3)

    return {"plot_base64": fig_to_base64(fig)}


# ------------------- SWEEP SIMULATION -------------------

@app.post("/sweep_steps")
def sweep_steps(req: SweepStepsRequest):

    # Sweep values: base ± step, ±2*step
    values = [
        req.base - 2 * req.step,
        req.base - req.step,
        req.base,
        req.base + req.step,
        req.base + 2 * req.step
    ]

    colors = ["#FF6B6B", "#F7B267", "#F9E784", "#63D471", "#4D8BFF"]

    plt.style.use("dark_background")
    fig, axs = plt.subplots(3, 2, figsize=(10, 12))
    fig.tight_layout(pad=3.0)
    plt.subplots_adjust(hspace=0.6)

    for idx, val in enumerate(values):

        params = base_params.copy()
        params["t_end"] = req.t_end

        if req.sweep_type == "pitch":
            params["pitch_amp"] = np.deg2rad(val)
            params["f"] = req.freq_hz
            label = f"{val} deg"

        elif req.sweep_type == "frequency":
            params["pitch_amp"] = np.deg2rad(req.pitch_deg)
            params["f"] = val
            label = f"{val} Hz"

        r = quasi_steady_flap(params)

        axs[0, 0].plot(r["t"], r["L"], color=colors[idx], label=label)
        axs[0, 1].plot(r["t"], r["D"], color=colors[idx])
        axs[1, 0].plot(r["t"], r["P"], color=colors[idx])
        axs[1, 1].plot(r["t"], r["eta"], color=colors[idx])
        axs[2, 0].plot(r["t"], r["theta_deg"], color=colors[idx])
        axs[2, 1].plot(r["t"], r["x_pos"], color=colors[idx])

    titles = [
        "Lift (N)", "Drag (N)",
        "Power (W)", "Efficiency",
        "Pitch Angle (deg)", "Stroke Position (m)"
    ]

    for ax, title in zip(axs.flat, titles):
        ax.set_title(title)
        ax.set_xlabel("Time (s)")
        ax.grid(True, alpha=0.3)

    # Legend: top-center
    axs[0, 0].legend(
        loc="upper center",
        bbox_to_anchor=(1.05, 1.40),
        ncol=3
    )

    return {"plot_base64": fig_to_base64(fig)}
