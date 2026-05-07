import re

def alloc(lines):
    return "  \n".join(lines)


def extract_amount(query: str):
    """
    Extract investment amount from natural language query.

    Supports:
    - 10000
    - 10k / 10 K
    - 5m
    - 10 thousand
    - ten thousand
    - twenty five thousand
    - 2 lakh
    - 2.5 lakh
    - 3 crores
    - 1 million
    - ₹10L
    - 50 grand
    """

    query = query.lower().replace(",", "").strip()

    # =====================================================
    # WORD → NUMBER MAP
    # =====================================================

    word_to_number = {

        # BASIC
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,

        # TEENS
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,

        # TENS
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,

        # MULTIPLIERS
        "hundred": 100,

        "thousand": 1000,
        "thousands": 1000,
        "k": 1000,
        "grand": 1000,

        "lakh": 100000,
        "lakhs": 100000,
        "lac": 100000,
        "lacs": 100000,
        "l": 100000,

        "million": 1000000,
        "millions": 1000000,
        "m": 1000000,

        "crore": 10000000,
        "crores": 10000000,
        "cr": 10000000,

        "billion": 1000000000,
        "billions": 1000000000,

        "trillion": 1000000000000,
        "trillions": 1000000000000
    }

    # =====================================================
    # CASE 2: SHORT FORMS
    # Examples:
    # 10k
    # 5m
    # 2cr
    # ₹10L
    # =====================================================

    short_forms = {
        "k": 1000,
        "m": 1000000,
        "l": 100000,
        "cr": 10000000
    }

    for suffix, multiplier in short_forms.items():

        match = re.search(
            rf"₹?\s*(\d+(?:\.\d+)?)\s*{suffix}\b",
            query
        )

        if match:
            return int(float(match.group(1)) * multiplier)

    # =====================================================
    # CASE 3: WORD MULTIPLIERS
    # Examples:
    # 10 lakh
    # 2.5 crore
    # 1 million
    # =====================================================

    multipliers = {
        "thousand": 1000,
        "lakh": 100000,
        "lac": 100000,
        "million": 1000000,
        "crore": 10000000,
        "billion": 1000000000,
        "trillion": 1000000000000
    }

    for word, multiplier in multipliers.items():

        match = re.search(
            rf"(\d+(?:\.\d+)?)\s*{word}s?\b",
            query
        )

        if match:
            return int(float(match.group(1)) * multiplier)

    # =====================================================
    # CASE 4: WORD NUMBERS
    # Examples:
    # ten thousand
    # twenty five thousand
    # two lakh
    # five crore
    # =====================================================

    words = query.split()

    current = 0
    total = 0

    for word in words:

        if word not in word_to_number:
            continue

        value = word_to_number[word]

        # Skip invalid placeholders
        if value is None:
            continue

        # MULTIPLIERS
        if value >= 100:

            if current == 0:
                current = 1

            current *= value

            # For large units finalize chunk
            if value >= 1000:
                total += current
                current = 0

        else:
            current += value

    total += current

    if total > 0:
        return total

    # =====================================================
    # CASE 5: GRAND
    # Example:
    # 50 grand
    # =====================================================

    match = re.search(r"(\d+(?:\.\d+)?)\s*grand", query)

    if match:
        return int(float(match.group(1)) * 1000)
    

    # =====================================================
    # CASE 1: PURE NUMBERS
    # Example: 10000
    # =====================================================

    match = re.search(r"\b\d{3,12}\b", query)

    if match:
        return int(match.group())

    return None


def extract_rate(query: str):
    """
    Extract expected return / interest rate from query.

    Supports:
    - 12%
    - 10 percent
    - 8 pct
    - 7.5 percent
    - double digit returns
    - single digit return
    """

    query = query.lower().replace(",", "").strip()

    # =====================================================
    # CASE 1: 12%
    # =====================================================

    match = re.search(r"(\d+(?:\.\d+)?)\s*%", query)

    if match:
        return float(match.group(1))

    # =====================================================
    # CASE 2: 12 percent / 12 pct
    # =====================================================

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(percent|pct)",
        query
    )

    if match:
        return float(match.group(1))

    # =====================================================
    # CASE 3: WORD-BASED RATES
    # =====================================================

    word_to_number = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "twenty": 20
    }

    for word, value in word_to_number.items():

        pattern = rf"\b{word}\s*(percent|pct)\b"

        if re.search(pattern, query):
            return float(value)

    # =====================================================
    # CASE 4: DOUBLE DIGIT / SINGLE DIGIT
    # =====================================================

    if "double digit" in query:
        return 12.0

    if "single digit" in query:
        return 8.0

    # =====================================================
    # CASE 5: RISK-BASED HEURISTICS
    # =====================================================

    aggressive_keywords = [
        "aggressive",
        "high return",
        "high growth"
    ]

    conservative_keywords = [
        "safe",
        "conservative",
        "low risk"
    ]

    moderate_keywords = [
        "balanced",
        "moderate",
        "medium risk"
    ]

    if any(k in query for k in aggressive_keywords):
        return 12.0

    if any(k in query for k in moderate_keywords):
        return 10.0

    if any(k in query for k in conservative_keywords):
        return 8.0

    return None


def extract_projection_duration(query):

    query = query.lower()

    patterns = [
        (r"(\d+)\s*year", 1),
        (r"(\d+)\s*yr", 1),
        (r"(\d+)\s*month", 1/12),
        (r"(\d+)\s*week", 1/52),
        (r"(\d+)\s*day", 1/365),
        (r"(\d+)\s*decade", 10)
    ]

    for pattern, multiplier in patterns:

        match = re.search(pattern, query)

        if match:

            value = int(match.group(1))

            return {
                "custom": True,
                "years": max(value * multiplier, 1)
            }

    # default projections
    return {
        "custom": False,
        "years": [10, 15]
    }


def extract_age(query: str):

    query = query.lower().replace("-", " ")

    word_to_number = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90
    }

    # =====================================================
    # CASE 1: Numeric age
    # =====================================================

    patterns = [
        r"i am (\d{1,3})",
        r"i'm (\d{1,3})",
        r"age is (\d{1,3})",
        r"aged (\d{1,3})",
        r"(\d{1,3}) years old",
        r"(\d{1,3}) yr old"
    ]

    for pattern in patterns:

        match = re.search(pattern, query)

        if match:

            age = int(match.group(1))

            if 1 <= age <= 120:
                return age

    # =====================================================
    # CASE 2: Word-based age
    # =====================================================

    words = query.split()

    for i in range(len(words)):

        current = words[i]

        if current not in word_to_number:
            continue

        value = word_to_number[current]

        # handle compound:
        # eighty nine
        if i + 1 < len(words):

            nxt = words[i + 1]

            if nxt in word_to_number and word_to_number[nxt] < 10:
                value += word_to_number[nxt]

        if 1 <= value <= 120:

            nearby_text = " ".join(words[max(0, i-2): i+4])

            if any(k in nearby_text for k in [
                "i am",
                "i'm",
                "age",
                "years old",
                "year old",
                "aged"
            ]):
                return value

    return None