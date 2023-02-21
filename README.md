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

