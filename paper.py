import os
import json
from typing import List

from lib import get_date_by_id
from reference import Reference
from arxiv import get_metadata, get_references

# TODO 
#    Implement look up in archiv search to double check if paper is available
#    Support other bibliography files such as '.bbl'
#    Support ability to force parsing large .bib files
class Paper:
    arxiv_id: str
    title: str
    abstract: str
    log: str
    references: List[Reference]
    reference_error: str | None
    cited_by: List[object]

    def __init__(self, arxiv_id: str = None):
        self.arxiv_id = arxiv_id
        self.title = None
        self.abstract = None
        self.reference_error = None
        self.date = None
        self.log = ''
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
                self.log = data["log"] if 'log' in data else ''
        else:
            metadata = get_metadata(self.arxiv_id)
            self.title = metadata["title"]
            self.abstract = metadata["abstract"]

        if os.path.exists(f'references/{clean_id}.json'):
            with open(f'references/{clean_id}.json', 'r') as f:
                for item in json.load(f):
                    self.references.append(Reference(item))
        else:
            references, log = get_references(self.arxiv_id)
            if type(references) == type(''):
                self.reference_error = references
                self.references = []
            for ref_data in references:
                self.references.append(Reference(ref_data))
            self.log = log
            with open(file_name, 'w') as f:
                o = self.to_obj()
                # Do not need to save reference data in paper file, it's saved in the references file
                o['references'] = []
                json.dump(o, f, indent=4)
    
    def reload(self) -> bool:
        clean_id = self.arxiv_id.replace('.', '')
        paper_file_name = f'papers/{clean_id}.json'
        if not os.path.exists(paper_file_name):
            return False
        os.remove(paper_file_name)
        ref_file_name = f'references/{clean_id}.json'
        if not os.path.exists(ref_file_name):
            return False
        os.remove(ref_file_name)
        self.date = get_date_by_id(self.arxiv_id)
        self.title = None
        self.abstract = None
        self.reference_error = None
        self.date = None
        self.log = ''
        self.references = []
        self.cited_by = []
        self.load()
        return True

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
            "log": self.log,
            "references_error": self.reference_error,
            "cited_by": self.cited_by
        }