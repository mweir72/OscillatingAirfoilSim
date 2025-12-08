function getInputs() {
    return {
        f: parseFloat(document.getElementById("freq").value),
        pitch_deg: parseFloat(document.getElementById("pitch").value),
        stroke: parseFloat(document.getElementById("stroke").value),
        step: parseFloat(document.getElementById("step").value)
    };
}

function showPlot(base64img) {
    document.getElementById("plot-img").src = "data:image/png;base64," + base64img;
}

// ------------------- SINGLE SIM -------------------
async function runSingle() {
    const inp = getInputs();

    const req = {
        f: inp.f,
        stroke_amp: inp.stroke,
        pitch_amp: inp.pitch_deg * Math.PI / 180,
        t_end: 0.02
    };

    const res = await fetch("/simulate_plot", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(req)
    });

    const data = await res.json();
    showPlot(data.plot_base64);
}

// ------------------- PITCH SWEEP -------------------
async function runPitchSweep() {
    const inp = getInputs();

    const req = {
        sweep_type: "pitch",
        base: inp.pitch_deg,  // center value of sweep
        freq_hz: inp.f,
        pitch_deg: inp.pitch_deg,
        step: inp.step,
        stroke_amp: inp.stroke,
        t_end: 0.02
    };

    const res = await fetch("/sweep_steps", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(req)
    });

    const data = await res.json();
    showPlot(data.plot_base64);
}

// ------------------- FREQUENCY SWEEP -------------------
async function runFreqSweep() {
    const inp = getInputs();

    const req = {
        sweep_type: "frequency",
        base: inp.f,  // center value of sweep
        freq_hz: inp.f,
        pitch_deg: inp.pitch_deg,
        step: inp.step,
        stroke_amp: inp.stroke,
        t_end: 0.02
    };

    const res = await fetch("/sweep_steps", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(req)
    });

    const data = await res.json();
    showPlot(data.plot_base64);
}
