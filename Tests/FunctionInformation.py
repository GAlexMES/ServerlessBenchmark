class FunctionInformation:
    path = None
    url = None
    detail = None

    def __init__(self, path, url, detail=None):
        self.path = path
        self.url = url
        self.detail = detail
