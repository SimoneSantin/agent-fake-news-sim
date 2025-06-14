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
            news = News(content_id=str(uuid.uuid4()), is_fake=True)
            for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                neighbor = self.model.agents_by_id[neighbor_id]
                if not neighbor.deleted:
                    news.sharers.add(self.unique_id)
                    self.news_registry[news.content_id] = news
                    self.model.update_credibility(news)
                    neighbor.receive_fake_news(self.unique_id, news)

        
        elif self.role in ["user", "influencer"]:
            if self.credulity == "gullible" and random.random() < 0.5:
                news = News(content_id=str(uuid.uuid4()), is_fake=True)
                for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                    neighbor = self.model.agents_by_id[neighbor_id]
                    if not neighbor.deleted:
                        news.sharers.add(self.unique_id)
                        self.news_registry[news.content_id] = news
                        self.model.update_credibility(news)
                        neighbor.receive_fake_news(self.unique_id, news)
            elif self.credulity == "non-believer" and random.random() < 0.2:
                news = News(content_id=str(uuid.uuid4()), is_fake=False)
                for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                    neighbor = self.model.agents_by_id[neighbor_id]
                    if not neighbor.deleted:
                        news.sharers.add(self.unique_id)
                        self.news_registry[news.content_id] = news
                        self.model.update_credibility(news)
                        neighbor.receive_fake_news(self.unique_id, news)
                       
                    
    def receive_fake_news(self, sender_id, news):
        sender = self.model.agents_by_id[sender_id]
        score = news.credibility_score

        # === NON-BELIEVER ===
        if self.credulity == "non-believer":
            if news.is_flagged:
                self.model.graph.remove_edge(self.unique_id, sender.unique_id)
                sender.reports_received += 1
                news.reports += 1
                self.news_registry[news.content_id] = news
                if news.reports >= 3 and not news.is_flagged:
                    news.is_flagged = True
                    print(f"News {news.content_id} è stata flaggata come sospetta")
                if sender.reports_received >= 5:
                    sender.deleted = True
                    print(sender.reports_received, "report received")
                    print(sender_id, "deleted")

            elif score >= 0.7 and random.random() < 0.6:
                news.sharers.add(self.unique_id)
                self.news_registry[news.content_id] = news
                self.model.update_credibility(news)
                for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                    neighbor = self.model.agents_by_id[neighbor_id]
                    if not neighbor.deleted and news.content_id not in neighbor.news_registry:
                        neighbor.receive_fake_news(self.unique_id, news)

            elif score < 0.3 and random.random() < 0.6:
                self.model.graph.remove_edge(self.unique_id, sender.unique_id)
                sender.reports_received += 1
                news.reports += 1
                self.news_registry[news.content_id] = news
                if news.reports >= 3 and not news.is_flagged:
                    news.is_flagged = True
                    print(f"News {news.content_id} è stata flaggata come sospetta")
                if sender.reports_received >= 5:
                    sender.deleted = True
                    print(sender.reports_received, "report received")
                    print(sender_id, "deleted")

            else:
                if random.random() < 0.3:
                    if news.is_fake:
                        print(f"Non-believer {score} ha condiviso una fake news")
                    news.sharers.add(self.unique_id)
                    self.news_registry[news.content_id] = news
                    self.model.update_credibility(news)
                    for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                        neighbor = self.model.agents_by_id[neighbor_id]
                        if not neighbor.deleted and news.content_id not in neighbor.news_registry:
                            neighbor.receive_fake_news(self.unique_id, news)

        # === SUSCEPTIBLE ===
        elif self.credulity == "susceptible":
            gullible_neighbors = [
                self.model.agents_by_id[n]
                for n in self.model.graph.neighbors(self.unique_id)
                if self.model.agents_by_id[n].credulity == "gullible"
            ]
            n_gullible = len(gullible_neighbors)

            if news.is_flagged and score < 0.3:
                if random.random() < 0.5:
                    self.credulity = "non-believer"
                 

            elif news.is_fake:
                prob = min(0.1 * n_gullible, 0.9)
                if random.random() < prob and news.content_id not in self.news_registry:
                    self.credulity = "gullible"
                    news.sharers.add(self.unique_id)
                    self.news_registry[news.content_id] = news
                    self.model.update_credibility(news)
                    for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                        neighbor = self.model.agents_by_id[neighbor_id]
                        if not neighbor.deleted and news.content_id not in neighbor.news_registry:
                            neighbor.receive_fake_news(self.unique_id, news)

        # === GULLIBLE ===
        elif self.credulity == "gullible" and news.content_id not in self.news_registry:
            share_prob = 1.0 if news.is_fake else 0.2  
            if random.random() < share_prob:
                if news.is_fake == False:
                     print(f"gullible {self.unique_id} ha condiviso una true news")
                news.sharers.add(self.unique_id)
                self.news_registry[news.content_id] = news
                self.model.update_credibility(news)
                for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                    neighbor = self.model.agents_by_id[neighbor_id]
                    if not neighbor.deleted and news.content_id not in neighbor.news_registry:
                        neighbor.receive_fake_news(self.unique_id, news)


