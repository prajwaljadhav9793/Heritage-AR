document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#assistant-form");
  const input = document.querySelector("#assistant-input");
  const status = document.querySelector("#assistant-status");
  const prompts = document.querySelectorAll(".prompt-chips button");

  const ask = async (question) => {
    const cleanQuestion = question.trim();
    if (!cleanQuestion) return;

    input.value = "";
    status.textContent = "HeritageAI is consulting the archive...";
    try {
      const response = await fetch("/assistant/api/ask", {
        body: JSON.stringify({ question: cleanQuestion }),
        headers: { "Content-Type": "application/json" },
        method: "POST",
      });
      if (!response.ok) throw new Error("Archive request failed");
      const data = await response.json();
      status.textContent = `HeritageAI: ${data.answer}`;
    } catch {
      status.textContent =
        "HeritageAI: The archive is temporarily unavailable. Please try again.";
    }
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    ask(input.value);
  });

  prompts.forEach((prompt) => {
    prompt.addEventListener("click", () => ask(prompt.textContent));
  });
});
