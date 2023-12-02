import pytest
import yaml
import importlib
import os
from datetime import datetime

from testing_functions import *
import check_env
from get_testing_scores import *

test_config_file = 'to_customize/test_config.yaml'
benchmark_file = 'benchmark.yaml'
custom_tests_file = 'to_customize/custom_prompts.yaml'
results_folder = 'scorecard/results/'

# local
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

# local
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
  
# local
def save_to_yaml(results):
    '''
    Takes the results from the test run and saves it to a yaml file on a per-LLM basis.
    '''
    now = datetime.now()
    current_time = now.strftime("%m.%d.%Y_%H.%M")
    results['time'] = current_time
    filename = "scorecard/results/" + results['ID'].lower() + '_' + current_time + ".yaml"
    if not os.path.exists(results_folder):
        os.mkdir(results_folder)
    with open(filename, 'a+') as file:
        documents = yaml.dump(results, file)                  
    print('---------- FILE SAVED ---------')
        
# local
def run_testing_tool():
    '''
    The central testing function. Loops through every test_case within every configured test_group for every configure LLM, gets a pass/fail, applies a score, saves the results to a .yaml for the scorecard, and returns the results for the CLI pytest.
    '''
    results = []
    llms = check_env.read_env()
    
    test_groups = pull_test_groups_from_config()
    
    for llm_env_vars in llms:
        # llm_test is a dictionary that stores all necessary values for doing anaylsis/generating scorecard. For each LLM run, it is stored in results. test_cases stores the details for each test_case run under that llm
        llm_test = dict()
        llm_test['ID'] = llm_env_vars['ID']
        llm_test['llm_platform'] = llm_env_vars['PLATFORM']
        llm_test['llm_model'] = llm_env_vars['MODEL']
        llm_test['test_cases'] = []    
        llm_test['test_group_score'] = dict()
        
        for test_group in test_groups.keys():
         
            test_group_scores=[] # save individual scores for test group score calculation

            # testing occurs at the test_case level
            for test_case in test_groups[test_group]:
                try:
                    # test_case_summary stores all of the details for doing analysis/generating scorecard. 
                    # After a test runs, it is appended to llm_test['test_cases']
                    test_case_summary = dict()
                    test_case_summary['LLM_ID'] = llm_test['ID']
                    test_case_summary['test_group'] = test_group
                    test_case_summary['test_type'] = test_case['test_type'].strip()
                    test_case_summary['test_id'] = int(test_case['id'])
                    test_case_summary['system_prompt'] = test_case['system_prompt']
                    test_case_summary['cases'] = test_case['cases']
                    test_case_summary['test_risk_weight'] = test_case['test_risk_weight']
                    test_case_summary['results_risk_level'] = test_case['results_risk_level']

                    print(f'\n----- TESTING -----\nLLM: {test_case_summary["LLM_ID"]} Test Group: {test_case_summary["test_group"]}, ID: {test_case_summary["test_id"]}')
                    # call LLM
                    if 'benchmark' in test_case_summary['test_group']:
                        bench_temp = 1
                    else:
                        bench_temp = -1

                    test_case_summary['prompts'], test_case_summary['responses'], test_case_summary['expected_all'] = call_llm(test_case_summary['system_prompt'], test_case_summary['cases'], llm_env_vars, bench_temp)

                    # call testing function
                    test_case_summary = choose_test(test_case_summary)

                    # calculate test risk score for a single test
                    test_case_summary['test_score'] = t_risk_score(test_case_summary)

                    test_group_scores.append(test_case_summary['test_score'])

                    llm_test['test_cases'].append(test_case_summary)
                    results.append(test_case_summary)
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}\nSkipping test case.")


            # calculate group test score and save to llm_test file
            group_risk_score = t_group_risk_score(test_group_scores)
            llm_test['test_group_score'][test_case_summary['test_group']] = group_risk_score
        
        # save results to yaml file on a per llm basis
        save_to_yaml(llm_test)
    # results is a list of all llm_tests run
    return results

# public
@pytest.mark.parametrize('results', run_testing_tool())
def test_run_tests(results):
    '''
    Runs run_testing_tool() through pytest which checks the tests and displays the results in the CLI.
    '''
    assert results['test_results'], f"LLM: {results['LLM_ID']}. Summary: {results['test_results']}; {results['test_results_detail']}" 
