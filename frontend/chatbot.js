async function sendQuestion() {

    const questionBox =
        document.getElementById("question");

    const question =
        questionBox.value;

    if (!question) {
        return;
    }

    const chatBox =
        document.getElementById("chat-box");

    chatBox.innerHTML += `
        <div class="user">
            <b>You:</b> ${question}
        </div>
    `;

    questionBox.value = "";

    const response =
        await fetch(
            "http://127.0.0.1:8000/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    question: question,
                    search_web: false
                })
            }
        );

    const data =
        await response.json();

    if (
        data.type ===
        "confirmation"
    ) {

        const answer =
            confirm(
                data.message
            );

        if (answer) {

            const webResponse =
                await fetch(
                    "http://127.0.0.1:8000/ask",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            question: question,
                            search_web: true
                        })
                    }
                );

            const webData =
                await webResponse.json();

            chatBox.innerHTML += `
                <div class="bot">
                    <b>AI:</b>
                    ${JSON.stringify(webData)}
                </div>
            `;
        }

        return;
    }

    let citations = "";

    if (data.citations) {

        citations +=
            "<br><b>Sources:</b><br>";

        data.citations.forEach(c => {

            citations +=
                `[${c.id}] ${c.source}
                Page ${c.page}<br>`;
        });
    }

    chatBox.innerHTML += `
        <div class="bot">

            <b>AI:</b><br>

            ${data.answer}

            <br><br>

            <b>Confidence:</b>
            ${data.confidence}

            <br>

            <b>Verdict:</b>
            ${data.verdict}

            <br>

            ${citations}

        </div>
    `;

    chatBox.scrollTop =
        chatBox.scrollHeight;
}