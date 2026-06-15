POLICY_KEYWORDS = [

    "leave policy",
    "leave",

    "attendance policy",
    "attendance",

    "work from home",
    "wfh",

    "holiday policy",
    "holiday list",

    "notice period",

    "working hours",

    "employee benefits",
    "benefits",

    "promotion policy",

    "increment policy",

    "company policy",

    "payroll policy",

    "reimbursement",

    "travel policy",

    "code of conduct",

    "employee handbook",

    "hr policy"
]


def route_question(question: str):

    question = question.lower().strip()

    # Company-related phrases
    for keyword in POLICY_KEYWORDS:

        if keyword in question:
            return "POLICY"

    # Questions about external companies
    external_company_words = [

        "google",
        "microsoft",
        "amazon",
        "apple",
        "meta",
        "tesla",
        "openai",
        "facebook",
        "netflix"
    ]

    for company in external_company_words:

        if company in question:
            return "OUTSIDE_POLICY"

    return "OUTSIDE_POLICY"


if __name__ == "__main__":

    while True:

        question = input(
            "\nAsk Question (q to quit): "
        )

        if question.lower() == "q":
            break

        route = route_question(
            question
        )

        print("\nRoute Selected:")
        print(route)