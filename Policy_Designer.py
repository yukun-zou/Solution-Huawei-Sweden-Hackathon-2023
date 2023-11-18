# Your solutions will be validated on a Docker container with 4 vCPUs, so we 
# suggest you use at most 4 threads 
# invalid input?
# 贪心？BBUcost和Cloudcost和actioncost是联动的
# IOcost是四选一，这个确定可以直接确定部署策略，但要确认是否valid
# BBU资源如果不够，就要考虑迁移，迁移会导致action cost，
# 迁移后的BBUcost和Cloudcost会变化
class Policy_Designer:
    policy_list=['CCC', 'CCB', 'CBB' , 'BBB']

    def countCost(self, policy_list, inputs):
        pass
    #TODO: implement your policy here

    def policy_output(self):
        policy = 'CCC'
        return (policy)