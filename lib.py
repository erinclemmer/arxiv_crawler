from typing import List
def make_selection(max: int) -> int:
    selection = input('#: ')
    num = None
    try:
        num = int(selection)
    except:
        return None
    if num < 1 or num > max:
        return None
    return num

class Reference:
    def __init__(self):
        self.arxiv_id = None
        self.fetched = False
        self.bib_data = None

    def to_obj(self):
        obj = {
            "arxiv_id": self.arxiv_id,
            "fetched": self.fetched
        }
        for key in self.bib_data.keys():
            obj[key] = self.bib_data[key]
        return obj

class Paper:
    id: str
    title: str
    abstract: str
    references: List[Reference]
    cited_by: List[Reference]

    def __init__(self):
        self.title = None
        self.references = []
        self.cited_by = []