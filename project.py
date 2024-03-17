import os
import json
from typing import List

from paper import Paper

class Project:
    def __init__(self, name: str):
        self.name = name
        self.papers: List[Paper] = []
        self.data = { }

        file_name = f'projects/{name}.json'
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                data = json.load(f)
                self.load_papers(data["papers"])

    def load_papers(self, papers: List[str]):
        for arxiv_id in papers:
            self.papers.append(Paper(arxiv_id))

    def save(self):
        with open(f'projects/{self.name}.json', 'w') as f:
            json.dump(self.to_obj(), f, indent=4)

    def add_paper(self, paper_id: str):
        paper = Paper(paper_id)
        self.papers.append(paper)

    def to_obj(self):
        paper_ids = []
        for p in self.papers:
            paper_ids.append(p.arxiv_id)
        return {
            "name": self.name,
            "papers": paper_ids
        }

def get_projects() -> List[Project]:
    projects = []
    for p in os.listdir('projects'):
        projects.append(Project(p.replace('.json', '')))
    return projects
