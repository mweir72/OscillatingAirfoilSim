document.addEventListener("DOMContentLoaded", () => {
    console.log("BumbleBeeSim script loaded (DOM ready)");

    function getInputs() {
        const f = parseFloat(document.getElementById("freq").value);
        const pitch = parseFloat(document.getElementById("pitch").value);
        const step = parseFloat(document.getElementById("step").value);
        const t_end = parseFloat(document.getElementById("tend").value);

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
        const img = document.getElementById("plot-img");
        if (!img) {
            console.error("plot-img element not found");
            return;
        }
        img.src = "data:image/png;base64," + base64img;
    }

    async function safeFetch(url, bodyObj) {
        try {
            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(bodyObj),
                cache: "no-cache"
            });

            if (!res.ok) {
                console.error(`Fetch to ${url} failed:`, res.status, res.statusText);
                alert(`Server error (${res.status}). Check logs.`);
                return null;
            }

            const data = await res.json();
            if (!data || !data.plot_base64) {
                console.error("Response missing plot_base64:", data);
                alert("Server response invalid. Check logs.");
                return null;
            }

            return data.plot_base64;
        } catch (err) {
            console.error(`Fetch to ${url} threw:`, err);
            alert("Network error when contacting server. Check console/logs.");
            return null;
        }
    }

    //SINGLE SIM
    async function runSingleHandler() {
        console.log("Run single simulation clicked");
        const inp = getInputs();

        const req = {
            f: inp.f,
            pitch_amp: inp.pitch_deg * Math.PI / 180,
            t_end: inp.t_end
        };

        const plot = await safeFetch("/simulate_plot", req);
        if (plot) {
            showPlot(plot);
        }
    }

    // PITCH SWEEP
    async function runPitchSweepHandler() {
        console.log("Run pitch sweep clicked");
        const inp = getInputs();

        const req = {
            sweep_type: "pitch",
            base: inp.pitch_deg,
            freq_hz: inp.f,
            pitch_deg: inp.pitch_deg,
            step: inp.step,
            t_end: inp.t_end
        };

        const plot = await safeFetch("/sweep_steps", req);
        if (plot) {
            showPlot(plot);
        }
    }

    // FREQUENCY SWEEP
    async function runFreqSweepHandler() {
        console.log("Run frequency sweep clicked");
        const inp = getInputs();

        const req = {
            sweep_type: "frequency",
            base: inp.f,
            freq_hz: inp.f,
            pitch_deg: inp.pitch_deg,
            step: inp.step,
            t_end: inp.t_end
        };

        const plot = await safeFetch("/sweep_steps", req);
        if (plot) {
            showPlot(plot);
        }
    }

    // Safari Work Around
    window.runSingle = runSingleHandler;
    window.runPitchSweep = runPitchSweepHandler;
    window.runFreqSweep = runFreqSweepHandler;

    console.log("BumbleBeeSim handlers bound");
});
