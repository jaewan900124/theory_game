import ast
import re


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def color_print(text, color):
    if color == "red":
        print(f"{Colors.RED}{text}{Colors.RESET}")
    elif color == "green":
        print(f"{Colors.GREEN}{text}{Colors.RESET}")
    elif color == "yellow":
        print(f"{Colors.YELLOW}{text}{Colors.RESET}")
    elif color == "blue":
        print(f"{Colors.BLUE}{text}{Colors.RESET}")


def parse_choice_combinations(response):
    candidates = []
    code_blocks = re.findall(r"```(?:python|py)?\s*\n?(.*?)```", response, re.DOTALL | re.IGNORECASE)
    candidates.extend(code_blocks)
    candidates.append(response)

    for candidate in candidates:
        for text in _extract_list_candidates(candidate):
            try:
                parsed = ast.literal_eval(text)
            except Exception:
                continue

            normalized = _normalize_choice_combinations(parsed)
            if normalized is not None:
                return normalized

        fallback = _parse_choice_pairs_from_text(candidate)
        if fallback is not None:
            return fallback

    raise ValueError("No valid choice combination list found")


def _extract_list_candidates(text):
    answer_match = re.search(r"answer\s*=", text, re.DOTALL)
    if answer_match:
        extracted = _extract_balanced_list(text, answer_match.end())
        if extracted is not None:
            yield extracted

    start = 0
    while True:
        extracted = _extract_balanced_list(text, start)
        if extracted is None:
            break
        yield extracted
        start = text.find(extracted, start) + len(extracted)


def _extract_balanced_list(text, start):
    list_start = text.find("[", start)
    if list_start == -1:
        return None

    depth = 0
    quote = None
    escaped = False
    for idx in range(list_start, len(text)):
        char = text[idx]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue

        if char in ("'", '"'):
            quote = char
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[list_start:idx + 1]

    return None


def _normalize_choice_combinations(parsed):
    if parsed == []:
        return []

    if _is_choice_pair(parsed):
        a, b = parsed
        return [(a.strip(), b.strip())]

    if not isinstance(parsed, list):
        return None

    normalized = []
    for choice in parsed:
        if not isinstance(choice, (tuple, list)) or len(choice) != 2:
            return None

        a, b = choice
        if not isinstance(a, str) or not isinstance(b, str):
            return None
        if not re.fullmatch(r"A[12]", a.strip()) or not re.fullmatch(r"B[12]", b.strip()):
            return None

        normalized.append((a.strip(), b.strip()))

    return normalized


def _is_choice_pair(value):
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        return False

    a, b = value
    return (
        isinstance(a, str)
        and isinstance(b, str)
        and re.fullmatch(r"A[12]", a.strip()) is not None
        and re.fullmatch(r"B[12]", b.strip()) is not None
    )


def _parse_choice_pairs_from_text(text):
    pairs = []

    tuple_pattern = re.compile(
        r"\(?\s*['\"]?(A[12])['\"]?\s*[,/]\s*['\"]?(B[12])['\"]?\s*\)?",
        re.IGNORECASE,
    )
    for a, b in tuple_pattern.findall(text):
        pair = (a.upper(), b.upper())
        if pair not in pairs:
            pairs.append(pair)

    if pairs:
        return pairs

    natural_pattern = re.compile(
        r"\b(A[12])\b.{0,80}?\b(B[12])\b",
        re.IGNORECASE | re.DOTALL,
    )
    for a, b in natural_pattern.findall(text):
        pair = (a.upper(), b.upper())
        if pair not in pairs:
            pairs.append(pair)

    if pairs:
        return pairs

    if re.search(
        r"\bempty\s+list\b|\banswer\s*=\s*\[\s*\]|\[\s*\]|\bno\s+pure\b|\bno\s+pure-strategy\b|\bno\s+pure\s+strategy\b|\bno\s+pure\s+nash\b|\bno\s+pure-strategy\s+nash\b|\bno\s+pure\s+strategy\s+nash\b",
        text,
        re.IGNORECASE,
    ):
        return []

    return None
