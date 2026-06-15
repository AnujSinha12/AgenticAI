import streamlit as st
import uuid, json, sys, os, logging, time
import pandas as pd

import matplotlib.pyplot as plt
from datetime import datetime
import time

# allow import of agent files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.langraph_agent import run_agent_stream

# create log dir if it doesn't exist
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# set unique log filename
log_filename = f'app_{datetime.now().strftime('%Y-%m-%d')}.log'
log_filepath = os.path.join(log_dir, log_filename)

# configure logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_filepath),
        logging.StreamHandler()
    ]
)

logging.info('Start')

#------------
st.set_page_config(layout='wide')

# session state
if 'conversations' not in st.session_state:
    st.session_state.conversations = {}

if 'current_chat' not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat = chat_id
    st.session_state.conversations[chat_id] = {
        'messages': [],
        'logs': [],
        'thread_id': chat_id
    }

# sidebar
with st.sidebar:
    st.title('Chats')

    if st.button('New Chat'):
        chat_id = str(uuid.uuid4())
        st.session_state.current_chat = chat_id
        st.session_state.conversations[chat_id] = {
            'messages': [],
            'logs': [],
            'thread_id': chat_id
        }
    
    st.divider()

    for chat_id, chat in st.session_state.conversations.items():
        messages = chat['messages']

        title = messages[0]['content'][:30] if messages else 'New Chat'

        if st.button(title, key=chat_id):
            st.session_state.current_chat = chat_id

# current chat
chat = st.session_state.conversations[
    st.session_state.current_chat
]

messages = chat['messages']
thread_id = chat['thread_id']

# Layout
col1, col2 = st.columns([3, 1])

# Chat Panel
with col1:
    st.title('Country Economic Indicator Agent')

    user_input = st.chat_input('Ask Something...')

    # render messages inside
    for msg in messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

    if user_input:
        # show user instantly
        with st.chat_message('user'):
            st.markdowm(user_input)

        # save user messages
        messages.append({'role': 'user', 'content': user_input})

        # Assistant streaming UI
        with st.chat_message('assistant'):
            placeholder = st.empty()
            full_response = ''

            for event in run_agent_stream(user_input, thread_id):
                if not isinstance(event, dict):
                    continue

                method = event.get('method')

                # stream tokens live
                if method == 'messages':
                    data = event.get('params', {}).get('data')

                    if not data or not isinstance(data, tuple):
                        continue

                    event_info = data[0]

                    if isinstance(event_info, dict):
                        if event_info.get('event') == 'content-block-delta':
                            text = event_info.get('delta', {}).get('text', '')

                            if text:
                                full_response += text
                                
                elif method == 'values':
                    state = event.get('params', {}).get('data', {})
                    msgs = state.get('messages', [])

                    if msgs:
                        last_msg = msgs[-1]
                    
                    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                        tools = [t['name'] for t in last_msg.tool_calls]
                        chat['logs'].append(f'Tool: {tools}')

                    if last_msg.__class__.__name__ == 'ToolMessage':
                        content = last_msg.content
                        content = json.loads(content)

                        if content['title'] == 'Inflation Rate':
                            logging.info('Inflation Rate')
                            
                            if content['type'] == 'line_chart':
                                logging.info('line_chart')
                                df = pd.DataFrame(content['data'])
                                df['Date'] = pd.to_datetime(df['Date'])

                                base_year = df['Date'][0].year

                                x_col = content['x']
                                y_col = content['y']

                                # create figure
                                fig, ax = plt.subplots(figsize=(6, 3))

                                # based on base and target countries
                                ax.plot(df[x_col].dt.strftime('%b'), df[y_col[0]], marker='o', label=y_col[0])
                                ax.plot(df[x_col].dt.strftime('%b'), df[y_col[1]], marker='o', label=y_col[1])

                                ax.set_title(f'Inflation Rate between {y_col[0]} and {y_col[1]} for year {base_year}')
                                ax.set_xlabel('Date')
                                ax.set_ylabel('Rate')
                                ax.grid(True, linestyle='--', alpha=0.5)
                                ax.legend(loc='upper right')
                                st.pyplot(fig)
                    
                        if content['title'] == 'Funds Rate':
                            logging.info('Funds Rate')
                            
                            if content['type'] == 'line_chart':
                                logging.info('line_chart')
                                df = pd.DataFrame(content['data'])
                                df['Date'] = pd.to_datetime(df['Date'])

                                base_year = df['Date'][0].year

                                x_col = content['x']
                                y_col = content['y']

                                # create figure
                                fig, ax = plt.subplots(figsize=(6, 3))

                                # based on base and target countries
                                ax.plot(df[x_col].dt.strftime('%b'), df[y_col[0]], marker='o', label=y_col[0])
                                ax.plot(df[x_col].dt.strftime('%b'), df[y_col[1]], marker='o', label=y_col[1])

                                ax.set_title(f'Funds Rate between {y_col[0]} and {y_col[1]} for year {base_year}')
                                ax.set_xlabel('Date')
                                ax.set_ylabel('Rate')
                                ax.grid(True, linestyle='--', alpha=0.5)
                                ax.legend(loc='upper right')
                                st.pyplot(fig)

                        if content['title'] == 'Exchange Rate':
                            logging.info('Exchange Rate')
                            
                            if content['type'] == 'line_chart':
                                logging.info('line_chart')
                                df = pd.DataFrame(content['data'])
                                df['date'] = pd.to_datetime(df['date'])

                                base_year = df['date'][0].year

                                x_col = content['x']
                                y_col = content['y']

                                base_currency = content['base_currency']
                                target_currency = content['target_currency']

                                # create figure
                                fig, ax = plt.subplots(figsize=(6, 3))

                                # based on base and target countries
                                ax.plot(df[x_col].dt.strftime('%b'), df[y_col], marker='o', label=y_col[0])
                                

                                ax.set_title(f'Exchange Rate between {base_currency} and {target_currency} for year {base_year}')
                                ax.set_xlabel('date')
                                ax.set_ylabel('rate')
                                ax.grid(True, linestyle='--', alpha=0.5)
                                ax.legend(loc='upper right')
                                st.pyplot(fig)

            # final clean render
            placeholder.markdown(full_response)

        # save assistant after streaming
        messages.append({'role': 'assistant', 'content': full_response})


# Log Panel
with col2:
    st.title('Logs')

    for log in chat['logs'][::-1]:
        st.markdown(f'- {log}')


# auto scroll to latest message
st.markdown(
    """"
    <script>
        const scroll = () => {
            window.scrollTo({
                top: document.body.scrollHeight,
                behaviour: 'smooth'
            });
        };
        setTimeout(scroll, 100)
    </script>
    """, unsafe_allow_html=True)

