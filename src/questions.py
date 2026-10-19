QUESTIONS: list[dict[str, str | None]] = [ 
    {  # each record is a dictionary with four keys, explained on the first one
        "question": "What is the 2026-27 budget for rainwater harvesting subsidies?",  # the text sent to the pipeline
        "expected": "Rs 5.6 crore",  # the fact a correct answer must contain
        "page": "2",  # printed page_label where the fact lives
        "tests": "plain lookup, and the budget chunk that could be confused with the household subsidy",  # why this question is here
    },
    {
        "question": "How much subsidy does a below-poverty-line household get for rainwater harvesting?",
        "expected": "75 percent, up to Rs 60,000",
        "page": "4",
        "tests": "plain lookup, and a fact that semantic chunking put in its own small chunk",  # explains the point of this question
    },
    {
        "question": "How many days does a household have to file a claim after completing the structure?",
        "expected": "90 days",
        "page": "4",
        "tests": "similar-sounding numbers elsewhere (21 days, 30 days) that the model must not mix up",
    },
    {
        "question": "Who are the Jal Sahayaks and what do they do?",
        "expected": "trained, mostly unpaid village volunteers: daily rain gauge June to September, weekly handpump check, monthly field kit test, attend the Jal Chaupal",
        "page": "3",
        "tests": "coined term used by name",
    },
    {
        "question": "Who checks the handpumps in each village and how often?",
        "expected": "the Jal Sahayaks, weekly",
        "page": "3",
        "tests": "the same fact as above, asked without the coined term",
    },
    {
        "question": "When is the Jal Chaupal held each month?",
        "expected": "the second Saturday of each month",
        "page": "3",
        "tests": "coined term, a single narrow fact",
    },
    {
        "question": "How many red-zone villages are in Bhimgarh block?",
        "expected": "5",
        "page": "7",
        "tests": "the block table, where extraction lost the row structure",
    },
    {
        "question": "By how much did the Karanpur pilot reduce tanker dependence?",
        "expected": "31 percent",
        "page": "6",
        "tests": "lost context: the sentence says 'it', and its chunk may not name the pilot",
    },
    {
        "question": "Within how many hours must a red-zone village receive a water tanker?",
        "expected": "48 hours",
        "page": "5",
        "tests": "plain lookup in a dense page with many other numbers",
    },
    {
        "question": "What is the name of the District Magistrate of Nandpur?",
        "expected": None,  # None means the document has no answer
        "page": None,  # so there is no page either
        "tests": "unanswerable: a good system says it could not find this in the document",
    },
]

FACTS: dict[int, list[str]] = {  # question number -> phrases that must all appear in one retrieved chunk
    1: ["5.6 crore", "rainwater harvesting subsidies"],  # the budget line, not the household subsidy
    2: ["75 percent", "60,000"],  # the BPL rate and its cap together
    3: ["90 days"],  # the claim deadline
    4: ["rain gauge", "handpump"],  # two of the Jal Sahayak duties, so the chunk must hold the duties list
    5: ["handpump", "once a week"],  # the weekly check, worded as the handbook words it
    6: ["second saturday"],  # when the Jal Chaupal is held
    7: ["bhimgarh 29 5 480"],  # the table row in order, so it checks the row survived extraction
    8: ["31 percent", "karanpur"],  # the result and the pilot's name together, which tests the lost "it"
    9: ["48 hours"],  # the tanker deadline
}  # question 10 has no entry because nothing in the document answers it