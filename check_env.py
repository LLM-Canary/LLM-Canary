import os
import getpass
         
# public
def check_env():
    '''
    Checks that the env file is properly formatted and all LLM's have the required parameters
    '''
    
    # to store all models that do not return errors
    models_configured = []
    # to store each individual model's parameters
    model = dict()
    LLM_ID = ''
    error=False
    
    with open('.env', 'r') as file:
        # count_of_models is the crux of this function. each line of the .env file is looped through. if the key matches a key in count_of_models, the count for that key increases. If there is anything other than a 1 in the counter, it is considered an error.
        count_of_models = {'ID': 0, 'PLATFORM':0, 'API-KEY':0, 'MODEL':0, 'TEMPERATURE':0}
        for index, line in enumerate(file):
            if '=' in line:
                # get key value and break up the key name into parts
                key, value = line.strip().split('=')
                if 'ID' in key:
                    LLM_ID = value
                        
                # checks if the current line has a key that matches any of the keys in count_of_models (the required keys)
                if any([True for var_type in count_of_models.keys() if var_type == key]):
                    model[key] = value
                    count_of_models[key] += 1
            # just to make sure this isn't the first line as an error will be returned if it is run on the first line
            elif index != 0:
                error = check_key_errors(count_of_models,LLM_ID)
                if not error:
                    print(f'- {LLM_ID} configured\n')
                LLM_ID = ''
                models_configured.append(model)
                model = dict()
                count_of_models = {'ID': 0, 'PLATFORM':0, 'API-KEY':0, 'MODEL':0, 'TEMPERATURE':0}

        error = check_key_errors(count_of_models,LLM_ID)
        if not error:
            print(f'- {LLM_ID} configured')
    return error

# local
def check_key_errors(count_of_models, LLM_ID):
    '''
    Support function for check_env. checks if there is an error with a single LLM Parameter Block 
    '''
    error = False
    if LLM_ID == '':
        print('- ERROR: ID is missing for one of the models\n')
        error = True
        return error
    for var_type in count_of_models.keys():
        if count_of_models[var_type] != 1:
            print(f'- ERROR: Missing {var_type} for {LLM_ID}')
            error = True
    print()
    return error

# public
def guided_env_setup():
    '''
    Used by the main menu to guide users through the .env LLM Parameter Block setup
    '''
    print()
    print('LLM Hosted Platforms:')
    print('1. OpenAI')
    print('2. TogetherAI')
    print('3. Private Hosting')
    print('4. Return to main menu')
    print()
    
    while True:
        choice = input('Select a platform to set configuration: ')
        if choice == '1':
            platform = 'OpenAI'
            set_env_parameters(platform.upper())
            break
        elif choice == '2':
            platform = 'TogetherAI'
            set_env_parameters(platform.upper())
            break
        elif choice == '3':
            platform = input('Please enter the name you would like to uniquely identify this host with. If there are multiple LLMs with different configurations, enter the name of the LLM: ')
            set_env_parameters(platform.upper())
            break
        elif choice == '4':
            break
        else:
            print('Invalid choice. Please select a valid option.')
            
# local
def set_env_parameters(platform):
    '''
    Guides the user through setting their environment parameters based on the platform they selected in the select_model_platform() function.
    '''
    
    # API KEY
    print()
    api_key = getpass.getpass(prompt=f'1. Please enter your {platform} API key: ')
    
    # MODEL
    openAI_models = ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k-0613', 'gpt-4', 'gpt-4-0314']
    togetherAI_models = ['togethercomputer/llama-2-70b-chat', 'huggyllama/llama-7b', 'NousResearch/Nous-Hermes-13b', 'EleutherAI/pythia-12b-v0', 'lmsys/vicuna-7b-v1.5', 'databricks/dolly-v2-7b', 'togethercomputer/RedPajama-INCITE-7B-Instruct', 'togethercomputer/falcon-40b']
    
    print()
    model_dict = dict()
    in_index = []
    if (platform == 'OPENAI'):
        print(f'Supported {platform} models: ')
        for index, model in enumerate(openAI_models):
            model_dict[str(index+1)] = model
            print(f'{index+1}. {model}')
            in_index.append(str(index+1))
        print()
        model_id = pick_model(in_index)
        
    elif (platform == 'TOGETHERAI'):
        print(f'Supported {platform} models: ')
        for index, model in enumerate(togetherAI_models):
            model_dict[str(index+1)] = model
            print(f'{index+1}. {model}')
            in_index.append(str(index+1))
        print()
        model_id = pick_model(in_index)

    else:
        print()
        model_name = input(f'2. Please enter the name of the model you wish to run: ')
    
    # TEMPERATURE
    temp = input(f'Please enter the desired temperature: ')
    print()

    # Write to .env file
    if platform == 'OPENAI' or platform == 'TOGETHERAI' or platform == 'VERTEXAI':
        write_env(platform, api_key, model_dict[model_id], temp)
        
    else:
        write_env(platform, api_key, model_name, temp)
    print('Configuration saved to .env.')

# local
def pick_model(in_index):
    '''
    This function is used to take user input and make sure they have entered a valid choice
    '''
    model_id = -1
    while model_id not in in_index:
        model_id = input(f'2. Please enter the number from the list above associated with the model you want to run: ')
        if model_id not in in_index:
            print('Please enter valid index')
        else:
            return model_id

# local
def write_env(platform, api_key, model_name, temp):
    '''
    writes LLM Parameter Block created by guided_env_setup() to the .env file
    '''
    model = model_name.replace('/', '.') # input handling required for importlib in run_test.py define_cases()
    LLM_ID = model.upper() + '-' + api_key[-4:].upper()
    
    # create .env file if it does not exist.
    if not os.path.isfile('.env'):
        with open('.env', 'a') as file:
            pass
    
    # checks whether the user input is a new model, or if it already exists in the .env file
    new_key = True
    with open('.env', 'r') as file:
        data = file.readlines()
        for line in data:
            new_key = False
            if '=' in line:
                if 'ID' in line and LLM_ID in line:
                    new_key=False
                    break
                else:
                    new_key=True
    in_section = False
    
    # if new_key is false, it means modifying an existing model; however, they can only modify temperature without it being declared a new model
    if new_key == False:
        with open('.env', 'r') as file:
            data = file.readlines()
            for index, line in enumerate(data):
                if '=' in line:
                    key, value = line.strip().split('=')
                    if f'ID' in line and LLM_ID in line:
                        in_section = True
                    elif f'TEMPERATURE' in line and in_section:
                        data[index] = f'TEMPERATURE={temp}\n'
                        in_section = False
            print('Overwriting file')
            with open('.env', 'w+') as file:
                file.writelines(data)
    else:
        print('Appending to file')
        with open('.env', 'a+') as file:
            file.write('\n')
            file.write(f'ID={LLM_ID}\n')
            file.write(f'PLATFORM={platform.upper()}\n')
            file.write(f'API-KEY={api_key}\n')
            file.write(f'MODEL={model_name}\n')
            file.write(f'TEMPERATURE={temp}\n')

# public
def read_env():
    '''
    Opens the .env file, creates a list with the parameters from the LLM Parameter Blocks in a dictionary and returns the list
    '''
    if os.path.isfile('.env'):
        prior_model = ''
        llms = []
        llm = dict()
        with open('.env', 'r+') as file:
            for index, line in enumerate(file):
                if '=' in line:
                    key, value = line.strip().split('=')
                    llm[key] = value
                elif index != 0:
                    llms.append(llm)
                    llm = dict()
            llms.append(llm)
        return llms
    else:
        print('ERROR: NO ENVIRONMENT DETECTED')