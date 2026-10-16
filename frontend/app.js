const form = document.getElementById("check-form");
const claimInput = document.getElementById("claim");
const submitBtn = document.getElementById("submit");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const verdictEl = document.getElementById("verdict");
const verdictLabel = document.getElementById("verdict-label");
const verdictExplanation = document.getElementById("verdict-explanation");
const evidenceList = document.getElementById("evidence");

const VERDICT_LABELS = {
  supported: "Supported by the evidence",
  contradicted: "Contradicted by the evidence",
  not_enough_evidence: "Not enough evidence",
};

const LANGUAGE_NAMES = { en: "English", am: "Amharic", ti: "Tigrinya", om: "Afaan Oromo" };

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function renderResult(data) {
  verdictEl.className = "verdict " + data.verdict;
  verdictLabel.textContent = VERDICT_LABELS[data.verdict] || data.verdict;
  verdictExplanation.textContent = data.explanation;

  evidenceList.replaceChildren();
  for (const item of data.evidence) {
    const li = document.createElement("li");

    if (item.url.startsWith("https://") || item.url.startsWith("http://")) {
      const link = document.createElement("a");
      link.href = item.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.className = "source-link";
      link.textContent = item.title || item.url;
      li.append(link);
    }

    const text = document.createElement("p");
    text.className = "text";
    text.textContent = item.text;

    const meta = document.createElement("p");
    meta.className = "meta";
    const language = LANGUAGE_NAMES[item.language] || item.language;
    meta.textContent = `${item.source}, ${language}`;
    if (data.evidence_ids.includes(item.id)) {
      const used = document.createElement("span");
      used.className = "used";
      used.textContent = " (used in this verdict)";
      meta.append(used);
    }

    li.append(text, meta);
    evidenceList.append(li);
  }
  resultEl.hidden = false;
}

async function checkClaim(claim) {
  submitBtn.disabled = true;
  resultEl.hidden = true;
  setStatus("Checking the claim. This can take a few seconds.");
  try {
    const response = await fetch("/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ claim }),
    });
    const data = await response.json();
    if (!response.ok) {
      const detail = typeof data.detail === "string" ? data.detail : "Enter a claim of 3 to 1000 characters.";
      throw new Error(detail);
    }
    setStatus("");
    renderResult(data);
  } catch (error) {
    setStatus(error.message || "Could not reach the server. Check that it is running and try again.", true);
  } finally {
    submitBtn.disabled = false;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const claim = claimInput.value.trim();
  if (claim) checkClaim(claim);
});

claimInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) form.requestSubmit();
});

document.querySelectorAll("[data-claim]").forEach((button) => {
  button.addEventListener("click", () => {
    claimInput.value = button.dataset.claim;
    claimInput.focus();
  });
});