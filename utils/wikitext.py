from wikitextparser import WikiText, Template


def title_equal(a: str, b: str) -> bool:
    if a is None and b is None:
        return True
    if (a is None) ^ (b is None):
        return False
    return a.strip().replace("_", " ").upper() == b.strip().replace("_", " ").upper()


def get_template_by_name(parsed: WikiText, target: str) -> list[Template]:
    result = []

    for t in parsed.templates:
        if title_equal(t.name, target):
            result.append(t)

    return result
