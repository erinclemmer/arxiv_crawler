import os
import re
import json
import shutil
import tarfile
import gzip
from typing import List

import requests
import bibtexparser

class Reference:
    def __init__(self):
        self.arxiv_id = None
        self.name = None

def get_source_file_name(paper_id: str):
    return 'source/' + paper_id.replace('.', '')

def download_arxiv(paper_id: str):
    source_file_name = get_source_file_name(paper_id)
    url = f'https://arxiv.org/e-print/{paper_id}'
    response = requests.get(url)
    if response.status_code == 404:
        print(f'Error reading source: recieved 404 for {url}')
        return None
    if response.status_code != 200:
        raise Exception(f'Error downloading source code for paper {paper_id}\n{response.content.decode()}')
    print('Found paper source code, parsing file')
    if not os.path.exists('source'):
        os.mkdir('source')
    with open(source_file_name, 'wb') as f:
        f.write(response.content)
    return True

def unzip(paper_id: str):
    source_file_name = get_source_file_name(paper_id)
    with gzip.open(source_file_name) as f:
        gzip_file = f.read()
        gzip.decompress(gzip_file)
        os.remove(source_file_name)
        with open(source_file_name, 'wb') as f:
            f.write(source_file_name)

def get_references_for_file(file_name: str):
    references = []
    with bibtexparser.parse_file(file_name) as library:
        ref = Reference()
        for entry in library.entries:
            fields = entry.fields_dict
            if 'title' in fields:
                ref.name = fields['title']
            if 'journal' in entry.fields_dict:
                journal = entry.fields_dict["journal"]
                match = re.findall('arxiv:\d{4}.\d{5}', journal)
                if len(match) != 0:
                    ref.arxiv_id = match[0].split('arxiv:')[1]
            
            # TODO if can't find id, look up on google scholar for arxiv

        references.append(ref)
    return references

def get_references(paper_id: str) -> List[str]:
    cleaned_id = paper_id.replace('.', '')
    source_file_name = f'source/{paper_id}'
    references_file_name = f'references/{cleaned_id}.json'

    if not os.path.exists('source'):
        os.mkdir('source')

    if not os.path.exists('references'):
        os.mkdir('references')

    if os.path.exists(references_file_name):
        with open(references_file_name, 'r') as f:
            return json.load(f)
    
    if not os.path.exists(source_file_name):
        print('Attempting to download source')
        res = download_arxiv(paper_id)
        if res is None:
            return None # Bail if not downloaded
    
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')
    os.mkdir('tmp')

    try:
        if not tarfile.is_tarfile(source_file_name):
            unzip(paper_id) # Unzip to tar file
        
        if not tarfile.is_tarfile(source_file_name):
            print('Error reading source: unzipped data is not a tarball')
            os.rmdir('tmp')
            return None # Bail if not tarfile
        
        with tarfile.open(source_file_name) as tar:
            tar.extractall(path='tmp', filter='data')
        
        references = []
        for file in os.listdir('tmp'):
            if '.bib' in file:
                for reference in get_references_for_file('tmp/' + file):
                    references.append(reference)

        with open(references_file_name, 'w') as f:
            json.dump(references, f, indent=4)    
    finally:
        shutil.rmtree('tmp')
    return references