document.addEventListener("DOMContentLoaded", () => {
  loadStreams();
});

async function loadStreams() {
  try {
    const res = await fetch("/api/streams");
    const streams = await res.json();

    const container = document.getElementById("stream-grid");
    container.innerHTML = "";

    streams.forEach(stream => {
      const box = document.createElement("div");
      box.className = "stream-box";
      box.innerHTML = `
        <h4>${stream.camera_id}</h4>
        <img src="/video_feed/${stream.feed_type}/${stream.id}" width="100%" />
      `;
      container.appendChild(box);
    });
  } catch (err) {
    console.error("Error loading streams:", err);
  }
}

function addCamera() {
  alert("Add Camera Modal Coming Soon...");
}
