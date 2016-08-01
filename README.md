benchmark_tools
===

Tools for running [Reticulated Python](http://github.com/mvitousek/reticulated) benchmarks.



Install
---

```
python setup.py install
```

(You may need root permissions)



Usage
---

1. Change directory to the program you want to benchmark.
2. Make sure all code is in a `./typed` sub-directory and is fully-typed Reticulated Python code.
3. Type `zrun 0` or (`zrun 1` for random sampling) and hit enter.
4. Wait.
5. Check `./output.txt` for results
