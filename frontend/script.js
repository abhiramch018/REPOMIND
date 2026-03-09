/* ═══════════════════════════════════════════════════════════════════════════
   RepoMind — Frontend Logic
   ═══════════════════════════════════════════════════════════════════════════ */

const API_BASE = window.location.origin;
let currentRepoUrl = "";
let isAnalyzed = false;

// ── DOM refs ──────────────────────────────────────────────────────────────
const repoUrlInput   = document.getElementById("repoUrl");
const analyzeBtn     = document.getElementById("analyzeBtn");
const repoInfo       = document.getElementById("repoInfo");
const messagesDiv    = document.getElementById("messages");
const questionInput  = document.getElementById("questionInput");
const askBtn         = document.getElementById("askBtn");
const statusBadge    = document.getElementById("statusBadge");

// ── Enter-key handlers ───────────────────────────────────────────────────
repoUrlInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") analyzeRepo();
});

questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !askBtn.disabled) askQuestion();
});

// ── Status badge ─────────────────────────────────────────────────────────
function setStatus(text, type = "ready") {
    const badge = statusBadge;
    badge.className = `header__status ${type === "analyzing" ? "analyzing" : type === "error" ? "error" : ""}`;
    badge.querySelector(".status-text").textContent = text;
}

// ── Scroll to bottom ─────────────────────────────────────────────────────
function scrollToBottom() {
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ── Clear welcome screen ─────────────────────────────────────────────────
function clearWelcome() {
    const welcome = messagesDiv.querySelector(".welcome");
    if (welcome) welcome.remove();
}

// ── Add a message to chat ────────────────────────────────────────────────
function addMessage(content, type = "ai", sources = []) {
    clearWelcome();
    const msg = document.createElement("div");
    msg.className = `message message--${type}`;

    if (type === "system") {
        msg.innerHTML = `<div class="message__content">${content}</div>`;
    } else {
        const avatarText = type === "user" ? "U" : "R";
        let html = `
            <div class="message__avatar">${avatarText}</div>
            <div class="message__content">
                ${type === "ai" ? renderMarkdown(content) : escapeHtml(content)}
        `;
        if (sources.length > 0) {
            html += `<div class="message__sources">
                <strong>Sources:</strong> ${sources.map(s => `<span>${escapeHtml(s)}</span>`).join("")}
            </div>`;
        }
        html += `</div>`;
        msg.innerHTML = html;
    }

    messagesDiv.appendChild(msg);
    scrollToBottom();
}

// ── Typing indicator ─────────────────────────────────────────────────────
function showTyping() {
    clearWelcome();
    const el = document.createElement("div");
    el.className = "message message--ai";
    el.id = "typingIndicator";
    el.innerHTML = `
        <div class="message__avatar">R</div>
        <div class="typing">
            <div class="typing__dot"></div>
            <div class="typing__dot"></div>
            <div class="typing__dot"></div>
        </div>
    `;
    messagesDiv.appendChild(el);
    scrollToBottom();
}

function hideTyping() {
    const el = document.getElementById("typingIndicator");
    if (el) el.remove();
}

// ── Loader ───────────────────────────────────────────────────────────────
function showLoader(text) {
    clearWelcome();
    const el = document.createElement("div");
    el.className = "loader";
    el.id = "analysisLoader";
    el.innerHTML = `
        <div class="loader__spinner"></div>
        <span class="loader__text">${text}</span>
    `;
    messagesDiv.appendChild(el);
    scrollToBottom();
}

function hideLoader() {
    const el = document.getElementById("analysisLoader");
    if (el) el.remove();
}

// ── Analyze repository ───────────────────────────────────────────────────
async function analyzeRepo() {
    const url = repoUrlInput.value.trim();
    if (!url) {
        repoUrlInput.focus();
        return;
    }

    // Validate URL pattern
    if (!url.match(/github\.com\/.+\/.+/)) {
        addMessage("⚠️ Please enter a valid GitHub repository URL (e.g. https://github.com/user/repo)", "system");
        return;
    }

    currentRepoUrl = url;
    isAnalyzed = false;
    analyzeBtn.disabled = true;
    questionInput.disabled = true;
    askBtn.disabled = true;
    setStatus("Analyzing…", "analyzing");

    addMessage(`Analyzing repository: ${url}`, "system");
    showLoader("Cloning repository and building search index… This may take a minute.");

    try {
        const res = await fetch(`${API_BASE}/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ repo_url: url }),
        });

        hideLoader();

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Analysis failed");
        }

        const data = await res.json();
        isAnalyzed = true;

        addMessage(
            `✅ **Analysis complete!**\n\n` +
            `- **Files scanned:** ${data.files_scanned}\n` +
            `- **Chunks indexed:** ${data.chunks_created}\n\n` +
            `You can now ask questions about the codebase.`,
            "ai"
        );

        // Show repo info
        repoInfo.textContent = `✓ ${data.repo_name} — ${data.files_scanned} files indexed`;
        repoInfo.classList.add("visible");

        setStatus("Ready", "ready");
        questionInput.disabled = false;
        askBtn.disabled = false;
        questionInput.focus();

    } catch (err) {
        hideLoader();
        addMessage(`❌ ${err.message}`, "system");
        setStatus("Error", "error");
    } finally {
        analyzeBtn.disabled = false;
    }
}

// ── Ask a question ───────────────────────────────────────────────────────
async function askQuestion() {
    const question = questionInput.value.trim();
    if (!question || !isAnalyzed) return;

    addMessage(question, "user");
    questionInput.value = "";
    questionInput.disabled = true;
    askBtn.disabled = true;

    showTyping();

    try {
        const res = await fetch(`${API_BASE}/ask`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                repo_url: currentRepoUrl,
                question: question,
            }),
        });

        hideTyping();

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Query failed");
        }

        const data = await res.json();
        addMessage(data.answer, "ai", data.sources || []);

    } catch (err) {
        hideTyping();
        addMessage(`❌ ${err.message}`, "system");
    } finally {
        questionInput.disabled = false;
        askBtn.disabled = false;
        questionInput.focus();
    }
}

// ── Markdown renderer (lightweight) ──────────────────────────────────────
function renderMarkdown(text) {
    if (!text) return "";

    let html = escapeHtml(text);

    // Code blocks (``` ... ```)
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
        return `<pre><code>${code.trim()}</code></pre>`;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Headers
    html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

    // Bold
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

    // Italic
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    // Unordered list items
    html = html.replace(/^[\-\*] (.+)$/gm, "<li>$1</li>");

    // Ordered list items
    html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");

    // Wrap consecutive <li> in <ul>
    html = html.replace(/((?:<li>.*<\/li>\s*)+)/g, "<ul>$1</ul>");

    // Horizontal rule
    html = html.replace(/^---$/gm, "<hr>");

    // Paragraphs (double newlines)
    html = html.replace(/\n\n/g, "</p><p>");
    html = `<p>${html}</p>`;

    // Single newlines → <br> (but not inside pre/code)
    html = html.replace(/(?<!<\/?\w+[^>]*)\n/g, "<br>");

    // Clean up empty paragraphs
    html = html.replace(/<p>\s*<\/p>/g, "");
    html = html.replace(/<p>\s*(<h[1-3]>)/g, "$1");
    html = html.replace(/(<\/h[1-3]>)\s*<\/p>/g, "$1");
    html = html.replace(/<p>\s*(<pre>)/g, "$1");
    html = html.replace(/(<\/pre>)\s*<\/p>/g, "$1");
    html = html.replace(/<p>\s*(<ul>)/g, "$1");
    html = html.replace(/(<\/ul>)\s*<\/p>/g, "$1");
    html = html.replace(/<p>\s*(<hr>)\s*<\/p>/g, "$1");

    return html;
}

// ── Escape HTML ──────────────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
