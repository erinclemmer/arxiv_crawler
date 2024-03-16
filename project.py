import re
import os
import json
from time import sleep
from typing import List

from arxiv import get_references, get_metadata
from lib import make_selection, Paper

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

    def view_references(self, paper: Paper):
        print(f"""
#####################
References for {paper.title}
1. Back to Paper
""")
        

    def view_paper(self, paper_id: str):
        paper = None
        for p in self.papers:
            if p.id == paper_id:
                paper = p
                break
        
        print(f"""
######################
Paper: {paper.title} ({paper.id})
{paper.abstract}

1. Back to Project
2. View References
3. View Cited By
""")
        num = make_selection(3)
        if num == 1:
            return
        if num == 2:
            self.view_references(paper_id)

    def show_action_menu(self):
        while True:
            print(f"""
    ###########################################
    Project: {self.name}
    1. Back to Project List
    2. Add paper id
    """)
            idx = 2
            for paper in self.papers:
                idx += 1
                print(f'{idx}. {paper.title}')

            num = make_selection(len(self.papers) + 2)
            if num is None:
                print('Incorrect selection')
                sleep(1)
                continue
            if num == 1:
                return
            if num == 2:
                paper_id = input('Paper ID: ')
                match = re.findall(r'\d{4}.\d{5}', paper_id)
                if len(match) == 0:
                    print(f'Incorrect paper id')
                    sleep(1)
                    continue
                self.add_paper(paper_id)
            