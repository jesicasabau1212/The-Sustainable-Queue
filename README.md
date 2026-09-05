
# The Sustainable Queue

A lightweight, percentile-based carbon-aware scheduler that delays flexible compute jobs to lower-carbon grid windows. Tested on simulated ATLAS workloads.

## Motivation

HEP computing consumes significant energy, the WLCG alone uses roughly 1.25 TWh/year across 170+ sites [1]. Carbon intensity of electricity varies substantially depending on the local energy mix, but jobs are typically dispatched the moment resources are free, regardless of how clean or dirty the grid is at that moment. This project tests whether that variation can be exploited to reduce emissions, without changing existing infrastructure.

## Method

The scheduler uses no machine learning or forecasting, but only the current carbon intensity of the local grid. Jobs are held in a queue and released according to tiered percentile thresholds:

- Below the 25th percentile → run immediately
- Below the 50th percentile → run once waited ≥12h
- Below the 75th percentile → run once waited ≥24h
- Always run once waited ≥48h (deadline override)

Workload sizes are converted from HS23 (a standard HEP CPU benchmark) to energy using an approximate site-level power conversion factor, based on typical WLCG benchmarking assumptions [2].

## Experiment design

Four scenarios isolate grid cleanliness from CPU capacity, tested against two contrasting national grids (one variable/renewables-heavy, one stable/nuclear-dominated), each simulated over a full year of hourly data.

|              | 2024 CPU capacity | 1.5× CPU capacity |
|--------------|--------------------|--------------------|
| **2024 grid**       | Scenario 1 | Scenario 3 |
| **2030 grid targets** | Scenario 2 | Scenario 4 |

## Results

- **Variable grid:** 20.7–29.0% reduction in annual emissions, up to ~784,000 tCO2 saved in the best case.
- **Stable grid:** 10.3–12.0% reduction, roughly half the relative impact, due to less carbon-intensity variation to exploit.
- **Key insight:** more hardware alone does not mean more savings. Extra CPU capacity clears the queue too fast for it to wait out dirty windows. Grid decarbonisation and hardware investment need to be planned together.

## Repository structure

src/ Core scheduler implementation (SustainableQueue class)
results/plots/ Emissions, workload, and carbon-intensity plots
results/graphs/ Execution vs queue backlog visualisations

Raw and processed input data (CPU workload logs, national grid carbon-intensity series) are excluded as they are not publicly redistributable.

## Limitations

Jobs are modelled as instantaneous. A fixed HS23-to-Watt conversion factor is used. Only one year of grid data is considered. Idle hardware energy use is not modelled. Reported savings should be treated as a likely upper bound.

## References

[1] D. Britton, S. Campana, B. Panzer-Stradel, "A holistic study of the WLCG energy needs for the LHC scientific program," *EPJ Web of Conf.* 295, 04001 (2024). https://doi.org/10.1051/epjconf/202429504001

[2] Z. Marshall, personal communication, 2025.

## Author

Jesica K. Sabau, Department of Mathematical and Physical Sciences, University of Sheffield
Supervisor: Kristin Lohwasser
