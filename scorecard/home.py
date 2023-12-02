import streamlit as st
import os
import yaml
import psutil
import pathlib

results_folder = 'scorecard/results'
pages_folder = 'scorecard/pages'
test_results_folder = '/draft_main_current/scorecard/results'
style_sheet = 'scorecard/assets/css/style.css'

# local
def create_website_structure():
    '''
    The main function of the scorecard that calls all of the other functions
    It will call create_scorecard_home to start. 
    It will then loop through all of the files in the results folder, sort them by llm_ID then date, then run create_scorecard_detail() on each results file.
    '''    
    with open(style_sheet) as file:
        st.markdown(f'<style>{file.read()}</style>', unsafe_allow_html=True)
    
    create_scorecard_home()
    
    if not os.path.exists(pages_folder):
        os.mkdir(pages_folder)
    for filename in os.listdir(results_folder):
        if filename.endswith('.yaml'):
            #strips off 'results_' and '.yaml' and creates a new .py file in /pages 
            file_path = os.path.join(pages_folder, filename[0:-5])
            add_ext = file_path + '.py'
            f = open(add_ext, 'w')
            f.write(f'from scorecard_subpage import create_scorecard_detail\nfrom home import get_data\n\nreference_file = "{filename}"\n\ndata = get_data(reference_file)\ncreate_scorecard_detail(data)')
    
# local
def get_data(filename):
    # open the yaml file provided
    with open(os.path.join(results_folder, filename), 'r') as file:
        data = yaml.safe_load(file)
        return data

# local
def create_scorecard_home():
    # add content to the home page
    
    # canary logo
    image_html = f'<div style="text-align: center;"><img src="https://drive.google.com/uc?export=view&id=19YUi7MQ0ATjg-KHBbWij3rhsiV-CBfS2" alt="Your Image" style="display: block; margin: 0 auto; max-width: 50%;"></div>'

    st.markdown(image_html, unsafe_allow_html=True)

    # Delete files from /results folder
    if st.sidebar.button('Delete Test Run Results'):
        files = os.listdir('scorecard/results')
        for file_name in files:
            file_path = pathlib.Path(f'scorecard/results/{file_name}')
            file_path.unlink()

    # Sidebar button to close website server and return to main menu
    if st.sidebar.button('Close Website'):
        # Terminate streamlit python process
        pid = os.getpid()
        p = psutil.Process(pid)
        p.terminate()
    
    # Main page content
    st.title('LLM Canary Cybersecurity Test Report')
    st.markdown('<h4>Welcome to the LLM Canary Scorecard!</h4><h4>All test runs can be found in the left navigation menu. Please select the desired test run to see the results.</h4>', unsafe_allow_html=True)    
    st.markdown('<h1>Resources</h1>', unsafe_allow_html=True)
    
    st.markdown('<h2>OWASP LLM Top 10</h2>', unsafe_allow_html=True)
    st.markdown('<a href="https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-2023-v1_0.pdf">Full Report Version 1.0</a>', unsafe_allow_html=True)
    st.markdown('<ul><li style="font-size: 18px;">Prevention and Remediation recommendations can also be found within this OWASP report.</li></ul>', unsafe_allow_html=True)
    st.markdown('<a href="https://owasp.org/www-project-top-10-for-large-language-model-applications/">OWASP LLM Top 10 Website</a>', unsafe_allow_html=True)
    
    st.markdown('<h2>Custom Test Design</h2>', unsafe_allow_html=True)
    st.markdown('<a href="https://research.ibm.com/blog/what-is-ai-prompt-tuning">Prompt Tuning</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://chat.lmsys.org/">Prompt Testing Tool - Chat Arena</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://doublespeak.chat/#/handbook">LLM Hacker Handbook</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.jailbreakchat.com/">The Prompt Report - Jailbreak Chat</a>', unsafe_allow_html=True)
    
    
    st.markdown('<h2>LLM Canary</h2>', unsafe_allow_html=True)
    st.markdown('<a href="https://llm-canary.webflow.io/">Website</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://github.com/LLM-Canary/LLM-Canary">Github</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://github.com/LLM-Canary/LLM-Canary/blob/main/documentation/4.Scoring_Methodology.md">Scorecard Methodology</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://github.com/LLM-Canary/LLM-Canary/blob/main/documentation/5.Benchmark_Methodology.md">Benchmark Methodology</a>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 20px">Contact us: <a href="llmcanarybenchmark.gmail.com">LLMcanarybenchmark@gmail.com</a></p>', unsafe_allow_html=True)
    
    
    
    
    
if __name__ == '__main__':
    create_website_structure()