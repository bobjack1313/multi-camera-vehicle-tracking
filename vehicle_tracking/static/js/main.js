document.addEventListener("DOMContentLoaded", () => {
  loadStreams();
});

async function loadStreams() {
  try {
    const res = await fetch("/api/streams");
    const streams = await res.json();
    console.log("Streams:", streams);
    const container = document.getElementById("stream-grid");
    container.innerHTML = "";

    const active = streams.filter(s => s.port); // Only show streams with a valid port

    if (active.length === 0) {
      container.innerHTML = "<p>No active streams.</p>";
      return;
    }

    active.forEach(stream => {
      const box = document.createElement("div");
      box.className = "stream-box";

      box.innerHTML = `
        <h4>${stream.camera_id}</h4>
        <img src="/video_feed/yolo/${stream.id}" width="100%" />
        <p>Model: ${stream.model.split('/').pop()}</p>
      `;

      container.appendChild(box);
    });
  } catch (err) {
    console.error("Error loading streams:", err);
  }
}
