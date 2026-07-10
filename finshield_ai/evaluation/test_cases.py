TEST_CASES = [

    {
        "question": "What is the waiting period?",
        "answer": "The waiting period is 30 days.",
        "contexts": [
            "The waiting period applicable under this policy is 30 days."
        ],
        "ground_truth": "The waiting period is 30 days."
    },

    {
        "question": "What is the deductible?",
        "answer": "The deductible is ₹5,000.",
        "contexts": [
            "Each claim is subject to a deductible of ₹5,000."
        ],
        "ground_truth": "The deductible is ₹5,000."
    },

    {
        "question": "What is the sum insured?",
        "answer": "The sum insured is ₹10,00,000.",
        "contexts": [
            "The maximum liability of the insurer under this policy is ₹10,00,000."
        ],
        "ground_truth": "The sum insured is ₹10,00,000."
    },

    {
        "question": "Does this policy cover fire damage?",
        "answer": "Yes, fire damage is covered.",
        "contexts": [
            "The policy covers loss or damage caused by fire, lightning and explosion."
        ],
        "ground_truth": "The policy covers fire damage."
    },

    {
        "question": "Is flood damage covered?",
        "answer": "Yes, flood damage is covered.",
        "contexts": [
            "Loss caused by flood, inundation and storm is covered."
        ],
        "ground_truth": "Flood damage is covered."
    },

    {
        "question": "Are earthquake damages covered?",
        "answer": "Yes, earthquake damage is covered under the policy.",
        "contexts": [
            "Earthquake (Fire & Shock) is covered under this policy."
        ],
        "ground_truth": "Earthquake damage is covered."
    },

    {
        "question": "What are the major exclusions?",
        "answer": "Wear and tear, war, nuclear risks and intentional damage are excluded.",
        "contexts": [
            "The policy excludes wear and tear, war, nuclear risks and intentional acts."
        ],
        "ground_truth": "Wear and tear, war, nuclear risks and intentional damage are excluded."
    },

    {
        "question": "Does the policy cover theft?",
        "answer": "Yes, theft is covered.",
        "contexts": [
            "Loss arising due to burglary or theft is covered."
        ],
        "ground_truth": "The policy covers theft."
    },

    {
        "question": "How can I file a claim?",
        "answer": "Notify the insurer immediately and submit the required documents.",
        "contexts": [
            "The insured should intimate the insurer immediately and submit claim documents."
        ],
        "ground_truth": "Claims should be reported immediately with supporting documents."
    },

    {
        "question": "What documents are required for claim settlement?",
        "answer": "Claim form, policy copy, identity proof and supporting documents are required.",
        "contexts": [
            "Documents required include claim form, policy schedule, ID proof and supporting evidence."
        ],
        "ground_truth": "Claim form, policy copy, identity proof and supporting documents are required."
    },

    {
        "question": "Does this policy offer cashless claims?",
        "answer": "Yes, cashless claims are available at network hospitals or garages.",
        "contexts": [
            "Cashless facility is available at authorized network providers."
        ],
        "ground_truth": "Cashless claims are available."
    },

    {
        "question": "What is the policy tenure?",
        "answer": "The policy tenure is one year.",
        "contexts": [
            "The policy shall remain valid for a period of one year."
        ],
        "ground_truth": "The policy tenure is one year."
    },

    {
        "question": "Who is eligible for this policy?",
        "answer": "Individuals meeting the eligibility criteria can purchase this policy.",
        "contexts": [
            "This policy is available to eligible individuals aged 18 years and above."
        ],
        "ground_truth": "Eligible individuals aged 18 years and above can purchase this policy."
    },

    {
        "question": "Can the policy be renewed?",
        "answer": "Yes, the policy can be renewed before expiry.",
        "contexts": [
            "The policy is renewable subject to payment of renewal premium."
        ],
        "ground_truth": "The policy can be renewed."
    },

    {
        "question": "Does the policy provide roadside assistance?",
        "answer": "Yes, 24×7 roadside assistance is available.",
        "contexts": [
            "The policy provides 24×7 roadside assistance."
        ],
        "ground_truth": "The policy provides 24×7 roadside assistance."
    }

]