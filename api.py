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

# Set backend AFTER imports to avoid flake8 E402
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
    sweep_type: str          # "pitch" or "frequency"
    base: float              # base value (deg for pitch, Hz for freq)
    freq_hz: float
    pitch_deg: float
    step: float
    stroke_amp: float
    t_end: float


# ------------------------- Helper -------------------------

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
    return FileResponse("static/index.html")


@app.post("/simulate_plot")
def simulate_plot(req: SimRequest):
    params = base_params.copy()
    params["f"] = req.f
    params["stroke_amp"] = req.stroke_amp
    params["pitch_amp"] = req.pitch_amp
    params["t_end"] = req.t_end

    result = quasi_steady_flap(params)

    fig, axs = plt.subplots(3, 2, figsize=(10, 10), dpi=90)

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

    fig, axs = plt.subplots(3, 2, figsize=(10, 10), dpi=90)
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

        r = quasi_steady_flap(params)

        axs[0, 0].plot(r["t"], r["L"], color=colors[idx], label=f"{val}")
        axs[0, 1].plot(r["t"], r["D"], color=colors[idx])
        axs[1, 0].plot(r["t"], r["P"], color=colors[idx])
        axs[1, 1].plot(r["t"], r["eta"], color=colors[idx])
        axs[2, 0].plot(r["t"], r["theta_deg"], color=colors[idx])
        axs[2, 1].plot(r["t"], r["x_pos"], color=colors[idx])

    axs[0, 0].set_title("Lift")
    axs[0, 1].set_title("Drag")
    axs[1, 0].set_title("Power")
    axs[1, 1].set_title("Efficiency")
    axs[2, 0].set_title("Pitch Angle")
    axs[2, 1].set_title("Stroke Position")

    for ax in axs.flat:
        ax.set_xlabel("Time (s)")
        ax.grid(True)

    axs[0, 0].legend(title=f"{req.sweep_type.capitalize()} Sweep")

    return {"plot_base64": fig_to_base64(fig)}
