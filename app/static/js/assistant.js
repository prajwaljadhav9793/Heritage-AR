document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#assistant-form");
  const input = document.querySelector("#assistant-input");
  const status = document.querySelector("#assistant-status");
  const prompts = document.querySelectorAll(".prompt-chips button");

  const questionBubble = document.querySelector(".question-bubble");
  const answerText = document.querySelector(".answer-row p");
  const sourceGrid = document.querySelector(".source-grid");
  const artifactList = document.querySelector("#artifact-list");

  // Add your files to app/static/images/heritage/ai-guide/ and map them here.
  const artifactSets = [
    {
      keywords: ["coronation", "1674", "crown", "shivaji"],
      items: [
        ["Coronation Regalia", "17th century · Royal ceremony", "../../historical/then-fort.jpg"],
        ["Royal Court at Raigad", "1674 · Maratha history", "../../heritage/discover-fort.jpg"],
      ],
    },
    {
      keywords: ["coin", "money", "currency", "shivrai"],
      items: [
        ["Shivrai Copper Coin", "Minted at Raigad · Numismatics", "../../heritage/discover-fort.jpg"],
        ["Maratha Inscription", "17th century · Epigraphy", "../../historical/then-fort.jpg"],
      ],
    },
    {
      keywords: ["fort", "gate", "built", "architecture", "capital"],
      items: [
        ["Raigad Fort Gateway", "17th century · Architecture", "../../historical/then-fort.jpg"],
        ["Raigad Mountain Capital", "Living heritage · Raigad", "../../heritage/discover-fort.jpg"],
      ],
    },
    {
      keywords: ["konark", "sun temple", "surya", "wheel", "chariot"],
      items: [
        ["Konark Sun Temple", "13th century · Odisha heritage", "../../timeline/konark-01.jpg"],
        ["The Stone Wheel", "Astronomy and architecture", "../../timeline/konark-02.jpg"],
      ],
    },
  ];

  const defaultArtifacts = [
    ["Raigad Fort Gateway", "17th century · Architecture", "../../historical/then-fort.jpg"],
    ["Raigad Mountain Capital", "Living heritage · Raigad", "../../heritage/discover-fort.jpg"],
  ];

  const displayArtifacts = (question) => {
    if (!artifactList) return;
    const normalizedQuestion = question.toLowerCase();
    const matchingSet = artifactSets.find((set) =>
      set.keywords.some((keyword) => normalizedQuestion.includes(keyword)),
    );
    const items = matchingSet ? matchingSet.items : defaultArtifacts;

    artifactList.innerHTML = items
      .map(
        ([title, detail, filename]) => `
          <article class="artifact-card">
            <div class="artifact-image" style="background-image: linear-gradient(0deg, rgba(28, 15, 7, .32), transparent), url('/static/images/heritage/ai-guide/${filename}');"></div>
            <strong>${escapeHtml(title)}</strong><small>${escapeHtml(detail)}</small>
          </article>
        `,
      )
      .join("");
  };

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
    displayArtifacts(cleanQuestion);

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