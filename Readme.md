# Campus Puzzle Scheduler

## Project Overview
This project implements a university timetable scheduler for the M603 Advanced Algorithms individual project.
The system schedules classes into available time slots and rooms while respecting hard constraints.

## Algorithms Used
1. Greedy baseline scheduling
2. Conflict graph construction and Welsh-Powell graph coloring
3. Dynamic programming room allocation optimisation
4. Recursive backtracking with best-effort conflict reporting

## Input Data
The project uses synthetic scheduling data stored in data/constraints.json.
An external dataset is not required because this is an algorithmic scheduling project.

## Final Results
| Method | Scheduled | Unscheduled | Conflicts | Room Waste |
|---|---:|---:|---:|---:|
| Greedy Baseline | 12 | 0 | 0 | 420 |
| Graph Coloring | 12 | 0 | 0 | 220 |
| Graph Coloring + DP | 12 | 0 | 0 | 220 |
| Backtracking Best Effort | 12 | 0 | 0 | 110 |

## Conflict Report
All classes were scheduled successfully. No manual intervention is required.

## Manual Fix Log
If future datasets produce unscheduled classes, the system will identify each class and reason.
A university manager can then add rooms, add time slots, split large classes, or manually move classes.

## How to Run
Run this command from the project folder:

python main.py

## Requirements
This project uses only Python standard libraries.
