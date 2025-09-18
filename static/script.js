let uploadedPaths = [];
let lastResultPath = null;

// Make the entire upload box clickable
document.getElementById("uploadBox1").addEventListener("click", () => {
  document.getElementById("file1").click();
});

document.getElementById("uploadBox2").addEventListener("click", () => {
  document.getElementById("file2").click();
});

// Handle file input for box 1
document.getElementById("file1").addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    uploadSingleFile(e.target.files[0], 1);
  }
});

// Handle file input for box 2
document.getElementById("file2").addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    uploadSingleFile(e.target.files[0], 2);
  }
});

// Helper to upload a single file
async function uploadSingleFile(file, index) {
  let formData = new FormData();
  formData.append("images", file);
  formData.append("slot", index - 1);  // Backend requires slot 0 and 1

  let res = await fetch("/upload", { method: "POST", body: formData });
  let data = await res.json();

  if (!res.ok || data.error) {
    document.getElementById("uploadError").innerText = data.error || "Upload failed.";
    document.getElementById("uploadError").style.display = "block";
    return;
  }

  document.getElementById("uploadError").style.display = "none";

  let uploadedPath = data.uploaded_path;
  let imgElem = document.getElementById(`img${index}`);
  let placeholder = document.getElementById(`placeholder${index}`);
  let clearBtn = document.querySelector(`#uploadBox${index} .clear-btn`);

  imgElem.src = "/" + uploadedPath + "?t=" + new Date().getTime();
  imgElem.style.display = "block";
  placeholder.style.display = "none";
  clearBtn.style.display = "block";  // show clear button after upload

  document.getElementById(`file${index}`).value = "";
}

// Clear button logic
document.querySelectorAll(".clear-btn").forEach(btn => {
  btn.addEventListener("click", async (e) => {
    e.stopPropagation();
    const slot = parseInt(e.target.getAttribute("data-slot"));
    const imgElem = document.getElementById(`img${slot + 1}`);
    const placeholder = document.getElementById(`placeholder${slot + 1}`);
    const fileInput = document.getElementById(`file${slot + 1}`);
    const clearBtn = e.target;

    imgElem.style.display = "none";
    imgElem.src = "";
    placeholder.style.display = "block";
    fileInput.value = "";
    clearBtn.style.display = "none";  // hide clear button again

    let formData = new FormData();
    formData.append("slot", slot);
    await fetch("/clear_slot", { method: "POST", body: formData });
  });
});

// Generate (parameters + generate in one step)
document.getElementById("generateBtn").onclick = async () => {
  const generateBtn = document.getElementById("generateBtn");

  generateBtn.disabled = true;  // disable button while generating

  document.getElementById("loadingMsg").style.display = "block";
  document.getElementById("resultImg").style.display = "none";
  document.getElementById("paramError").style.display = "none";

  let formData = new FormData(document.getElementById("paramForm"));
  let jsonData = Object.fromEntries(formData.entries());

  let res = await fetch("/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(jsonData)
  });
  let data = await res.json();

  document.getElementById("loadingMsg").style.display = "none";
  generateBtn.disabled = false;  // re-enable after completion

  if (!res.ok || data.error) {
    document.getElementById("paramError").innerText = Array.isArray(data.error)  // check if backend sent an array of errors
      ? data.error.join(", ")                                                    // if yes → join them into a single string
      : data.error || "Generation failed.";                                      // if no → use the string error, or fallback to "Upload failed."
    document.getElementById("paramError").style.display = "block";
    return;
  }

  if (data.result_path) {
    lastResultPath = data.result_path;
    const cacheBustedPath = "/" + data.result_path + "?t=" + new Date().getTime();
    document.getElementById("resultImg").src = cacheBustedPath;
    document.getElementById("resultImg").style.display = "block";
    document.getElementById("resultPlaceholder").style.display = "none";
    document.getElementById("downloadBtn").disabled = false;
  }
};

// Download
document.getElementById("downloadBtn").onclick = () => {
  if (lastResultPath) {
    const link = document.createElement("a");  // download the specific file generated
    link.href = "/" + lastResultPath;
    link.download = "result.png";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};