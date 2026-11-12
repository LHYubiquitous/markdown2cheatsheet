const STORAGE_KEY = "markdown2cheatsheet.settings.v2";
const AUTO_PREVIEW_DELAY = 650;
const byId = (id) => document.getElementById(id);

const controls = {
  columns: byId("columns"),
  colorTemplate: byId("colorTemplate"),
  latinFont: byId("latinFont"),
  cjkFont: byId("cjkFont"),
  codeFont: byId("codeFont"),
  fontSize: byId("fontSize"),
  lineHeight: byId("lineHeight"),
  pageOrientation: byId("pageOrientation"),
  pageMargin: byId("pageMargin"),
  columnGap: byId("columnGap"),
  tableScale: byId("tableScale"),
  codeScale: byId("codeScale"),
  imageWidth: byId("imageWidth"),
  blockSpacing: byId("blockSpacing"),
  columnRule: byId("columnRule"),
  autoPreview: byId("autoPreview"),
};

const numericControlNames = [
  "fontSize", "lineHeight", "pageMargin", "columnGap",
  "tableScale", "codeScale", "imageWidth", "blockSpacing",
];
const settingsControlNames = Object.keys(controls);
const filenameInput = byId("filename");
const fontSizePreset = byId("fontSizePreset");
const fileInput = byId("fileInput");
const filePickerButton = byId("filePickerButton");
const filePickerLabel = byId("filePickerLabel");
const markdownInput = byId("markdownInput");
const generateBtn = byId("generateBtn");
const downloadBtn = byId("downloadBtn");
const resetBtn = byId("resetBtn");
const statusText = byId("statusText");
const previewFrame = byId("previewFrame");
const previewFilename = byId("previewFilename");
const recipePrimary = byId("recipePrimary");
const recipeSecondary = byId("recipeSecondary");

let templateMeta = null;
let latestBlobUrl = null;
let latestOutputName = "cheatsheet.html";
let selectedSourceFilename = null;
let previewTimer = 0;
let activeRequest = null;
let initialized = false;

function normalizeOutputName(value) {
  const trimmed = value.trim();
  if (!trimmed) return "cheatsheet";
  return trimmed.replace(/\.html?$/i, "");
}

function setStatus(text, isError = false) {
  statusText.textContent = text;
  statusText.classList.toggle("status-error", isError);
}

function revokePreviewUrl() {
  if (!latestBlobUrl) return;
  URL.revokeObjectURL(latestBlobUrl);
  latestBlobUrl = null;
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

function configureNumericControl(name, metadata) {
  const input = controls[name];
  input.min = String(metadata.min);
  input.max = String(metadata.max);
  input.step = String(metadata.step);
  input.value = String(metadata.default);
}

function readStoredSettings() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
  } catch (_error) {
    return null;
  }
}

function currentSettings() {
  const settings = {};
  settingsControlNames.forEach((name) => {
    settings[name] = controls[name].type === "checkbox"
      ? controls[name].checked
      : controls[name].value;
  });
  return settings;
}

function saveSettings() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(currentSettings()));
  } catch (_error) {
    // Persistence is optional; conversion remains available.
  }
}

function setDefaults() {
  const defaults = templateMeta.defaults;
  controls.columns.value = String(defaults.columns);
  controls.colorTemplate.value = defaults.color;
  controls.latinFont.value = defaults.latinFont;
  controls.cjkFont.value = defaults.cjkFont;
  controls.codeFont.value = defaults.codeFont;
  controls.pageOrientation.value = defaults.pageOrientation;
  numericControlNames.forEach((name) => {
    controls[name].value = String(templateMeta.controls[name].default);
  });
  controls.columnRule.checked = Boolean(defaults.columnRule);
  controls.autoPreview.checked = false;
}

function restoreSettings() {
  const stored = readStoredSettings();
  if (!stored) return;
  settingsControlNames.forEach((name) => {
    if (!(name in stored)) return;
    const control = controls[name];
    if (control.type === "checkbox") {
      control.checked = Boolean(stored[name]);
      return;
    }
    const candidate = String(stored[name]);
    if (control.tagName === "SELECT") {
      if ([...control.options].some((option) => option.value === candidate)) {
        control.value = candidate;
      }
      return;
    }
    control.value = candidate;
    if (!control.checkValidity()) {
      control.value = String(templateMeta.controls[name].default);
    }
  });
}

function numberValue(name) {
  return Number(controls[name].value);
}

function renderRecipe() {
  if (!templateMeta) return;
  const orientation = controls.pageOrientation.value === "portrait" ? "Portrait" : "Landscape";
  recipePrimary.textContent = `A4 · ${orientation} · ${controls.columns.value} columns`;
  recipeSecondary.textContent =
    `${controls.fontSize.value}pt · ${controls.pageMargin.value}mm margin · `
    + `${controls.columnGap.value}mm gap · ${controls.imageWidth.value}% images`;
}

function validateControls(report = false) {
  for (const name of numericControlNames) {
    const input = controls[name];
    if (input.checkValidity() && Number.isFinite(Number(input.value))) continue;
    if (report) input.reportValidity();
    const label = input.closest("label").querySelector(":scope > span").textContent;
    setStatus(`Check ${label}.`, true);
    return false;
  }
  return true;
}

async function loadTemplates() {
  const response = await fetch("/api/templates");
  if (!response.ok) throw new Error("Could not load layout controls.");
  templateMeta = await response.json();
  fillSelect(
    controls.columns,
    templateMeta.columns.values.map((value) => ({ value, label: `${value} columns` })),
  );
  fillSelect(
    controls.colorTemplate,
    Object.entries(templateMeta.colors).map(([value, meta]) => ({ value, label: meta.label })),
  );
  fillSelect(
    controls.latinFont,
    Object.entries(templateMeta.latinFonts).map(([value, meta]) => ({ value, label: meta.label })),
  );
  fillSelect(
    controls.cjkFont,
    Object.entries(templateMeta.cjkFonts).map(([value, meta]) => ({ value, label: meta.label })),
  );
  fillSelect(
    controls.codeFont,
    Object.entries(templateMeta.codeFonts).map(([value, meta]) => ({ value, label: meta.label })),
  );
  numericControlNames.forEach((name) => configureNumericControl(name, templateMeta.controls[name]));
  setDefaults();
  restoreSettings();
  renderRecipe();
}

async function loadDefaultMarkdown() {
  const response = await fetch("/api/default-markdown");
  if (!response.ok) throw new Error("Could not load the example Markdown.");
  const data = await response.json();
  markdownInput.value = data.markdown || "";
  filenameInput.value = normalizeOutputName(data.filename || "cheatsheet");
  if (data.markdown) {
    filePickerLabel.textContent = "Example loaded";
    setStatus("Example loaded.");
  }
}

async function readLocalFile(file) {
  markdownInput.value = await file.text();
  filenameInput.value = file.name.replace(/\.[^.]+$/, "") || "cheatsheet";
  selectedSourceFilename = file.name;
  filePickerLabel.textContent = file.name;
  setStatus(`Loaded ${file.name}`);
  schedulePreview();
}

function requestPayload() {
  return {
    filename: selectedSourceFilename || `${normalizeOutputName(filenameInput.value)}.md`,
    outputName: `${normalizeOutputName(filenameInput.value)}.html`,
    markdown: markdownInput.value,
    columns: Number(controls.columns.value),
    colorTemplate: controls.colorTemplate.value,
    latinFont: controls.latinFont.value,
    cjkFont: controls.cjkFont.value,
    codeFont: controls.codeFont.value,
    fontSize: numberValue("fontSize"),
    lineHeight: numberValue("lineHeight"),
    pageOrientation: controls.pageOrientation.value,
    pageMargin: numberValue("pageMargin"),
    columnGap: numberValue("columnGap"),
    tableScale: numberValue("tableScale"),
    codeScale: numberValue("codeScale"),
    imageWidth: numberValue("imageWidth"),
    blockSpacing: numberValue("blockSpacing"),
    columnRule: controls.columnRule.checked,
  };
}

async function generatePreview() {
  if (!markdownInput.value.trim()) {
    setStatus("Enter or import Markdown content first.", true);
    return;
  }
  if (!validateControls(true)) return;

  if (activeRequest) activeRequest.abort();
  const controller = new AbortController();
  activeRequest = controller;
  generateBtn.disabled = true;
  downloadBtn.disabled = true;
  setStatus("Generating preview…");

  try {
    const response = await fetch("/api/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestPayload()),
      signal: controller.signal,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Generation failed.");
    if (activeRequest !== controller) return;

    revokePreviewUrl();
    latestOutputName = data.outputName;
    latestBlobUrl = URL.createObjectURL(
      new Blob([data.html], { type: "text/html;charset=utf-8" }),
    );
    previewFrame.src = latestBlobUrl;
    previewFilename.textContent = latestOutputName;
    downloadBtn.disabled = false;
    setStatus(data.warning
      ? `Generated ${latestOutputName}. ${data.warning}`
      : `Generated ${latestOutputName}`);
  } catch (error) {
    if (error.name !== "AbortError") {
      setStatus(error.message || "Generation failed.", true);
    }
  } finally {
    if (activeRequest === controller) {
      activeRequest = null;
      generateBtn.disabled = false;
    }
  }
}

function schedulePreview() {
  window.clearTimeout(previewTimer);
  if (!initialized || !controls.autoPreview.checked || !markdownInput.value.trim()) return;
  previewTimer = window.setTimeout(generatePreview, AUTO_PREVIEW_DELAY);
}

function downloadHtml() {
  if (!latestBlobUrl) return;
  const link = document.createElement("a");
  link.href = latestBlobUrl;
  link.download = latestOutputName;
  link.click();
}

function handleSettingChange() {
  renderRecipe();
  saveSettings();
  if (validateControls()) schedulePreview();
}

filePickerButton.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (file) await readLocalFile(file);
});
filenameInput.addEventListener("blur", () => {
  filenameInput.value = normalizeOutputName(filenameInput.value);
});
settingsControlNames.forEach((name) => {
  controls[name].addEventListener("input", handleSettingChange);
  controls[name].addEventListener("change", handleSettingChange);
});
markdownInput.addEventListener("input", schedulePreview);
fontSizePreset.addEventListener("change", () => {
  if (!fontSizePreset.value) return;
  controls.fontSize.value = fontSizePreset.value;
  handleSettingChange();
  fontSizePreset.value = "";
});

resetBtn.addEventListener("click", () => {
  setDefaults();
  saveSettings();
  renderRecipe();
  setStatus("Settings reset.");
  schedulePreview();
});
generateBtn.addEventListener("click", generatePreview);
downloadBtn.addEventListener("click", downloadHtml);

window.addEventListener("beforeunload", () => {
  window.clearTimeout(previewTimer);
  if (activeRequest) activeRequest.abort();
  revokePreviewUrl();
});

Promise.all([loadTemplates(), loadDefaultMarkdown()])
  .then(() => {
    initialized = true;
    renderRecipe();
    if (controls.autoPreview.checked) schedulePreview();
  })
  .catch((error) => setStatus(error.message || "Initialization failed.", true));
