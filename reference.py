class Reference:
    def __init__(self, data: object):
        self.title = None
        self.arxiv_id = None
        self.url = None
        self.author = None
        self.data = data

        if 'arxiv_id' in data:
            self.arxiv_id = data["arxiv_id"]
        if 'url' in data:
            self.url = data["url"]
        if 'author' in data:
            self.author = data["author"]
        if 'title' in data:
            self.title = data["title"]