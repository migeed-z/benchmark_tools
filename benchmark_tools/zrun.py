import os
from benchmark_tools.Runner import run_all
from benchmark_tools.Reader import gen_all

def main():
  if os.path.exists("typed"):
    gen_all("./typed")
    run_all("./Benchmark", "./Test", "output.txt")
  else:
    print("Error: could not find `typed/` folder in current directory.")

if __name__ == "__main__":
  main()
