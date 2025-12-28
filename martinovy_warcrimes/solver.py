from preprocessing import *


class Solver():
    def __init__(self, shapes, obstacles, ROWS, COLS):
        self.ROWS = ROWS
        self.COLS = COLS
        self.uv, self.intervals = create_unique_variants(shapes + [[[1]]])
        self.uv_flat = [flatten(s, COLS) for s in self.uv]
        self.table = get_invalid_offset_table(self.uv_flat, self.intervals, COLS)
        self.interval_sets = get_interval_sets(self.intervals)

        self.end = rc2offset([ROWS - 1, COLS - 1], COLS) + 1
        self.all_uv_indicies = set(range(len(self.uv) - 1))
        self.obstacle_uvf_index = len(self.uv) - 1

        self.obstacle_indices = [rc2offset(obstacle, COLS) for obstacle in obstacles]
        self.obstacle_indices.sort()


    def print_solution(self, solution):
        grid = ['_' for _ in range(self.ROWS * self.COLS)]
        for i, item in enumerate(solution):
            marker = chr(ord('a')+i)
            if item[0] == self.obstacle_uvf_index:
                marker = '#'

            for j, element in enumerate(self.uv_flat[item[0]]):
                index = item[1] + j
                if element == 1:
                    grid[index] = marker

        for obstacle_index in self.obstacle_indices:
            grid[obstacle_index] = 'X'

        for r in range(self.ROWS):
            start = r*self.COLS
            end = (r+1)*self.COLS
            print(grid[start:end])
        print(f"\n{solution}")
        print("=============\n\n")


    def check_filling(self, solution):
        if len(solution) == 0:
            return -1

        grid = [-1] * self.ROWS * self.COLS
        for solution_index, solution_item in enumerate(solution):
            shape_flat = self.uv_flat[solution_item[0]]
            for i in range(len(shape_flat)):
                if shape_flat[i] == 0:
                    continue
                index = solution_item[1] + i
                if index >= self.ROWS * self.COLS:
                    break
                grid[index] = solution_index

        last_item = solution[-1]
        if -1 not in grid[:last_item[1]]:
            return -1
        space_index = grid[:last_item[1]].index(-1)
        for solution_index, solution_item in enumerate(solution):
            if space_index <= solution_item[1]:
                return  space_index





    def find_candidate(self, solution, current_offset, min_candidate_index=0):
        available_indices_set = self.all_uv_indicies.copy()
        for solution_item in solution:
            used_indices = self.interval_sets[solution_item[0]]
            available_indices_set = available_indices_set.difference(used_indices)

        available_indices = list(available_indices_set)
        available_indices.sort()

        for candidate in available_indices:
            if candidate < min_candidate_index:
                continue
            candidate_offset = -1
            candidate_length = len(self.uv_flat[candidate])
            candidate_offset_ok = False

            while not candidate_offset_ok:
                candidate_offset_ok = True
                for solution_item in solution:
                    distance = current_offset + candidate_offset - solution_item[1]
                    if distance in self.table[solution_item[0]][candidate]:
                        candidate_offset += 1
                        candidate_offset_ok = False
                        break

                candidate_width = len(self.uv[candidate][0])
                offset_col = (current_offset + candidate_offset) % self.COLS
                if offset_col + candidate_width > self.COLS:
                    candidate_offset += 1
                    candidate_offset_ok = False

                if current_offset + candidate_offset + candidate_length > self.end:
                    candidate_offset_ok = False
                    break

            if not candidate_offset_ok:
                continue

            for obstacle in self.obstacle_indices:
                distance = obstacle - current_offset - candidate_offset
                if distance in self.table[candidate][self.obstacle_uvf_index]:
                    candidate_offset_ok = False

            if not candidate_offset_ok:
                continue

            return (candidate, current_offset + candidate_offset)

        return None


    def solve(self):
        current_offset = 0
        solution = []

        longest = 0

        target_shape_count = len(self.intervals) - 1
        shape_count = 0
        first_shape_index = -1
        last_variant = -1
        variant_cnt = len(self.uv_flat) - 1

        while True:
            # self.print_solution(solution)

            if shape_count > 1:
                variant = solution[first_shape_index][0]
                if variant != last_variant:
                    last_variant = variant
                    print(f"State-space search progress: {variant+1} / {variant_cnt}")

            # if len(solution) > longest:
            #     longest = len(solution)
            #     print(f"{shape_count} / {target_shape_count}")
                # self.print_solution(solution)

            if shape_count == target_shape_count:
                print(f"Solution found: {solution}")
                self.print_solution(solution)
                return solution


            if current_offset in self.obstacle_indices:
                solution.append(
                    (self.obstacle_uvf_index, current_offset)
                )
                current_offset += 1
                continue


            next_item = self.find_candidate(solution, current_offset)

            if next_item is not None:
                next_offset = next_item[1] + 1
                for skipped_offset in range(current_offset+1, next_offset):
                    if skipped_offset in self.obstacle_indices:
                        solution.append(
                            (self.obstacle_uvf_index, skipped_offset)
                        )
                current_offset = next_offset
                solution.append(next_item)
                shape_count += 1
                if shape_count == 1:
                    first_shape_index = len(solution) -1
                if self.check_filling(solution) == -1:
                    continue


            fillcheck = self.check_filling(solution)
            if fillcheck != -1:
                for si in solution[fillcheck + 1:]:
                    if si[0] != self.obstacle_uvf_index:
                        shape_count -= 1
                solution = solution[:fillcheck + 1]


            while True:
                if len(solution) == 0:
                    print("Its joever")
                    return None

                while solution[-1][0] == self.obstacle_uvf_index:
                    solution.pop()
                    if len(solution) == 0:
                        print("No solution found")
                        return None

                last_item = solution.pop()
                shape_count -= 1
                current_offset = 0
                if len(solution) != 0:
                    current_offset = solution[-1][1] + 1
                replacement = self.find_candidate(solution, current_offset, last_item[0] + 1)

                if replacement is not None:
                    replacement_offset = replacement[1] + 1
                    for skipped_offset in range(current_offset, replacement_offset):
                        if skipped_offset in self.obstacle_indices:
                            solution.append(
                                (self.obstacle_uvf_index, skipped_offset)
                            )
                    current_offset = replacement_offset
                    solution.append(replacement)
                    shape_count += 1
                    if shape_count == 1:
                        first_shape_index = len(solution) -1
                    if self.check_filling(solution) == -1:
                        break







