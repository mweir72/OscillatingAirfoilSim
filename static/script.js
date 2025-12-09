function getInputs() {

    let f = parseFloat(document.getElementById("freq").value);
    let pitch = parseFloat(document.getElementById("pitch").value);
    let step = parseFloat(document.getElementById("step").value);
    let t_end = parseFloat(document.getElementById("tend").value);

    // Render bug fix — ensure no NaN
    if ([f, pitch, step, t_end].some(v => isNaN(v))) {
        alert("Please enter valid numeric values in all fields.");
        throw new Error("Invalid input");
    }

    return {
        f,
        pitch_deg: pitch,
        step,
        t_end
    };
}

function showPlot(base64img) {
    document.getElementById("plot-img").src =
        "data:image/png;base64," + base64img;
}


// ------------------- SINGLE SIM -------------------

async function runSingle() {
    const inp = getInputs();

    const req = {
        f: inp.f,
        pitch_amp: inp.pitch_deg * Math.PI / 180,
        t_end: inp.t_end
    };

    const res = await fetch("/simulate_plot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
        base: inp.pitch_deg,
        freq_hz: inp.f,
        pitch_deg: inp.pitch_deg,
        step: inp.step,
        t_end: inp.t_end
    };

    const res = await fetch("/sweep_steps", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
        base: inp.f,
        freq_hz: inp.f,
        pitch_deg: inp.pitch_deg,
        step: inp.step,
        t_end: inp.t_end
    };

    const res = await fetch("/sweep_steps", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req)
    });

    const data = await res.json();
    showPlot(data.plot_base64);
}
