const columnsSelect = document.getElementById("columns");
const colorTemplateSelect = document.getElementById("colorTemplate");
const latinFontSelect = document.getElementById("latinFont");
const cjkFontSelect = document.getElementById("cjkFont");
const codeFontSelect = document.getElementById("codeFont");
const fontSizeSelect = document.getElementById("fontSize");
const lineHeightSelect = document.getElementById("lineHeight");
const filenameInput = document.getElementById("filename");
const fileInput = document.getElementById("fileInput");
const filePickerButton = document.getElementById("filePickerButton");
const filePickerLabel = document.getElementById("filePickerLabel");
const markdownInput = document.getElementById("markdownInput");
const templateSummary = document.getElementById("templateSummary");
const generateBtn = document.getElementById("generateBtn");
const downloadBtn = document.getElementById("downloadBtn");
const statusText = document.getElementById("statusText");
const previewFrame = document.getElementById("previewFrame");

let templateMeta = null;
let latestBlobUrl = null;
let latestOutputName = "cheatsheet.html";

function normalizeOutputName(value) {
  const trimmed = value.trim();
  if (!trimmed) return "cheatsheet";
  return trimmed.replace(/\.html?$/i, "");
}

function setStatus(text, isError = false) {
  statusText.textContent = text;
  statusText.style.color = isError ? "#b00020" : "";
}

function revokePreviewUrl() {
  if (latestBlobUrl) {
    URL.revokeObjectURL(latestBlobUrl);
    latestBlobUrl = null;
  }
}

function fillSelect(select, entries) {
  select.innerHTML = "";
  entries.forEach((entry) => {
    const option = document.createElement("option");
    option.value = String(entry.value);
    option.textContent = entry.label;
    select.appendChild(option);
  });
}

function renderTemplateSummary() {
  if (!templateMeta) return;
  const color = templateMeta.colors[colorTemplateSelect.value];
  const latin = templateMeta.latinFonts[latinFontSelect.value];
  const cjk = templateMeta.cjkFonts[cjkFontSelect.value];
  const code = templateMeta.codeFonts[codeFontSelect.value];
  const fontSize = templateMeta.fontSizes[fontSizeSelect.value];
  const lineHeight = templateMeta.lineHeights[lineHeightSelect.value];

  templateSummary.textContent =
    `Current: ${columnsSelect.value} columns | Color ${color.label} | Latin ${latin.label} | 中文字体 ${cjk.label} | Code ${code.label} | Size ${fontSize.label} | Line Height ${lineHeight.label}`;
}

async function loadTemplates() {
  const response = await fetch("/api/templates");
  const data = await response.json();
  templateMeta = data;

  fillSelect(columnsSelect, data.columns.values.map((value) => ({ value, label: String(value) })));
  fillSelect(
    colorTemplateSelect,
    Object.entries(data.colors).map(([value, meta]) => ({ value, label: meta.label }))
  );
  fillSelect(
    latinFontSelect,
    Object.entries(data.latinFonts).map(([value, meta]) => ({ value, label: meta.label }))
  );
  fillSelect(
    cjkFontSelect,
    Object.entries(data.cjkFonts).map(([value, meta]) => ({ value, label: meta.label }))
  );
  fillSelect(
    codeFontSelect,
    Object.entries(data.codeFonts).map(([value, meta]) => ({ value, label: meta.label }))
  );
  fillSelect(
    fontSizeSelect,
    Object.entries(data.fontSizes).map(([value, meta]) => ({ value, label: meta.label }))
  );
  fillSelect(
    lineHeightSelect,
    Object.entries(data.lineHeights).map(([value, meta]) => ({ value, label: meta.label }))
  );

  columnsSelect.value = String(data.defaults.columns);
  colorTemplateSelect.value = data.defaults.color;
  latinFontSelect.value = data.defaults.latinFont;
  cjkFontSelect.value = data.defaults.cjkFont;
  codeFontSelect.value = data.defaults.codeFont;
  fontSizeSelect.value = data.defaults.fontSize;
  lineHeightSelect.value = data.defaults.lineHeight;
  renderTemplateSummary();
}

async function loadDefaultMarkdown() {
  const response = await fetch("/api/default-markdown");
  const data = await response.json();
  markdownInput.value = data.markdown || "";
  filenameInput.value = normalizeOutputName(data.filename || "cheatsheet");
  if (data.markdown) {
    filePickerLabel.textContent = "Default example loaded";
    setStatus("Default example loaded.");
  }
}

async function readLocalFile(file) {
  const text = await file.text();
  markdownInput.value = text;
  filenameInput.value = file.name.replace(/\.[^.]+$/, "") || "cheatsheet";
  filePickerLabel.textContent = file.name;
  setStatus(`Loaded ${file.name}`);
}

async function generatePreview() {
  const markdown = markdownInput.value.trim();
  if (!markdown) {
    setStatus("Please enter or import Markdown content.", true);
    return;
  }

  generateBtn.disabled = true;
  downloadBtn.disabled = true;
  setStatus("Generating...");

  try {
    const response = await fetch("/api/convert", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        filename: filenameInput.value.trim() || "cheatsheet.md",
        outputName: `${normalizeOutputName(filenameInput.value)}.html`,
        markdown: markdownInput.value,
        columns: Number(columnsSelect.value),
        colorTemplate: colorTemplateSelect.value,
        latinFont: latinFontSelect.value,
        cjkFont: cjkFontSelect.value,
        codeFont: codeFontSelect.value,
        fontSize: fontSizeSelect.value,
        lineHeight: lineHeightSelect.value,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Generation failed.");
    }

    revokePreviewUrl();
    latestOutputName = data.outputName;
    latestBlobUrl = URL.createObjectURL(
      new Blob([data.html], { type: "text/html;charset=utf-8" })
    );
    previewFrame.src = latestBlobUrl;
    downloadBtn.disabled = false;
    setStatus(`Generated: ${latestOutputName}`);
  } catch (error) {
    setStatus(error.message || "Generation failed.", true);
  } finally {
    generateBtn.disabled = false;
  }
}

function downloadHtml() {
  if (!latestBlobUrl) return;
  const link = document.createElement("a");
  link.href = latestBlobUrl;
  link.download = latestOutputName;
  link.click();
}

filePickerButton.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  await readLocalFile(file);
});

filenameInput.addEventListener("blur", () => {
  filenameInput.value = normalizeOutputName(filenameInput.value);
});

[columnsSelect, colorTemplateSelect, latinFontSelect, cjkFontSelect, codeFontSelect, fontSizeSelect, lineHeightSelect].forEach((element) => {
  element.addEventListener("change", renderTemplateSummary);
});

generateBtn.addEventListener("click", generatePreview);
downloadBtn.addEventListener("click", downloadHtml);

window.addEventListener("beforeunload", revokePreviewUrl);

Promise.all([loadTemplates(), loadDefaultMarkdown()]).catch((error) => {
  setStatus(error.message || "Initialization failed.", true);
});
