from mesa import Model
import networkx as nx
import random

from numpy import size
from SocialAgent import SocialAgent
from mesa.agent import AgentSet

class FakeNewsModel(Model):
    def __init__(self, num_agents, num_influencers, num_bots):
        super().__init__() 
        self.all_news = {}
        self.step_num = 0
        self.num_agents = num_agents
        self.agent_set = AgentSet([])
        self.agents_by_id = {} #In modo da avere un accesso diretto agli agenti
        self.graph = nx.Graph() 
        num_non_bots = num_agents - num_bots
        num_gullible = int(num_non_bots * 0.20)
        num_susceptible = int(num_non_bots * 0.60)
        num_non_believer = num_non_bots - num_gullible - num_susceptible  
        credulities = (["gullible"] * num_gullible +
                    ["susceptible"] * num_susceptible +
                    ["non-believer"] * num_non_believer)
        random.shuffle(credulities)
        credulity_index = 0   

        for i in range(num_agents):
            node_id = i + 1
            if i < num_bots:
                role = "bot"
                custom_agents = SocialAgent(self, role)
                self.graph.add_node(node_id)
                self.graph.add_edges_from([(node_id, random.choice(list(self.graph.nodes))) for _ in range(3)])
            elif i < num_bots + num_influencers:
                role = "influencer"
                credulity = credulities[credulity_index]
                credulity_index += 1
                custom_agents = SocialAgent(self, role, credulity)
                self.graph.add_node(node_id)
                self.graph.add_edges_from([(node_id, random.choice(list(self.graph.nodes))) for _ in range(10)])
            else:
                role = "user"
                credulity = credulities[credulity_index]
                credulity_index += 1
                custom_agents = SocialAgent(self, role, credulity)
                self.graph.add_node(node_id)
                self.graph.add_edges_from([(node_id, random.choice(list(self.graph.nodes))) for _ in range(5)])

            self.agent_set.add(custom_agents)
            self.agents_by_id[custom_agents.unique_id] = custom_agents

                                
    def update_credibility(self, news):
        if not news.sharers:
            news.credibility_score = 0.5
            return

        gullible = 0
        susceptible = 0
        non_believer = 0
        bots = 0

        for agent_id in news.sharers:
            agent = self.agents_by_id[agent_id]
            if agent.role == "bot":
                bots += 1
            elif agent.credulity == "gullible":
                gullible += 1
            elif agent.credulity == "susceptible":
                susceptible += 1
            elif agent.credulity == "non-believer":
                non_believer += 1

        total = gullible + susceptible + non_believer + bots
        if total == 0:
            news.credibility_score = 0.5
            return

        score = (
            0.2 * gullible +
            0.4 * susceptible +
            0.8 * non_believer +
            0.0 * bots
        ) / total

        penalty = 0.05 * news.reports
        score = max(0.0, score - penalty)

        news.credibility_score = round(score, 3)



    def step(self):
        print("Step number:", self.step_num)
        self.step_num += 1
        self.agent_set.shuffle_do("step")


    def send_report(self, news, reporter, sender_id):
        sender = self.agents_by_id[sender_id]
        reporter.news_registry[news.content_id] = news

        if reporter.report_cooldown == 0:
            if news.is_fake:
                sender.reports_received += 1
                news.reports += 1
                if news.reports >= 3 and not news.is_flagged:
                    news.is_flagged = True

                if news.reports >= 5 and not news.is_banned:
                    news.is_banned = True

                if sender.reports_received >= 5:
                    sender.deleted = True

            else: 
                reporter.false_reports += 1
                if reporter.false_reports >= 5:
                    reporter.deleted = True
                sender.reports_received += 1
                news.reports += 1
                if news.reports >= 3 and not news.is_flagged:
                    news.is_flagged = True

                if news.reports >= 5 and not news.is_banned:
                    news.is_banned = True

                if sender.reports_received >= 5:
                    sender.deleted = True
                reporter.report_cooldown = 2
        
    
    def share_news(self, sharer_agent, news):
        news.sharers.add(sharer_agent.unique_id)
        sharer_agent.news_registry[news.content_id] = news
        self.update_credibility(news)
        news.total_shares += 1
        reports = sharer_agent.reports_received
        visible_ratio = max(0, 1.0 - 0.2 * reports) 
        neighbors = list(self.graph.neighbors(sharer_agent.unique_id))

        if visible_ratio == 1.0:
            target_neighbors = neighbors
        else:
            k = int(visible_ratio * len(neighbors))
            target_neighbors = random.sample(neighbors, k)

        for neighbor_id in target_neighbors:
            neighbor = self.agents_by_id[neighbor_id]
            if not neighbor.deleted and news.content_id not in neighbor.news_registry:
                neighbor.receive_fake_news(sharer_agent.unique_id, news)


                
