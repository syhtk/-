import re
content = open('app.py', encoding='utf-8').read()

content = re.sub(r'(?s)(# 渲染滚动区\n\s*if st\.session_state\.active_session == "VIP_天明":.*?)(?=st\.markdown\("<div style=\'height:280)', r'            if st.session_state.active_session == "VIP_天明":\n                default_text="非常感谢你们的售后，换货很快！"\n            elif st.session_state.active_session == "李女士":\n                default_text="请快点解决我的退款！"\n            elif st.session_state.active_session.startswith("王"):\n                default_text="你这衣服怎么起起球啊，是不是假冒伪劣？"\n\n            ', content)

open('app.py', 'w', encoding='utf-8').write(content)
