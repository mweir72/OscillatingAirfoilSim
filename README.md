# BumbleBeeSim

Interactive environment for assessing quasi-steady aerodynamics of oscillating airfoils inspired by insect wing motion. The FastAPI backend exposes a parameterized solver while the browser client renders multi-panel diagnostics describing aerodynamic loads, power requirements, and energetic efficiency.

**Live demo:** [BumbleBeeSim.onrender.com](https://bumblebeesim.onrender.com)  
**Stack:** FastAPI · NumPy · Matplotlib · Vanilla JS · Render

---

## Key capabilities
- Returns full wingbeat histories for lift, drag, power, and efficiency in a single API call.
- Web interface supports both single-run analyses and structured pitch/frequency sweeps.
- Solver reflects standard quasi-steady formulations (Dickinson, Sane & Dickinson, Hoerner, Theodorsen) for rapid evaluation without resorting to CFD.
- Server-rendered matplotlib panels ensure consistent visualization across deployments.

---

## Quick start
1. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the API + UI**
   ```bash
   uvicorn api:app --reload
   ```
3. Navigate to `http://127.0.0.1:8000/` to access the interface.

> The desktop client (`run_simulation.py`) remains helpful for exploratory sweeps or regression plots outside the web stack.

---

## Repository map
```
.
├── api.py             # FastAPI service + plotting endpoints
├── physics.py         # Quasi-steady aerodynamic model
├── run_simulation.py  # Local driver for sweeps / figures
├── static/            # Front-end HTML, CSS, JS
├── test_simulation.py # Basic regression tests
├── requirements.txt
└── README.md
```

---

## Browser controls
| Input | Description |
| --- | --- |
| Frequency (Hz) | Primary oscillation frequency applied to plunge and pitch motion. |
| Pitch (deg) | Peak pitch amplitude; converted to radians prior to integration. |
| Sweep step | Increment for the ±2 step sweep around the selected base value. |
| Simulation length (s) | Total simulated duration; temporal resolution (`dt`) is set server-side. |

Available actions:
- **Run Single Simulation** – evaluates one parameter set.
- **Run Pitch Sweep** – changed pitch amplitude about the baseline using ±step and ±2·step.
- **Run Frequency Sweep** – changes oscillation frequency in the same fashion.

---

## Physics model
The wing is approximated as a rigid flat plate undergoing sinusoidal plunge (stroke) and sinusoidal pitch with a configurable phase offset (not available in web app). Aerodynamic forces comprise the following terms:

- **Lift**  
  `L = L_trans + L_rot + L_added_mass`
- **Drag**  
  `D = 0.5 * ρ * S * U² * C_D`
- **Power**  
  `P = aerodynamic work from translation, rotation, and added mass`
- **Efficiency**  
  `η = (L · U) / P`

Parameters governing dynamic pressure corrections, rotational lift augmentation, and added-mass response are consistent with quasi-steady insect flight literature (Dickinson et al., Sane & Dickinson, Hoerner, Theodorsen).

---

## Default bumblebee setup

| Parameter | Value |
| --- | --- |
| Air density (ρ) | 1.225 kg/m³ |
| Wing area (S) | 2e-4 m² |
| Chord length (c) | 4 mm |
| Frequency (f) | 150 Hz |
| Stroke amplitude | 0.01 m |
| Pitch amplitude | 45° |
| Phase offset | 180° |
| CL<sub>α</sub> | 2π |
| CD₀ | 0.1 |
| CD<sub>α</sub> | 1.5 |
| Added-mass coefficient | 0.05 |

Modify `run_simulation.base_params` or provide new values to the API to approximate other species or experimental setups.

---

## API surface
| Endpoint | Payload | Notes |
| --- | --- | --- |
| `POST /simulate_plot` | `{ f, pitch_amp (rad), t_end }` | Returns base64 PNG containing six subplots. |
| `POST /sweep_steps` | `{ sweep_type, base, freq_hz, pitch_deg, step, t_end }` | Sweep either pitch or frequency around `base`; delivers multi-series plots. |
| `GET /` | – | Serves the front-end (`static/index.html`). |

`fig_to_base64` handles server-side PNG conversion so the client updates plots by swapping the `<img>` source.

---

## Testing
```
pytest
```
`test_simulation.py` verifies the solver remains finite and that array lengths stay synchronized; augment with regression baselines before major refactors.

---

## License
```
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
