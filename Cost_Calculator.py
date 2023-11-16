class Cost_Calculator:

    def calculate_costs(baseline_cost, action_cost, CPU_cost, MEM_cost, B, CPU, MEM, ACC, cost_per_set, N, T, X,
                        slices):
        cloud_costs = [0] * T
        #BBU_costs = [cost_per_set * B] * T
        BBU_costs = [0] * T
        IO_costs = [0] * T
        #action_costs = [action_cost * N] * T
        action_costs = [0 * N] * T
        for slice in slices:
            for t in range(T):
                cloud_costs[t] += (slice['CU'][0] + slice['DU'][0] + slice['PHY'][0]) * slice['traffic'][t] * CPU_cost
                cloud_costs[t] += (slice['CU'][1] + slice['DU'][1] + slice['PHY'][1]) * slice['traffic'][t] * MEM_cost
                IO_costs[t] += slice['IO'][0] * slice['traffic'][t]

        total_costs = [cloud_costs[t] + BBU_costs[t] + IO_costs[t] + action_costs[t] for t in range(T)]
        return cloud_costs, BBU_costs, IO_costs, action_costs, total_costs