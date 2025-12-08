import io
import base64
import numpy as np
import matplotlib.pyplot as plt

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from physics import quasi_steady_flap
from run_simulation import base_params


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
    sweep_type: str          # "pitch" or "frequency"
    freq_hz: float
    pitch_deg: float
    step: float
    stroke_amp: float
    t_end: float


# ------------------------- Helper Function -------------------------

def fig_to_base64(fig):
    """Convert a Matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return img_str


# ------------------------- Endpoints -------------------------

@app.get("/")
def serve_ui():
    """Serve the web-based UI."""
    return FileResponse("static/index.html")


@app.post("/simulate_plot")
def simulate_plot(req: SimRequest):
    """
    Run a single simulation and return a base64-encoded plot.
    """

    params = base_params.copy()
    params["f"] = req.f
    params["stroke_amp"] = req.stroke_amp
    params["pitch_amp"] = req.pitch_amp
    params["t_end"] = req.t_end

    result = quasi_steady_flap(params)

    fig, axs = plt.subplots(3, 2, figsize=(10, 10))

    axs[0, 0].plot(result["t"], result["L"])
    axs[0, 0].set_title("Lift")

    axs[0, 1].plot(result["t"], result["D"])
    axs[0, 1].set_title("Drag")

    axs[1, 0].plot(result["t"], result["P"])
    axs[1, 0].set_title("Power")

    axs[1, 1].plot(result["t"], result["eta"])
    axs[1, 1].set_title("Efficiency")

    axs[2, 0].plot(result["t"], result["theta_deg"])
    axs[2, 0].set_title("Pitch Angle")

    axs[2, 1].plot(result["t"], result["x_pos"])
    axs[2, 1].set_title("Stroke Position")

    for ax in axs.flat:
        ax.set_xlabel("Time (s)")
        ax.grid(True)

    img_b64 = fig_to_base64(fig)

    return {"plot_base64": img_b64}


@app.post("/sweep_steps")
def sweep_steps(req: SweepStepsRequest):
    """
    Perform a 5-step sweep (±2 step, ±1 step, base) for either
    pitch or frequency and return a multi-curve plot.
    """

    values = [
        req.base - 2 * req.step,
        req.base - req.step,
        req.base,
        req.base + req.step,
        req.base + 2 * req.step
    ]

    fig, axs = plt.subplots(3, 2, figsize=(10, 10))
    colors = plt.cm.viridis(np.linspace(0.0, 1.0, len(values)))

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

        result = quasi_steady_flap(params)

        axs[0, 0].plot(
            result["t"], result["L"],
            color=colors[idx], label=f"{val}"
        )
        axs[0, 1].plot(result["t"], result["D"], color=colors[idx])
        axs[1, 0].plot(result["t"], result["P"], color=colors[idx])
        axs[1, 1].plot(result["t"], result["eta"], color=colors[idx])
        axs[2, 0].plot(result["t"], result["theta_deg"], color=colors[idx])
        axs[2, 1].plot(result["t"], result["x_pos"], color=colors[idx])

    axs[0, 0].set_title("Lift")
    axs[0, 1].set_title("Drag")
    axs[1, 0].set_title("Power")
    axs[1, 1].set_title("Efficiency")
    axs[2, 0].set_title("Pitch Angle")
    axs[2, 1].set_title("Stroke Position")

    for ax in axs.flat:
        ax.set_xlabel("Time (s)")
        ax.grid(True)

    axs[0, 0].legend(
        title=f"{req.sweep_type.capitalize()} Sweep"
    )

    img_b64 = fig_to_base64(fig)
    return {"plot_base64": img_b64}
