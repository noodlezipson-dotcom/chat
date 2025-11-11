import streamlit as st
import openai
import os
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="Role-based Creative Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .response-box {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-top: 1rem;
    }
    .api-key-input {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # 应用标题
    st.markdown('<div class="main-header">🤖 Role-based Creative Chatbot</div>', unsafe_allow_html=True)
    
    # 创建两列布局
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # API和角色设置区域
        st.header("API & Role Settings")
        
        # API密钥输入
        st.markdown('<div class="api-key-input">', unsafe_allow_html=True)
        api_key = st.text_input(
            "Enter your OpenAI API Key:",
            type="password",
            placeholder="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            help="Your API key is never stored and is only used for this session."
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 角色选择
        st.subheader("Choose a role:")
        
        # 角色定义
        roles = {
            "Video Director": {
                "description": "You are a professional film director. Always analyze ideas in terms of visual storytelling — use camera movement, lighting, framing, and emotional tone to explain your thoughts. Describe concepts as if you are planning a film scene.",
                "example": "How can I shoot a dream sequence?"
            },
            "Dance Instructor": {
                "description": "You are an experienced dance instructor. Focus on movement, rhythm, body expression, and emotional conveyance through dance. Provide practical advice for expressing emotions through movement.",
                "example": "How can I express sadness through movement?"
            },
            "Fashion Stylist": {
                "description": "You are a professional fashion stylist. Discuss color trends, materials, silhouettes, and how clothing choices reflect personality and confidence. Provide style recommendations based on different contexts.",
                "example": "What style fits a confident personality?"
            },
            "Acting Coach": {
                "description": "You are a skilled acting coach. Teach emotion delivery, scene breakdown, character development, and natural expression techniques. Focus on authenticity and emotional truth in performance.",
                "example": "How to express fear naturally on stage?"
            },
            "Art Curator": {
                "description": "You are an expert art curator. Interpret artwork, connect pieces with historical context and emotional impact. Explain how composition, color, and technique convey meaning and emotion.",
                "example": "How does this composition convey emotion?"
            }
        }
        
        # 角色选择下拉菜单
        selected_role = st.selectbox(
            "Select a creative role:",
            list(roles.keys()),
            index=0
        )
        
        # 显示角色描述
        st.markdown('<div class="role-card">', unsafe_allow_html=True)
        st.write(f"**{selected_role}**")
        st.write(roles[selected_role]["description"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # 聊天机器人区域
        st.header("Role-based Creative Chatbot")
        st.write("Select a creative role and ask your question!")
        
        # 问题输入
        question = st.text_area(
            "Enter your question or idea:",
            placeholder=f"e.g., {roles[selected_role]['example']}",
            height=100
        )
        
        # 生成响应按钮
        if st.button("Generate Response", type="primary", use_container_width=True):
            if not api_key:
                st.error("Please enter your OpenAI API key first.")
            elif not question:
                st.error("Please enter a question or idea.")
            else:
                # 生成响应
                with st.spinner("Generating response..."):
                    response = generate_response(api_key, selected_role, roles[selected_role]["description"], question)
                
                if response:
                    # 显示响应
                    st.markdown('<div class="response-box">', unsafe_allow_html=True)
                    st.markdown("### Response:")
                    st.write(response)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 添加到会话历史
                    if "conversation_history" not in st.session_state:
                        st.session_state.conversation_history = []
                    
                    st.session_state.conversation_history.append({
                        "role": selected_role,
                        "question": question,
                        "response": response,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                else:
                    st.error("Failed to generate response. Please check your API key and try again.")
        
        # 显示对话历史
        if "conversation_history" in st.session_state and st.session_state.conversation_history:
            st.markdown("---")
            st.subheader("Conversation History")
            
            for i, conversation in enumerate(reversed(st.session_state.conversation_history[-5:])):  # 显示最近5条
                with st.expander(f"{conversation['role']} - {conversation['timestamp']}"):
                    st.write(f"**Question:** {conversation['question']}")
                    st.write(f"**Response:** {conversation['response']}")
    
    # 页脚
    st.markdown("---")
    st.markdown("Built for 'Art & Advanced Big Data' • Prof. Jahwan Koo (SKKU)")

def generate_response(api_key, role, role_description, question):
    """使用OpenAI API生成响应"""
    try:
        # 设置OpenAI API密钥
        openai.api_key = api_key
        
        # 构建系统提示
        system_prompt = f"""
        You are a {role}. {role_description}
        
        Guidelines for your response:
        1. Stay strictly in character as a {role}
        2. Provide detailed, practical advice
        3. Use professional terminology appropriate for your field
        4. Be creative and insightful
        5. Structure your response clearly
        6. Focus on the artistic and creative aspects
        """
        
        # 调用OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except openai.error.AuthenticationError:
        st.error("Invalid API key. Please check your API key and try again.")
        return None
    except openai.error.RateLimitError:
        st.error("Rate limit exceeded. Please try again later.")
        return None
    except openai.error.APIError as e:
        st.error(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    main()
