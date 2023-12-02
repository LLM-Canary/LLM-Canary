import streamlit as st
import os
import psutil
import yaml

style_sheet = 'scorecard/assets/css/style.css'
benchmark_scores_file = 'scorecard/benchmark/benchmark_scores.yaml'

# public
def create_scorecard_detail(data):
    ''' 
    This will be the actual scorecard; what displays the results for an individual test run
    Will call display_benchmark() and display_custom()
    '''
    with open(style_sheet) as file:
        st.markdown(f'<style>{file.read()}</style>', unsafe_allow_html=True)
    
    is_benchmark = False
    
    st.markdown(f'<h1>LLM: {data["llm_platform"].lower()} {data["llm_model"]}</h1><h1>Model ID: {data["ID"]}</h1><h1>DateTime Run: {data["time"]}</h1>', unsafe_allow_html=True)
    
    # check if benchmark was run
    for case in data['test_cases']:
        test_suite, test_group = case['test_group'].split('-')
        if test_suite.lower() == 'benchmark':
            is_benchmark = True
            break
    
    # display webpage contents
    if is_benchmark:
        display_benchmark(data['test_group_score'])
    
    display_table_details(data['test_cases'], data['test_group_score'])
        
    display_test_results_details(data['test_cases'])

    # Sidebar button to close website server and return to main menu
    if st.sidebar.button('Close Website '):
        # Terminate streamlit python process
        pid = os.getpid()
        p = psutil.Process(pid)
        p.terminate()

# local
def display_benchmark(group_scores):
    '''
    creates benchmark table. Markdown used for formatting purposes.
    '''
    st.markdown("<h3>Benchmark</h3>", unsafe_allow_html=True)
    
    # createing table. html variable holds the html that creates the table and is passed to st.markdown
    with open(benchmark_scores_file, 'r+') as file:
        benchmark_scores = yaml.safe_load(file)
        html = f'<div class="scorecard_table">'
        html = html + f'<table style="width: 100%;">'
        columns = ['Test Group', 'Group Test Score', 'Benchmark']
        html = html + f'<tr class="scorecard_table">'
        for column in columns:
            html = html + f'<th>{column}</th>'
        html = html + f'</tr>'
        for group in group_scores.keys():
            if "benchmark" in group.lower():
                group_name = group.split('-')
                html = html + f'<td class="scorecard_table_first_column">{group_name[1]}</td>'
                html = html + f'<td class="scorecard_table">{round(group_scores[group] * 100,2)}%</td>'
                html = html + f'<td class="scorecard_table">{round(benchmark_scores[group_name[1].lower()] * 100,2)}%</td>'
            html = html + f'</tr>'
        html = html + f'</table></div>'
        st.markdown(html, unsafe_allow_html=True)
        
# local
def display_table_details(data_case, group_scores):
    '''
    creates the details table. Markdown used for formatting purposes.
    '''
    test_groups = group_by_test_group(data_case)

    st.markdown("<h3>Test Breakdown</h3>", unsafe_allow_html=True)
    
    # createing table. html variable holds the html that creates the table and is passed to st.markdown
    html = f'<div class="scorecard_table">'
    html = html + f'<table style="width: 100%;">'
    columns = ['Test ID', 'Test Result', 'Risk Level', 'Test Score']
    html = html + f'<tr class="scorecard_table">'
    for column in columns:
        html = html + f'<th>{column}</th>'
    html = html + f'</tr>'
    for test_group in test_groups.keys():
        
        html = html + f'<tr class="scorecard_table_test_group">'
        html = html + f'<td colspan="3">{test_group}</td>'
        _id = test_groups[test_group][0]['test_group']
        html = html + f'<td>{round(group_scores[_id] * 100,2)}%</td>'
        html = html + f'</tr>'
        for case in test_groups[test_group]:
            test_result = get_test_result(case)
            html = html + f'<tr>'
            link = case["test_id"]
            html = html + f'<td class="scorecard_table_first_column"><a href="#test-{link}-result-{test_result.lower()}">Test {str(int(case["test_id"]))}</a></td>'
            if test_result == 'Pass': # for styling purposes
                html = html + f'<td style="background-color: var(--canary-green); color: white">{test_result}</td>'
            else:
                html = html + f'<td style="background-color: var(--canary-orange); color: var(--canary-yellow)">{test_result}</td>'
            html = html + f'<td class="scorecard_table">{case["results_risk_level"]}</td>'
            html = html + f'<td class="scorecard_table">{int(round(case["test_score"] * 100, 0))}%</td>'
            html = html + f'</tr>'
    html = html + f'</table></div>'
    st.markdown(html, unsafe_allow_html=True)

# local
def display_test_results_details(data_case):
    '''
    displays the prompt/response/expected details for every test
    '''
    st.markdown("<h3>\nTest Details</h3>", unsafe_allow_html=True)
    
    test_groups = group_by_test_group(data_case)
    for test_group in test_groups.keys():
        st.markdown(f'<h6 class="test_group">Test Group: {test_group}</h6>', unsafe_allow_html=True)
        for case in test_groups[test_group]:
            test_result = get_test_result(case)
            response_detail = get_response_detail(case)
            link1 = case["test_id"]
            if test_result == "Pass":
                st.markdown(f'<h5 id="Test-{link1}-result-{test_result}" style="color: var(--canary-green)">Test {case["test_id"]}: ----- Result: {test_result} ----- </h5>', unsafe_allow_html=True)

            else:
                st.markdown(f'<h5 id="Test-{link1}-result-{test_result}" style="color: var(--canary-orange)">Test {case["test_id"]}: ----- Result: {test_result} ----- </h5>', unsafe_allow_html=True)
            st.markdown(f'<h5 class ="test_type">Test Type: {clean_test_type(case["test_type"])}</h5>', unsafe_allow_html=True)
            st.markdown(f'{response_detail}', unsafe_allow_html=True)

def clean_test_type(test_type):
    if test_type == 'positive_pass':
        return 'Positive Pass (Pass once a passing response is detected)'
    elif test_type == 'negative_pass':
        return 'Negative Pass (Fail once a failing response is detected)'
    elif test_type == 'positive_fail':
        return 'Positive Fail (Pass if no fails are detected)'
    elif test_type == 'similarity':
        return 'Similarity (Pass if there are no matching responses)'
    else:
        return test_type
    
# local
def group_by_test_group(data_cases):
    '''
    removes the test_suite identifier from the test_group name
    '''
    test_groups = dict()
    for case in data_cases:
        test_group_name = case['test_group'].split('-') # [test_suite_name, test_group_name]
        test_group_name = test_group_name[1]
        if test_group_name not in test_groups.keys():
            test_groups[test_group_name] = [case]
        else:
            test_groups[test_group_name].append(case)
    return test_groups

# local
def get_test_result(test_case):
    # Converts True/False to Pass/Fail
    if test_case['test_results'] == True:
        return 'Pass'
    else:
        return 'Fail'

# local
def get_response_detail(test_case):
    # formats the prompt, expected, and responses for display to the webpage
    response = ''
    for prompt, expected, act_response in zip(test_case['prompts'], test_case['expected_all'], test_case['responses']):
        response = response + '<p class="prompt"><span style="color: var(--canary-navy); font-weight: bold;">Prompt: </span>' +prompt+ '</p>'
        if expected == []:
            expected = 'None'
        else:
            expected = 'ANY(' + str(expected) + ')'
            response = response + '<p  class="response_detail"><span style="color: var(--canary-blue); font-weight: bold;">Expected Response: </span>' + expected + '</p>'
            
        if act_response in [failed_case['response'] for failed_case in test_case['test_results_detail']]:
            response = response + '<p  class="response_detail"><span style="color: var(--canary-amber); font-weight: bold;">Actual Response: </span>' + format_response(act_response) + '</p>'
        elif test_case['test_type'].lower() == 'positive_pass' and test_case['test_results'] == False and expected != 'None':
            response = response + '<p  class="response_detail"><span style="color: var(--canary-amber); font-weight: bold;">Actual Response: </span>' + format_response(act_response) + '</p>'
        else:
            response = response + '<p  class="response_detail"><span style="color: var(--canary-blue); font-weight: bold;">Actual Response: </span>' + format_response(act_response) + '</p>'
    return response

# local
def format_response(response):
    # to remove unwanted characters from the LLM responses
    response = response.replace('\n', '.')
    return response