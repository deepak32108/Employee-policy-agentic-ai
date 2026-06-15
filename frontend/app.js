const API_URL = "http://127.0.0.1:8000";

let currentAnswer = "";
let currentQuestion = "";

async function sendQuestion(searchWeb = false) {

    const questionBox =
        document.getElementById("question");

    let question;

    if (searchWeb) {
        question = currentQuestion;
    } else {
        question = questionBox.value.trim();

        if (!question) {
            return;
        }

        currentQuestion = question;

        addUserMessage(question);

        questionBox.value = "";
    }

    showLoading();

    try {

        const response = await fetch(
            `${API_URL}/ask`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: question,
                    search_web: searchWeb
                })
            }
        );

        const data = await response.json();

        removeLoading();

        if (data.requires_confirmation) {

            document.getElementById(
                "confirmation-box"
            ).innerHTML = `
                <div class="card">
                    <p>${data.answer}</p>

                    <button onclick="confirmWebSearch(true)">
                        Yes
                    </button>

                    <button onclick="confirmWebSearch(false)">
                        No
                    </button>
                </div>
            `;

            return;
        }

        let answer =
            data.answer ||
            "No answer found.";

        currentAnswer = answer;

        const confidence =
            data.confidence || 0;

        const verdict =
            data.verdict || "UNKNOWN";

        let sourcesHtml = "";

        if (
            data.citations &&
            data.citations.length > 0
        ) {

            sourcesHtml =
                "<br><br><b>Sources:</b><br>";

            data.citations.forEach(
                citation => {

                    sourcesHtml +=
                        `• ${citation.source}
                        (Page ${citation.page})<br>`;
                }
            );
        }

        answer += `
            <br><br>
            <b>Verdict:</b> ${verdict}
            <br>
            <b>Confidence:</b> ${confidence}%
            ${sourcesHtml}
        `;

        addBotMessage(answer);

        saveHistory(
            currentQuestion,
            answer
        );

        document.getElementById(
            "confirmation-box"
        ).innerHTML = "";

        currentQuestion = "";

    }
    catch (error) {

        removeLoading();

        addBotMessage(
            "Error connecting to backend."
        );

        console.error(error);
    }
}

function confirmWebSearch(choice) {

    document.getElementById(
        "confirmation-box"
    ).innerHTML = "";

    if (choice) {

        sendQuestion(true);

    } else {

        currentQuestion = "";

        addBotMessage(
            "Web search cancelled."
        );
    }
}

function addUserMessage(message) {

    const chatBox =
        document.getElementById(
            "chat-box"
        );

    chatBox.innerHTML += `
        <div class="user">
            ${message}
        </div>
    `;

    scrollChat();
}

function addBotMessage(message) {

    const chatBox =
        document.getElementById(
            "chat-box"
        );

    chatBox.innerHTML += `
        <div class="bot">
            ${message}
        </div>
    `;

    scrollChat();
}

function scrollChat() {

    const chatBox =
        document.getElementById(
            "chat-box"
        );

    chatBox.scrollTop =
        chatBox.scrollHeight;
}

function showLoading() {

    const chatBox =
        document.getElementById(
            "chat-box"
        );

    chatBox.innerHTML += `
        <div id="loading" class="bot">
            Thinking...
        </div>
    `;

    scrollChat();
}

function removeLoading() {

    const loading =
        document.getElementById(
            "loading"
        );

    if (loading) {
        loading.remove();
    }
}

function clearChat() {

    document.getElementById(
        "chat-box"
    ).innerHTML = "";

    currentAnswer = "";
    currentQuestion = "";
}

function toggleTheme() {

    document.body.classList.toggle(
        "dark-mode"
    );
}

function showSection(section) {

    document.getElementById(
        "chat-section"
    ).classList.add("hidden");

    document.getElementById(
        "analytics-section"
    ).classList.add("hidden");

    document.getElementById(
        "monitoring-section"
    ).classList.add("hidden");

    document.getElementById(
        "feedback-section"
    ).classList.add("hidden");

    document.getElementById(
        section + "-section"
    ).classList.remove("hidden");
}

function saveHistory(
    question,
    answer
) {

    let history = JSON.parse(
        localStorage.getItem(
            "chat_history"
        ) || "[]"
    );

    history.unshift({
        question: question,
        answer: answer,
        timestamp:
            new Date().toLocaleString()
    });

    localStorage.setItem(
        "chat_history",
        JSON.stringify(history)
    );

    loadHistory();
}

function loadHistory() {

    const historyDiv =
        document.getElementById(
            "history-list"
        );

    if (!historyDiv) return;

    let history = JSON.parse(
        localStorage.getItem(
            "chat_history"
        ) || "[]"
    );

    historyDiv.innerHTML = "";

    history.forEach(
        (item, index) => {

            historyDiv.innerHTML += `
                <div
                    class="history-item"
                    onclick="openHistory(${index})"
                >
                    ${item.question}
                </div>
            `;
        }
    );
}

function openHistory(index) {

    let history = JSON.parse(
        localStorage.getItem(
            "chat_history"
        ) || "[]"
    );

    const item =
        history[index];

    document.getElementById(
        "chat-box"
    ).innerHTML = `
        <div class="user">
            ${item.question}
        </div>

        <div class="bot">
            ${item.answer}
        </div>
    `;
}

window.onload = function () {

    loadHistory();

    const questionInput =
        document.getElementById(
            "question"
        );

    if (questionInput) {

        questionInput.addEventListener(
            "keypress",
            function (event) {

                if (
                    event.key === "Enter"
                ) {

                    sendQuestion();
                }
            }
        );
    }
};