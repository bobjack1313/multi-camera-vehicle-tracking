// document.addEventListener("DOMContentLoaded", () => {
//   loadStreams();
// });

// async function loadStreams() {
//   try {
//     const res = await fetch("/api/streams");
//     const streams = await res.json();
//     console.log("Streams:", streams);
//     const container = document.getElementById("stream-grid");
//     container.innerHTML = "";

//     const active = streams.filter(s => s.port); // Only show streams with a valid port

//     if (active.length === 0) {
//       container.innerHTML = "<p>No active streams.</p>";
//       return;
//     }

//     active.forEach(stream => {
//       const box = document.createElement("div");
//       box.className = "stream-box";

//       box.innerHTML = `
//         <h4>${stream.camera_id}</h4>
//         <img src="/video_feed/yolo/${stream.id}" width="100%" />
//         <p>Model: ${stream.model.split('/').pop()}</p>
//       `;

//       container.appendChild(box);
//     });
//   } catch (err) {
//     console.error("Error loading streams:", err);
//   }
// }





document.addEventListener("DOMContentLoaded", () => {
  loadStreams();
  loadActiveStreamsDropdown();

  const feedType = document.getElementById("feed_type");
  if (feedType) {
    feedType.addEventListener("change", toggleFeedInput);
    toggleFeedInput();
  }

  const stopForm = document.getElementById("stop-stream-form");
  if (stopForm) {
    stopForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const selected = document.getElementById("stop_camera_id").value;
      if (!selected) {
        showToast("Please select a stream to stop.");
        return;
      }
      try {
        const res = await fetch(`/stop_stream/${selected}`, { method: "POST" });
        if (res.redirected) {
          window.location.href = res.url;
          return;
        }

        const msg = await res.text();
        showToast(msg);
        loadStreams(); // Refresh stream grid
        loadActiveStreamsDropdown(); // Refresh dropdown
      } catch (err) {
        console.error("Failed to stop stream:", err);
        showToast("An error occurred while trying to stop the stream.");
      }
    });
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

// async function loadStreams() {
//   try {
//     const res = await fetch("/api/streams");
//     const streams = await res.json();
//     console.log("Streams:", streams);
//     const container = document.getElementById("stream-grid");
//     container.innerHTML = "";

//     const active = streams.filter(s => s.port);

//     if (active.length === 0) {
//       container.innerHTML = "<p>No active streams.</p>";
//       return;
//     }
//     console.log("Stream UUIDs:", streams.map(s => s.id));
//     active.forEach(stream => {
//       const box = document.createElement("div");
//       box.className = "stream-box";

//       const imgId = `img-${stream.id}`;

//       box.innerHTML = `
//         <h4>${stream.camera_id}</h4>
//         <img id="${imgId}" width="100%" />
//         <p>Model: ${stream.model.split('/').pop()}</p>
//       `;
//       container.appendChild(box);

//       // Retry loading image up to 5 times with 1s delay
//       let attempts = 0;
//       const maxAttempts = 5;
//       const loadImage = () => {
//         const img = document.getElementById(imgId);
//         if (!img) return;

//         const streamId = `${stream.camera_id}|${stream.id}`;
//         // img.src = `/internal_proxy/${stream.port}/video?t=${Date.now()}`;
//         img.src = `/stream/${stream.flask_port}/video?t=${Date.now()}`;

//         // img.src = `${location.protocol}//${location.hostname}:${stream.flask_port}/video?t=${Date.now()}`;

//         img.onerror = () => {
//           attempts++;
//           if (attempts < maxAttempts) {
//             console.warn(`[Retry] Reloading image for stream ${streamId} (Attempt ${attempts})`);
//             setTimeout(loadImage, 5000);
//           } else {
//             img.alt = "Failed to load stream.";
//             img.style.opacity = 0.5;
//           }
//         };
//       };

//       // Delay first load to avoid race with session update
//       setTimeout(loadImage, 4000);
//     });
//   } catch (err) {
//     console.error("Error loading streams:", err);
//   }
// }

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

async function loadActiveStreamsDropdown() {
  try {
    const res = await fetch("/api/streams");
    const streams = await res.json();
    const select = document.getElementById("stop_camera_id");
    if (!select) return;

    select.innerHTML = '<option value="">-- Select Stream --</option>';
    streams
      .filter(s => s.port)
      .forEach(stream => {
        const opt = document.createElement("option");
        opt.value = stream.camera_id;

        // opt.value = `${stream.camera_id}|${stream.id}`;
        opt.textContent = `${stream.camera_id}`;
        select.appendChild(opt);
      });
  } catch (err) {
    console.error("Failed to load active streams:", err);
  }
}


// Toast utility
function showToast(message, duration = 4000) {
  let toast = document.createElement("div");
  toast.textContent = message;
  toast.style.position = "fixed";
  toast.style.bottom = "20px";
  toast.style.left = "50%";
  toast.style.transform = "translateX(-50%)";
  toast.style.background = "#333";
  toast.style.color = "#fff";
  toast.style.padding = "0.75rem 1.25rem";
  toast.style.borderRadius = "8px";
  toast.style.boxShadow = "0 2px 8px rgba(0,0,0,0.3)";
  toast.style.zIndex = "10000";
  toast.style.opacity = "0";
  toast.style.transition = "opacity 0.4s ease-in-out";

  document.body.appendChild(toast);

  setTimeout(() => (toast.style.opacity = "1"), 50);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 400);
  }, duration);
}



//  document.addEventListener("DOMContentLoaded", () => {
//    loadStreams();
// +  loadActiveStreamsDropdown();
// +
//    const feedType = document.getElementById("feed_type");
//    if (feedType) {
//      feedType.addEventListener("change", toggleFeedInput);
//      toggleFeedInput();
//    }
// +
// +  const stopForm = document.getElementById("stop-stream-form");
// +  if (stopForm) {
// +    stopForm.addEventListener("submit", async (e) => {
// +      e.preventDefault();
// +      const selected = document.getElementById("stop_camera_id").value;
// +      if (!selected) {
// +        showToast("Please select a stream to stop.");
// +        return;
// +      }
// +      try {
// +        const res = await fetch(`/stop_stream/${selected}`, { method: "POST" });
// +        if (res.redirected) {
// +          window.location.href = res.url;
// +          return;
// +        }
// +
// +        const msg = await res.text();
// +        showToast(msg);
// +        loadStreams(); // Refresh stream grid
// +        loadActiveStreamsDropdown(); // Refresh dropdown
// +      } catch (err) {
// +        console.error("Failed to stop stream:", err);
// +        showToast("An error occurred while trying to stop the stream.");
// +      }
// +    });
// +  }
//  });

//  async function loadStreams() {
// @@ -15,7 +44,7 @@ async function loadStreams() {
//      const container = document.getElementById("stream-grid");
//      container.innerHTML = "";

// -    const active = streams.filter(s => s.port); // Only show streams with a valid port
// +    const active = streams.filter(s => s.port);

//      if (active.length === 0) {
//        container.innerHTML = "<p>No active streams.</p>";
// @@ -26,20 +55,42 @@ async function loadStreams() {
//        const box = document.createElement("div");
//       box.className = "stream-box";

// +      const imgId = `img-${stream.id}`;
//        box.innerHTML = `
//          <h4>${stream.camera_id}</h4>
// -        <img src="/video_feed/yolo/${stream.id}" width="100%" />
// +        <img id="${imgId}" width="100%" />
//          <p>Model: ${stream.model.split('/').pop()}</p>
//        `;
// -
//        container.appendChild(box);
// +
// +      // Retry loading image up to 5 times with 1s delay
// +      let attempts = 0;
// +      const maxAttempts = 5;
// +      const loadImage = () => {
// +        const img = document.getElementById(imgId);
// +        if (!img) return;
// +
// +        img.src = `/video_feed/yolo/${stream.id}?t=${Date.now()}`;
// +        img.onerror = () => {
// +          attempts++;
// +          if (attempts < maxAttempts) {
// +            console.warn(`[Retry] Reloading image for stream ${stream.id} (Attempt ${attempts})`);
// +            setTimeout(loadImage, 1000);
// +          } else {
// +            img.alt = "Failed to load stream.";
// +            img.style.opacity = 0.5;
// +          }
// +        };
// +      };
// +
// +      // Delay first load to avoid race with session update
// +      setTimeout(loadImage, 400);
//      });
//    } catch (err) {
//      console.error("Error loading streams:", err);
//    }
//  }

// -
//  function updateFilename(input) {
//    const fileLabel = document.getElementById("filename");
//    if (input.files.length > 0) {
// @@ -59,8 +110,49 @@ function toggleFeedInput() {
//    rtspInput.style.display = type === "rtsp" ? "block" : "none";
//  }

// -// function toggleFeedInput() {
// -//   const type = document.getElementById("feed_type").value;
// -//   document.getElementById("video_input").style.display = (type === "video") ? "block" : "none";
// -//   document.getElementById("rtsp_input").style.display = (type === "rtsp") ? "block" : "none";
// -// }
// +async function loadActiveStreamsDropdown() {
// +  try {
// +    const res = await fetch("/api/streams");
// +    const streams = await res.json();
// +    const select = document.getElementById("stop_camera_id");
// +    if (!select) return;
// +
// +    select.innerHTML = '<option value="">-- Select Stream --</option>';
// +    streams
// +      .filter(s => s.port)
// +      .forEach(stream => {
// +        const opt = document.createElement("option");
// +        opt.value = stream.camera_id;
// +        opt.textContent = stream.camera_id;
// +        select.appendChild(opt);
// +      });
// +  } catch (err) {
// +    console.error("Failed to load active streams:", err);
// +  }
// +}
// +
// +// Toast utility
// +function showToast(message, duration = 4000) {
// +  let toast = document.createElement("div");
// +  toast.textContent = message;
// +  toast.style.position = "fixed";
// +  toast.style.bottom = "20px";
// +  toast.style.left = "50%";
// +  toast.style.transform = "translateX(-50%)";
// +  toast.style.background = "#333";
// +  toast.style.color = "#fff";
// +  toast.style.padding = "0.75rem 1.25rem";
// +  toast.style.borderRadius = "8px";
// +  toast.style.boxShadow = "0 2px 8px rgba(0,0,0,0.3)";
// +  toast.style.zIndex = "10000";
// +  toast.style.opacity = "0";
// +  toast.style.transition = "opacity 0.4s ease-in-out";
// +
// +  document.body.appendChild(toast);
// +
// +  setTimeout(() => (toast.style.opacity = "1"), 50);
// +  setTimeout(() => {
// +    toast.style.opacity = "0";
// +    setTimeout(() => toast.remove(), 400);
// +  }, duration);
// +}
