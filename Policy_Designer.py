# Your solutions will be validated on a Docker container with 4 vCPUs, so we 
# suggest you use at most 4 threads 
# invalid input?
# 贪心？BBUcost和Cloudcost和actioncost是联动的
# IOcost是四选一，这个确定可以直接确定部署策略，但要确认是否valid
# BBU资源如果不够，就要考虑迁移，迁移会导致action cost，
# 迁移后的BBUcost和Cloudcost会变化
import numpy as np

from Cost_Calculator import Cost_Calculator


class Policy_Designer:
    def __init__(self):
        pass

    def policy_output(self, slices, inputs):
        """
        使用贪心算法找到最小OPEX的部署方案
        slices: 服务实例列表
        inputs: 输入参数
        """
        policy_list = ['CCC', 'CCB', 'CBB', 'BBB']
        N = inputs[9]  # 切片数量
        T = inputs[10]  # 时间步长
        X = inputs[11]  # 代表ACC的CPU倍数
        action_cost = inputs[1]  # 每次迁移的成本

        # 初始化一个 N*T 的矩阵，所有元素都是 'CCC'
        policy = np.full((N, T), 'CCC')
        for t in range(T):
            for i in range(N):
                # 尝试替换每个切片的部署策略，计算OPEX
                current_policy = policy.copy()
                for new_policy in ['BBB', 'CCB', 'CBB']:
                    current_policy[i,t] = new_policy
                    opex = self.calculate_opex(slices, current_policy, inputs, t, action_cost)

                    # 如果当前部署策略的OPEX更小，更新部署策略
                    if opex < self.calculate_opex(slices, policy, inputs, t, action_cost):
                        policy[i,t] = current_policy[i,t]

        return policy

    def calculate_opex(self, slices, policy, inputs, t, action_cost):
        """
        计算给定部署策略的OPEX
        """
        OPEX = 0
        cost_calculator = Cost_Calculator(*inputs, policy)

        for i in range(len(slices)):
            p = policy[i][t]
            if t > 0:
                pre_p = policy[i][t - 1]
                difference = sum(c1 != c2 for c1, c2 in zip(p, pre_p))
            if p == 'CCC':
                OPEX += cost_calculator.cost_CCC(slices[i], difference, t)
            elif p == 'BBB':
                OPEX += cost_calculator.cost_BBB(slices[i], difference, t)
            elif p == 'CCB':
                OPEX += cost_calculator.cost_CCB(slices[i], difference, t)
            elif p == 'CBB':
                OPEX += cost_calculator.cost_CBB(slices[i], difference, t)
            #OPEX += cost_calculator.cost_CCC(slices[i], 0, t)  # 默认计算CCC的OPEX，可以根据实际情况替换成其他部署策略的计算方法

        return OPEX

