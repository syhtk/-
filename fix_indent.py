content = open('app.py', encoding='utf-8').read()
import re
bad_block = '''                        if st.session_state.active_session == "VIP_天明":
                default_text="非常感谢你们的售后，换货很快！"
            elif st.session_state.active_session == "李女士":
                default_text="请快点解决我的退款！"
            elif st.session_state.active_session.startswith("王"):
                default_text="你这衣服怎么起起球啊，是不是假冒伪劣？"'''

good_block = '''            if st.session_state.active_session == "VIP_天明":
                default_text="非常感谢你们的售后，换货很快！"
            elif st.session_state.active_session == "李女士":
                default_text="请快点解决我的退款！"
            elif st.session_state.active_session.startswith("王"):
                default_text="你这衣服怎么起起球啊，是不是假冒伪劣？"'''

content = content.replace(bad_block, good_block)
open('app.py', 'w', encoding='utf-8').write(content)
