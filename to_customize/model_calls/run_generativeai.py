import google.generativeai as palm

'''
palm input/output format: '[PROMPT]' 
    where [PROMPT] is the prompt
not included in input/output - author: user = 0, chatbot = 1
'''

def clean_input(system_prompt, prompts):
    '''
    converts unformatted prompts into formatted ones ready to be passed to the LLM
    '''
    conversation = []
    expected = [[]] # start with empty for system prompt
    if system_prompt != '':
        conversation.append(system_prompt)
    for prompt in prompts:
        conversation.append(prompt['prompt'])
        expected.append(prompt['expected'])
    inputs = conversation
    return inputs, conversation, expected

def run_model(env_var, messages, temp_bench):
    '''
    calls the API and returns the prompt/response
    '''
    palm.configure(api_key = env_var['API-KEY'])
    
    if temp_bench == 1:
        temp = 1
    else:
        temp = float(env_var['TEMPERATURE'])
    
    responses = palm.chat(
        messages = messages,
        temperature = temp,
    )
    conversation = responses.messages
    return(conversation)
    
def clean_output(response):
    '''
    converts the LLM-formatted prompts into strings of content only
    '''
    responses_only = []
    for comment in response:
        if comment['author'] == '1':
            responses_only.append(comment['content'])
    return responses_only
