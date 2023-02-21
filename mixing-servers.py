#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Simulation of Simple Queuing Models

Part2 : Mixing Servers

Author: Deepankar Sharma

"""
import random
import itertools
import numpy as np
import simpy
from matplotlib import pyplot

SIM_TIME = 1000
RANDOM_SEED = 10
ARRIVAL_RATE = [x for x in range(10, 210, 10)]
SERV_RATE = 100
CAPACITY = 10
Nservers = 5

##--QUEUING SYSTEM DEFINITION--------------------------------------------------
# SERVER PROCESS
class ServerProcess(object):
    def __init__(self, env, servers, serverId, serviceRate):
        self.env = env
        self.servers = servers
        self.serverId = serverId
        self.serviceRate = serviceRate
        self.lost = 0

    def arrival(self, cache):
        if len(servers[self.serverId].queue) < CAPACITY:
            start = self.env.now
            with self.server.request() as req:
                yield req
                yield self.env.process(self.departure(self.serviceRate))
                responseTime = self.env.now - start
                cache[self.serverId].append(responseTime)
        else:
            self.loss = 1

    def departure(self, serviceRate):
        yield self.env.timeout(random.expovariate(serviceRate))

# CUSTOMER PROCESS
class CustomerProcess(object):
    def __init__(self, env, servers, serviceRate):
        self.env = env
        self.servers = servers
        self.serviceRate = serviceRate
        self.client = []
        self.Id = 0

    def run(self, arrivalRates, model, cache):
        self.Id = 0
        while True:
            yield self.env.timeout(random.expovariate(arrivalRate))
            serverId = getserverId(model)
            if serverId == 0:# direct to fast processor
                server = self.server[serverId]
                self.client.append(ServerProcess(self.env, server, serverId, Nservers*self.serviceRate))
                self.env.process(self.client[clientId].arrival(cache))
            else:# direct to normal processor
                server = self.server[serverId]
                self.client.append(ServerProcess(self.env, server, serverId, self.serviceRate))
                self.env.process(self.client[self.Id].arrival(cache))
            self.Id += 1

def getserverId(model):
    if model:# model m
        sid = []
        for x in range(4):
            sid.append(np.mean(logMine[x])*len(servers[x].queue))
        serverId = np.argmin(sid)
    else:# model r
        serverId = np.random.randint(0, len(servers))
    return serverId

##----Obtain needed data from logs--------------------------------------------
def getResponseTime(cachename):
    time = sum([sum(x) for x in cachename])
    num = sum([len(x) for x in cachename])
    return time/num #Avg response time of the system 

def getThroughput(model):
    total = len(model.client)
    loss = sum([x.loss for x in model.client])
    throughput = (total-loss)/SIM_TIME
    return throughput #System throughput per second 

def getServerInfo(model, cachename):
    tot_per_server = [[x.serverId for x in model.client if not x.loss].count(y) for y in range(4)]
    avg_per_server = [np.mean(x) for x in cachename]
    return [tot_per_server, avg_per_server] 
#%% Main
if __name__ == "__main__":
    ET_tmp = []
    Xt_tmp = []
    np.random.seed(RANDOM_SEED)

    for arrivalRate in ARRIVAL_RATE:
        #data logs for each model
        logRand = []
        logMine = []
        for i in range(N+1): # creating data logs for each server
            log_rand.append([])
            log_mine.append([])
        # model: choose a random server on arrival
        env = simpy.Environment()
        servers = [simpy.Resource(env, 1) for x in range(Nservers)]
        servers = [simpy.Resource(env, 1)] + servers #adding a fast server in front of the server list
        modelRand = CustomerProcess(env, servers, SERV_RATE)
        env.process(modelRand.run(arrivalRate, model=0, logRand))
        env.run(until=SIM_TIME)
        ET_tmp.append(getResponseTime(logRand))
        Xt_tmp.append(getThroughput(modelRand))
        
        # model: choose the fastest server on arrival
        env = simpy.Environment()
        servers = [simpy.Resource(env, 1) for x in range(N)]
        servers = [simpy.Resource(env, 1)] + servers #adding a fast server
        modelMine = CustomerProcess(env, servers, SERV_RATE)
        env.process(modelMine.run(arrivalRate, model=1, logMine))
        env.run(until=SIM_TIME)
        ET_tmp.append(getResponseTime(logMine))
        Xt_tmp.append(getThroughput(modelMine))

##--PLOTS---------------------------------------------------------------------- 
    ET = []
    Xt = []
    for j in range(2):
        ET.append([ET_tmp[i] for i in range(2*len(ARRIVAL_RATE)) if i%2 == j])
        Xt.append([Xt_tmp[i] for i in range(2*len(ARRIVAL_RATE)) if i%2 == j])

    rho = [arrivalRate/SERV_RATE for arrivalRate in ARRIVAL_RATE] #server utilization values
    ind = np.arange(len(ARRIVAL_RATE))
    label = ['{:0.2}'.format(x) for x in rho]
    width = 0.25

    fig, axes = pyplot.subplots(1, 2, figsize=(9, 4))

    axes[0].plot(ro, ET[0], '-s', ro, ET[1], '-o')
    axes[0].set_title("Average Response Time at different Traffic Load")
    axes[0].set_xlabel('ρ')
    axes[0].set_ylabel('E(T)')
    axes[0].set_xbound(0, 1.6)
    axes[0].legend(['randmodel', 'mymodel'])

    axes[1].bar(ind, Xt[0], width)
    axes[1].bar(ind + width, Xt[1], width)
    axes[1].set_xticks(ind + width/2.)
    axes[1].set_xticklabels(label)
    axes[1].set_title("Throughput at different Traffic Load")
    axes[1].set_xlabel('ρ')
    axes[1].set_ylabel('X')
    axes[1].legend(['randmodel', 'mymodel'])
    pyplot.tight_layout()
    pyplot.savefig('fig1b.png')
#%%
# =============================================================================
#     rinfo = getServerInfo(model_rand, cache_rand)
#     minfo = getServerInfo(model_mine, cache_mine)
#     ind = np.arange(len(servers))
#     label = ['fast', 'normal', 'normal', 'normal']
# 
#     fig, bx = pyplot.subplots()
# 
#     bx.bar(ind, rinfo[0], width)
#     bx.bar(ind + width, minfo[0], width)
#     bx.set_xticks(ind + width/2.)
#     bx.set_xticklabels(label)
#     bx.set_title("Number of served requests in each server at ρ=1.5")
#     bx.set_xlabel('Server')
#     bx.set_ylabel('N')
#     bx.legend(['randmodel', 'mymodel'])
#     pyplot.tight_layout()
# 
#     fig, bxes = pyplot.subplots(1, 2, sharey=True, figsize=(9, 3))
#     bxes[0].hist(cache_rand[0], bins=100, normed=True)
#     bxes[1].hist(cache_mine[0], bins=100, normed=True, color='#ff7f0e')
#     bxes[0].set_title('randmodel')
#     bxes[1].set_title('mymodel')
#     fig.text(0.51, 0.001, 'Response Time', ha='center')
#     fig.text(0, 0.51, 'Density', va='center', rotation='vertical')
#     fig.text(0.35, 0.99, 'Response Time PDF in fast server at ρ=1.5')
#     pyplot.tight_layout()
#     
#     fig, bxes = pyplot.subplots(3, 2, sharey=True, figsize=(9, 7))
#     for i in range(3):
#         bxes[i][0].hist(cache_rand[i+1], bins=100, normed=True)
#         bxes[i][1].hist(cache_mine[i+1], bins=100, normed=True, color='#ff7f0e')
#         bxes[i][0].set_title('randmodel')
#         bxes[i][1].set_title('mymodel')
#     fig.text(0.51, 0.001, 'Response Time', ha='center')
#     fig.text(0, 0.51, 'Density', va='center', rotation='vertical')
#     fig.text(0.35, 0.99, 'Response Time PDF in normal servers at ρ=1.5')
#     pyplot.tight_layout()
# 
#     fig, cxes = pyplot.subplots(1, 2, sharey=True, figsize=(9, 3))
#     cxes[0].hist(cache_rand[0], bins=100, normed=True, cumulative=True)
#     cxes[1].hist(cache_mine[0], bins=100, normed=True, cumulative=True, color='#ff7f0e')
#     cxes[0].set_title('randmodel')
#     cxes[1].set_title('mymodel')
#     fig.text(0.51, 0.001, 'Response Time', ha='center')
#     fig.text(0, 0.51, 'Density', va='center', rotation='vertical')
#     fig.text(0.35, 0.99, 'Response Time CDF in fast server at ρ=1.5')
#     pyplot.tight_layout()
# 
#     fig, cxes = pyplot.subplots(3, 2, sharey=True, figsize=(9, 7))
#     for i in range(3):
#         cxes[i][0].hist(cache_rand[i+1], bins=100, normed=True, cumulative=True)
#         cxes[i][1].hist(cache_mine[i+1], bins=100, normed=True, cumulative=True, color='#ff7f0e')
#         cxes[i][0].set_title('randmodel')
#         cxes[i][1].set_title('mymodel')
#     fig.text(0.51, 0.001, 'Response Time', ha='center')
#     fig.text(0, 0.51, 'Density', va='center', rotation='vertical')
#     fig.text(0.35, 0.99, 'Response Time CDF in normal servers at ρ=1.5')
#     pyplot.tight_layout()
# =============================================================================
