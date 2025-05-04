document.addEventListener("DOMContentLoaded", () => {
  loadStreams();
  const feedType = document.getElementById("feed_type");
  if (feedType) {
    feedType.addEventListener("change", toggleFeedInput);
    toggleFeedInput();
  }
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


function updateFilename(input) {
  const fileLabel = document.getElementById("filename");
  if (input.files.length > 0) {
    fileLabel.textContent = input.files[0].name;
  } else {
    fileLabel.textContent = "No file chosen";
  }
}

function toggleFeedInput() {
  const type = document.getElementById("feed_type")?.value;
  const videoInput = document.getElementById("video_input");
  const rtspInput = document.getElementById("rtsp_input");
  if (!type || !videoInput || !rtspInput) return;

  videoInput.style.display = type === "video" ? "block" : "none";
  rtspInput.style.display = type === "rtsp" ? "block" : "none";
}

// function toggleFeedInput() {
//   const type = document.getElementById("feed_type").value;
//   document.getElementById("video_input").style.display = (type === "video") ? "block" : "none";
//   document.getElementById("rtsp_input").style.display = (type === "rtsp") ? "block" : "none";
// }
