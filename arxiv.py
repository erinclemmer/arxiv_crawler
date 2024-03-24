import os
import re
import json
import magic
import shutil
import tarfile
import gzip
from typing import List

from bs4 import BeautifulSoup
import requests
import bibtexparser

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

def get_file_type(file_name: str):
    return magic.from_file(file_name)

def get_tex_files_recursive(folder: str, files: List[str] = []) -> List[str]:
    files_copy = []
    for file in files:
        files_copy.append(file)
    for file in os.listdir(folder):
        if os.path.isdir(folder + '/' + file):
            tex_files = get_tex_files_recursive(f'{folder}/{file}')
            for new_file in tex_files:
                files_copy.append(new_file)
        if '.tex' in file:
            files_copy.append(f'{folder}/{file}')
    return files_copy

def extract_citations_from_latex() -> List[str]:
    citation_pattern = re.compile(r'\\cite.?\{(.*?)\}')
    citation_keys = set()
    latex_file_paths = get_tex_files_recursive('tmp')
    print(f'Found {len(latex_file_paths)} .tex files')
    for latex_file_path in latex_file_paths:
        with open(latex_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            matches = citation_pattern.findall(content)
            for match in matches:
                # Split in case of multiple citations within a single \cite{}
                keys: List[str] = match.split(',')
                for key in keys:
                    citation_keys.add(key.strip())
    return citation_keys

def get_references_for_file(file_name: str, found_citations: List[str]) -> List[str] | str:
    references = []
    with open(file_name, 'r', encoding='utf-8') as f:
        try:
            print('Loading file into memory')
            file_contents = f.read()
            print('Paring .bib file')
            library = bibtexparser.bparser.parse(file_contents)
            print('.bib file parsed')
        except Exception as e:
            return f'Error parsing .bib file: {e}'
        print(f'Found {len(library.entries)} entries in .bib file')
        found_ids = []
        index = 0
        for entry in library.entries:
            if entry["ID"] not in found_citations:
                continue
            if entry["ID"] in found_ids:
                continue
            entry["index"] = index
            index += 1
            found_ids.append(entry["ID"])
            if 'journal' in entry:
                journal: str = entry["journal"]
                match = re.findall(r'arxiv:\d{4}.\d{5}', journal.lower())
                if len(match) != 0:
                    entry["arxiv_id"] = match[0].split('arxiv:')[1]
            if 'doi' in entry:
                match = re.findall(r'arxiv.\d{4}.\d{5}', entry["doi"].lower())
                if len(match) != 0:
                    entry["arxiv_id"] = match[0].split('arxiv.')[1]
            if 'eprint' in entry:
                match = re.findall(r'^\d{4}.\d{5}$', entry["eprint"].lower())
                if len(match) != 0:
                    entry["arxiv_id"] = match[0]
            references.append(entry)
    print(f'Done parsing .bib file, found {len(references)} references')
    return references

def get_references(paper_id: str) -> List[str] | str:
    paper_id = paper_id
    cleaned_id = paper_id.replace('.', '')
    source_file_name = f'source/{cleaned_id}'
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
            return 'Could not download arxiv archive' # Bail if not downloaded
    
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')
    os.mkdir('tmp')

    try:
        if not tarfile.is_tarfile(source_file_name): # Assuming it's a gzip file
            unzip(paper_id) # Unzip to tar file
        
        if not tarfile.is_tarfile(source_file_name):
            print('Error reading source: unzipped data is not a tarball')
            os.rmdir('tmp')
            file_type = get_file_type(source_file_name)
            return f'Downloaded archive is not the correct type (file type: {file_type})' # Bail if not tarfile
        
        with tarfile.open(source_file_name) as tar:
            tar.extractall(path='tmp', filter='data')
        
        print('Extracting citations .tex files')
        citations = extract_citations_from_latex()
        print(f'Found {len(citations)} citations')
        references = []
        found_file = False
        for file in os.listdir('tmp'):
            if '.bib' in file:
                print('Found .bib file, loading file into memory')
                found_file = True
                references_data = get_references_for_file('tmp/' + file, citations)
                if type(references_data) == type(''):
                    return references_data
                for reference in references_data:
                    references.append(reference)

        if not found_file:
            return 'Could not find .bib file in source'
        reference_file_data = []
        for reference in references:
            reference_file_data.append(reference)
        with open(references_file_name, 'w') as f:
            json.dump(reference_file_data, f, indent=4)
    finally:
        shutil.rmtree('tmp')
    return references

def get_metadata(paper_id: str):
    clean_id = paper_id.replace('.', '')
    if os.path.exists(f'papers/{clean_id}.json'):
        with open(f'papers/{clean_id}.json', 'r') as f:
            return json.load(f)
    abs_url = f'https://arxiv.org/abs/{paper_id}'
    response = requests.get(abs_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    abstract_elem = soup.find('blockquote', {'class': 'abstract'})
    abstract = abstract_elem.text if abstract_elem is not None else ""

    if not os.path.exists('papers'):
        os.mkdir('papers')
    obj = {
        "id": paper_id,
        "title": soup.title.string,
        "abstract": abstract
    }
    with open(f'papers/{clean_id}.json', 'w') as f:
        json.dump(obj, f)
    return obj