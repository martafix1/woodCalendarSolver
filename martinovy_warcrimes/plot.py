import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV
df = pd.read_csv("report.csv")

# Plot histogram of the 'time' column
plt.figure()
# plt.xscale("log")
plt.xlim(0, 2)
median_time = df["time"].median()
print(f"Median time: {median_time:.3f} s")

plt.hist(df["time"], bins=3000)
plt.axvline(median_time, linestyle=":", linewidth=2, label=f"Median = {median_time:.3f}")


plt.xlabel("Time [s]")
plt.ylabel("Count [-]")
plt.title("Ez")

plt.show()
