import numpy as np
from physics import quasi_steady_flap
from run_simulation import base_params

def test_sim_runs_without_nan():
    # Use a short simulation for fast CI testing
    p = base_params.copy()
    p["t_end"] = 0.005

    res = quasi_steady_flap(p)

    # Regression checks
    assert not np.isnan(res["L"]).any()
    assert not np.isnan(res["D"]).any()
    assert len(res["t"]) == len(res["L"])
    assert len(res["t"]) == len(res["D"])
    assert (res["eta"] >= 0).all()
