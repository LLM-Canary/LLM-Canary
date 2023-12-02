import yaml

custom_tests_file = 'to_customize/custom_prompts.yaml'
benchmark_tests_file = 'benchmark.yaml'

test_config_file = 'to_customize/test_config.yaml'

# public
def selection_menu():
    '''
    Central function for Main Menu check model configuration option.
    '''
    # runs all of the other functions in the file
    test_groups_avaiable = display_avaiable_tests()
    print()
    display_configured_tests()
    user_selection = confirm_user_selection()
    return user_selection

# local
def display_avaiable_tests():
    '''
    Opens the benchmark.yaml and the custom_prompts.yaml files and displays all test_groups. Benchmark is displayed as a test_suite as it can only be run as a test_suite.
    '''
    with open(custom_tests_file, 'r') as file:
        custom_tests = yaml.safe_load(file)
    with open(benchmark_tests_file, 'r') as file:
        benchmark_tests = yaml.safe_load(file)
    
    test_groups_avaiable = {1: 'benchmark'}
    
    print('\n\n ----- SETUP TEST CONFIGURATION -----\n')
    print('Tests avaiable to run:')
    print('1. Benchmark\n   - Test groups in benchmark include:')
    for index, bench_test in enumerate(benchmark_tests):
        print(f'      {index + 1}. {bench_test}')
    if custom_tests:
        for index, custom_test in enumerate(custom_tests):
            print(f'{index + 2}. {custom_test}')
            test_groups_avaiable[index + 1] = custom_tests
    else:
        print('No custom tests have been configured in the "custom_prompts.yaml" file')
    return test_groups_avaiable
    
# local
def display_configured_tests():
    '''
    Opens the test_config.yaml file and displays the test_suites/test_groups set to run.
    '''
    with open(test_config_file, 'r') as file:
        configured_tests = yaml.safe_load(file)
    print('The LLM Canary tool is currently configured to run the following tests')
    for test in configured_tests:
        print(f' - {test}')
    
# local
def confirm_user_selection():
    '''
    Confirms the user would like to proceed with the configured tests. If not, the program will exit.
    '''
    while True:
        user_input = input('\nDo you wish to proceed with the following tests? Y for yes, N for no: ')
        if user_input.lower() == 'n':
            print('Please navigate to the "test_config.yaml" to adjust tests to run')
            return False
        elif user_input.lower() == 'y':
            print('User confirmed to proceed. Please select "Run testing tool" in the main menu to start testing')
            return True
        else:
            print('Please enter a valid input.')

        