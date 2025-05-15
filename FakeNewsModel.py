from mesa import Model
import networkx as nx
import random

from numpy import size
from SocialAgent import SocialAgent
from mesa.agent import AgentSet

class FakeNewsModel(Model):
    def __init__(self, num_agents, num_influencers, num_bots):
        super().__init__() 
        self.delayed_news = {}
        self.step_num = 0
        self.num_agents = num_agents
        self.agent_set = AgentSet([])
        self.agents_by_id = {} #In modo da avere un accesso diretto agli agenti
        self.graph = nx.Graph() 
        num_non_bots = num_agents - num_bots
        num_gullible = int(num_non_bots * 0.15)
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
                self.graph.add_edges_from([(node_id, random.choice(list(self.graph.nodes))) for _ in range(3)])

            self.agent_set.add(custom_agents)
            self.agents_by_id[custom_agents.unique_id] = custom_agents




    def step(self):
        print("Step number:", self.step_num)
        self.step_num += 1
        self.agent_set.shuffle_do("step")
