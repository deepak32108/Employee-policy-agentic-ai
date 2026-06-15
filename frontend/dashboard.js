async function loadAnalytics() {

    const response = await fetch(
        "http://127.0.0.1:8000/analytics"
    );

    const data = await response.json();

    document.getElementById(
        "total"
    ).innerText =
        data.total_questions || 0;

    document.getElementById(
        "policy"
    ).innerText =
        data.policy_questions || 0;

    document.getElementById(
        "web"
    ).innerText =
        data.web_questions || 0;

    document.getElementById(
        "gaps"
    ).innerText =
        data.knowledge_gaps || 0;

    document.getElementById(
        "confidence"
    ).innerText =
        Number(
            data.average_confidence || 0
        ).toFixed(2);

    const ctx = document
        .getElementById(
            "questionChart"
        );

    new Chart(ctx, {

        type: "bar",

        data: {

            labels: [
                "Policy Questions",
                "Web Questions",
                "Knowledge Gaps"
            ],

            datasets: [

                {
                    label: "Analytics",

                    data: [

                        data.policy_questions || 0,

                        data.web_questions || 0,

                        data.knowledge_gaps || 0
                    ]
                }
            ]
        },

        options: {

            responsive: true
        }
    });
}

loadAnalytics();