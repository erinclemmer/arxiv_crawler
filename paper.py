import os
import json
from typing import List

from lib import get_date_by_id
from reference import Reference
from arxiv import get_metadata, get_references

class Paper:
    arxiv_id: str
    title: str
    abstract: str
    references: List[Reference]
    reference_error: str | None
    cited_by: List[object]

    def __init__(self, arxiv_id: str = None):
        self.arxiv_id = arxiv_id
        self.title = None
        self.abstract = None
        self.reference_error = None
        self.date = None
        self.references = []
        self.cited_by = []

        if self.arxiv_id is not None:
            self.date = get_date_by_id(arxiv_id)
            self.load()

    def load(self):
        clean_id = self.arxiv_id.replace('.', '')
        file_name = f'papers/{clean_id}.json'
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                data = json.load(f)
                self.title = data["title"]
                self.abstract = data["abstract"]
        else:
            metadata = get_metadata(self.arxiv_id)
            self.title = metadata["title"]
            self.abstract = metadata["abstract"]
            with open(file_name, 'w') as f:
                json.dump(self.to_obj(), f, indent=4)

        if os.path.exists(f'references/{clean_id}.json'):
            with open(f'references/{clean_id}.json', 'r') as f:
                for item in json.load(f):
                    self.references.append(Reference(item))
        else:
            references = get_references(self.arxiv_id)
            if type(references) == type(''):
                self.reference_error = references
                self.references = []
            for ref_data in references:
                self.references.append(Reference(ref_data))
        
    def to_obj(self):
        refs = []
        for ref in self.references:
            refs.append(ref.to_obj())
        return {
            "arxiv_id": self.arxiv_id,
            "clean_id": self.arxiv_id.replace('.', ''),
            "date": self.date,
            "title": self.title,
            "abstract": self.abstract,
            "references": refs,
            "references_error": self.reference_error,
            "cited_by": self.cited_by
        }