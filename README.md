# Roofline Generator
![MPI_Roofline](https://github.com/Luca-G17/Roofline_Generator/assets/63655147/8b9a2f0b-9abd-4ad9-9646-2a5c8649e59e)
## Usage 
### Rooflines
Define memory hierarchy rooflines with the highest bandwidth (GB/s) roof in index 0, generally this will be L1 cache. Similary the highest operational intensity (GFLOPS) compute roof should be in index 0, generally this will be a single precision vector operation.
```
memory_roofs = [
    ['L1', 276.62],
    ['L2', 75.70],
    ['L3', 34.94],
    ['DRAM', 12.87]
]

compute_roofs = [
    ['SP Vector FMA', 178.16],
    ['SP Vector Add', 22.32],
    ['SP Scalar Add', 2.8]
]
```

### Input Data
This project is designed to use Intel Advisor's `roofline.data` file containing the relavant data for each loop. However we discard most of the data in the file so the program should work with the following formatting, the $x$ and $y$ coordinates are stored in the format of $\log_{10}(\text{Measured Value})$

```
{
  'loops': [
    {
      '<LOOP_NAME>',
      'x':<X>,
      'y':<Y>
    },
    ...
  ]
}
```
Additionally these `roofline.data` files are stored in the following directory structure, enabling us to average the roofline data across multiple ranks. 
```
<RUN_NAME>
|
|--rank.0
|  |--roofline.data
|
|--rank.1
|  |--roofline.data
```

Finally we can specify which <RUN_NAME> directories to include on the roofline plot and for each run we must specify the <LOOP_NAME> to use the data from: `average_roofline_data(<RUN_NAME>, <LOOP_NAME>)`. As well as the data we can define a list of labels to use for each datapoint.
```
data = [
    average_roofline_data('single_rank', 'timestep'),
    average_roofline_data('baseline_ranks', 'timestep'),
    average_roofline_data('single_rank_1024', 'timestep'),
    average_roofline_data('baseline_rank_1024', 'timestep')
]

labels = [
    '2048 - Single Core', 
    '2048 - Rank Average - 56 Core (2x Nodes)',
    '1024 - Single Core',  
    '1024 - Rank Average - 56 Core (2x Nodes)'
]
```
