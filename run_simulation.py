import numpy as np
import matplotlib.pyplot as plt
from physics import quasi_steady_flap

# ============================================================
# ---------------------- CONFIGURATION ------------------------
# ============================================================

# Choose run type:
#   "single"
#   "sweep_freq"
#   "sweep_stroke"
#   "sweep_pitch"
mode = "sweep_freq"

# Baseline parameters (same as MATLAB)
base_params = {
    "rho": 1.225,
    "S": 2e-4,
    "c": 0.004,
    "f": 150,
    "stroke_amp": 0.01,
    "pitch_amp": np.deg2rad(45),
    "pitch_phase": np.deg2rad(180),
    "dt": 1e-4,
    "t_end": 0.03,
    "CL_alpha": 2*np.pi,
    "Uref": 2.0,
    "K_am": 0.05,
    "CD0": 0.1,
    "CD_alpha": 1.5,
}

# Sweep values (only used if mode == "sweep_xxx")
freq_sweep = [50, 100, 150, 200, 250]
stroke_sweep = [0.001, 0.002, 0.003, 0.004, 0.005]
pitch_sweep_deg = [15, 30, 45, 60, 75]
pitch_sweep = np.deg2rad(pitch_sweep_deg)

# ============================================================
# -------------------- RUN SINGLE SIM -------------------------
# ============================================================
def run_single():
    p = base_params.copy()
    res = quasi_steady_flap(p)
    t = res["t"]

    plt.figure(figsize=(8,10))

    plt.subplot(6,1,1); plt.plot(t, res["L"]); plt.title("Lift"); plt.grid()
    plt.subplot(6,1,2); plt.plot(t, res["D"]); plt.title("Drag"); plt.grid()
    plt.subplot(6,1,3); plt.plot(t, res["P"]); plt.title("Power"); plt.grid()
    plt.subplot(6,1,4); plt.plot(t, res["eta"]); plt.title("Efficiency"); plt.grid()
    plt.subplot(6,1,5); plt.plot(t, res["theta_deg"]); plt.title("Pitch (deg)"); plt.grid()
    plt.subplot(6,1,6); plt.plot(t, res["x_pos"]); plt.title("Stroke Pos"); plt.grid()

    plt.tight_layout()
    plt.show()

# ============================================================
# -------------------- GENERIC SWEEP PLOTTER ------------------
# ============================================================
def run_sweep(label, values, param_key):
    plt.figure(figsize=(10,12))

    for v in values:
        p = base_params.copy()
        p[param_key] = v
        r = quasi_steady_flap(p)
        t = r["t"]

        lab = f"{label}={v if label != 'pitch' else np.rad2deg(v):.0f}"

        plt.subplot(3,2,1); plt.plot(t, r["L"], label=lab); plt.title("Lift"); plt.grid()
        plt.subplot(3,2,2); plt.plot(t, r["D"], label=lab); plt.title("Drag"); plt.grid()
        plt.subplot(3,2,3); plt.plot(t, r["P"], label=lab); plt.title("Power"); plt.grid()
        plt.subplot(3,2,4); plt.plot(t, r["eta"], label=lab); plt.title("Efficiency"); plt.grid()
        plt.subplot(3,2,5); plt.plot(t, r["theta_deg"], label=lab); plt.title("Pitch"); plt.grid()
        plt.subplot(3,2,6); plt.plot(t, r["x_pos"], label=lab); plt.title("Stroke Pos"); plt.grid()

    for i in range(1,7):
        plt.subplot(3,2,i); plt.legend()

    plt.tight_layout()
    plt.show()

# ============================================================
# ----------------------- MAIN EXECUTION ----------------------
# ============================================================
if __name__ == "__main__":

    if mode == "single":
        run_single()

    elif mode == "sweep_freq":
        run_sweep("f", freq_sweep, "f")

    elif mode == "sweep_stroke":
        run_sweep("A", stroke_sweep, "stroke_amp")

    elif mode == "sweep_pitch":
        run_sweep("pitch", pitch_sweep, "pitch_amp")

    else:
        raise ValueError(f"Unknown mode: {mode}")
