content = open('app.py', encoding='utf-8').read()
content = content.replace('''            st.markdown("<br>", unsafe_allow_html=True)
            # 控制项：让用户选择
            gen_positive = st.checkbox("🤔 切换为好评场景进线")''', '')
open('app.py', 'w', encoding='utf-8').write(content)
