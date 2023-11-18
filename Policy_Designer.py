import numpy as np
import time
import Cost_Calculator

class Policy_Designer:
    """
    Policy designer with the proposed optimization algorithm
    """

    cost_Calculator = None

    def __init__(self, cost_Calculator):
        self.cost_Calculator = cost_Calculator
    def valid_BBU(self,slice,t,bbu_resource):
        """
        Check whether the BBU resource usage is valid
        """
        for i in enumerate(bbu_resource):
            if bbu_resource[i]-slice["IO"][i]*slice["traffic"][t]<0:
                return False
        return True
    def policy_output(self,inputs):
        """
        Use the proposed optimization algorithm to find the deployment strategy with the minimum OPEX
        slices: Service instance list
        inputs: Input parameters
        """
        N = inputs[9]  # Number of slices
        T = inputs[10]  # Time steps
    
        slices = inputs[-1]  # Service instance list
        # Initialize a matrix of size N*T, all elements are 'CCC'
        policy = np.full((N, T), "CCC")
        
        # Arrays to store costs for each timestep
        cloud_costs = []
        bbu_costs = []
        action_costs = []
        total_opex = 0
        start = time.time()

        for t in range(T):
            current_cloud_cost = 0
            current_bbu_cost = 0
            current_io_cost=0
            
            BBU_resource = self.cost_Calculator.BBU_resource
            # Update the BBU resource usage for each slice
            for i in range(N):
                # Find the index of the IO chain with the minimum cost at the current timestep
            
                min_io_index = np.argmin(slices[i]["IO"])
                #计算cost
                ccc_c,ccc_b,ccc_i,opex_ccc = self.cost_Calculator.cost_CCC(slices[i], 0, t)[0]
                
                if min_io_index == 0:#La 最小，BBB
                    #计算BBB是否valid，如果valid，计算cost，如果invalid，直接使用CCC的数据
                    c,b,io,opex_bbb = self.cost_Calculator.cost_BBB(slices[i], 3, t)[0]
                    if opex_bbb<opex_ccc and self.valid_BBU(slices[i],t,BBU_resource):
                        current_cloud_cost += b
                        current_bbu_cost += c
                        current_io_cost += io
                        BBU_resource=[BBU_resource[j]-slices[i]["IO"][j] for j in range(len(BBU_resource))]
                        policy[i, t] = "BBB"
                        total_opex += opex_bbb
                    
                elif min_io_index == 1:#Lb 最小，CBB
                    opex_cbb = self.cost_Calculator.cost_CBB(slices[i], 2, t)[0]
                    if opex_cbb<opex_ccc and self.valid_BBU(slices[i],t,BBU_resource):
                        current_cloud_cost += b
                        current_bbu_cost += c
                        current_io_cost += io
                        BBU_resource=[BBU_resource[j]-slices[i]["IO"][j] for j in range(len(BBU_resource))]
                        policy[i, t] = "CBB"
                        total_opex += opex_cbb
                    
                elif min_io_index == 2:#Lc 最小，CCB
                    opex_ccb = self.cost_Calculator.cost_CCB(slices[i], 1, t)[0]
                    if opex_ccb<opex_ccc and self.valid_BBU(slices[i],t,BBU_resource):
                        current_cloud_cost += b
                        current_bbu_cost += c
                        current_io_cost += io
                        BBU_resource=[BBU_resource[j]-slices[i]["IO"][j] for j in range(len(BBU_resource))]
                        policy[i, t] = "CCB"
                        total_opex += opex_ccb
                   
                    
                else:#Ld 最小，CCC
                    current_cloud_cost += ccc_b
                    current_bbu_cost += ccc_c
                    current_io_cost += ccc_i
                    total_opex += opex_ccc 
                    policy[i, t] = "CCC"
                    
                
            # Update the cost calculator with the accumulated costs for the current timestep
            cloud_costs.append(current_cloud_cost)
            bbu_costs.append(current_cloud_cost)
            action_costs.append(current_bbu_cost)

            # Update the cost calculator with the accumulated costs for the current timestep
        self.cost_Calculator.cost_updater(cloud_costs, bbu_costs, action_costs)

        end = time.time()

        print("Policy:", policy, "\nTotal OPEX:", self.cost_Calculator.OPEX)

        # Export results
        self.cost_Calculator.set_policy(policy)
        self.cost_Calculator.OPEX = sum(cloud_costs) + sum(bbu_costs) + sum(action_costs)
        self.cost_Calculator.get_score()
        self.cost_Calculator.execution_time = end - start
        self.cost_Calculator.export_csv()

        return policy, self.cost_Calculator.OPEX
