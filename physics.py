import numpy as np

def quasi_steady_flap(params):
    """
    Python translation of your MATLAB quasi_steady_flap(params) function.
    Returns a dict of time histories for lift, drag, power, efficiency,
    pitch angle, stroke kinematics, etc.
    """

    rho   = params["rho"]
    S     = params["S"]
    c     = params["c"]
    f     = params["f"]

    stroke_amp  = params["stroke_amp"]
    pitch_amp   = params["pitch_amp"]        # radians
    pitch_phase = params["pitch_phase"]      # radians

    AR = (S / c) / c
    CL_alpha = params["CL_alpha"] / (1 + 2 * np.pi / (np.pi * AR))
    Uref     = params["Uref"]

    dt   = params["dt"]
    t_end = params["t_end"]
    t = np.arange(0, t_end + dt, dt)

    omega = 2 * np.pi * f

    K_am     = params["K_am"]
    CD0      = params["CD0"]
    CD_alpha = params["CD_alpha"]

    # -------------------------
    # KINEMATICS
    # -------------------------
    x_pos = stroke_amp * np.sin(omega * t)

    # MATLAB: U = Uref + stroke_amp * c * omega * cos(omega*t)
    U = Uref + stroke_amp * c * omega * np.cos(omega * t)

    alpha = pitch_amp * (np.sin(omega * t + pitch_phase) + 1) / 2
    alpha_dot = omega * pitch_amp * np.cos(omega * t + pitch_phase)
    alpha_ddot = -omega**2 * pitch_amp * np.sin(omega * t + pitch_phase)

    theta_deg = np.rad2deg(alpha)

    # -------------------------
    # LIFT COMPONENTS
    # -------------------------
    CL_trans = CL_alpha * alpha

    k = 0.5
    S_d = 1 + k * np.sin(np.abs(alpha))**2
    CL_trans_LEV = CL_trans * S_d

    k_rot = 0.1
    CL_rot = k_rot * (np.pi/2) * (c / U) * alpha_dot

    CL_total = CL_trans_LEV + CL_rot

    # -------------------------
    # DRAG
    # -------------------------
    CD = CD0 + CD_alpha * alpha**2

    # -------------------------
    # FORCES
    # -------------------------
    q = 0.5 * rho * U**2

    L_trans = q * S * CL_trans_LEV
    L_rot   = q * S * CL_rot
    L_added = K_am * 0.25 * np.pi * rho * c**2 * S * alpha_ddot

    L = L_trans + L_rot + L_added
    D = q * S * CD

    P = D * U
    P[P == 0] = 1e-12   # avoid division by zero in efficiency

    eta = (L * U) / P

    return {
        "t": t,
        "L": L,
        "D": D,
        "P": P,
        "eta": eta,
        "alpha": alpha,
        "theta_deg": theta_deg,
        "x_pos": x_pos,
        "U": U,
        "CL": CL_total,
        "CD": CD
    }
