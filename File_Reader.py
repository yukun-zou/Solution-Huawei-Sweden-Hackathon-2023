class File_Reader:

    def __init__(self, file_path):
        self.file_path = file_path
        self.lines = []

    def read_input(self):
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
        return [line.strip() for line in lines]

    def parse_input(self, lines):
        baseline_cost, action_cost = map(int, lines[0].split())
        CPU_cost, MEM_cost = map(int, lines[1].split())
        B, CPU, MEM, ACC, cost_per_set = map(int, lines[2].split())
        N, T, X = map(int, lines[3].split())

        slices = []
        line_index = 4
        for _ in range(N):
            slices.append({
                'CU': list(map(int, lines[line_index].split())),
                'DU': list(map(int, lines[line_index + 1].split())),
                'PHY': list(map(int, lines[line_index + 2].split())),
                'IO': list(map(int, lines[line_index + 3].split())),
                'traffic': list(map(int, lines[line_index + 4].split()))
            })
            line_index += 5

        return baseline_cost, action_cost, CPU_cost, MEM_cost, B, CPU, MEM, ACC, cost_per_set, N, T, X, slices

