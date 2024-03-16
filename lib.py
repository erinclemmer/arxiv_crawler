from typing import List

class Reference:
    def __init__(self):
        self.arxiv_id = None
        self.bib_data = None

    def to_obj(self):
        obj = {
            "arxiv_id": self.arxiv_id
        }
        for key in self.bib_data.keys():
            obj[key] = self.bib_data[key]
        return obj

class Paper:
    references: List[Reference]
    cited_by: List[Reference]

    def __init__(self):
        self.references = []
        self.cited_by = []