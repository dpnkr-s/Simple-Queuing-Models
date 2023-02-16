#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Management and Content Delivery for Smart Networks

Simulation of Simple Queuing Models

Part 1 : Comparing Queue Models

Author: Deepankar Sharma

"""
import math
import numpy as np
import random
import simpy
from matplotlib import pyplot

Nprocessors=5
SIM_TIME = 1000
#SIM_TIME = 100 #to obtain quick results for debugging
RANDOM_SEED = 10
ARRIV_RATE = 100 #average arrival rate of customers (lambda) = no. customers per second
SERV_RATE = [x for x in reversed(range(100, 600, 100))] #average service rate (mu)
SERV_RATE.extend([x for x in reversed(range(30, 100, 10))])
SERV_RATE.extend([x for x in reversed(range(10, 30, 1))]) 
BUFFER_CAP = [1]+[x for x in range(5, 105, 5)] #max size buffer
rho = [(ARRIV_RATE/(x*Nprocessors)) for x in SERV_RATE] #server utilization

##--QUEUING NETWORK MODEL DEFINITION-------------------------------------------
# SERVER PROCESS
class ServerProcess(object):
    def __init__(self, env, servers, serverId, serviceRate):
        self.env = env
        self.servers = servers
        self.serverId = serverId
        self.serviceRate = serviceRate
        self.lost = 0 #customer loss indicator
        self.response = None

    def arrival(self, Qlimit):
        if len(servers[self.serverId].queue) < Qlimit: #to check if server queue has empty slots
            start = self.env.now # beginning of waiting time for customer in system
            with self.servers.request() as req:
                yield req #free server is allocated to serve the customer
                yield self.env.process(self.departure(self.serviceRate)) #begin service time
                self.response = self.env.now - start #total time from arrival in system
        else:
            self.lost = 1 #queue is full : customer is discarded

    def departure(self, serviceRate):
        yield self.env.timeout(random.expovariate(serviceRate))
        # exponentially distributed service time with lambda = serviceRate

# CUSTOMER PROCESS
class CustomerProcess(object):
    def __init__(self, env, servers, serviceRate, Qlimit):
        self.env = env
        self.servers = servers
        self.serviceRate = serviceRate
        self.Qlimit = Qlimit # maximum buffer capacity of server queue
        self.client = []
        self.id = 0

    def beginArrivals(self, arrival, numServer):
        self.id = 0
        while True:
            yield self.env.timeout(random.expovariate(arrival))
            serverId = np.random.randint(0, numServer) #random allocation of server queue
            rsrc = self.servers[serverId] #replacer for simpy server resource 
            self.client.append(ServerProcess(self.env, rsrc, serverId, self.serviceRate))
            self.env.process(self.client[self.id].arrival(self.Qlimit))
            self.id += 1

## Function definitions
def getResponseTime(config):
    respTime = [x.response for x in config.client if not x.lost]
    avgTime = np.mean([x for x in respTime if x is not None])
    return avgTime

def getLossRate(config):
    lostCustomers = sum(x.lost for x in config.client)
    totalCustomers = len(config.client)
    return lostCustomers/totalCustomers

# erlangC function to compute theoretical values for config A (M/M/m queue)
def erlangC(rho, m):#rho=lambda/mu, m=no. of servers
    Val = (rho**m / math.factorial(m)) * (m / (m - rho))
    sum_n = 0
    for i in range(m):
        sum_n += (rho**i) / math.factorial(i)
    return (Val / (sum_n + Val))  
#%% Main
if __name__ == "__main__":

    #empty arrays acting as value logs for selected attributes per configuration
    respTime=[[],[],[]]
    loss=[[],[],[]]
    
    respTimeBuff1 = [[], [], []]
    lossBuff1 = [[], [], []]
    respTimeBuff2 = [[], [], []]
    lossBuff2 = [[], [], []]
    
    # two different random number generator functions are used throughout     
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    itern = 0
    # Fixed buffer capacity = 10, iteration over changing service rate
    for serviceRate in SERV_RATE:
                        
        #1 waiting line, N processors
        env = simpy.Environment()
        servers = [simpy.Resource(env, Nprocessors)]
        configA = CustomerProcess(env, servers, serviceRate, BUFFER_CAP[3])
        env.process(configA.beginArrivals(ARRIV_RATE, 1))
        env.run(until=SIM_TIME)
        respTime[0].append(getResponseTime(configA))
        loss[0].append(getLossRate(configA))
        
        #N independent servers
        env = simpy.Environment()
        servers = [simpy.Resource(env, 1) for x in range(Nprocessors)]
        configB = CustomerProcess(env, servers, serviceRate, BUFFER_CAP[3])
        env.process(configB.beginArrivals(ARRIV_RATE, Nprocessors))
        env.run(until=SIM_TIME)
        respTime[1].append(getResponseTime(configB))
        loss[1].append(getLossRate(configB))
        
        #1 waiting line, fast processor
        env = simpy.Environment()
        servers = [simpy.Resource(env, 1)]
        configC = CustomerProcess(env, servers, Nprocessors*serviceRate, BUFFER_CAP[3])
        env.process(configC.beginArrivals(ARRIV_RATE, 1))
        env.run(until=SIM_TIME)
        respTime[2].append(getResponseTime(configC))
        loss[2].append(getLossRate(configC))
        print('Server utilization = ', '{:0.3}'.format(rho[itern]))
        itern += 1
       
    # FIX service rate, CHANGE buffer size
    val = 10
    for serviceRate in [SERV_RATE[10], SERV_RATE[25]]:
        for capacity in BUFFER_CAP:
            #1 waiting line, N processors
            env = simpy.Environment()
            servers = [simpy.Resource(env, Nprocessors)]
            configA = CustomerProcess(env, servers, serviceRate, capacity)
            env.process(configA.beginArrivals(ARRIV_RATE, 1))
            env.run(until=SIM_TIME)
            if val == 10:
                respTimeBuff1[0].append(getResponseTime(configA))
                lossBuff1[0].append(getLossRate(configA))
            else:
                respTimeBuff2[0].append(getResponseTime(configA))
                lossBuff2[0].append(getLossRate(configA))
          
            #N independent servers
            env = simpy.Environment()
            servers = [simpy.Resource(env, 1) for x in range(Nprocessors)]
            configB = CustomerProcess(env, servers, serviceRate, capacity)
            env.process(configB.beginArrivals(ARRIV_RATE, Nprocessors))
            env.run(until=SIM_TIME)
            if val == 10:
                respTimeBuff1[1].append(getResponseTime(configB))
                lossBuff1[1].append(getLossRate(configB))
            else:
                respTimeBuff2[1].append(getResponseTime(configB))
                lossBuff2[1].append(getLossRate(configB))
            
            #1 waiting line, fast processor
            env = simpy.Environment()
            servers = [simpy.Resource(env, 1)]
            configC = CustomerProcess(env, servers, Nprocessors*serviceRate, capacity)
            env.process(configC.beginArrivals(ARRIV_RATE, 1))
            env.run(until=SIM_TIME)
            if val == 10:
                respTimeBuff1[2].append(getResponseTime(configC))
                lossBuff1[2].append(getLossRate(configC))
            else:
                respTimeBuff2[2].append(getResponseTime(configC))
                lossBuff2[2].append(getLossRate(configC))
            print('Buffer capacity =', capacity, ', rho =', rho[val])
        val = 25 # only for printing rho value, not used in algorithm
                
 ##--Plots---------------------------------------------------------------------  
    #variables for indexing
    ind = np.arange(1, (len(SERV_RATE)+1))
    label = ['{:0.2}'.format(x) for x in rho]
    idx = ind[::4] # to select only a few points for xtick
    lbl = label[::4]
    
   
    fig1, axes = pyplot.subplots(1, 2, sharex=True, figsize=(12, 4))

    axes[0].plot(rho, respTime[0], '--', rho, respTime[1], '--', rho, respTime[2], '--')
    axes[0].set_title("Average Response Time vs. Server utilization at B=10")
    axes[0].set_xlabel('ρ')
    axes[0].set_ylabel('E(T)')
    axes[0].legend(['Config-A', 'Config-B', 'Config-C'])
    axes[1].plot(rho, loss[0], '--', rho, loss[1], '--', rho, loss[2], '--')
    axes[1].set_title("Customer Loss Rate vs. Server utilization at B=10")
    axes[1].set_xlabel('ρ')
    axes[1].set_ylabel('L')
    axes[1].legend(['Config-A', 'Config-B', 'Config-C'])
    pyplot.tight_layout()
    pyplot.savefig('fig1a-1.png')

    fig2, axes2 = pyplot.subplots(1, 2, figsize=(12, 4))

    axes2[0].plot(BUFFER_CAP, respTimeBuff1[0], '--', BUFFER_CAP, respTimeBuff1[1], '--', BUFFER_CAP, respTimeBuff1[2], '--')
    axes2[0].set_title("Average Response Time vs. Buffer Capacity at ρ=0.5")
    axes2[0].set_xlabel('B')
    axes2[0].set_ylabel('E(T)')
    axes2[0].legend(['Config-A', 'Config-B', 'Config-C'])
    axes2[1].plot(BUFFER_CAP, respTimeBuff2[0], '--', BUFFER_CAP, respTimeBuff2[1], '--', BUFFER_CAP, respTimeBuff2[2], '--')
    axes2[1].set_title("Average Response Time vs. Buffer Capacity at ρ=1.25")
    axes2[1].set_xlabel('B')
    axes2[1].set_ylabel('E(T)')
    #axes2[1].set_ybound(,)
    axes2[1].legend(['Config-A', 'Config-B', 'Config-C'])
    pyplot.tight_layout()
    pyplot.savefig('fig1a-2.png')
    
    fig3, axes3 = pyplot.subplots(1, 2, figsize=(12, 4))

    axes3[0].plot(BUFFER_CAP, lossBuff1[0], '--', BUFFER_CAP, lossBuff1[1], '--', BUFFER_CAP, lossBuff1[2], '--')
    axes3[0].set_title("Customer Loss Rate vs. Buffer Capacity at ρ=0.5")
    axes3[0].set_xlabel('B')
    axes3[0].set_ylabel('L')
    #axes3[0].set_ybound(,)
    axes3[0].legend(['Config-A', 'Config-B', 'Config-C'])
    axes3[1].plot(BUFFER_CAP, lossBuff2[0], '--', BUFFER_CAP, lossBuff2[1], '--', BUFFER_CAP, lossBuff2[2], '--')
    axes3[1].set_title("Customer Loss Rate vs. Buffer Capacity at ρ=1.25")
    axes3[1].set_xlabel('B')
    axes3[1].set_ylabel('L')
    #axes3[1].set_ybound(,)
    axes3[1].legend(['Config-A', 'Config-B', 'Config-C'], loc=1)
    pyplot.tight_layout()
    pyplot.savefig('fig1a-3.png')

    #Comparing theoretical models of queue configs with simulation performance
    theoC = [1/(Nprocessors*x-ARRIV_RATE) for x in SERV_RATE[2:20]]
    #full departure list is not used fully to avoid zero-division 
    theoB = [Nprocessors*x for x in theoC]
    #calculating E(T) = C(rho,m)/(m*mu - lambda) + 1/mu
    theoA =[]
    for x in SERV_RATE[2:20]:
        CC = erlangC((ARRIV_RATE/x),Nprocessors)
        theoA.append(CC + (1/x))
    
    fig4, axes4 = pyplot.subplots(3, 1, sharex=True)
    
    axes4[0].plot(rho[2:20], respTime[2][2:20], rho[2:20], theoC, '--')
    axes4[0].set_title('Config-C: 1 waiting line, 1 fast processor')
    axes4[0].legend(['Simulation', 'Theoretical'])
    axes4[0].set_ylabel('E(T)')
    axes4[1].plot(rho[2:20], respTime[1][2:20], rho[2:20], theoB, '--')
    axes4[1].set_title('Config-B: N independent servers')
    axes4[1].legend(['Simulation', 'Theoretical'])
    axes4[1].set_ylabel('E(T)')
    axes4[2].plot(rho[2:20], respTime[0][2:20], rho[2:20], theoA, '--')
    axes4[2].set_title('Config-A: 1 waiting line, N processors')
    axes4[2].legend(['Simulation', 'Theoretical'])
    axes4[2].set_xlabel('ρ')
    axes4[2].set_ylabel('E(T)')
    pyplot.savefig('fig1a-4.png')
