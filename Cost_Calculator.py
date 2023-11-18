# Cost_Calculator.py is used to calculate the cost of the policy=cost builder
import csv
import math
import time


class Cost_Calculator:
    """
    This class is used to calculate the cost of the policy=cost builder
    """

    OPEX = 0
    BBU_cost = 0
    cloud_cost = 0
    IO_cost = 0
    action_cost = 0

    baseline_cost = 0
    CPU_cost = 0
    MEM_cost = 0
    B = 0
    CPU = 0
    MEM = 0
    ACC = 0
    cost_per_set = 0
    N = 0
    T = 0
    X = 0
    slices = []
    policy = []
    cloud_costs = []
    BBU_costs = []
    IO_costs = []
    execution_time = 0
    score = 0

    def __init__(
        self,
        baseline_cost,
        action_cost,
        CPU_cost,
        MEM_cost,
        B,
        CPU,
        MEM,
        ACC,
        cost_per_set,
        N,
        T,
        X,
        slices,
        policy=[],
    ):
        """
        initialize the cost calculator
        """
        self.baseline_cost = baseline_cost
        self.action_cost = action_cost
        self.CPU_cost = CPU_cost
        self.MEM_cost = MEM_cost
        # BBU boards
        self.B = B
        # per set
        self.CPU = CPU
        self.MEM = MEM
        self.ACC = ACC
        self.cost_per_set = cost_per_set
        self.N = N
        self.T = T
        self.X = X
        self.slices = slices
        self.policy = policy

    def calculate_cloud_cost(
        self, traffic, CPU_required, MEM_required, ACC_required, CPU_cost, MEM_cost, X
    ) -> int:
        """
        calculate the cost of the cloud no use of ACC
        if ACC is used, ACC is replaced by X*CPU_required
        eg if X=4 then 4 CPUs provide the same performance as 1 ACC
        cloud resource unlimited
        """
        cloud_cost = traffic * (
            CPU_required * CPU_cost
            + MEM_required * MEM_cost
            + X * ACC_required * CPU_cost
        )
        return cloud_cost

    def calculate_BBU_cost(
        self, CPU, MEM, ACC, cost_per_set, CPU_required, MEM_required, ACC_required
    ):
        """
        calculate the cost of the BBU
        BBU sets must smaller than BBU boards B, source limited
        """

        BBU_sets = max(
            math.ceil(CPU_required / CPU),
            math.ceil(MEM_required / MEM),
            math.ceil(ACC_required / ACC),
        )

        BBU_cost = BBU_sets * cost_per_set
        # print("BBU sets", BBU_sets,"BBU boards" ,self.B ,"BBU cost", BBU_cost)
        return BBU_cost

    def calculate_IO_cost(self, traffic, IO_linkUsed) -> int:
        """
        calculate the cost of the IO
        """
        IO_cost = traffic * IO_linkUsed
        return IO_cost

    def calculate_action_cost(self, relocation, action_cost) -> int:
        """
        calculate the cost of the action
        """
        action_cost = relocation * action_cost
        return action_cost

    def calculate_OPEX(self, cloud_cost, BBU_cost, IO_cost, action_cost) -> int:
        """
        calculate the OPEX
        """
        OPEX = cloud_cost + BBU_cost + IO_cost + action_cost
        return OPEX

    def cost_CCC(self, s, relocation, t):
        """calculate the cost of the policy CCB

        Args:
            s (dict): _description_
            relocation (int): _description_
            t (int): _description_

        Returns:
            _type_: _description_
        """
        # cpu
        total_cpu = s["CU"][0] + s["DU"][0] + s["PHY"][0]
        # mem
        total_mem = s["CU"][1] + s["DU"][1] + s["PHY"][1]
        # acc
        total_acc = s["CU"][2] + s["DU"][2] + s["PHY"][2]

        cloud_cost = self.calculate_cloud_cost(
            s["traffic"][t],
            total_cpu,
            total_mem,
            total_acc,
            self.CPU_cost,
            self.MEM_cost,
            self.X,
        )

        BBU_cost = 0
        # LD io cost
        IO_cost = self.calculate_IO_cost(s["traffic"][t], s["IO"][3])

        action_cost = self.calculate_action_cost(relocation, self.action_cost)

        OPEX = self.calculate_OPEX(cloud_cost, BBU_cost, IO_cost, action_cost)

        return (cloud_cost, BBU_cost, IO_cost, OPEX)

    def cost_BBB(self, s, relocation, t):
        """
        calculate the cost of the policy CCB
        """
        # cpu
        total_cpu = s["CU"][0] + s["DU"][0] + s["PHY"][0]
        # mem
        total_mem = s["CU"][1] + s["DU"][1] + s["PHY"][1]
        # acc
        total_acc = s["CU"][2] + s["DU"][2] + s["PHY"][2]

        cloud_cost = 0

        BBU_cost = self.calculate_BBU_cost(
            self.CPU,
            self.MEM,
            self.ACC,
            self.cost_per_set,
            total_cpu,
            total_mem,
            total_acc,
        )
        # LA io cost
        IO_cost = self.calculate_IO_cost(s["traffic"][t], s["IO"][0])

        action_cost = self.calculate_action_cost(relocation, self.action_cost)

        OPEX = self.calculate_OPEX(cloud_cost, BBU_cost, IO_cost, action_cost)

        return (cloud_cost, BBU_cost, IO_cost, OPEX)

    def cost_CCB(self, s, relocation, t):
        """
        calculate the cost of the policy CCB
        """
        # cpu
        cloud_cpu = s["CU"][0] + s["DU"][0]
        BBU_cpu = s["PHY"][0]

        # mem
        cloud_mem = s["CU"][1] + s["DU"][1]
        BBU_mem = s["PHY"][1]

        # acc
        cloud_acc = s["CU"][2] + s["DU"][2]
        BBU_acc = s["PHY"][2]

        cloud_cost = self.calculate_cloud_cost(
            s["traffic"][t],
            cloud_cpu,
            cloud_mem,
            cloud_acc,
            self.CPU_cost,
            self.MEM_cost,
            self.X,
        )

        BBU_cost = self.calculate_BBU_cost(
            self.CPU, self.MEM, self.ACC, self.cost_per_set, BBU_cpu, BBU_mem, BBU_acc
        )
        # LA io cost
        IO_cost = self.calculate_IO_cost(s["traffic"][t], s["IO"][2])

        action_cost = self.calculate_action_cost(relocation, self.action_cost)

        OPEX = self.calculate_OPEX(cloud_cost, BBU_cost, IO_cost, action_cost)

        return (cloud_cost, BBU_cost, IO_cost, OPEX)

    def cost_CBB(self, s, relocation, t):
        """
        calculate the cost of the policy CBB
        """
        # cpu
        cloud_cpu = s["CU"][0]
        BBU_cpu = s["DU"][0] + s["PHY"][0]

        # mem
        cloud_mem = s["CU"][1]
        BBU_mem = s["DU"][1] + s["PHY"][1]

        # acc
        cloud_acc = s["CU"][2]
        BBU_acc = s["DU"][2] + s["PHY"][2]

        cloud_cost = self.calculate_cloud_cost(
            s["traffic"][t],
            cloud_cpu,
            cloud_mem,
            cloud_acc,
            self.CPU_cost,
            self.MEM_cost,
            self.X,
        )

        BBU_cost = self.calculate_BBU_cost(
            self.CPU, self.MEM, self.ACC, self.cost_per_set, BBU_cpu, BBU_mem, BBU_acc
        )
        # LA io cost
        IO_cost = self.calculate_IO_cost(s["traffic"][t], s["IO"][1])

        action_cost = self.calculate_action_cost(relocation, self.action_cost)

        OPEX = self.calculate_OPEX(cloud_cost, BBU_cost, IO_cost, action_cost)

        return (cloud_cost, BBU_cost, IO_cost, OPEX)

    def get_score(self):
        """
        calculate the score of the policy
        """
        return max(0, self.baseline_cost / self.OPEX - 1)

    def set_policy(self, policy):
        self.policy = policy

    def cost_updater(self, cloud_costs, BBU_costs, IO_costs):
        
        
        self.cloud_costs.append( cloud_costs)
        self.BBU_costs.append( BBU_costs)
        self.IO_costs.append(IO_costs)

    def cost_builder(self):
        """
        calculate the cost of all slices
        """
        # TODO: add the cost of all slices,关于relocation的问题需要讨论，增加output构建

        
        start = time.time()
        # policy 应该为二维数组[[],[]]
        for t in range(self.T):
            # print("time",t,self.T)
            s_cloud = 0
            s_bbucost = 0
            s_iocost = 0
            for i, s in enumerate(self.slices):
               
                p = self.policy[t][i]
                # print('i',i,'t',t,'policy',p)
                if p == "CCC":
                    output_tuple = self.cost_CCC(s, 0, t)
                    s_cloud += output_tuple[0]
                    s_bbucost += output_tuple[1]
                    s_iocost += output_tuple[2]
                    self.OPEX += self.cost_CCC(s, 0, t)[3]
                elif p == "BBB":
                    output_tuple = self.cost_BBB(s, 0, t)
                    s_cloud += output_tuple[0]
                    s_bbucost += output_tuple[1]
                    s_iocost += output_tuple[2]
                    self.OPEX += self.cost_BBB(s, 0, t)[3]

                elif p == "CCB":
                    output_tuple = self.cost_CCB(s, 0, t)
                    s_cloud += output_tuple[0]
                    s_bbucost += output_tuple[1]
                    s_iocost += output_tuple[2]
                    self.OPEX += self.cost_CCB(s, 0, t)[3]

                elif p == "CBB":
                    output_tuple = self.cost_CBB(s, 0, t)
                    s_cloud += output_tuple[0]
                    s_bbucost += output_tuple[1]
                    s_iocost += output_tuple[2]
                    self.OPEX += self.cost_CBB(s, 0, t)[3]
                else:
                    print("policy error")
            self.cloud_costs.append(s_cloud)
            self.BBU_costs.append(s_bbucost)
            self.IO_costs.append(s_iocost)

        end = time.time()
        self.execution_time = end - start
        self.score = self.get_score()
        print(
            self.policy,
            "\n",
            self.cloud_costs,
            "\n",
            self.BBU_costs,
            "\n",
            self.IO_costs,
            "\n",
            self.OPEX,
            "\n",
            self.score,
            "\n",
            self.execution_time,
        )
        self.export_csv()
        return self.OPEX

    def export_csv(self,output_path="output.csv"):
        """
        export the result to csv
        """
        with open(output_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=" ")
            output_policy = [list(i) for i in zip(*self.policy)]
            writer.writerows(output_policy)
            writer.writerow(self.cloud_costs)
            writer.writerow(self.BBU_costs)
            writer.writerow(self.IO_costs)
            writer.writerow([self.OPEX])
            writer.writerow([self.score])
            writer.writerow([self.execution_time])

            csvfile.close()

    # def calculate_costs(
    #     self,
    #     baseline_cost,
    #     action_cost,
    #     CPU_cost,
    #     MEM_cost,
    #     B,
    #     CPU,
    #     MEM,
    #     ACC,
    #     cost_per_set,
    #     N,
    #     T,
    #     X,
    #     slices,
    # ):
    #     """
    #     calculate the cost of the policy
    #     OPEX=sum(cloud costs, BBU costs, I/O costs, action costs)
    #     BBU sets=max(CPU/CPU_per_set, MEM/MEM_per_set,ACC/ACC_per_set)
    #     BBU cost=cost_per_set*BBU sets
    #     cloud costs=CPU_cost*traffic*CPU_required+MEM_cost*traffic*MEM_required+ACC*X*CPU_cost*traffic
    #     IO costs=traffic*IO_linkUsed
    #     Action costs=action_cost*relocation
    #     """
    #     cloud_costs = [0] * T
    #     # BBU_costs = [cost_per_set * B] * T
    #     BBU_costs = [0] * T
    #     IO_costs = [0] * T
    #     # action_costs = [action_cost * N] * T
    #     action_costs = [0 * N] * T
    #     for s in slices:
    #         for t in range(T):
    #             cloud_costs[t] += (
    #                 (s["CU"][0] + s["DU"][0] + s["PHY"][0])
    #                 * s["traffic"][t]
    #                 * CPU_cost
    #             )
    #             cloud_costs[t] += (
    #                 (s["CU"][1] + s["DU"][1] + s["PHY"][1])
    #                 * s["traffic"][t]
    #                 * MEM_cost
    #             )
    #             IO_costs[t] += s["IO"][0] * s["traffic"][t]

    #     total_costs = [
    #         cloud_costs[t] + BBU_costs[t] + IO_costs[t] + action_costs[t]
    #         for t in range(T)
    #     ]
    #     return cloud_costs, BBU_costs, IO_costs, action_costs, total_costs
