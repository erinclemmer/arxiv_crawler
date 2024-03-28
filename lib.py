import re
import datetime

def make_selection(max: int) -> int:
    selection = input('#: ')
    num = None
    try:
        num = int(selection)
    except:
        return None
    if num < 1 or num > max:
        return None
    return num

def get_date_by_id(arxiv_id: str):
    yearMatcher = re.findall(r'(\d{2})\d{2}.\d{5}', arxiv_id)
    if len(yearMatcher) == 0:
        return None
    monthMatcher = re.findall(r'\d{2}(\d{2}).\d{5}', arxiv_id)
    if len(monthMatcher) == 0:
        return None
    try:
        date = datetime.date(int('20' + yearMatcher[0]), int(monthMatcher[0]), 1).isoformat()
    except Exception as e:
        print(e)
        return None
    return date