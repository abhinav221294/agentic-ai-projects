from difflib import get_close_matches

def normalize_term(word, choices, cutoff=0.7):
    matches = get_close_matches(word, choices, n=1, cutoff=cutoff)
    return matches[0] if matches else None