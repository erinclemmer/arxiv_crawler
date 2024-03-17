import os
import json
from typing import List

from arxiv import get_references, get_metadata
from lib import Paper

class Project:
    def __init__(self, name: str):
        self.name = name
        self.papers: List[Paper] = []
        self.data = { }

        file_name = f'projects/{name}.json'
        if os.path.exists(file_name):
            with open(f'projects/{name}.json', 'r') as f:
                self.data = json.load(f)
                self.load(self.data)

    def load(self, data):
        self.papers = data["papers"]

    def save(self):
        self.data["papers"] = self.papers
        with open(f'projects/{self.name}.json', 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_paper(self, paper_id: str):
        clean_id = paper_id.replace('.', '')
        paper_data_file = f'papers/{clean_id}.json'
        paper_data = { }
        if os.path.exists(paper_data_file):
            with open(paper_data_file, 'r') as f:
                paper_data = json.load(f)
        else:
            title, abstract = get_metadata(paper_id)
            paper_data = {
                "id": paper_id,
                "title": title,
                "abstract": abstract
            }
            with open(paper_data_file, 'r') as f:
                json.dump(paper_data, f, indent=4)
        paper = Paper()
        paper.id = paper_data["id"]
        paper.title = paper_data["title"]
        paper.abstract = paper_data["abstract"]
        paper.references = get_references(paper_id)
        self.papers.append(paper)