from mesa import Agent
import random
from News import News
import uuid

class SocialAgent(Agent):
    def __init__(self, model, role, credulity=None):
        super().__init__(model)
        self.role = role
        self.credulity = credulity
        self.news_registry = {}
        self.reports_received = 0
        self.deleted = False

    def step(self):
        if self.deleted:
            return
        if self.role == "bot":
            news = News(content_id=str(uuid.uuid4()))
            for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                neighbor = self.model.agents_by_id[neighbor_id]
                if not neighbor.deleted:
                    self.news_registry[news.content_id] = news
                    neighbor.receive_fake_news(self.unique_id, news)

        
        elif self.role in ["user", "influencer"]:
            if self.credulity == "gullible":
                news = News(content_id=str(uuid.uuid4()))
                for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                    neighbor = self.model.agents_by_id[neighbor_id]
                    if not neighbor.deleted:
                        self.news_registry[news.content_id] = news
                        neighbor.receive_fake_news(self.unique_id, news)
                       
                    
    def receive_fake_news(self, sender_id, news):
        release_step = self.model.delayed_news.get(news.content_id, 0)
        if self.model.step_num >= release_step:
            if self.credulity == "non-believer":
                sender = self.model.agents_by_id[sender_id]
                if random.random() < 0.2: 
                        print(f"Non-believer {self.unique_id} non crede a {sender.unique_id} per news {news.content_id}")
                        self.model.graph.remove_edge(self.unique_id, sender.unique_id)
                        sender = self.model.agents_by_id[sender_id]
                        sender.reports_received += 1
                        news.reports += 1
                        if news.reports >= 2 and not news.is_flagged:
                            news.is_flagged = True
                            self.model.delayed_news[news.content_id] = self.model.step_num + 2
                            print(f"News {news.content_id} è stata flaggata come sospetta")
                        self.news_registry[news.content_id] = news
                        if sender.reports_received >= 3:
                            sender.deleted = True
                            print(sender.reports_received, "report received")
                            print(sender_id, "deleted")

            elif self.credulity == "susceptible":
                gullible_neighbors = [
                    self.model.agents_by_id[n]
                    for n in self.model.graph.neighbors(self.unique_id)
                    if self.model.agents_by_id[n].credulity == "gullible"
                ]
                n_gullible = len(gullible_neighbors)
                if news.is_flagged:
                    if random.random() < 0.3:
                        self.credulity = "non-believer"
                        print(f"{self.unique_id} è diventato non-believer per notizia flaggata {news.content_id}")
                else:
                    prob = min(0.1 * n_gullible, 0.9)
                    if random.random() < prob and news.content_id not in self.news_registry:
                        self.credulity = "gullible"
                        for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                            neighbor = self.model.agents_by_id[neighbor_id]
                            if not neighbor.deleted:
                                self.news_registry[news.content_id] = news
                                neighbor.receive_fake_news(self.unique_id, news)
                    

            elif self.credulity == "gullible" and news.content_id not in self.news_registry:
                if random.random() < 0.5: 
                    for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                        neighbor = self.model.agents_by_id[neighbor_id]
                        if not neighbor.deleted:
                            self.news_registry[news.content_id] = news
                            neighbor.receive_fake_news(self.unique_id, news)
                            


