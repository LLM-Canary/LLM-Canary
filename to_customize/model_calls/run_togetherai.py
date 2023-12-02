import together

'''
togetherai input/output format: '<[ROLE]>: [CONTENT]\n<bot>: ' 
    where [ROLE] and [CONTENT] are filled in.
'''

def clean_input(system_prompt, prompts):
    '''
    converts the LLM-formatted prompts into strings of content only
    '''
    expected = [[]]
    conversation = []
    if system_prompt != '':
        conversation.append(f'<human>: {system_prompt}\n<bot>: ')
    for prompt in prompts:
        conversation.append(f'<human>: {prompt["prompt"]}\n<bot>: ')
        expected.append(prompt['expected'])
    inputs = conversation
    
    return inputs, conversation, expected

def run_model(env_var, messages, temp_bench):
    '''
    converts the LLM-formatted prompts into strings of content only
    '''
    together.api_key = env_var['API-KEY']
    together.Models.start(env_var['MODEL'])
    
    if temp_bench == 1:
        temp = 1
    else:
        temp = float(env_var['TEMPERATURE'])
    
    conversation = []
    for message in messages:
        output = together.Complete.create(
            prompt = message,
            model = f'{env_var["MODEL"]}',
            max_tokens=128,
            temperature = temp,
            top_k = 60,
            top_p = 0.6,
            repetition_penalty = 1.1,
            stop = ['<human>', '\n\n']
        )
        conversation.append(output['prompt'][0]+output['output']['choices'][0]['text'])
        
    together.Models.stop(env_var['MODEL'])
    
    return conversation

def clean_output(response):
    '''
    converts the LLM-formatted prompts into strings of content only
    '''
    responses_only = []
    for item in response: 
            intermediate = item.split('<bot>: ')
            responses_only.append(intermediate[1])
    return responses_only