import os
from arxiv import get_references
from project import Project

from lib import make_selection

if not os.path.exists('projects'):
    os.mkdir('projects')

# TODO Look up cited by on google scholar
    # Create a graph of papers 

def main_menu():
    while True:
        idx = 0
        projects = os.listdir('projects')
        for project in projects:
            idx += 1 
            print(f'{idx}: {project}')

        print(f'{idx + 1}: New Project')
        num = make_selection(len(projects) + 1)
        if num is None:
            continue
        name = None
        if num == len(projects) + 1:
            name = input("Project name: ")
        else:
            name = projects[num - 1]
        
        project = Project(name)
        if num == len(projects) + 1:
            project.save()
    



    



get_references('2402.00898')