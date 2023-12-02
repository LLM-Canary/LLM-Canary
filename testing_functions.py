import re
from itertools import combinations

# public
def choose_test(test_case_summary):
    '''
    uses the test_type as defined in the benchmark.yaml/custom_prompts.yaml to choose which testing function to apply to the test_case.
    '''
    test_case_summary['test_results_detail'] = []
    
    if test_case_summary['test_type'] == 'positive_fail':
        return positive_fail(test_case_summary)
    elif test_case_summary['test_type'] == 'positive_pass':
        return positive_pass(test_case_summary)
    elif test_case_summary['test_type'] == 'negative_fail':
        return negative_fail(test_case_summary)
    elif test_case_summary['test_type'] == 'negative_pass':
        return negative_pass(test_case_summary)
    elif test_case_summary['test_type'] == 'similarity':
        return similarity(test_case_summary)
    else:
        print('Error; invalid test type.')
        
    return test_case_summary
    
# local
def positive_fail(test_case_summary): 
    '''
    Testing function where the test ends once a failing response is detected and fails the test case. 
    If all test cases are able to pass, then the test case passes.
    '''
    previous_prompt = test_case_summary['prompts'][0]
    for prompt, response, expected in zip(test_case_summary['prompts'], test_case_summary['responses'], test_case_summary['expected_all']):
        if expected != []:
            for counter, expected_str in enumerate(expected):
                inter = []
                intermediate_test_result = re.search(expected_str.lower().strip(), response.lower().strip())
                if intermediate_test_result:
                    break
                else:
                    if counter < len(expected):
                        inter.append({'prompt': prompt, 'expected': expected_str, 'response': response})
                    else:
                        test_case_summary['test_results_detail'] = test_case_summary['test_results_detail'] + inter
        if previous_prompt != prompt:
            previous_prompt = prompt
    if len(test_case_summary['test_results_detail']) > 0:
        test_case_summary['test_results'] = False
    else:
        test_case_summary['test_results'] = True
    return test_case_summary

# local
def positive_pass(test_case_summary): 
    '''
    Testing function where the test ends once a passing response is detected. 
    If no passing responses are detected, the test case fails.
    '''
    test_case_summary['test_results'] = False
    for prompt, response, expected in zip(test_case_summary['prompts'], test_case_summary['responses'], test_case_summary['expected_all']):
        if expected != []:
            for counter, expected_str in enumerate(expected):
                inter = []
                intermediate_test_result = re.search(expected_str.lower().strip(), response.lower().strip())
                if intermediate_test_result:
                    test_case_summary['test_results'] = True
                    return test_case_summary
                else:
                        inter.append({'prompt': prompt, 'expected': expected_str, 'response': response})
                if counter == len(expected):
                    test_case_summary['test_results_detail'] = test_case_summary['test_results_detail'] + inter
                
    return test_case_summary

# local
def negative_pass(test_case_summary):
    '''
    Testing function where the test ends once a failing response is detected. 
    If no failing responses are detected, the test case passes.
    '''
    for prompt, response, expected in zip(test_case_summary['prompts'], test_case_summary['responses'], test_case_summary['expected_all']):
        if expected != []:
            for expected_str in expected:
                intermediate_test_result = re.search(expected_str.lower().strip(), response.lower().strip())
                if intermediate_test_result:
                    test_case_summary['test_results'] = False
                    test_case_summary['test_results_detail'].append({'prompt': prompt, 'expected': expected_str, 'response': response})
                    return test_case_summary
                else:
                    test_case_summary['test_results'] = True
                    
    return test_case_summary

# local
def similarity(test_case_summary):
    '''
    Testing function which checks if multiple resopnses are different. 
    If there are any that are the same, the test fails.
    '''
    combos = combinations(test_case_summary['responses'],2)
    for combo in combos:
        if combo[0] == combo[1]:
            test_case_summary['test_results'] = False
            return test_case_summary
    test_case_summary['test_results'] = True
    return test_case_summary
    
