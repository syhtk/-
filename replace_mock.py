import re
import pandas as pd
import random

content = open('app.py', encoding='utf-8').read()

replacement = '''
# 动态加载真实数据作为接入列队
@st.cache_data
def get_real_sessions():
    try:
        df = pd.read_csv("raw_comments.csv")
        # 随机取5条真实的客单
        sample = df.sample(5).to_dict('records')
        sessions = []
        for i, row in enumerate(sample):
            uid_short = str(row['user_id'])[:8]
            desc = str(row['content'])[:15] + "..." if pd.notna(row['content']) else "咨询..."
            sessions.append({
                "id": f"用户_{uid_short}",
                "status": "待处理" if i < 3 else "处理中",
                "desc": desc,
                "full_text": str(row['content'])
            })
        return sessions
    except Exception as e:
        return []

sessions = get_real_sessions()

# 采用三栏经典客服布局
col_list, col_chat, col_crm = st.columns([1.5, 3.5, 2.5], gap="small")

# -------- 左侧：会话列表 --------
with col_list:
    with st.container(border=True, height=550):
        st.markdown("**📅 真实客户进线列队**")
        
        if not sessions:
            st.warning("暂无进线数据")
        else:
            if 'active_session' not in st.session_state or st.session_state.active_session not in [s['id'] for s in sessions]:
                st.session_state.active_session = sessions[0]['id']

            for s in sessions:
                is_active = (st.session_state.active_session == s['id'])
                btn_label = f"💬 {s['id']}  [{s['status']}]"
                if st.button(btn_label, use_container_width=True, type='primary' if is_active else 'secondary'):
                    st.session_state.active_session = s['id']
                    st.rerun()
                st.caption(f"{s['desc']}")
                st.markdown('<hr style="margin: 0.1em 0px;" />', unsafe_allow_html=True)
'''

# Find the start block
start_str = '''# 采用三栏经典客服布局
    col_list, col_chat, col_crm = st.columns([1.5, 3.5, 2.5], gap="small")      

    # -------- 左侧：会话列表 --------
    with col_list:
        with st.container(border=True, height=550):
            st.markdown("**📅 待处理列队 (Queue)**")
            if 'active_session' not in st.session_state:
                st.session_state.active_session = '匿名用户_8921'

            sessions = [
                {"id": "匿名用户_8921", "status": "待处理", "desc": "天猫客诉 / 商品质量问题..."},
                {"id": "VIP_天明", "status": "已回复", "desc": "非常感谢你们的售后，换货很快！"},
                {"id": "李女士", "status": "处理中", "desc": "请快点解决我的退款..."},
                {"id": "王先生 (抖音)", "status": "已挂断", "desc": "你这衣服怎么起球啊？"}
            ]

            for s in sessions:
                is_active = (st.session_state.active_session == s['id'])
                btn_label = f"💬 {s['id']}  [{s['status']}]"
                if st.button(btn_label, use_container_width=True, type='primary' if is_active else 'secondary'):
                    st.session_state.active_session = s['id']
                    st.rerun()
                st.caption(f"{s['desc']}")
                st.markdown('<hr style="margin: 0.1em 0px;" />', unsafe_allow_html=True)'''

# Using regex to extract and replace
content = re.sub(r'# 采用三栏经典客服布局.*?unsafe_allow_html=True\)', replacement.strip(), content, flags=re.DOTALL)

# Middle Chat part replacement
middle_chat_old = r'''            if gen_positive:
                if "耳机" in selected_category:.*?(?=st\.markdown\("<div style='height:280px;)'''

middle_chat_new = '''            # 根据选中的真实会话加载对应文本
            default_text = ""
            for s in sessions:
                if s['id'] == st.session_state.active_session:
                    default_text = s.get('full_text', '无内容')
                    break
            
            '''

content = re.sub(r'st\.markdown\("\*\*💬 当前进线会话\*\* \| 渠道：电商平台 🛒"\).*?(?=st\.markdown\("<div style=\'height:280px; overflow-y:auto; padding-right:5px;\'>", unsafe_allow_html=True\))', 
    '''st.markdown(f"**💬 当前真实会话**: {st.session_state.get('active_session', '')} | 渠道：全渠道接入")\n\n''' + middle_chat_new, 
    content, flags=re.DOTALL)

open('app.py', 'w', encoding='utf-8').write(content)
