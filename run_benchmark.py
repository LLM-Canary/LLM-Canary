import pytest
import yaml

import importlib
from datetime import datetime
from testing_functions import *
import check_env

from get_testing_scores import *

benchmark_file = 'benchmark.yaml'
test_config_file = 'to_customize/test_config.yaml'
custom_tests_file = 'to_customize/custom_prompts.yaml'

# Log files for raw test output (prompts/responses), LLM group scores, benchmark scores for multiple LLMs
raw_output_file = 'logs/raw_output_'
llm_benchmark_file = 'scorecard/benchmark/llm_benchmark_'
canary_benchmark_file = 'scorecard/benchmark/canary_benchmark_'

TEST_RUNS=25

def call_llm(system_prompts, cases, env_vars, bench_temp):
    '''
    Opens the model_calls run_[PLATFORM].py files and calls the model API
    '''
    path_to_platform = 'to_customize.model_calls.run_' + env_vars['PLATFORM'].lower()
    llm_model = importlib.import_module(path_to_platform)
    prompts_only, input_prompts, expected = llm_model.clean_input(system_prompts, cases)
    response = llm_model.run_model(env_vars, input_prompts, bench_temp)
    cleaned_response = llm_model.clean_output(response)
    return prompts_only, cleaned_response, expected

def pull_test_groups_from_config():
    '''
    Opens the test_config.yaml and pulls the test_groups to run.
    Separates test_groups by test_suite (benchmark vs custom)
    '''
    
    with open(test_config_file, 'r+') as file:
        config_data = yaml.safe_load(file)
        test_groups = dict()
        for test in config_data:
            if test.lower() == 'benchmark':
                with open(benchmark_file, 'r+') as benchmark:
                    benchmark_groups = yaml.safe_load(benchmark)
                    for test_group in benchmark_groups:
                        key_name = 'Benchmark-' + test_group
                        test_groups[key_name] = benchmark_groups[test_group]
                pass
            elif test is not None:
                with open(custom_tests_file, 'r+') as custom_file:
                    custom_groups = yaml.safe_load(custom_file)
                    for test_group in custom_groups:
                        key_name = 'Custom-' + test_group
                        if test.lower() == test_group.lower():
                            test_groups[key_name]= custom_groups[test_group]
    return test_groups
  
     
def get_log_filename(results,output_filename):
    '''
    Returns the name of the output file based on the time of the test run.
    '''
    
    current_time = datetime.now().strftime("%m.%d.%Y_%H.%M")
    filename = output_filename + current_time + ".yaml"      
    return filename

def append_to_yaml(results, filename):
    '''
    Adds results to the end of an existing .yaml
    '''
    current_time = datetime.now().strftime("%m.%d.%Y_%H.%M")
    results['time'] = current_time

    with open(filename, 'a+') as file:
        documents = yaml.dump(results, file)  
        
    
def save_to_yaml(results, output_filename):
    '''
    Takes the results from the test run and saves it to a yaml file on a per-LLM basis.
    '''
    now = datetime.now()
    current_time = now.strftime("%m.%d.%Y_%H.%M")
    results['time'] = current_time
    
    filename = output_filename + results['ID'].lower() + '_' + current_time + ".yaml"
    
    with open(filename, 'a+') as file:
        documents = yaml.dump(results, file)                  
        
    return filename
   
    
def run_testing_tool():
    '''
    The central testing function. Loops through every test_case within the benchmark, applies scoring, then calculates the benchmark scores.
    '''
    
    test_runs=TEST_RUNS
    
    results = []
    llms = check_env.read_env()    
    test_groups = pull_test_groups_from_config()

    canary_data = dict()
    canary_data['canary_benchmarks'] = {}  
    canary_filename = get_log_filename(canary_data, canary_benchmark_file)
    
    for llm_env_vars in llms:            
        benchmark_data = dict()        
        benchmark_data['ID'] = llm_env_vars['ID']
        benchmark_data['llm_platform'] = llm_env_vars['PLATFORM']
        benchmark_data['llm_model'] = llm_env_vars['MODEL']
        benchmark_data['b_test_scores'] = {}   # multiple test scores by test_id
        benchmark_data['b_group_scores'] = {}    # multiple group scores by testsuite run
        benchmark_data['llm_group_score'] = {}   # multiple group scores for an llm run

        
        # llm_test is a dictionary that stores all necessary values for doing anaylsis/generating scorecard. For each LLM run, it is stored in results. test_cases stores the details for each test_case run under that llm
        llm_test = dict()
        llm_test['ID'] = llm_env_vars['ID']
        llm_test['llm_platform'] = llm_env_vars['PLATFORM']
        llm_test['llm_model'] = llm_env_vars['MODEL']
        llm_test['llm_group_score'] = {}
        llm_test['test_group_score'] = {}
            
        # loop through benchmark test runs for an LLM
        for test_run in range(test_runs):
            
            canary_data['llm_test_runs'] = test_run+1

            llm_test['llm_test_run'] = test_run+1
            llm_test['test_cases'] = []
            
            benchmark_data['llm_test_run'] = test_run+1
            benchmark_data['llm_benchmarks'] = {}
            b_group_scores=[] # group scores for a single group run, for benchmark group calculation
            llm_test['test_cases_log'] = {}

            # loop through tests in a group
            for test_group in test_groups.keys():
                test_case_summary = dict()
                test_case_summary['LLM_ID'] = llm_test['ID']
                test_case_summary['llm_test_run'] = test_run +1                       

                b_test_scores=[] # individual scores for a single test, for group score calculation
                
                # testing occurs at the test_case level
                for test_case in test_groups[test_group]:
                    # test_case_summary stores all of the details for doing analysis/generating scorecard. 
                    # After a test runs, it is appended to llm_test['test_cases']
                    test_case_summary['test_group'] = test_group
                    test_case_summary['test_type'] = test_case['test_type'].strip()
                    test_case_summary['test_id'] = test_case['id']
                    test_case_summary['system_prompt'] = test_case['system_prompt']
                    test_case_summary['cases'] = test_case['cases']
                    test_case_summary['test_risk_weight'] = test_case['test_risk_weight']
                    test_case_summary['results_risk_level'] = test_case['results_risk_level']

                    print(f'\n ----- TESTING -- RUN {test_run+1} -----\nLLM: {test_case_summary["LLM_ID"]} Test Group: {test_case_summary["test_group"]}, ID: {test_case_summary["test_id"]}')


                    if 'benchmark' in test_case_summary['test_group']:
                        bench_temp = 1
                    else:
                        bench_temp = -1

                    # call LLM
                    test_case_summary['prompts'], test_case_summary['responses'], test_case_summary['expected_all'] = call_llm(test_case_summary['system_prompt'], test_case_summary['cases'], llm_env_vars, bench_temp)

                    # call testing function
                    test_case_summary = choose_test(test_case_summary)

                    # get test risk score, save the score to benchmark and test_case_summary
                    test_score = get_benchmark_test_score(test_case_summary, benchmark_data['b_test_scores'])
                    b_test_scores.append(test_score)
                    print ("test score:", test_score)

                    # save the test data for this test run
                    results.append(test_case_summary)
            
                    if test_group not in llm_test['test_cases_log']:
                        llm_test['test_cases_log'][test_group]={}
                    llm_test['test_cases_log'][test_group][test_case['id']]=test_case_summary.copy()

                ### End loop for a test group     
                print ("test group scores:", b_test_scores)

                # calculate group score for the tests in a group                
                group_score = get_benchmark_group_score(test_case_summary, b_test_scores, benchmark_data['b_group_scores'])
                llm_test['test_group_score'][test_case_summary['test_group']] = group_score
                print ("group mean score:", group_score)

            ### End loop for all test groups          

            # calculate the benchmark per run by group score
            for test_group in test_groups.keys():
                llm_group_score = get_benchmark_score(test_group, benchmark_data, canary_data['canary_benchmarks'])               
                benchmark_data['llm_group_score'][test_group]=llm_group_score
                llm_test['llm_group_score'][test_group]=llm_group_score
                print ("llm group score:", test_group, llm_group_score)
                
            # save test and score results to log files 
            save_to_yaml(llm_test, raw_output_file)
            save_to_yaml(benchmark_data, llm_benchmark_file)

        ### End loop for an llm run         

        # Save benchmark data after every LLM run for backup - in case of timeouts
        append_to_yaml(canary_data, canary_filename)
        

    ### End loop for all llms 
    # calculate the final canary benchmark score here for all runs   
    canary_data['opera_benchmarks']={}
    for test_group in test_groups.keys():
        canary_data['opera_benchmarks'][test_group] = get_canary_benchmark_score(test_group, canary_data['canary_benchmarks'][test_group])    
        
        print ('canary benchmark scores', canary_data['opera_benchmarks'])
    
    append_to_yaml(canary_data, canary_filename)
 
    # results is a list of all llm_tests run
    return results


@pytest.mark.parametrize('results', run_testing_tool())
def test_run_tests(results):
    '''
    Runs run_testing_tool() through pytest which checks the tests and displays the results in the CLI.
    '''
    assert results['test_results'], f"LLM: {results['LLM_ID']}. Summary: {results['test_results']}; {results['test_results_detail']}" 

