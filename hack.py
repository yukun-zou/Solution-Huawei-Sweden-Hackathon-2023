###### Running instructions
## python3 hack.py 
## will run all test cases under ./testcases/ directory and output them to ./solutions/ directory
##
## Optional parameter:
## -t [testcases_path]  Will use this directory as testcases folder
## -f [file_name]       Will only run the testcase on this file
##
## Example:
## python3 hack.py -t ./testcases/ -f case20.txt
## runs only testcase 20 on ./testcases/ directory

import os
import sys
import csv
import math
from enum import Enum
from timeit import default_timer as timer

# Modelling the problem

class Problem :
    def __init__(self, bs = 0, action_cost = 0,  cloud_CPU_cost = 0, cloud_MEM_cost = 0, cloud_ACC_cost = 0, \
     BBU_sets = 0, BBU_CPU_set = 0, BBU_MEM_set = 0, BBU_ACC_set = 0, BBU_cost_set = 0,\
     CPU_ACC_ratio = 0, trans_period = 0, episode_length = 0, num_slices = 0, slices = []):
        self.bs = bs # Baseline cost
        self.action_cost    = action_cost
        self.cloud_CPU_cost = cloud_CPU_cost
        self.cloud_MEM_cost = cloud_MEM_cost
        self.cloud_ACC_cost = cloud_ACC_cost
        self.CPU_ACC_ratio  = CPU_ACC_ratio
        self.BBU_sets = BBU_sets
        self.BBU_CPU_set = BBU_CPU_set
        self.BBU_MEM_set = BBU_MEM_set
        self.BBU_ACC_set = BBU_ACC_set
        self.BBU_cost_set = BBU_cost_set
        self.episode_length = episode_length
        self.num_slices = num_slices
        self.slices = slices

class io_lock:
    def __init__(self, lock = False, time = 0):
        self.lock = lock
        self.time = time
    #每过一个timestep，lock的时间减一
    def update(self):
        if self.lock:
            self.time -= 1
            if self.time == 0:
                self.lock = False
    #锁住io，持续time个timestep
    def lock(self, time):
        self.lock = True
        self.time = time
    #判断io是否被锁住
    def is_locked(self):
        return self.lock
    #返回io还剩多少时间被锁住
    def get_time(self):
        return self.time
    #解锁
    def unlock(self):
        self.lock = False
        self.time = 0

class S_T(Enum):
    CU  = 1
    DU  = 2
    PHY = 3


class Slice :
    def __init__(self, services = [], io = [], traffic = []):
        self.services = services
        self.io = io
        self.traffic  = traffic

class Service :
    def __init__(self, parent_slice = 0, service_type = S_T.CU, CPU = 0, MEM  = 0, ACC = 0):
        self.parent_slice = parent_slice
        self.service_type = service_type
        self.CPU = CPU
        self.MEM = MEM
        self.ACC = ACC


class Solution :
    def __init__(self, CLOUD_OPEX = 0, CLOUD_Costs = [], BBU_OPEX = 0, BBU_Costs= [], IO_OPEX = 0, IO_Costs = [], allocation = []):
        self.CLOUD_OPEX = CLOUD_OPEX
        self.CLOUD_Costs= CLOUD_Costs
        self.BBU_alloc  = []
        self.BBU_OPEX   = BBU_OPEX
        self.BBU_Costs  = BBU_Costs
        self.IO_OPEX    = IO_OPEX
        self.IO_Costs   = IO_Costs
        self.action_cost= 0
        self.total_cost = 0
        self.allocation = allocation # List of lists, where each element in the 2nd list is the alloc for the slice at T(t)
        self.score      = 0

    
    def calculate_bbu_costs(self, p:Problem):
        for i in range(p.episode_length) :
            sets = max(math.ceil(self.BBU_alloc[i].CPU/p.BBU_CPU_set), math.ceil(self.BBU_alloc[i].MEM/p.BBU_MEM_set), math.ceil(self.BBU_alloc[i].ACC/p.BBU_ACC_set))
            self.BBU_Costs[i] = sets * p.BBU_cost_set 

    def calculate_action_costs(self, p:Problem) :
        cost = 0
        for i in range(len(self.allocation)) :
            for j in range(1,len(self.allocation[i])) :
                if self.allocation[i][j] == self.allocation[i][j-1] :
                    pass
                else :
                    a = [char for char in self.allocation[i][j]]
                    b = [char for char in self.allocation[i][j-1]]
                    for k in range(len(a)) :
                        if not a[k] == b[k] :
                            self.action_cost += p.action_cost



    def total_OPEX(self):
        return self.CLOUD_OPEX + self.BBU_OPEX + self.IO_OPEX + self.action_cost

    def set_score(self, baseline:int) :
        self.score = max(0, float(baseline) / self.total_OPEX() - 1)
        return self.score

    def calculate_costs(self, p:Problem) :
        self.calculate_bbu_costs(p)
        self.calculate_action_costs(p)
        self.CLOUD_OPEX = sum(self.CLOUD_Costs)
        self.BBU_OPEX   = sum(self.BBU_Costs)
        self.IO_OPEX    = sum(self.IO_Costs)
        self.total_cost = self.total_OPEX()
        self.set_score(p.bs)
        return self.total_cost

class BBU_Allocation :
    def __init__(self, CPU = 0, MEM = 0, ACC = 0):
        self.CPU = CPU
        self.MEM = MEM
        self.ACC = ACC

    def list(self) : 
        return [self.site, self.CPU, self.MEM, self.ACC]

### Input and Output        

def read_slice(p:Problem,r:str,i:str,tr:str):
    s = Slice([], [], [])
    s.services.append(Service(s, S_T.CU , int(r[0]), int(r[1]), int(r[2])))
    s.services.append(Service(s, S_T.DU , int(r[3]), int(r[4]), int(r[5])))
    s.services.append(Service(s, S_T.PHY, int(r[6]), int(r[7]), int(r[8])))
    s.io = [int(n) for n in i]
    s.traffic = [int(z) for z in tr]
    p.slices.append(s)

def read_problem(file:str='./testcases/input.csv', delimiter:str=' '):
    p = Problem()
    p.slices = []

    with open(file, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        line_count = 0
        l = []
        i = []
        for r in csv_reader:
            if line_count == 0:
                p.bs = int(r[0])
                p.action_cost   = int(r[1])
            if line_count == 1:
                p.cloud_CPU_cost = int(r[0])
                p.cloud_MEM_cost = int(r[1])
            if line_count == 2:
                p.BBU_sets     = int(r[0])
                p.BBU_CPU_set  = int(r[1])
                p.BBU_MEM_set  = int(r[2])
                p.BBU_ACC_set  = int(r[3])
                p.BBU_cost_set = int(r[4])
            if line_count == 3:
                p.num_slices = int(r[0])
                p.episode_length = int(r[1])
                p.CPU_ACC_ratio  = int(r[2])
                p.cloud_ACC_cost = p.cloud_CPU_cost * p.CPU_ACC_ratio
            if line_count >= 4 :
                s_l = (line_count - 4) % 5 
                if s_l == 0 :
                    l = r
                if s_l == 1 or s_l == 2 :
                    l = l + r
                if s_l == 3 :
                    i = r
                if s_l == 4 :
                    read_slice(p, l, i, r)
            line_count += 1
    return p


def print_solution (s:Solution, p:Problem, file:str = './solutions/solution.csv', delimiter:str = ' ', time:int = 0):
    with open(file, mode='w',newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_NONE,  escapechar= ' ')

        for i, sl in enumerate(p.slices) :
            writer.writerow(s.allocation[i])

        writer.writerow(s.CLOUD_Costs)
        writer.writerow(s.BBU_Costs)
        writer.writerow(s.IO_Costs)

        writer.writerow([s.total_cost])
        writer.writerow([s.score])
        writer.writerow([time])

        csv_file.close()


def slice_cost(p:Problem, sol:Solution, sl:Slice, time:int, alloc:str):
    ret = 0
    for i, s in enumerate(sl.services):
        if alloc[i] == 'C':
            ret += sl.traffic[time] * (s.CPU * p.cloud_CPU_cost + s.MEM * p.cloud_MEM_cost + s.ACC * p.cloud_ACC_cost) 
        else :
            sol.BBU_alloc[time].CPU += sl.traffic[time] * s.CPU
            sol.BBU_alloc[time].MEM += sl.traffic[time] * s.MEM
            sol.BBU_alloc[time].ACC += sl.traffic[time] * s.ACC
    return ret

### SOLUTION STRATEGY : all_cloud
### Description : allocate everything to the cloud
def all_cloud(p:Problem):
    sol = Solution(allocation = [])

    sol.CLOUD_Costs = [0] * p.episode_length
    sol.BBU_Costs   = [0] * p.episode_length
    sol.BBU_alloc   = [BBU_Allocation(0,0,0) for i in range(p.episode_length)]
    sol.IO_Costs    = [0] * p.episode_length
    sol.allocation  = []


    for index, sl in enumerate(p.slices) :
        a = []
        for i in range(p.episode_length) :
            if(
                sol.BBU_alloc[i].CPU +  sl.traffic[i] *(sl.services[0].CPU+sl.services[1].CPU+sl.services[2].CPU)
                                                        <= p.BBU_CPU_set*p.BBU_sets and
                sol.BBU_alloc[i].MEM + sl.traffic[i] * (sl.services[0].MEM+sl.services[1].MEM+sl.services[2].MEM)
                                                        <= p.BBU_MEM_set*p.BBU_sets and
                sol.BBU_alloc[i].ACC + sl.traffic[i] * (sl.services[0].ACC+sl.services[1].ACC+sl.services[2].ACC)
                <= p.BBU_ACC_set*p.BBU_sets
            ):
                a.append("BBB")
                # sol.BBU_alloc[i].CPU+= sl.traffic[i] * sl.services[0].CPU
                # sol.BBU_alloc[i].MEM+= sl.traffic[i] * sl.services[0].MEM
                # sol.BBU_alloc[i].ACC+= sl.traffic[i] * sl.services[0].ACC
                sol.CLOUD_Costs[i] += slice_cost(p, sol, sl, i, "BBB")
                sol.IO_Costs[i]    += sl.io[0] * sl.traffic[i]
            elif(
                sol.BBU_alloc[i].CPU +  sl.traffic[i] *(sl.services[0].CPU+sl.services[1].CPU+sl.services[2].CPU)
                                                        > p.BBU_CPU_set and
                sol.BBU_alloc[i].MEM + sl.traffic[i] * (sl.services[0].MEM+sl.services[1].MEM+sl.services[2].MEM)
                                                        <= p.BBU_MEM_set and
                sol.BBU_alloc[i].ACC + sl.traffic[i] * (sl.services[0].ACC+sl.services[1].ACC+sl.services[2].ACC)
                <= p.BBU_ACC_set
            ):
                            
                a.append("CBB")
                sol.CLOUD_Costs[i] += slice_cost(p, sol, sl, i, "CBB")
                sol.IO_Costs[i]    += sl.io[1] * sl.traffic[i]
            elif(
                sol.BBU_alloc[i].CPU +  sl.traffic[i] *(sl.services[0].CPU+sl.services[1].CPU+sl.services[2].CPU)
                                                        > p.BBU_CPU_set and
                sol.BBU_alloc[i].MEM + sl.traffic[i] * (sl.services[0].MEM+sl.services[1].MEM+sl.services[2].MEM)
                                                        > p.BBU_MEM_set and
                sol.BBU_alloc[i].ACC + sl.traffic[i] * (sl.services[0].ACC+sl.services[1].ACC+sl.services[2].ACC)
                <= p.BBU_ACC_set
            ):
                a.append("CCB")
                # sol.BBU_alloc[i].CPU+= sl.traffic[i] * sl.services[0].CPU
                # sol.BBU_alloc[i].MEM+= sl.traffic[i] * sl.services[0].MEM
                # sol.BBU_alloc[i].ACC+= sl.traffic[i] * sl.services[0].ACC
                sol.CLOUD_Costs[i] += slice_cost(p, sol, sl, i, "CCB")
                sol.IO_Costs[i]    += sl.io[2] * sl.traffic[i]
                
            else :
                a.append("CCC")
                sol.CLOUD_Costs[i] += slice_cost(p, sol, sl, i, "CCC")
                sol.IO_Costs[i]    += sl.io[3] * sl.traffic[i]
        sol.allocation.append(a)
        

    sol.calculate_costs(p)

    return sol

def solve(d:str, f:str):

    ds = './solutions/'

    p = read_problem(d+f)

    start = timer()
    solution = all_cloud(p)
    end = timer()
    time_taken = int((end - start)*1000)

    f = f.replace("case","")
    f = f.replace("txt", "csv")

    print_solution(solution, p, ds+f, time = time_taken)

    return



if __name__ == "__main__":

    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]

    t = './testcases/'

    if "-t" in opts:
        t = sys.argv[sys.argv.index("-t")+1];

    if "-f" in opts:
        f = sys.argv[sys.argv.index("-f")+1];
        solve(t,f)

    else : 
        dir_list = os.listdir(t)

        for f in dir_list:
            if '.txt' in f:
                ans = solve(t,f)
