document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-voice-assistant]");
  if (!root) return;

  const form = root.querySelector("[data-voice-form]");
  const input = root.querySelector("[data-voice-input]");
  const mic = root.querySelector("[data-mic]");
  const replay = root.querySelector("[data-replay]");
  const answerPanel = root.querySelector("[data-answer-panel]");
  const answer = root.querySelector("[data-answer]");
  const state = root.querySelector("[data-state]");
  const hint = root.querySelector("[data-hint]");
  const status = root.querySelector("[data-status]");
  const orb = root.querySelector("[data-orb]");
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let lastAnswer = "";
  let recognition;
  let isRecognizing = false;
  let recognitionError = false;

  const getSpeechVoice = () => {
    const voices = window.speechSynthesis.getVoices();
    return voices.find((voice) => voice.lang.toLowerCase() === "en-in")
      || voices.find((voice) => voice.lang.toLowerCase().startsWith("en-in"))
      || voices.find((voice) => voice.lang.toLowerCase() === "en-gb")
      || voices.find((voice) => voice.lang.toLowerCase().startsWith("en"));
  };

  const cleanSpeechText = (text) => text
    .replace(/[\u201c\u201d]/g, '"')
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u2013\u2014]/g, "-")
    .replace(/\s+/g, " ")
    .trim();

  const speak = (text) => {
    if (!("speechSynthesis" in window) || !text) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(cleanSpeechText(text));
    utterance.lang = "en-IN";
    utterance.rate = 0.86;
    utterance.pitch = 0.98;
    utterance.volume = 1;
    utterance.voice = getSpeechVoice() || null;
    window.speechSynthesis.speak(utterance);
  };

  const setListening = (listening) => {
    mic.classList.toggle("is-listening", listening);
    orb.classList.toggle("is-listening", listening);
    mic.setAttribute("aria-label", listening ? "Stop listening" : "Speak your question");
    state.textContent = listening ? "Listening..." : "Voice mode ready";
    hint.textContent = listening ? "Speak your question clearly." : "Ask about Raigad, the Maratha Empire, or any story in the archive.";
  };

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onstart = () => {
      isRecognizing = true;
      recognitionError = false;
      setListening(true);
      status.textContent = "Listening for your question...";
    };
    recognition.onresult = (event) => {
      input.value = event.results[0][0].transcript;
      input.focus();
      state.textContent = "Question captured";
      hint.textContent = "Review your question, then press Ask to hear the answer.";
      status.textContent = "Your spoken question is ready to send.";
    };
    recognition.onerror = (event) => {
      isRecognizing = false;
      recognitionError = true;
      setListening(false);
      const message = event.error === "not-allowed"
        ? "Microphone permission was denied. Allow microphone access, then try again."
        : "Microphone unavailable. Check your microphone, then try again.";
      state.textContent = "Microphone unavailable";
      status.textContent = message;
    };
    recognition.onend = () => {
      isRecognizing = false;
      if (!recognitionError) setListening(false);
      mic.classList.remove("is-listening");
      orb.classList.remove("is-listening");
      mic.setAttribute("aria-label", "Speak your question");
    };
  } else {
    mic.disabled = true;
    mic.title = "Speech input is not supported in this browser";
    hint.textContent = "Type your question below. Your answer will still be spoken aloud.";
  }

  mic.addEventListener("click", async () => {
    if (!recognition) return;
    if (isRecognizing) {
      recognition.stop();
      return;
    }

    if (navigator.mediaDevices?.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach((track) => track.stop());
      } catch (error) {
        state.textContent = "Microphone unavailable";
        status.textContent = "Allow microphone access in your browser, then try again.";
        return;
      }
    }

    try {
      recognition.start();
    } catch (error) {
      status.textContent = "Microphone could not start. Please try again.";
    }
  });

  const ask = async (question) => {
    const cleanQuestion = question.trim();
    if (!cleanQuestion) {
      status.textContent = "Please enter a question first.";
      input.focus();
      return;
    }

    state.textContent = "Searching the archive...";
    status.textContent = "HeritageAI is preparing a spoken answer...";
    answerPanel.hidden = false;
    answer.textContent = "Consulting the HeritageAI knowledge base...";

    try {
      const response = await fetch("/assistant/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: cleanQuestion }),
      });
      if (!response.ok) throw new Error("Archive request failed");
      const data = await response.json();
      lastAnswer = data.answer || "No answer was returned from the archive.";
      answer.textContent = lastAnswer;
      state.textContent = "Answer ready";
      status.textContent = "Speaking your answer...";
      speak(lastAnswer);
      window.setTimeout(() => { status.textContent = "HeritageAI"; }, 1800);
    } catch (error) {
      console.error("Voice Assistant error:", error);
      lastAnswer = "HeritageAI is temporarily unavailable. Please try again.";
      answer.textContent = lastAnswer;
      state.textContent = "Archive unavailable";
      status.textContent = lastAnswer;
    }
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const question = input.value;
    input.value = "";
    ask(question);
  });

  replay.addEventListener("click", () => {
    speak(lastAnswer);
    status.textContent = "Replaying your answer...";
  });
});
