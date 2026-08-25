document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#assistant-form");
  const input = document.querySelector("#assistant-input");
  const status = document.querySelector("#assistant-status");
  const prompts = document.querySelectorAll(".prompt-chips button");

  const questionBubble = document.querySelector(".question-bubble");
  const answerText = document.querySelector(".answer-row p");
  const sourceGrid = document.querySelector(".source-grid");

  const ask = async (question) => {
    const cleanQuestion = question.trim();

    if (!cleanQuestion) return;

    // Show user's question
    if (questionBubble) {
      questionBubble.innerHTML = `
        ${escapeHtml(cleanQuestion)}
        <small>You</small>
      `;
    }

    // Clear input
    input.value = "";

    // Loading message
    status.textContent = "HeritageAI is consulting the archive...";

    // Temporary answer
    if (answerText) {
      answerText.textContent = "Searching the HeritageAI knowledge base...";
    }

    try {
      const response = await fetch("/assistant/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: cleanQuestion,
        }),
      });

      if (!response.ok) {
        throw new Error("Archive request failed");
      }

      const data = await response.json();

      // ------------------------------------------
      // Display answer
      // ------------------------------------------

      if (answerText) {
        answerText.textContent = data.answer;
      }

      // ------------------------------------------
      // Display sources
      // ------------------------------------------

      displaySources(data.sources || []);

      // Status
      status.textContent = "HeritageAI";

    } catch (error) {

      console.error("HeritageAI error:", error);

      if (answerText) {
        answerText.textContent =
          "HeritageAI: The archive is temporarily unavailable. Please try again.";
      }

      status.textContent =
        "HeritageAI: The archive is temporarily unavailable. Please try again.";
    }
  };


  // ==================================================
  // DISPLAY SOURCES
  // ==================================================

  const displaySources = (sources) => {

    if (!sourceGrid) return;

    // No sources
    if (!sources || sources.length === 0) {

      sourceGrid.innerHTML = `
        <article>
          <span>ⓘ &nbsp; Knowledge base</span>
          <p>No source found in the HeritageAI knowledge base.</p>
        </article>
      `;

      return;
    }

    // Show maximum 2 source cards
    const visibleSources = sources.slice(0, 2);

    sourceGrid.innerHTML = visibleSources
      .map((source) => {
        return `
          <article>
            <span>▣ &nbsp; Heritage source</span>
            <p>${escapeHtml(source.section)}</p>
            <small>${escapeHtml(source.source)}</small>
          </article>
        `;
      })
      .join("");
  };


  // ==================================================
  // PROTECT HTML
  // ==================================================

  const escapeHtml = (text) => {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
  };


  // ==================================================
  // FORM SUBMIT
  // ==================================================

  form.addEventListener("submit", (event) => {

    event.preventDefault();

    ask(input.value);
  });


  // ==================================================
  // QUICK PROMPTS
  // ==================================================

  prompts.forEach((prompt) => {

    prompt.addEventListener("click", () => {

      ask(prompt.textContent);
    });
  });
});