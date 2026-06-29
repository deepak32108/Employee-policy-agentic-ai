const API_URL =
    window.location.protocol === "file:"
        ? "http://127.0.0.1:8000"
        : window.location.origin;

let currentQuestion = "";
const answerStore = {};
const analyticsCharts = {};

function getUserId() {
    let userId = localStorage.getItem("hr_copilot_user_id");

    if (!userId) {
        userId =
            "user_" +
            Date.now().toString(36) +
            "_" +
            Math.random().toString(36).slice(2, 10);

        localStorage.setItem(
            "hr_copilot_user_id",
            userId
        );
    }

    return userId;
}

function escapeHtml(value) {
    return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

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
                    search_web: searchWeb,
                    user_id: getUserId()
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
                    <p>${escapeHtml(data.answer)}</p>

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

        const renderedAnswer =
            renderAnswer(
                question,
                data
            );

        addBotMessage(
            renderedAnswer
        );

        saveHistory(
            question,
            renderedAnswer
        );

        document.getElementById(
            "confirmation-box"
        ).innerHTML = "";

        currentQuestion = "";

        loadAnalytics();
    }
    catch (error) {
        removeLoading();

        addBotMessage(
            "Error connecting to backend."
        );

        console.error(error);
    }
}

function renderAnswer(question, data) {
    const answerId =
        "answer_" +
        Date.now().toString(36) +
        "_" +
        Math.random().toString(36).slice(2, 8);

    const answer =
        data.answer ||
        "No answer found.";

    answerStore[answerId] = {
        question,
        answer
    };

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
                if (citation.link) {
                    sourcesHtml +=
                        `* <a href="${escapeHtml(citation.link)}" target="_blank">
                            ${escapeHtml(citation.source)}
                        </a><br>`;
                } else {
                    sourcesHtml +=
                        `* ${escapeHtml(citation.source)}
                        (Page ${escapeHtml(citation.page)})<br>`;
                }
            }
        );
    }

    return `
        <div class="answer-content">
            ${escapeHtml(answer).replace(/\n/g, "<br>")}
            <br><br>
            <b>Verdict:</b> ${escapeHtml(verdict)}
            <br>
            <b>Confidence:</b> ${escapeHtml(confidence)}%
            ${sourcesHtml}
        </div>

        <div class="feedback-widget" id="feedback-${answerId}">
            <div class="feedback-title">Rate this answer</div>
            <div class="star-row">
                ${[1, 2, 3, 4, 5].map(
                    rating => `
                        <button
                            class="star-button"
                            onclick="selectRating('${answerId}', ${rating})"
                            title="${rating} star${rating > 1 ? "s" : ""}"
                        >
                            ${rating <= 5 ? "★" : ""}
                        </button>
                    `
                ).join("")}
            </div>
            <textarea
                id="feedback-comment-${answerId}"
                class="feedback-comment"
                placeholder="Optional feedback..."
            ></textarea>
            <button
                class="feedback-submit"
                onclick="submitFeedback('${answerId}')"
            >
                Send Feedback
            </button>
            <span
                class="feedback-status"
                id="feedback-status-${answerId}"
            ></span>
        </div>
    `;
}

function selectRating(answerId, rating) {
    const widget =
        document.getElementById(
            `feedback-${answerId}`
        );

    if (!widget) return;

    widget.dataset.rating = rating;

    widget.querySelectorAll(
        ".star-button"
    ).forEach(
        (button, index) => {
            button.classList.toggle(
                "selected",
                index < rating
            );
        }
    );
}

async function submitFeedback(answerId) {
    const widget =
        document.getElementById(
            `feedback-${answerId}`
        );

    const status =
        document.getElementById(
            `feedback-status-${answerId}`
        );

    if (!widget || !answerStore[answerId]) {
        return;
    }

    const rating =
        Number(widget.dataset.rating || 0);

    if (!rating) {
        status.innerText =
            "Please select a rating.";
        return;
    }

    const comment =
        document.getElementById(
            `feedback-comment-${answerId}`
        ).value.trim();

    try {
        const response = await fetch(
            `${API_URL}/feedback`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: answerStore[answerId].question,
                    answer: answerStore[answerId].answer,
                    rating,
                    comment,
                    user_id: getUserId(),
                    answer_id: answerId
                })
            }
        );

        if (!response.ok) {
            throw new Error("Feedback request failed");
        }

        status.innerText =
            "Feedback sent.";

        widget.querySelectorAll(
            "button, textarea"
        ).forEach(
            element => {
                element.disabled = true;
            }
        );

        loadAnalytics();
    }
    catch (error) {
        status.innerText =
            "Could not send feedback.";

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
            ${escapeHtml(message)}
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

    if (section === "analytics") {
        loadAnalytics();
    }

    if (section === "monitoring") {
        loadMonitoring();
    }

    if (section === "feedback") {
        loadFeedbackSummary();
    }
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
                    ${escapeHtml(item.question)}
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
            ${escapeHtml(item.question)}
        </div>

        <div class="bot">
            ${item.answer}
        </div>
    `;
}

async function loadAnalytics() {
    const content =
        document.getElementById(
            "analytics-content"
        );

    if (!content) return;

    const response = await fetch(
        `${API_URL}/analytics`
    );

    const data = await response.json();

    content.innerHTML = `
        <div class="metric-grid">
            <div class="metric-card">
                <span>Total Users</span>
                <strong>${data.total_users || 0}</strong>
            </div>
            <div class="metric-card">
                <span>Total Questions</span>
                <strong>${data.total_questions || 0}</strong>
            </div>
            <div class="metric-card">
                <span>Average Rating</span>
                <strong>${Number(data.average_rating || 0).toFixed(2)}</strong>
            </div>
            <div class="metric-card">
                <span>Total Feedback</span>
                <strong>${data.total_feedback || 0}</strong>
            </div>
            <div class="metric-card">
                <span>Policy Questions</span>
                <strong>${data.policy_questions || 0}</strong>
            </div>
            <div class="metric-card">
                <span>Web Questions</span>
                <strong>${data.web_questions || 0}</strong>
            </div>
            <div class="metric-card">
                <span>Knowledge Gaps</span>
                <strong>${data.knowledge_gaps || 0}</strong>
            </div>
            <div class="metric-card">
                <span>Average Confidence</span>
                <strong>${Number(data.average_confidence || 0).toFixed(2)}%</strong>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="chart-card">
                <h2>Rating Distribution</h2>
                <canvas id="ratingDistributionChart"></canvas>
            </div>
            <div class="chart-card">
                <h2>Usage Mix</h2>
                <canvas id="questionMixChart"></canvas>
            </div>
            <div class="chart-card wide">
                <h2>Trends</h2>
                <canvas id="trendChart"></canvas>
            </div>
        </div>
    `;

    renderAnalyticsCharts(data);
}

function destroyChart(id) {
    if (analyticsCharts[id]) {
        analyticsCharts[id].destroy();
    }
}

function renderAnalyticsCharts(data) {
    if (!window.Chart) {
        renderCanvasFallbackCharts(data);
        return;
    }

    const distribution =
        data.rating_distribution || {};

    destroyChart("ratingDistributionChart");
    analyticsCharts.ratingDistributionChart =
        new Chart(
            document.getElementById(
                "ratingDistributionChart"
            ),
            {
                type: "bar",
                data: {
                    labels: ["1", "2", "3", "4", "5"],
                    datasets: [
                        {
                            label: "Ratings",
                            data: [1, 2, 3, 4, 5].map(
                                star => distribution[String(star)] || 0
                            ),
                            backgroundColor: "#2563eb"
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            }
        );

    destroyChart("questionMixChart");
    analyticsCharts.questionMixChart =
        new Chart(
            document.getElementById(
                "questionMixChart"
            ),
            {
                type: "doughnut",
                data: {
                    labels: [
                        "Policy",
                        "Web",
                        "Knowledge Gaps"
                    ],
                    datasets: [
                        {
                            data: [
                                data.policy_questions || 0,
                                data.web_questions || 0,
                                data.knowledge_gaps || 0
                            ],
                            backgroundColor: [
                                "#2563eb",
                                "#16a34a",
                                "#f97316"
                            ]
                        }
                    ]
                },
                options: {
                    responsive: true
                }
            }
        );

    const trends =
        data.trends || {};

    destroyChart("trendChart");
    analyticsCharts.trendChart =
        new Chart(
            document.getElementById(
                "trendChart"
            ),
            {
                type: "line",
                data: {
                    labels: trends.labels || [],
                    datasets: [
                        {
                            label: "Users",
                            data: trends.users || [],
                            borderColor: "#2563eb",
                            tension: 0.3
                        },
                        {
                            label: "Questions",
                            data: trends.questions || [],
                            borderColor: "#16a34a",
                            tension: 0.3
                        },
                        {
                            label: "Average Rating",
                            data: trends.average_rating || [],
                            borderColor: "#f97316",
                            tension: 0.3
                        },
                        {
                            label: "Feedback",
                            data: trends.feedback || [],
                            borderColor: "#7c3aed",
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            }
        );
}

function getCanvasContext(id) {
    const canvas =
        document.getElementById(id);

    if (!canvas) {
        return null;
    }

    canvas.width =
        canvas.clientWidth || 600;

    canvas.height =
        300;

    return canvas.getContext("2d");
}

function drawText(ctx, text, x, y, color = "#0f172a") {
    ctx.fillStyle = color;
    ctx.font = "13px Segoe UI, Arial";
    ctx.fillText(text, x, y);
}

function renderCanvasFallbackCharts(data) {
    const distribution =
        data.rating_distribution || {};

    drawBarChart(
        "ratingDistributionChart",
        ["1", "2", "3", "4", "5"],
        [1, 2, 3, 4, 5].map(
            star => distribution[String(star)] || 0
        ),
        "#2563eb"
    );

    drawBarChart(
        "questionMixChart",
        ["Policy", "Web", "Gaps"],
        [
            data.policy_questions || 0,
            data.web_questions || 0,
            data.knowledge_gaps || 0
        ],
        "#16a34a"
    );

    const trends =
        data.trends || {};

    drawLineChart(
        "trendChart",
        trends.labels || [],
        [
            {
                label: "Users",
                values: trends.users || [],
                color: "#2563eb"
            },
            {
                label: "Questions",
                values: trends.questions || [],
                color: "#16a34a"
            },
            {
                label: "Avg Rating",
                values: trends.average_rating || [],
                color: "#f97316"
            },
            {
                label: "Feedback",
                values: trends.feedback || [],
                color: "#7c3aed"
            }
        ]
    );
}

function drawBarChart(id, labels, values, color) {
    const ctx =
        getCanvasContext(id);

    if (!ctx) return;

    const width =
        ctx.canvas.width;

    const height =
        ctx.canvas.height;

    ctx.clearRect(0, 0, width, height);

    const maxValue =
        Math.max(1, ...values);

    const chartLeft = 36;
    const chartBottom = height - 36;
    const chartTop = 20;
    const chartWidth = width - 56;
    const barGap = 12;
    const barWidth =
        (chartWidth - barGap * (values.length - 1)) /
        values.length;

    ctx.strokeStyle = "#cbd5e1";
    ctx.beginPath();
    ctx.moveTo(chartLeft, chartTop);
    ctx.lineTo(chartLeft, chartBottom);
    ctx.lineTo(width - 16, chartBottom);
    ctx.stroke();

    values.forEach(
        (value, index) => {
            const barHeight =
                ((chartBottom - chartTop) * value) /
                maxValue;

            const x =
                chartLeft + index * (barWidth + barGap);

            const y =
                chartBottom - barHeight;

            ctx.fillStyle = color;
            ctx.fillRect(
                x,
                y,
                barWidth,
                barHeight
            );

            drawText(
                ctx,
                String(value),
                x + barWidth / 2 - 4,
                y - 6
            );

            drawText(
                ctx,
                labels[index],
                x,
                chartBottom + 20
            );
        }
    );
}

function drawLineChart(id, labels, datasets) {
    const ctx =
        getCanvasContext(id);

    if (!ctx) return;

    const width =
        ctx.canvas.width;

    const height =
        ctx.canvas.height;

    ctx.clearRect(0, 0, width, height);

    const allValues =
        datasets.flatMap(
            dataset => dataset.values
        );

    const maxValue =
        Math.max(1, ...allValues);

    const chartLeft = 42;
    const chartRight = width - 24;
    const chartTop = 24;
    const chartBottom = height - 48;

    ctx.strokeStyle = "#cbd5e1";
    ctx.beginPath();
    ctx.moveTo(chartLeft, chartTop);
    ctx.lineTo(chartLeft, chartBottom);
    ctx.lineTo(chartRight, chartBottom);
    ctx.stroke();

    datasets.forEach(
        dataset => {
            ctx.strokeStyle = dataset.color;
            ctx.lineWidth = 2;
            ctx.beginPath();

            dataset.values.forEach(
                (value, index) => {
                    const x =
                        labels.length <= 1
                            ? chartLeft
                            : chartLeft +
                              ((chartRight - chartLeft) * index) /
                              (labels.length - 1);

                    const y =
                        chartBottom -
                        ((chartBottom - chartTop) * value) /
                        maxValue;

                    if (index === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                }
            );

            ctx.stroke();
        }
    );

    datasets.forEach(
        (dataset, index) => {
            const x =
                chartLeft + index * 110;

            ctx.fillStyle = dataset.color;
            ctx.fillRect(x, height - 22, 12, 12);

            drawText(
                ctx,
                dataset.label,
                x + 18,
                height - 11
            );
        }
    );

    if (labels.length > 0) {
        drawText(
            ctx,
            labels[0],
            chartLeft,
            chartBottom + 20
        );

        drawText(
            ctx,
            labels[labels.length - 1],
            Math.max(chartLeft, chartRight - 90),
            chartBottom + 20
        );
    }
}

async function loadMonitoring() {
    const content =
        document.getElementById(
            "monitoring-content"
        );

    if (!content) return;

    const response = await fetch(
        `${API_URL}/monitoring`
    );

    const data = await response.json();

    const rows =
        data.slice(-25).reverse().map(
            item => `
                <tr>
                    <td>${escapeHtml(item.timestamp)}</td>
                    <td>${escapeHtml(item.question)}</td>
                    <td>${escapeHtml(item.route)}</td>
                    <td>${escapeHtml(item.confidence)}</td>
                    <td>${escapeHtml(item.verdict)}</td>
                </tr>
            `
        ).join("");

    content.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Question</th>
                    <th>Route</th>
                    <th>Confidence</th>
                    <th>Verdict</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>
    `;
}

async function loadFeedbackSummary() {
    const content =
        document.getElementById(
            "feedback-content"
        );

    if (!content) return;

    const response = await fetch(
        `${API_URL}/feedback/stats`
    );

    const data = await response.json();

    content.innerHTML = `
        <div class="metric-grid">
            <div class="metric-card">
                <span>Total Feedback</span>
                <strong>${data.total || 0}</strong>
            </div>
            <div class="metric-card">
                <span>Average Rating</span>
                <strong>${Number(data.average_rating || 0).toFixed(2)}</strong>
            </div>
        </div>
        <p class="muted">
            Feedback can be submitted directly below each answer in the chat.
        </p>
    `;
}

window.onload = function () {
    getUserId();
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

window.sendQuestion = sendQuestion;
window.confirmWebSearch = confirmWebSearch;
window.selectRating = selectRating;
window.submitFeedback = submitFeedback;
window.clearChat = clearChat;
window.toggleTheme = toggleTheme;
window.showSection = showSection;
window.openHistory = openHistory;
