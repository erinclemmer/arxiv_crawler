import os
from arxiv import get_references

if not os.path.exists('projects'):
    os.mkdir('projects')

# TODO Look up cited by on google scholar
    # Create a graph of papers 

get_references('2402.00898')