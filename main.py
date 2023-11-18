from Cost_Calculator import Cost_Calculator
from File_Reader import File_Reader
from Policy_Designer import Policy_Designer



def main():
    file_path = 'testcases/case1.txt'  #test_case

    reader = File_Reader(file_path)
    lines = reader.read_input()
    print(lines)
    inputs = reader.parse_input(lines)

    designer = Policy_Designer()
    policy = designer.policy_output(inputs[-1], inputs)
    print(policy)
    
    cost_builder=Cost_Calculator(*inputs,['CCB']*len(inputs[-1]))

    costs = cost_builder.cost_builder()
    print(costs)
    # for t in range(inputs[9]):
    #     print(
    #         f"Time {t + 1}: Cloud costs: {costs[0][t]}, BBU costs: {costs[1][t]}, \
    #         I/O costs: {costs[2][t]}, Action costs: {costs[3][t]}, \
    #         Total costs: {costs[4][t]}")
    

if __name__ == '__main__':
    main()
