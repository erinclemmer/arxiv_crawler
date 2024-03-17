import os
import json
from typing import List

from arxiv import get_metadata, get_references

class Paper:
    arxiv_id: str
    title: str
    abstract: str
    references: List[object]
    cited_by: List[object]

    def __init__(self, arxiv_id: str = None):
        self.arxiv_id = arxiv_id
        self.title = None
        self.abstract = None
        self.references = []
        self.cited_by = []

        if self.arxiv_id is not None:
            self.load()

    def load(self):
        clean_id = self.arxiv_id.replace('.', '')
        file_name = f'papers/{clean_id}.json'
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                data = json.load(f)
                self.title = data["title"]
                self.abstract = data["abstract"]
            if os.path.exists(f'references/{clean_id}.json'):
                with open(f'references/{clean_id}.json', 'r') as f:
                    self.references = json.load(f)
            return

        metadata = get_metadata(self.arxiv_id)
        self.title = metadata["title"]
        self.abstract = metadata["abstract"]

        for ref_data in get_references(self.arxiv_id):
            self.references.append(ref_data)
        
        with open(file_name, 'r') as f:
            json.dump(self.to_obj(), f, indent=4)

    def to_obj(self):
        return {
            "title": self.title,
            "abstract": self.abstract,
            "references": self.references,
            "cited_by": self.cited_by
        }