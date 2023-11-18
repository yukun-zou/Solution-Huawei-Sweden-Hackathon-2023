# Your solutions will be validated on a Docker container with 4 vCPUs, so we
# suggest you use at most 4 threads
# invalid input?
# 贪心？BBUcost和Cloudcost和actioncost是联动的
# IOcost是四选一，这个确定可以直接确定部署策略，但要确认是否valid
# BBU资源如果不够，就要考虑迁移，迁移会导致action cost，
# 迁移后的BBUcost和Cloudcost会变化
import numpy as np
import time
from Cost_Calculator import Cost_Calculator


class Policy_Designer:
    """
    policy designer with greedy algorithm
    """

    cost_Calculator = None

    def __init__(self, cost_Calculator):
        self.cost_Calculator = cost_Calculator

    def policy_output(self, slices, inputs):
        """
        使用贪心算法找到最小OPEX的部署方案
        slices: 服务实例列表
        inputs: 输入参数
        """
        policy_list = ["CCC", "CCB", "CBB", "BBB"]
        N = inputs[9]  # 切片数量
        T = inputs[10]  # 时间步长
        action_cost = inputs[1]  # 每次迁移的成本
        total_opex = 0
        # 初始化一个 N*T 的矩阵，所有元素都是 'CCC'
        policy = np.full((N, T), "CCC")
        start = time.time()
        for t in range(T):
            s_cloud = 0
            s_bbucost = 0
            s_iocost = 0
            for i in range(N):
                # 尝试替换每个切片的部署策略，计算OPEX
                difference = 0
                current_opex = self.cost_Calculator.cost_CCC(slices[i], 0, t)[3]
                methods = [
                    getattr(self.cost_Calculator, "cost_" + i) for i in policy_list[1:]
                ]

                for method, p in zip(methods, policy_list[1:]):
                    c, b, io, new_opex = method(slices[i], 0, t)
                    # print("output tuple",c,b,io,new_opex)
                    difference = self.count_difference("CCC", p)
                    if (new_opex + difference * action_cost) < current_opex:
                        current_opex = new_opex
                        policy[i, t] = p
                        s_cloud += c
                        s_bbucost += b
                        s_iocost += io

                self.cost_Calculator.cost_updater(s_cloud, s_bbucost, s_iocost)
                total_opex += current_opex + difference * action_cost
        end = time.time()
        print(
            "policy",
            policy,
            "\ntotal_opex",
            total_opex,
            "\nbase",
            self.cost_Calculator.baseline_cost,
        )
        self.cost_Calculator.set_policy(policy)
        self.cost_Calculator.OPEX = total_opex
        self.cost_Calculator.get_score()
        self.cost_Calculator.execution_time = end - start
        self.cost_Calculator.export_csv()
        return policy, total_opex

    def count_difference(self, p, pre_p):
        difference = sum(c1 != c2 for c1, c2 in zip(p, pre_p))
        return difference

    # def calculate_opex(self, slices, policy, inputs, t, action_cost):
    #     """
    #     计算给定部署策略的OPEX
    #     """
    #     difference = 0
    #     OPEX = 0
    #     cost_calculator = Cost_Calculator(*inputs, policy)

    #     for i,s in enumerate(slices):
    #         p = policy[i][t]
    #         if t > 0:
    #             pre_p = policy[i][t - 1]
    #             difference = sum(c1 != c2 for c1, c2 in zip(p, pre_p))
    #         if p == 'CCC':
    #             OPEX += cost_calculator.cost_CCC(s, difference, t)[3]
    #         elif p == 'BBB':
    #             OPEX += cost_calculator.cost_BBB(s, difference, t)[3]
    #         elif p == 'CCB':
    #             OPEX += cost_calculator.cost_CCB(s, difference, t)[3]
    #         elif p == 'CBB':
    #             OPEX += cost_calculator.cost_CBB(s, difference, t)[3]
    #         #OPEX += cost_calculator.cost_CCC(slices[i], 0, t)  # 默认计算CCC的OPEX，可以根据实际情况替换成其他部署策略的计算方法

    #     return OPEX
