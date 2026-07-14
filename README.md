# Fake News Diffusion: An Agent-Based Social Network Simulation

An agent-based simulation designed to explore how fake news spreads through a dynamic social network and how individual behaviour, social influence and moderation mechanisms affect information diffusion.

The model represents a social platform as a graph populated by autonomous users, influencers and bots. Each agent independently decides whether to create, share, ignore or report content according to its role, behavioural profile, previous exposure to information and surrounding social connections.

## Overview

Online misinformation is influenced not only by the characteristics of individual users, but also by network structure, repeated exposure, social influence and platform moderation.

This project models these interactions through an agent-based approach. Rather than predicting whether a specific article is true or false, the simulation focuses on the collective behaviour that emerges when agents with different characteristics interact over time.

The model investigates questions such as:

* How do bots and highly connected influencers affect information diffusion?
* How does repeated exposure influence user behaviour?
* Can interactions with sceptical users reduce susceptibility to misinformation?
* How do reporting and moderation mechanisms affect the spread of fake news?
* How does an evolving social network influence the final outcome?

## Agent Types

The simulation includes three main social roles.

### Users

Standard members of the social network. Their decisions depend on their behavioural profile, previous exposure and neighbouring agents.

### Influencers

Highly connected agents with a larger number of initial social connections. Their network position allows the content they share to potentially reach a wider audience.

### Bots

Automated accounts designed to generate and spread fake news. Bots contribute to the amplification of misinformation across the network.

## Behavioural Profiles

Human agents are assigned one of three behavioural profiles.

### Gullible

Agents with a high tendency to believe and redistribute misleading information.

### Susceptible

Agents whose behaviour can change according to repeated exposure and social influence. Depending on the information they receive and the characteristics of neighbouring users, they may become more critical or more vulnerable to misinformation.

### Non-believer

More sceptical agents that evaluate content credibility more critically and are more likely to report suspicious information.

## News Model

Each news item contains information about:

* Whether the content is true or fake
* Its current credibility score
* The users who shared it
* The total number of shares
* The number of reports received
* Whether the content has been flagged
* Whether the content has been removed

The credibility score changes according to the profiles of the agents sharing the content and the reports received during the simulation.

## Moderation System

The model includes several moderation mechanisms:

* User reporting
* Content flagging
* Content removal
* Reduced visibility for repeatedly reported accounts
* Temporary reporting restrictions
* Account deletion
* Penalties for repeated false reports

These mechanisms make moderation part of the simulation rather than treating content removal as an immediate or error-free process.

## Dynamic Social Network

The social environment is represented as a graph using NetworkX.

Connections between agents can evolve during the simulation, allowing new relationships to emerge between users with similar or different behavioural profiles.

The network structure influences how quickly information spreads and which agents are exposed to each piece of content.

## Visualizations

The simulation generates:

* Social network snapshots during different timesteps
* Agent population evolution over time
* True news diffusion
* Fake news diffusion
* Changes in behavioural profiles

Generated figures are stored in the `results` directory.

## Technologies

* Python
* Mesa
* NetworkX
* Matplotlib
* NumPy

## Project Structure

```text
agent-fake-news-sim/
│
├── FakeNewsModel.py
│   Main simulation model, network management and moderation logic
│
├── SocialAgent.py
│   Agent behaviour, content generation, sharing and reporting rules
│
├── News.py
│   Representation of individual news items
│
├── main.py
│   Simulation execution, data collection and visualization
│
├── results/
│   Generated network snapshots and plots
│
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/SimoneSantin/agent-fake-news-sim.git
cd agent-fake-news-sim
```

Install the required dependencies:

```bash
pip install mesa networkx matplotlib numpy
```

## Running the Simulation

Run the main script:

```bash
python main.py
```

The simulation executes multiple timesteps and generates network snapshots and analytical plots inside the `results` directory.

## Configuration

The default simulation parameters can be modified in `main.py`:

```python
model = FakeNewsModel(
    num_agents=100,
    num_influencers=10,
    num_bots=5
)
```

The number of simulation steps can also be changed:

```python
for step_num in range(100):
```

These parameters can be adjusted to analyse networks with different population sizes and proportions of users, influencers and bots.

## Purpose

This project was developed to explore misinformation as a complex systems problem.

It demonstrates how large-scale information diffusion patterns can emerge from local interactions between autonomous agents with different levels of influence, credibility and susceptibility.

The simulation is intended as an educational and experimental model rather than an accurate representation or prediction of real social media behaviour.

## Author

Simone Santin
