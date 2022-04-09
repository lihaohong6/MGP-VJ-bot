from wikitextparser import WikiText, Template


def title_equal(a: str, b: str) -> bool:
    return a.strip().replace("_", " ").upper() == b.strip().replace("_", " ").upper()


def get_template_by_name(parsed: WikiText, target: str) -> list[Template]:
    result = []

    def get_recursive(wikitext: WikiText):
        for t in wikitext.templates:
            if title_equal(t.name, target):
                result.append(t)
                continue
            get_recursive(t)

    get_recursive(parsed)
    return result
