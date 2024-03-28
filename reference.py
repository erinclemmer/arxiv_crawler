from lib import get_date_by_id

class Reference:
    def __init__(self, data: object):
        self.id = None
        self.title = None
        self.arxiv_id = None
        self.url = None
        self.author = None
        self.date = None
        self.data = data

        if 'ID' in data:
            self.id = data["ID"]
        if 'arxiv_id' in data:
            self.arxiv_id = data["arxiv_id"]
            self.date = get_date_by_id(self.arxiv_id)
        if 'url' in data:
            self.url = data["url"]
        if 'author' in data:
            self.author = data["author"]
        if 'title' in data:
            self.title = data["title"]

    def to_obj(self):
        return {
            "id": self.id,
            "title": self.title,
            "arxiv_id": self.arxiv_id,
            "date": self.date,
            "url": self.url,
            "author": self.author,
            "data": self.data
        }