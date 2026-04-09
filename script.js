const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatWindow = document.getElementById("chatWindow");
const intentValue = document.getElementById("intentValue");
const matchValue = document.getElementById("matchValue");
const scoreValue = document.getElementById("scoreValue");
const tokensValue = document.getElementById("tokensValue");

function appendMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.appendChild(paragraph);
  chatWindow.appendChild(article);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage(message) {
  appendMessage("user", message);

  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const data = await response.json();

  if (!response.ok) {
    appendMessage("bot", data.error || "Something went wrong.");
    return;
  }

  appendMessage("bot", data.reply);
  intentValue.textContent = data.intent;
  matchValue.textContent = data.matched_question;
  scoreValue.textContent = data.similarity;
  tokensValue.textContent = data.processed_query.join(", ") || "-";
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = userInput.value.trim();
  if (!message) {
    return;
  }

  userInput.value = "";
  await sendMessage(message);
});

document.querySelectorAll(".chip").forEach((button) => {
  button.addEventListener("click", async () => {
    const message = button.dataset.question;
    userInput.value = "";
    await sendMessage(message);
  });
});
