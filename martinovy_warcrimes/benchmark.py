import time
import csv

from solver import *





def run_benchmark(shapes, fixed_obstacles, ROWS, COLS):
    months = []
    for i in range(6):
        for j in range(2):
            months.append([j, i])

    days = [[6,0],[6,1],[6,2]]
    for i in range(7):
        for j in range(4):
            days.append([2+j, i])

    daynames = [[6, 3]]
    for i in range(3):
        for j in range(2):
            daynames.append([6+j, 4+i])

    OK = 0
    NOK = 0
    TOTAL = 0

    with open("report.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow(["month_row","month_col","day_row","day_col","dayname_row","dayname_col","time","success"])

        t0 = time.time()
        for ob1 in months:
            for ob2 in daynames:
                for ob3 in days:
                    TOTAL += 1
                    obstacles = fixed_obstacles.copy()
                    obstacles.extend([ob1,ob2,ob3])

                    csv_row = []
                    csv_row.extend(ob1)
                    csv_row.extend(ob2)
                    csv_row.extend(ob3)

                    t_sol = time.time()
                    s = Solver(shapes, obstacles, ROWS, COLS)
                    solution = None
                    try:
                        solution = s.solve()
                    except:
                        pass
                    t_sol = time.time() - t_sol
                    csv_row.append(t_sol)

                    if solution is None:
                        NOK += 1
                        csv_row.append(0)
                    else:
                        OK += 1
                        csv_row.append(1)

                    writer.writerow(csv_row)
                    csv_file.flush()

                    dt = time.time() - t0
                    print(f"\n  OK: {OK}, NOK: {NOK}, TOTAL: {TOTAL}")
                    print(f"  Solution rate: {TOTAL/dt:.3f} sol/s")
                    print(f"  Solution time: {dt/TOTAL:.3f} s/sol")
                    print(f"  Elapsed time: {dt:.3f} s\n")

    dt = time.time() - t0
    print("\n\n==========================================\n")
    print("            BENCHMARK FINSHED\n")
    print(f" OK: {OK}, NOK: {NOK}, TOTAL: {TOTAL}")
    print(f"Solution rate: {TOTAL/dt:.3f} sol/s")
    print(f"Solution time: {dt/TOTAL:.3f} s/sol")
    print(f"Elapsed time: {dt:.3f} s\n")
    print("\n\n==========================================")





