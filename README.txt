# file_read_execution.py

## Goal
This scripts searches the directory where the domain (a file that ends with '.pddl') and the problems (files that start with pfile...)
are saved in the IPC3 folder, type Time. Every problem is excuted using the planners introduced (sgplan, optic, lpg and/or lama**), with the timeout desired. 
Its solutions are saved and cvs and excels files are generated. 

## Requirements
``pip install natsort
pip install xlsxwriter`` 

## Inputs
file_read_execution.py can receive as input in the cmd: 
    -p: String with the name of the planners that are going to be analysed. Just "sgplan", "lpg", "optic" and "lama**" are included. *IMPORTANT: WRITTEN THIS WAY.
    -d: Path of the main directory, the base path.
    -r: (OPTIONAL) Path where results will be saved. By default, results are saved in the base path in a folder name results. 
    -pp: (OPTIONAL) The path where the planners analysed are located. *IMPORTANT: same order as -p.
    -t: (OPTIONAL) Maximum time that planners' search can take in seconds. By default it is 30s. 

## Execution example
Example execution file_read_execution.py in cmd: 
``python -u file_read_execution.py -p "sgplan lpg" -d "/home/malola/ICAPS/IPC3" -t 120``

## Outputs
This script has no outputs, but it generates a folder called results, divided by group task's folders that are also divided by planner's folders where the solutions are saved. 
It also creates CSV and excel files for every group task solution. 



# Table_tracks.ipynb
## Goal
This notebook opens the CSV and computes the tables for:
 - OPTIONAL TRACK: The score of a planner is the number of solved tasks. 
 - AGILE TRACK: The score of a planner on a solved task is 1 if the task was solved within 1 second and 0 if the task was not solved within the resource limits. If the task was solved in T seconds (1 ≤ T ≤ "timeout") then its score is 1 - log(T)/log("timeout"). 
                The score of a planner is the sum of its scores for all tasks.
Based on IPC2023 competition metrics: https://ipc2023-classical.github.io/ 

## Requirements
This file required Jupyter to be executed (i.e. Jupyter Notebooks, VisualStudio with Jupyter Extension, Google Colabs...)
And it also must be saved in the same directory as the "results_Deports.csv", etc. 


