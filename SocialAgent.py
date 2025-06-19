from mesa import Agent
import random
from News import News
import uuid

class SocialAgent(Agent):
    def __init__(self, model, role, credulity=None):
        super().__init__(model)
        self.role = role
        self.credulity = credulity
        self.pending_shares = []
        self.news_registry = {}
        self.reports_received = 0
        self.deleted = False
        self.true_news_exposure = 0
        self.fake_news_exposure = 0
        self.false_reports = 0
        self.report_cooldown = 0

    def step(self):
        if self.deleted:
            return
        if self.report_cooldown > 0:
            self.report_cooldown -= 1
        if self.role == "bot":
            news = News(content_id=str(uuid.uuid4()), is_fake=True)
            self.model.all_news[news.content_id] = news
            if self.reports_received >= 3:
                news.is_flagged = True
            for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                neighbor = self.model.agents_by_id[neighbor_id]
                if not neighbor.deleted:
                    news.sharers.add(self.unique_id)
                    self.news_registry[news.content_id] = news
                    neighbor.receive_fake_news(self.unique_id, news)

        
        elif self.role in ["user", "influencer"]:
            if self.credulity == "gullible" and random.random() < 0.5:
                news = News(content_id=str(uuid.uuid4()), is_fake=True)
                self.model.all_news[news.content_id] = news
                if self.reports_received >= 3:
                    news.is_flagged = True
                for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                    neighbor = self.model.agents_by_id[neighbor_id]
                    if not neighbor.deleted:
                        news.sharers.add(self.unique_id)
                        self.news_registry[news.content_id] = news
                        neighbor.receive_fake_news(self.unique_id, news)
            elif self.credulity == "non-believer" and random.random() < 0.5:
                news = News(content_id=str(uuid.uuid4()), is_fake=False)
                self.model.all_news[news.content_id] = news
                if self.reports_received >= 3:
                     news.is_flagged = True
                for neighbor_id in list(self.model.graph.neighbors(self.unique_id)):
                    neighbor = self.model.agents_by_id[neighbor_id]
                    if not neighbor.deleted:
                        news.sharers.add(self.unique_id)
                        self.news_registry[news.content_id] = news
                        neighbor.receive_fake_news(self.unique_id, news)
                       

    def receive_fake_news(self, sender_id, news):
        if news.is_banned:
            return
        score = news.credibility_score
        # === NON-BELIEVER ===
        if self.credulity == "non-believer":
            if news.is_flagged:
                if score < 0.5:
                    self.model.send_report(news, self, sender_id)

            elif score >= 0.7:
                self.model.share_news(self, news)

            elif score <= 0.3:
                self.model.send_report(news, self, sender_id)

            elif random.random() < 0.2:
                self.model.share_news(self, news)

        # === SUSCEPTIBLE ===
        elif self.credulity == "susceptible":
            gullible_neighbors = [
                self.model.agents_by_id[n]
                for n in self.model.graph.neighbors(self.unique_id)
                if self.model.agents_by_id[n].credulity == "gullible"
            ]
            
            n_gullible = len(gullible_neighbors)

            nonBeliever_neighbors = [
                self.model.agents_by_id[n]
                for n in self.model.graph.neighbors(self.unique_id)
                if self.model.agents_by_id[n].credulity == "non-believer"
            ]
            n_nonBeliever = len(nonBeliever_neighbors)

            if news.is_fake:
                self.fake_news_exposure = self.fake_news_exposure + 1
            else:
                self.true_news_exposure = self.true_news_exposure + 1

            if news.is_flagged and score < 0.3:
                prob = min(0.1 * n_nonBeliever, 0.9)
                if random.random() < prob:
                    self.credulity = "non-believer"
                    self.model.send_report(news, self, sender_id)
                 
            else:
                exp_true = self.true_news_exposure
                exp_fake = self.fake_news_exposure

                if exp_true > exp_fake:
                    prob = min(0.05 * n_nonBeliever, 0.9)
                    if random.random() < prob:
                        self.model.share_news(self, news)
                        self.credulity = "non-believer"
                        self.news_registry[news.content_id] = news
                
                elif exp_fake > exp_true:
                    prob = min(0.05 * n_gullible, 0.9)
                    if random.random() < prob:
                        self.model.share_news(self, news)
                        self.credulity = "gullible"
                        self.news_registry[news.content_id] = news

        # === GULLIBLE ===
        elif self.credulity == "gullible" and news.content_id not in self.news_registry:
            if news.is_fake:
                self.model.share_news(self, news)
            else:  
                if random.random() < 0.2:
                    self.model.share_news(self, news)
                else:
                    self.model.send_report(news, self, sender_id)


