from setuptools import setup

setup(name='benchmark_tools',
      version='0.1',
      description='Benchmark tools',
      url='https://github.com/migeed-z/benchmark_tools.git',
      packages=['benchmark_tools'],
      zip_safe=False,

      entry_points={
        'console_scripts': [
          'zrun = benchmark_tools.zrun:main'
      ]}
)

