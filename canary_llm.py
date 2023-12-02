import os
import subprocess
import pathlib

import check_env
import check_tests
import encrypt
import check_benchmark

canary = '''
     _____
    | o o |
   <      |_
     |    __|
     |____ /
      |  |
'''

# private
def display_menu(icon):
    '''
    # canary main menu CLI printout
    '''
    print()
    print('Welcome to LLM Canary')
    print(icon)
    print()
    print('Please select from one of the following options:')
    print('1. Guided set up for LLM model configuration')
    print('2. Check model configuration')
    print('3. Guided set up for test configuration')
    print('4. Run testing tool')
    print('5. View scorecard')
    print('6. Exit')
    print()
    
# private
def main_menu():
    '''
    logic behind the main menu
    '''
    while True:
        display_menu(canary)
        choice = input('Enter the number of your selection: ')
        
        if choice == '1': # Guided Config    
            while True:
                check_env.guided_env_setup()
                user_input = ''
                while user_input.lower() != 'y' or user_input.lower() != 'n':
                    user_input = input('Add another model? Y for yes, N for no: ')
                    if user_input.lower() == 'n' or user_input.lower() == 'y':
                        break
                    else:
                        print('Please enter a valid input.')
                if user_input.lower() == 'n' and os.path.isfile('.env'):
                    encrypt.generate_key()
                    encrypt.encrypt_file(encrypt.load_key())
                    break
                elif user_input.lower() == 'n':
                    break
                    
        elif choice == '2': # Check Config/encrypt
            if os.path.isfile('.env'):
                error = check_env.check_env()
                if not error:
                    encrypt.generate_key()
                    encrypt.encrypt_file(encrypt.load_key())
                    os.remove('.env')
            elif os.path.isfile('.env.enc'):
                encrypt.decrypt_file(encrypt.load_key())
                error = check_env.check_env()
                if not error:
                    encrypt.encrypt_file(encrypt.load_key())
                    os.remove('.env')
            else:
                print('ERROR. .env file does not exist.')
            
        elif choice == '3': # Check Test Config
            user_selection = check_tests.selection_menu()
            if user_selection == False:
                return 
            
        elif choice == '4': # Run Tool
            encrypt.decrypt_file(encrypt.load_key())
            if check_benchmark.calc_benchmark_hash():
                subprocess.run(['pytest','-s'])
            else:
                print('Benchmark file may have been altered. Please download again from LLM Canary repo')
                
        elif choice == '5': # Run Scorecard
            subprocess.run(['streamlit', 'run', 'scorecard/home.py'])
            
            # To clean up scorecard/pages directory after scorecard website is closed
            files = os.listdir('scorecard/pages')
            for file_name in files:
                file_path = pathlib.Path(f'scorecard/pages/{file_name}')
                file_path.unlink()
                
        elif choice == '6': # close program and delete .env
            if os.path.isfile('.env'):
                os.remove('.env')
            print('Exiting the program. Thank you for using LLM Canary!')
            return
        
        else:
            print('\nInvalid choice. Please select a valid option.\n')

if __name__ == "__main__":
    main_menu()
