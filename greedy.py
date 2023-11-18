class Policy_Designer:
    def __init__(self):
        pass

    def policy_output(self, slices, inputs):
        """
        使用贪心算法找到最小OPEX的部署方案
        slices: 服务实例列表
        inputs: 输入参数
        """
        N = inputs[9]  # 切片数量
        T = inputs[10]  # 时间步长
        X = inputs[11]  # 代表ACC的CPU倍数
        action_cost = inputs[1]  # 每次迁移的成本

        # 初始化部署策略，初始全部为CCC
        policy = ['CCC'] * N

        for t in range(T):
            for i in range(N):
                # 尝试替换每个切片的部署策略，计算OPEX
                current_policy = policy.copy()
                for new_policy in ['BBB', 'CCB', 'CBB']:
                    current_policy[i] = new_policy
                    opex = self.calculate_opex(slices, current_policy, inputs, t)
                    
                    # 如果当前部署策略的OPEX更小，更新部署策略
                    if opex < self.calculate_opex(slices, policy, inputs, t):
                        policy = current_policy.copy()

        return policy

    def calculate_opex(self, slices, policy, inputs, t):
        """
        计算给定部署策略的OPEX
        """
        opex = 0
        cost_calculator = Cost_Calculator(*inputs, policy)

        for i in range(len(slices)):
            opex += cost_calculator.cost_CCC(slices[i], 0, t)  # 默认计算CCC的OPEX，可以根据实际情况替换成其他部署策略的计算方法

        return opex
