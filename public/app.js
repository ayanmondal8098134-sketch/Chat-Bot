const form = document.querySelector("#chat-form");
const promptInput = document.querySelector("#prompt");
const messagesEl = document.querySelector("#messages");
const webSearch = document.querySelector("#web-search");
const statusEl = document.querySelector("#status");
const sendButton = document.querySelector("#send");
const clearButton = document.querySelector("#clear-chat");

let history = [];

function addMessage(role, text, sources = []) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.append(paragraph);

  if (sources.length) {
    const list = document.createElement("ul");
    list.className = "sources";
    for (const source of sources) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.textContent = source.title || source.url;
      item.append(link);
      list.append(item);
    }
    article.append(list);
  }
  messagesEl.append(article);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setBusy(busy) {
  sendButton.disabled = busy;
  promptInput.disabled = busy;
  statusEl.textContent = busy ? "Thinking…" : "";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = promptInput.value.trim();
  if (!text) return;

  history.push({ role: "user", content: text });
  addMessage("user", text);
  promptInput.value = "";
  setBusy(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history, web_search: webSearch.checked }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Request failed");

    history.push({ role: "assistant", content: data.reply });
    addMessage("assistant", data.reply, data.sources || []);
  } catch (error) {
    addMessage("assistant", `Sorry — ${error.message}`);
  } finally {
    setBusy(false);
    promptInput.focus();
  }
});

clearButton.addEventListener("click", () => {
  history = [];
  messagesEl.innerHTML = "";
  addMessage("assistant", "Chat cleared. What would you like to talk about?");
});
