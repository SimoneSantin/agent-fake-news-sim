import random
from FakeNewsModel import FakeNewsModel
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

model = FakeNewsModel(num_agents=1000, num_influencers=100, num_bots=50)

color_map = {
    "non-believer": "green",
    "susceptible": "orange",
    "gullible": "red"
}

shape_map = {
    "user": "o",         # cerchio
    "influencer": "s",   # quadrato
    "bot": "^"           # triangolo
}

susceptible_count = []
gullible_count = []
non_believer_count = []


true_news_shares = []
fake_news_shares = []
pos = nx.spring_layout(model.graph, seed=42)

for step_num in range(70):
    print(f"Step {step_num}")
    if step_num % 3 == 0:
        gullible = [a for a in model.agent_set if a.credulity == "gullible"]
        susceptible = [a for a in model.agent_set if a.credulity == "susceptible"]
        non_believer = [a for a in model.agent_set if a.credulity == "non-believer"]

        def try_add_edge(a1, a2, prob=0.3):
            if a1.unique_id != a2.unique_id and not model.graph.has_edge(a1.unique_id, a2.unique_id):
                if random.random() < prob:
                    model.graph.add_edge(a1.unique_id, a2.unique_id)

        for _ in range(2):
            if len(gullible) >= 2:
                a1, a2 = random.sample(gullible, 2)
                try_add_edge(a1, a2)

        for _ in range(2):
            if len(susceptible) >= 2:
                a1, a2 = random.sample(susceptible, 2)
                try_add_edge(a1, a2)

        for _ in range(2):
            if gullible and susceptible:
                a1 = random.choice(gullible)
                a2 = random.choice(susceptible)
                try_add_edge(a1, a2)

        for _ in range(2):
            if susceptible and non_believer:
                a1 = random.choice(susceptible)
                a2 = random.choice(non_believer)
                try_add_edge(a1, a2)


        for _ in range(2):
            if gullible and non_believer:
                a1 = random.choice(gullible)
                a2 = random.choice(non_believer)
                try_add_edge(a1, a2)
                
    for agent in list(model.agent_set):
        if(agent.deleted):
            model.agent_set.remove(agent)
            del model.agents_by_id[agent.unique_id]
            model.graph.remove_node(agent.unique_id)
        agent.shared = False
    
    plt.figure(figsize=(10, 8))
   



    for role in shape_map:
        agents = [a for a in model.agents_by_id.values() if a.role == role]
        nodes = [a.unique_id for a in agents]


        if role == "bot":
            colors = ["gray"] * len(nodes)
        else:
            colors = [color_map[a.credulity] for a in agents]
        nx.draw_networkx_nodes(
            model.graph, pos, nodelist=nodes, node_color=colors,
            node_shape=shape_map[role], label=role, node_size=100
        )

    nx.draw_networkx_edges(model.graph, pos, alpha=0.2)
    plt.title(f"Step {step_num}")
    plt.axis("off")
    plt.tight_layout()
    legend_elements = []

    legend_elements.append(
        Line2D([0], [0], marker=shape_map["bot"], color='w', label='bot',
            markerfacecolor='gray', markersize=8, linestyle='None')
    )
    for role in ("user", "influencer"):
        for credulity in ("gullible", "susceptible", "non-believer"):
            color = color_map[credulity]
            legend_elements.append(
                Line2D([0], [0], marker=shape_map[role], color='w', 
                    label=f"{role} ({credulity})", markerfacecolor=color, 
                    markersize=8, linestyle='None')
            )

    plt.legend(handles=legend_elements, loc='upper right')
    plt.savefig(f"results/step_{step_num:02d}.png")
    plt.close()

    susceptible_count.append(sum(1 for a in model.agents_by_id.values() if a.credulity == "susceptible" and not a.deleted))
    gullible_count.append(sum(1 for a in model.agents_by_id.values() if a.credulity == "gullible" and not a.deleted))
    non_believer_count.append(sum(1 for a in model.agents_by_id.values() if a.credulity == "non-believer" and not a.deleted))

    model.step()

    true_shares = sum(news.total_shares for news in model.all_news.values() if not news.is_fake)
    fake_shares = sum(news.total_shares for news in model.all_news.values() if news.is_fake)

    true_news_shares.append(true_shares)
    fake_news_shares.append(fake_shares)

plt.figure(figsize=(8, 5))
plt.plot(susceptible_count, label="Susceptible", color="orange", linestyle='-', linewidth=2)
plt.plot(gullible_count, label="Gullible", color="red", linestyle='-', linewidth=2)
plt.plot(non_believer_count, label="Non-Believer", color="green", linestyle='-', linewidth=2)

plt.xlabel("Timesteps", fontsize=12)
plt.ylabel("Number of agents", fontsize=12)
plt.title("Agents' Credulity Over Time", fontsize=14)

plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig("results/agents_evolution_better.png")
plt.close()
  

plt.figure(figsize=(8, 5))
plt.plot(true_news_shares, label="True News Shares", color="blue", linestyle='-', linewidth=2, marker='o', markersize=4)
plt.plot(fake_news_shares, label="Fake News Shares", color="purple", linestyle='-', linewidth=2, marker='x', markersize=4)

plt.xlabel("Timesteps", fontsize=12)
plt.ylabel("Total Shares", fontsize=12)
plt.title("News Diffusion Over Time", fontsize=14)

plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig("results/news_diffusion_better.png")
plt.close()
