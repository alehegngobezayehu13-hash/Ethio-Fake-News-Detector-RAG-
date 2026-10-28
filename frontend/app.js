
const form = document.getElementById("check-form");
const claimInput = document.getElementById("claim");
const submitBtn = document.getElementById("submit");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const verdictEl = document.getElementById("verdict");
const verdictLabel = document.getElementById("verdict-label");
const verdictExplanation = document.getElementById("verdict-explanation");
const evidenceList = document.getElementById("evidence");
const languageSelect = document.getElementById("language-select");
const clearBtn = document.getElementById("clear-claim");
const characterCount = document.getElementById("character-count");

const LANGUAGE_NAMES = {
  en: "English",
  am: "አማርኛ",
  om: "Afaan Oromo",
  ti: "ትግርኛ",
};

const TRANSLATIONS = {
  en: {
    language: "Language",
    eyebrow: "ETHIOPIA · FACT CHECKING",
    headline: "Before you believe it, check it.",
    intro: "Have a news claim you're unsure about? Check it against retrieved evidence and explore the original sources.",
    stepLabel: "YOUR CLAIM",
    formHeading: "What would you like to check?",
    fourLanguages: "4 languages supported",
    claimLabel: "News claim or statement",
    claimPlaceholder: "Paste a news claim here...",
    clear: "Clear",
    tryExample: "Try an example:",
    checkButton: "Check this claim",
    resultsLabel: "THE FINDINGS",
    resultsHeading: "What the evidence says",
    verdictLabel: "VERDICT",
    evidenceLabel: "CHECK THE SOURCES",
    evidenceHeading: "Evidence and original sources",
    howLabel: "OUR APPROACH",
    howHeading: "Look at the evidence, not just the headline.",
    stepOneTitle: "Submit a claim",
    stepOneText: "Enter a news statement in any of the four supported languages.",
    stepTwoTitle: "Find relevant evidence",
    stepTwoText: "The system searches its available collection for relevant material.",
    stepThreeTitle: "Review the sources",
    stepThreeText: "Read the result and visit the original sources to assess the evidence.",
    disclaimer: "Automated results can be wrong. Review the evidence and original sources before drawing a conclusion.",
    footerText: "Built to encourage informed decisions through evidence.",
    supported: "Supported by the evidence",
    contradicted: "Contradicted by the evidence",
    not_enough_evidence: "Not enough evidence",
    checking: "Checking the claim. This can take a little while.",
    loadingButton: "Checking...",
    emptyClaim: "Please enter a claim to check.",
    requestError: "Could not check the claim. Please try again.",
    connectionError: "Could not reach the server. Check that it is running and try again.",
    invalidClaim: "Enter a claim of 3 to 1000 characters.",
    noEvidence: "No evidence was returned for this claim.",
    source: "Source",
    article: "Read original article",
    sourceUnavailable: "Source link unavailable",
    languageUnknown: "Unknown language",
  },

  am: {
    language: "ቋንቋ",
    eyebrow: "ኢትዮጵያ · የዜና እውነታ ማረጋገጫ",
    headline: "ከማመንዎ በፊት ያረጋግጡ።",
    intro: "እውነትነቱን ያልተረጋገጡት የዜና መረጃ አለ? በተገኙ ማስረጃዎች ያረጋግጡና ዋና ምንጮቹን ይመልከቱ።",
    stepLabel: "የእርስዎ ጥያቄ",
    formHeading: "ምን ማረጋገጥ ይፈልጋሉ?",
    fourLanguages: "4 ቋንቋዎች ይደገፋሉ",
    claimLabel: "የዜና መረጃ ወይም አረፍተ ነገር",
    claimPlaceholder: "የዜና መረጃውን እዚህ ያስገቡ...",
    clear: "አጽዳ",
    tryExample: "ምሳሌ ይሞክሩ፦",
    checkButton: "መረጃውን አረጋግጥ",
    resultsLabel: "ውጤቶቹ",
    resultsHeading: "ማስረጃው ምን ይላል?",
    verdictLabel: "ውሳኔ",
    evidenceLabel: "ምንጮቹን ይመልከቱ",
    evidenceHeading: "ማስረጃዎችና ዋና ምንጮች",
    howLabel: "አሰራራችን",
    howHeading: "የዜናውን ርዕስ ብቻ ሳይሆን ማስረጃውንም ይመልከቱ።",
    stepOneTitle: "መረጃ ያስገቡ",
    stepOneText: "ከሚደገፉት አራት ቋንቋዎች በአንዱ የዜና መረጃ ያስገቡ።",
    stepTwoTitle: "ተዛማጅ ማስረጃ ፈልግ",
    stepTwoText: "ስርዓቱ በሚገኙት መረጃዎች ውስጥ ተዛማጅ ማስረጃዎችን ይፈልጋል።",
    stepThreeTitle: "ምንጮቹን ይመርምሩ",
    stepThreeText: "ውጤቱን ያንብቡና ማስረጃዎቹን ለመገምገም ዋና ምንጮቹን ይጎብኙ።",
    disclaimer: "ራስ-ሰር ውጤቶች ስህተት ሊኖራቸው ይችላል። ውሳኔ ከመስጠትዎ በፊት ማስረጃዎቹንና ዋና ምንጮቹን ይመርምሩ።",
    footerText: "በማስረጃ የተደገፈ ውሳኔ እንዲወስኑ የተዘጋጀ።",
    supported: "በማስረጃው የተደገፈ",
    contradicted: "ከማስረጃው ጋር የሚቃረን",
    not_enough_evidence: "በቂ ማስረጃ የለም",
    checking: "መረጃው እየተመረመረ ነው። ትንሽ ሊወስድ ይችላል።",
    loadingButton: "በማረጋገጥ ላይ...",
    emptyClaim: "እባክዎ ለማረጋገጥ መረጃ ያስገቡ።",
    requestError: "መረጃውን ማረጋገጥ አልተቻለም። እንደገና ይሞክሩ።",
    connectionError: "ከሰርቨሩ ጋር መገናኘት አልተቻለም። ሰርቨሩ መስራቱን ያረጋግጡ።",
    invalidClaim: "ከ3 እስከ 1000 ቁምፊዎች ያሉት መረጃ ያስገቡ።",
    noEvidence: "ለዚህ መረጃ ማስረጃ አልተገኘም።",
    source: "ምንጭ",
    article: "ዋናውን ጽሑፍ ያንብቡ",
    sourceUnavailable: "የምንጭ አገናኝ የለም",
    languageUnknown: "ያልታወቀ ቋንቋ",
  },

  om: {
    language: "Afaan",
    eyebrow: "ITOOPHIYAA · DHUGAA MIIDHAA ODUU",
    headline: "Oduu sana amanuu kee dura mirkaneessi.",
    intro: "Oduu dhugaa ta'uu isaa shakkitu qabdaa? Ragaa argame waliin ilaali, madda jalqabaa irrattis qoradhu.",
    stepLabel: "ODEEFFANNOO KEE",
    formHeading: "Maal mirkaneessuu barbaadda?",
    fourLanguages: "Afaanota 4 ni deeggarra",
    claimLabel: "Oduu ykn himannaa",
    claimPlaceholder: "Oduu asitti maxxansi...",
    clear: "Haqi",
    tryExample: "Fakkeenya yaali:",
    checkButton: "Oduu kana mirkaneessi",
    resultsLabel: "BU'AA",
    resultsHeading: "Ragaan maal jedha?",
    verdictLabel: "MURTII",
    evidenceLabel: "MADDA QORADHU",
    evidenceHeading: "Ragaa fi maddoota jalqabaa",
    howLabel: "AKKAATAA HOJII KEENYAA",
    howHeading: "Mata-duree qofa osoo hin taane ragaa ilaali.",
    stepOneTitle: "Oduu galchi",
    stepOneText: "Afaanota deeggaraman afran keessaa tokkoon oduu galchi.",
    stepTwoTitle: "Ragaa barbaadi",
    stepTwoText: "Sirnichi odeeffannoo jiru keessaa ragaa walqabatu barbaada.",
    stepThreeTitle: "Maddoota qoradhu",
    stepThreeText: "Bu'aa dubbisi; ragaa madaaluuf maddoota jalqabaa daawwadhu.",
    disclaimer: "Bu'aan ofumaan argamu dogoggora qabaachuu danda'a. Murtii kennuu dura ragaa fi maddoota jalqabaa qoradhu.",
    footerText: "Ragaa irratti hundaa'uun murtii sirrii akka kennamu gargaaruuf kan hojjetame.",
    supported: "Ragaan ni deeggara",
    contradicted: "Ragaan ni faallessa",
    not_enough_evidence: "Ragaan gahaan hin jiru",
    checking: "Oduun qorachaa jirra. Yeroo muraasa fudhachuu danda'a.",
    loadingButton: "Qorachaa jira...",
    emptyClaim: "Maaloo oduu mirkaneessuu barbaaddu galchi.",
    requestError: "Oduu mirkaneessuun hin danda'amne. Irra deebi'ii yaali.",
    connectionError: "Sarvariin hin argamne. Hojjechaa jiraachuu isaa mirkaneessi.",
    invalidClaim: "Dheerinni oduu qubee 3 hanga 1000 ta'uu qaba.",
    noEvidence: "Oduu kanaaf ragaan hin argamne.",
    source: "Madda",
    article: "Barruu jalqabaa dubbisi",
    sourceUnavailable: "Geessituun madda hin jiru",
    languageUnknown: "Afaan hin beekamne",
  },

  ti: {
    language: "ቋንቋ",
    eyebrow: "ኢትዮጵያ · ምርግጋጽ ሓቂ ዜና",
    headline: "ቅድሚ ምእማንካ ኣረጋግጽ።",
    intro: "እቲ ዜና ሓቂ ምዃኑ ትጠራጠር ዲኻ? ምስ ዝተረኽበ መርትዖ ኣነጻጽሮ፣ እቶም መበቆላዊ ምንጭታት እውን ተመልከት።",
    stepLabel: "ናትካ ሓበሬታ",
    formHeading: "እንታይ ከተረጋግጽ ትደሊ?",
    fourLanguages: "4 ቋንቋታት ይድገፉ",
    claimLabel: "ዜና ወይ ሓበሬታ",
    claimPlaceholder: "እቲ ዜና ኣብዚ ኣእቱ...",
    clear: "ኣጽርይ",
    tryExample: "ኣብነት ፈትን፦",
    checkButton: "ነዚ ዜና ኣረጋግጽ",
    resultsLabel: "ውጽኢት",
    resultsHeading: "እቲ መርትዖ እንታይ ይብል?",
    verdictLabel: "ውሳነ",
    evidenceLabel: "ምንጭታት መርምር",
    evidenceHeading: "መርትዖን መበቆላዊ ምንጭታትን",
    howLabel: "ኣገባብ ስራሕና",
    howHeading: "ነቲ ኣርእስቲ ጥራይ ዘይኮነስ ነቲ መርትዖ እውን ተመልከት።",
    stepOneTitle: "ሓበሬታ ኣእቱ",
    stepOneText: "ብሓደ ካብቶም ኣርባዕተ ዝድገፉ ቋንቋታት ዜና ኣእቱ።",
    stepTwoTitle: "ተዛማዲ መርትዖ ርኸብ",
    stepTwoText: "እቲ ስርዓት ኣብ ዘለዎ ሓበሬታ ተዛማዲ መርትዖ ይደሊ።",
    stepThreeTitle: "ምንጭታት መርምር",
    stepThreeText: "ነቲ ውጽኢት ኣንብብ፣ ነቲ መርትዖ ንምግምጋም ከኣ ናብ መበቆላዊ ምንጭታት ኪድ።",
    disclaimer: "ብኣውቶማቲክ ዝርከብ ውጽኢት ጌጋ ክኸውን ይኽእል። ውሳነ ቅድሚ ምሃብካ መርትዖን መበቆላዊ ምንጭታትን መርምር።",
    footerText: "ብመርትዖ ዝተደገፈ ውሳነ ንምውሳን ንምሕጋዝ ዝተዳለወ።",
    supported: "ብመርትዖ ዝተደገፈ",
    contradicted: "ምስ መርትዖ ዝጋጮ",
    not_enough_evidence: "እኹል መርትዖ የለን",
    checking: "እቲ ዜና ይምርመር ኣሎ። ቁሩብ ግዜ ክወስድ ይኽእል።",
    loadingButton: "ይምርመር ኣሎ...",
    emptyClaim: "በጃኻ ከተረጋግጾ እትደሊ ዜና ኣእቱ።",
    requestError: "ነቲ ዜና ምርግጋጽ ኣይተኻእለን። እንደገና ፈትን።",
    connectionError: "ምስ ሰርቨር ምትእስሳር ኣይተኻእለን። ሰርቨሩ ይሰርሕ ከም ዘሎ ኣረጋግጽ።",
    invalidClaim: "ካብ 3 ክሳብ 1000 ቁምፊታት ዘለዎ ሓበሬታ ኣእቱ።",
    noEvidence: "ንዚ ዜና ዝኸውን መርትዖ ኣይተረኽበን።",
    source: "ምንጪ",
    article: "መበቆላዊ ጽሑፍ ኣንብብ",
    sourceUnavailable: "መላግቦ ምንጪ የለን",
    languageUnknown: "ዘይተፈልጠ ቋንቋ",
  },
};

let currentLanguage = "en";
let isChecking = false;

function t(key) {
  return TRANSLATIONS[currentLanguage]?.[key]
    ?? TRANSLATIONS.en[key]
    ?? key;
}

function applyLanguage(language) {
  currentLanguage = TRANSLATIONS[language] ? language : "en";

  document.documentElement.lang = currentLanguage;
  languageSelect.value = currentLanguage;

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (t(key)) element.textContent = t(key);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });

  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute(
      "aria-label",
      t(element.dataset.i18nAriaLabel)
    );
  });

  updateCharacterCount();

  if (!isChecking && !statusEl.classList.contains("error")) {
    statusEl.textContent = "";
  }

  if (!resultEl.hidden) {
    verdictLabel.textContent = t(verdictEl.dataset.verdict || "");
    verdictExplanation.textContent =
      verdictEl.dataset.explanation || "";

    if (verdictEl.dataset.explanationKey) {
      verdictExplanation.textContent = t(
        verdictEl.dataset.explanationKey
      );
    }

    const evidenceHeading = document.querySelector(
      ".evidence-heading h2"
    );
    if (evidenceHeading) {
      evidenceHeading.textContent = t("evidenceHeading");
    }
  }
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function updateCharacterCount() {
  characterCount.textContent = `${claimInput.value.length} / 1000`;
}

function safeHttpUrl(value) {
  try {
    const url = new URL(value);
    if (url.protocol === "https:" || url.protocol === "http:") {
      return url.href;
    }
  } catch {
    
  }
  return null;
}

function renderResult(data) {
  const verdict = TRANSLATIONS.en[data.verdict]
    ? data.verdict
    : "not_enough_evidence";

  verdictEl.className = `verdict ${verdict}`;
  verdictEl.dataset.verdict = verdict;
  verdictLabel.textContent = t(verdict);

  const explanation = data.explanation || "";
  verdictEl.dataset.explanation = explanation;
  delete verdictEl.dataset.explanationKey;
  verdictExplanation.textContent = explanation;

  evidenceList.replaceChildren();

  const evidence = Array.isArray(data.evidence) ? data.evidence : [];

  if (evidence.length === 0) {
    const emptyItem = document.createElement("li");
    emptyItem.className = "evidence-empty";
    emptyItem.textContent = t("noEvidence");
    evidenceList.append(emptyItem);
  }

  for (const item of evidence) {
    const li = document.createElement("li");
    li.className = "evidence-card";

    const heading = document.createElement("div");
    heading.className = "evidence-card-heading";

    const sourceName = document.createElement("span");
    sourceName.className = "source-name";
    sourceName.textContent = item.source || t("source");
    heading.append(sourceName);

    const language = document.createElement("span");
    language.className = "source-language";
    language.textContent =
      LANGUAGE_NAMES[item.language] || t("languageUnknown");
    heading.append(language);

    li.append(heading);

    const title = document.createElement("h3");
    title.className = "evidence-title";

    const safeUrl = safeHttpUrl(item.url);

    if (safeUrl) {
      const link = document.createElement("a");
      link.href = safeUrl;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = item.title || t("article");
      title.append(link);
    } else {
      title.textContent = item.title || t("sourceUnavailable");
    }

    li.append(title);

    const text = document.createElement("p");
    text.className = "text";
    text.textContent = item.text || "";
    li.append(text);

    if (safeUrl) {
      const sourceLink = document.createElement("a");
      sourceLink.className = "source-link";
      sourceLink.href = safeUrl;
      sourceLink.target = "_blank";
      sourceLink.rel = "noopener noreferrer";
      sourceLink.textContent = t("article");
      sourceLink.setAttribute("aria-label", `${t("article")}: ${item.source || ""}`);
      li.append(sourceLink);
    }

    evidenceList.append(li);
  }

  resultEl.hidden = false;
}

async function checkClaim(claim) {
  if (isChecking) return;

  isChecking = true;
  submitBtn.disabled = true;
  submitBtn.querySelector("[data-i18n]").textContent = t("loadingButton");
  resultEl.hidden = true;
  setStatus(t("checking"));

  try {
    const response = await fetch("/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ claim }),
    });

    let data;

    try {
      data = await response.json();
    } catch {
      throw new Error(t("requestError"));
    }

    if (!response.ok) {
      const detail = typeof data.detail === "string"
        ? data.detail
        : t("invalidClaim");
      throw new Error(detail);
    }

    setStatus("");
    renderResult(data);
  } catch (error) {
    setStatus(
      error.message || t("connectionError"),
      true
    );
  } finally {
    isChecking = false;
    submitBtn.disabled = false;
    submitBtn.querySelector("[data-i18n]").textContent = t("checkButton");
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const claim = claimInput.value.trim();

  if (!claim) {
    setStatus(t("emptyClaim"), true);
    claimInput.focus();
    return;
  }

  checkClaim(claim);
});

claimInput.addEventListener("input", updateCharacterCount);

claimInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    form.requestSubmit();
  }
});

document.querySelectorAll("[data-claim]").forEach((button) => {
  button.addEventListener("click", () => {
    claimInput.value = button.dataset.claim;
    updateCharacterCount();
    claimInput.focus();
  });
});

clearBtn.addEventListener("click", () => {
  claimInput.value = "";
  updateCharacterCount();
  setStatus("");
  claimInput.focus();
});

languageSelect.addEventListener("change", () => {
  const language = languageSelect.value;
  applyLanguage(language);

  try {
    localStorage.setItem("ethiofact-language", language);
  } catch {

  }
});

let savedLanguage = "en";

try {
  savedLanguage = localStorage.getItem("ethiofact-language") || "en";
} catch {

}

applyLanguage(savedLanguage);
updateCharacterCount();
