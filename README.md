## Simulation of simple queuing models

Basic queue models are simulated to analyze the effects of model parameters,
e.g. arrival and service rates. Different models for handling requests are defined and implemented
in Python using an event based simulation package **SimPy**.

Assumptions:
- servers satisfy requests sequentially, one at a time in all cases
- client arrivals in queue are served in FCFS fashion
- client arrival and service rates follow a Poisson process with arrival rate **λ** and service rate **μ**, with values of all μ being same (μ1, μ2, . . ., μn = μ)
- arrivals are split in different waiting lines randomly (for models with independent servers)
- servers have limited buffer capacity to hold **B** pending requests
- requests are discarded when there is no more buffer space


### Part 1: [Comparing queue models](/compare-queue-models.py)

The queuing systems presented below are described in Python to perform simulation analysis to study the effect of model parameters (**λ, μ, B**) on the system behaviour and performance. The performance of a system is measured by considering attributes like, **response time per request E(T)** and **loss rate L**, which is the number of requests rejected due to lack of buffer space.

<img width="620" alt="image" src="https://user-images.githubusercontent.com/25234772/220382305-8a5f7d08-3b5f-49c0-97f9-19c386976b61.png">

In the Python code, each of the above queueing configuration is abbreviated as,
- Config-A: 1 waiting line, 5 processors
- Config-B: 5 independent servers
- Config-C: 1 waiting line, 1 fast processor with μfast=5*μ

An example chart from simulation result is shown below.

<img width="620" alt="image" src="https://user-images.githubusercontent.com/25234772/220383386-9ea0149e-9d5b-47a8-a9d0-28f47edfaa0a.png">

### Part 2: [Mixing servers](/mixing-servers.py)

A simulation model for queuing configuration below is realized to devise a strategy to switch arriving clients to different waiting queues (belonging to different servers), in a way such that the throughput of the system is maximized.

<img width="420" alt="image" src="https://user-images.githubusercontent.com/25234772/220384796-45a53340-1433-404a-a16e-ca89c293a3ce.png">

Service rate is kept constant to 10 clients served per second and arrival rates are varied such that the value of server utilization (ρ) varies from 0.1 to 2.0 in 20 steps.

In order to decide, towards which queue the arriving clients must be switched to obtain maximum throughput, following three strategies are considered,
- switch client to any random server on arrival
- switch client to the least loaded server with fastest response time
- switch client to fast server with probability = 0.5

An example chart from simulation result is shown below.

<img width="620" alt="image" src="https://user-images.githubusercontent.com/25234772/220386246-fe0ac18c-c32c-47f6-99d8-c8cfb7b2d0f4.png">


