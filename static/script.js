function getInputs() {
    return {
        f: parseFloat(document.getElementById("freq").value),
        pitch_deg: parseFloat(document.getElementById("pitch").value),
        stroke: parseFloat(document.getElementById("stroke").value),
        step: parseFloat(document.getElementById("step").value),
        t_end: parseFloat(document.getElementById("t_end").value)
    };
}

function showPlot(b64) {
    document.getElementById("plot-img").src =
        "data:image/png;base64," + b64;
}

async function runSingle() {
    const inp = getInputs();

    const req = {
        f: inp.f,
        stroke_amp: inp.stroke,
        pitch_amp: inp.pitch_deg * Math.PI / 180,
        t_end: inp.t_end
    };

    const res = await fetch("/simulate_plot", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(req)
    });

    showPlot((await res.json()).plot_base64);
}

async function runPitchSweep() {
    const inp = getInputs();

    const req = {
        sweep_type: "pitch",
        base: inp.pitch_deg,
        freq_hz: inp.f,
        pitch_deg: inp.pitch_deg,
        step: inp.step,
        stroke_amp: inp.stroke,
        t_end: inp.t_end
    };

    const res = await fetch("/sweep_steps", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(req)
    });

    showPlot((await res.json()).plot_base64);
}

async function runFreqSweep() {
    const inp = getInputs();

    const req = {
        sweep_type: "frequency",
        base: inp.f,
        freq_hz: inp.f,
        pitch_deg: inp.pitch_deg,
        step: inp.step,
        stroke_amp: inp.stroke,
        t_end: inp.t_end
    };

    const res = await fetch("/sweep_steps", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(req)
    });

    showPlot((await res.json()).plot_base64);
}
