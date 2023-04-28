import re
import os
import pandas as pd
from natsort import natsorted 
import argparse
import subprocess

#pip install natsort

def read_files(dir, result):
    for files_dir in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, files_dir)):
            if dir[-4:] == 'Time':
                list_files = os.listdir(dir)
                name = dir.split("/")[-2]                
                domain = [os.path.join(dir, x) for x in filter(lambda x: x.endswith(".pddl"), list_files)]
                files = [os.path.join(dir, x) for x in filter(lambda x: x.startswith("pfile"), list_files)]
                result.append([name, domain, files])
                break
        elif os.path.isdir(os.path.join(dir, files_dir)):
            read_files(os.path.join(dir, files_dir), result)
    return result

def extract_sol_info_to_csv(results_group_path, planner):
    result = pd.DataFrame(columns=["Planner", "File", "Number_Actions", "Duration", "Search_Time", "States_Evaluated", "Cost"])
    path = os.path.join(results_group_path, planner)
    n_files = 0
    for file in natsorted(os.listdir(path)):
        file_split = file.split('_')[-1:][0]
        with open(path+'/'+file, 'r') as f:
            def_plan = False
            act_cont = 0
            max_dur = 0
            act_plan = False
            for line in f:
                if planner == "lpg":
                    if line.startswith('Number of actions'):
                        states_ev = int(line.strip().split(' ')[-1])
                    elif line.startswith('Total time'):
                        time = float(line.strip().split(' ')[-1])
                    elif line.startswith('Actions'):
                        actions = int(line.strip().split(' ')[-1])
                    elif line.startswith('Duration'):
                        duration = float(line.strip().split(' ')[-1])
                    elif line.startswith('Plan quality'):
                        cost = float(line.strip().split(' ')[-1])
                
                if planner == 'optic':
                    if line.startswith(';;;; Solution Found'):
                        def_plan = True
                    elif line.startswith('; States evaluated:') and def_plan:
                        states_ev = int(line.strip().split(' ')[-1])
                    elif line.startswith('; Time') and def_plan:
                        time = float(line.strip().split(' ')[-1])
                        act_plan = True
                    elif line.startswith('; Cost') and def_plan:
                        cost = float(line.strip().split(' ')[-1])
                    elif def_plan and act_plan:
                        cont = cont + 1
                        actions = cont
                        t = float(line[:line.index(':')])
                        dur = float(line[line.index('[')+1:line.index(']')])
                        durat = t+dur
                        if durat > max_dur:
                            max_dur = durat
                        duration = max_dur
                
                if planner == 'sgplan':
                    states_ev = "-"
                    if line.startswith('; Time'):
                        time = float(line.strip().split(' ')[-1])
                    elif line.startswith('; MetricValue'):
                        cost = float(line.strip().split(' ')[-1])
                    elif line.startswith('; NrActions'):
                        actions = int(line.strip().split(' ')[-1])
                    elif line.startswith('; PlanningTechnique Modified-FF') or (line.startswith('Solution found')):
                        def_plan = True
                    elif def_plan and (len(line.strip())!=0) and not(line.startswith('; ParsingTime')) and not(line.startswith('; MakeSpan')):
                        t = float(line[:line.index(':')])
                        dur = float(line[line.index('[')+1:line.index(']')])
                        durat = t+dur
                        if durat > max_dur:
                            max_dur = durat
                        duration = max_dur   

                if planner == 'lama**':
                    if line.startswith('Duration'):
                        duration = float(line.strip().split(' ')[-1])
                    elif line.startswith('Cost'):
                        cost = float(line.strip().split(' ')[-1])
                    elif line.startswith('States Evaluated'):
                        states_ev = int(line.strip().split(' ')[-1])
                    else:
                        act_cont = act_cont + 1
                        actions = act_cont

        result.loc[n_files] = [planner, file_split, actions, duration, time, states_ev, cost]
        n_files = n_files+1
    return result


def execute_planners(planners_analysed, files, base_path, results_path = None, planners_path = None, timeout = 30):
    
    if results_path == None:
        results_path = os.path.join(base_path, 'results')

    if not os.path.exists(results_path):
        os.makedirs(results_path)

    for i in range(0,len(files)): #for group
        
        group_name = files[i][0]
        
        result_group_path = os.path.join(results_path, group_name)
        
        if not os.path.exists(result_group_path):
            os.makedirs(result_group_path)
        
        
        for d in range(len(files[i][1])): #for domain
            domain = files[i][1][d]
            
            for f in files[i][2]: #for file
                problem_name = f
                f_split = f.split('/')
                
                for pl in planners_analysed: #for planner
                    
                    results_planner_path = os.path.join(result_group_path, pl)
                    
                    if not os.path.exists(results_planner_path):
                        os.makedirs(results_planner_path)
                    
                    sol_name = 'sol_'+group_name+'_'+pl+'_'+f_split[-1:][0]+'.txt'
                    sol = os.path.join(results_planner_path, sol_name)
                    
                    if planners_path != None:
                        if pl == 'lpg':
                            try:
                                subprocess.run(f'{planners_path[planners_analysed.index(pl)]} -o {domain} -f {problem_name} -speed > {sol}', shell=True, timeout=timeout)
                            except subprocess.TimeoutExpired:
                                print(f"The problem {problem_name}, from domain: {domain} with {pl} planner, doesn't reach a solution in {timeout}s.")
                                os.remove(sol)
                                continue

                        elif pl == 'sgplan':
                            try:
                                subprocess.run(f'{planners_path[planners_analysed.index(pl)]} -o {domain} -f {problem_name} > {sol}', shell=True, timeout=timeout)
                            except subprocess.TimeoutExpired:
                                print(f"The problem {problem_name}, from domain: {domain} with {pl} planner, doesn't reach a solution in {timeout}s.")
                                os.remove(sol)
                                continue
                
                        elif pl == 'optic':
                            try:
                                subprocess.run(f'{planners_path[planners_analysed.index(pl)]} {domain} {problem_name} > {sol}', shell=True, timeout=timeout)
                            except subprocess.TimeoutExpired:
                                print(f"The problem {problem_name}, from domain: {domain} with {pl} planner, doesn't reach a solution in {timeout}s.")
                                os.remove(sol)
                                continue
                        
                        """elif pl == 'lama**':
                            try:
                                subprocess.run(f'{planners_path[planners_analysed.index(pl)]}', shell=True, timeout=timeout)
                            except subprocess.TimeoutExpired:
                                print(f"The problem {problem_name}, from domain: {domain} with {pl} planner, doesn't reach a solution in {timeout}s.")
                                continue"""
                    else:

                        if pl == 'lpg':
                            try: 
                                subprocess.run(f"~/Downloads/LPG-td-1.4/lpg-td -o {domain} -f {problem_name} -speed > {sol}", shell= True, timeout=timeout)
                            except subprocess.TimeoutExpired:
                                print(f"The problem {problem_name}, from domain: {domain} with {pl} planner, doesn't reach a solution in {timeout}s.")
                                os.remove(sol)
                                continue
                
                        elif pl == 'sgplan':
                            try:
                                subprocess.run(f"/home/malola/Downloads/LPG-td-1.4/sgplan522 -o {domain} -f {problem_name} > {sol}", shell=True, timeout=timeout)
                            except subprocess.TimeoutExpired:
                                print(f"The problem {problem_name}, from domain: {domain} with {pl} planner, doesn't reach a solution in {timeout}s.")
                                os.remove(sol)
                                continue
                
                        elif pl == 'optic':
                            try: 
                                subprocess.run(f"/home/malola/Downloads/LPG-td-1.4/optic {domain} {problem_name} > {sol}", shell= True, timeout=timeout)
                            except subprocess.TimeoutExpired:
                                print(f"The problem {problem_name}, from domain: {domain} with {pl} planner, doesn't reach a solution in {timeout}s.")
                                os.remove(sol)
                                continue
                        
                        """elif pl == 'lama**':
                            try:
                                subprocess.run(f'', shell=True, timeout=timeout)
                            except subprocess.TimeoutExpired:
                                print(f"The problem {problem_name}, from domain: {domain} with {pl} planner, doesn't reach a solution in {timeout}s.")
                                continue"""
                        
                        
        df_group = {}
        df_general = pd.DataFrame()
        for pl_an in planners_analysed:
            locals()['df_'+pl_an] = extract_sol_info_to_csv(result_group_path, pl_an)
            df_group[pl_an] = locals()['df_'+pl_an]
            df_general = pd.concat([df_general, locals()['df_'+pl_an]])

        excel_pl_name = 'results_planners_'+group_name+'.xlsx'
        excel_pl_path = os.path.join(base_path, excel_pl_name)
        with pd.ExcelWriter(excel_pl_path) as writer:
            for planner_name, df_planner in df_group.items():
                df_planner.to_excel(writer, sheet_name=planner_name, index=False) 
        
        excel_name = 'results_'+group_name+'.csv'
        excel_path = os.path.join(base_path, excel_name)
        df_general.to_csv(excel_name, index=False)
        print(f"Done. {excel_name} is saved!")
        

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--planners_analysed", help="List of planners analysed")
    parser.add_argument("-d", "--base_path", help="Path from the main directory")
    parser.add_argument("-r", "--results_path", help="(optional) Path where results will be saved.", required= False)
    parser.add_argument("-pp", "--planners_path", help="(optional) The path where the planners analysed are located.", required= False)
    parser.add_argument("-t", "--timeout", help="(optional) Maximum time that planners' search can take.", required= False)
    
    args = parser.parse_args()
    
    base_path = args.base_path #"/home/malola/ICAPS/IPC3"
    planners_analysed = args.planners_analysed.split() #["lpg"]
    results_path = args.results_path
    planners_path = args.planners_path
    if planners_path != None:
        planners_path = planners_path.split()                                                                                                                                                                                                                                                                           
    timeout = int(args.timeout)

    unsorted_files = read_files(base_path, [])
    files = natsorted(unsorted_files, key=lambda x: x[1])
    execute_planners(planners_analysed, files, base_path, results_path, planners_path, timeout)


if __name__ == '__main__':
    main()
    
