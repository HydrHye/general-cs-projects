const form = document.getElementById("tts-form");
const submitBtn = document.getElementById("submit-btn");
const statusEl = document.getElementById("status");
const speedInput = document.getElementById("speed");
const speedVal = document.getElementById("speed-val");
const resultSection = document.getElementById("result");
const player = document.getElementById("player");
const downloadLink = document.getElementById("download");

speedInput.addEventListener("input", () => {
  speedVal.textContent = Number(speedInput.value).toFixed(2);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusEl.textContent = "Generating speech...";
  submitBtn.disabled = true;

  const formData = new FormData(form);

  try {
    const res = await fetch("/api/read", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(err.detail || "Failed to generate audio");
    }

    const blob = await res.blob();
    const audioUrl = URL.createObjectURL(blob);
    player.src = audioUrl;
    resultSection.classList.remove("hidden");

    const format = formData.get("response_format") || "mp3";
    downloadLink.href = audioUrl;
    downloadLink.download = `speech.${format}`;

    statusEl.textContent = "Done! Press play or download your file.";
  } catch (error) {
    statusEl.textContent = `Error: ${error.message}`;
  } finally {
    submitBtn.disabled = false;
  }
});
