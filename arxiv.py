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

class Logger:
    log_s: str

    def __init__(self):
        self.log_s = ''
    
    def log(self, output: str):
        print(output)
        self.log_s += output + '\n'

def get_source_file_name(paper_id: str):
    return 'source/' + paper_id.replace('.', '')

def download_arxiv(logger: Logger, paper_id: str):
    source_file_name = get_source_file_name(paper_id)
    url = f'https://arxiv.org/e-print/{paper_id}'
    response = requests.get(url)
    if response.status_code == 404:
        logger.log(f'Error reading source: recieved 404 for {url}')
        return None
    if response.status_code != 200:
        raise Exception(f'Error downloading source code for paper {paper_id}\n{response.content.decode()}')
    logger.log('Found paper source code, parsing file')
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

def get_files_recursive(folder: str, files: List[str] = [], extension: str = '.tex') -> List[str]:
    files_copy = []
    for file in files:
        files_copy.append(file)
    for file in os.listdir(folder):
        if os.path.isdir(folder + '/' + file):
            for new_file in get_files_recursive(f'{folder}/{file}', [], extension):
                files_copy.append(new_file)
        if extension in file:
            files_copy.append(f'{folder}/{file}')
    return files_copy

def extract_citations_from_latex(logger: Logger) -> List[str]:
    citation_pattern = re.compile(r'\\cite.?\{(.*?)\}')
    citation_keys = set()
    latex_file_paths = get_files_recursive('tmp')
    logger.log(f'Found {len(latex_file_paths)} .tex files')
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

def get_references_for_file(logger: Logger, file_name: str, found_citations: List[str]) -> List[str] | str:
    references = []
    file_size_in_mb = os.stat(file_name).st_size / (1024 * 1024)
    logger.log(f'.bib file: {file_size_in_mb:.2f}MB')
    if file_size_in_mb > 10:
        return f'Large .bib file found size {file_size_in_mb:.2f}MB'
    with open(file_name, 'r', encoding='utf-8') as f:
        try:
            logger.log('Loading file into memory')
            file_contents = f.read()
            logger.log('Paring .bib file')
            library = bibtexparser.bparser.parse(file_contents)
            logger.log('.bib file parsed')
        except Exception as e:
            return f'Error parsing .bib file: {e}'
        logger.log(f'Found {len(library.entries)} entries in .bib file')
        found_ids = []
        index = 1
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
    logger.log(f'Done parsing .bib file, found {len(references)} references')
    return references

def get_references(paper_id: str) -> List[str] | str:
    paper_id = paper_id
    cleaned_id = paper_id.replace('.', '')
    source_file_name = f'source/{cleaned_id}'
    references_file_name = f'references/{cleaned_id}.json'
    logger = Logger()

    if not os.path.exists('source'):
        os.mkdir('source')

    if not os.path.exists('references'):
        os.mkdir('references')

    if os.path.exists(references_file_name):
        with open(references_file_name, 'r') as f:
            return json.load(f), logger.log_s
    
    if not os.path.exists(source_file_name):
        logger.log('Attempting to download source')
        res = download_arxiv(logger, paper_id)
        if res is None:
            err = 'Could not download arxiv archive'
            logger.log(err)
            return err, logger.log_s # Bail if not downloaded
    
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')
    os.mkdir('tmp')

    try:
        if not tarfile.is_tarfile(source_file_name): # Assuming it's a gzip file
            unzip(paper_id) # Unzip to tar file
        
        if not tarfile.is_tarfile(source_file_name):
            logger.log('Error reading source: unzipped data is not a tarball')
            os.rmdir('tmp')
            file_type = get_file_type(source_file_name)
            err = f'Downloaded archive is not the correct type (file type: {file_type})'
            logger.log(err)
            return err, logger.log_s # Bail if not tarfile
        
        with tarfile.open(source_file_name) as tar:
            tar.extractall(path='tmp', filter='data')
        
        logger.log('Extracting citations .tex files')
        citations = extract_citations_from_latex(logger)
        logger.log(f'Found {len(citations)} citations')
        references = []
        bib_files = get_files_recursive('tmp', [], '.bib')
        if len(bib_files) == 0:
            err = 'Could not find .bib file in source'
            logger.log(err)
            return err, logger.log_s
        logger.log('Found .bib file, loading file into memory')
        for bib_file in bib_files:
            references_data = get_references_for_file(logger, bib_file, citations)
            if type(references_data) == type(''):
                continue
            for reference in references_data:
                references.append(reference)

        logger.log(f'Found {len(references)} of {len(citations)} citations')
        
        reference_file_data = []
        for reference in references:
            reference_file_data.append(reference)
        with open(references_file_name, 'w') as f:
            json.dump(reference_file_data, f, indent=4)
    finally:
        shutil.rmtree('tmp')
    return references, logger.log_s

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