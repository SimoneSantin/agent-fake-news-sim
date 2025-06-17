class News:
    def __init__(self, content_id, is_fake):
        self.content_id = content_id  
        self.is_flagged = False  
        self.reports = 0
        self.is_fake = is_fake
        self.sharers = set()
        self.credibility_score = 0.5
        self.is_banned = False