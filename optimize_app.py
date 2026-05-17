def optimize_ui():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Improve labels and add icons
    content = content.replace('st.text_area("生成的回复内容：", value=response, height=250)', 
                              'st.info("💡 基于图谱 SOP 与大语言模型动态生成的回复：")\n            st.text_area(label="Response", value=response, height=280, label_visibility="collapsed")')
                              
    content = content.replace('st.subheader("📚 图谱数据概览")', 
                              'st.subheader("📚 业务知识图谱概览")')
                              
    content = content.replace('st.markdown("**(实时从 KnowledgeGraphSchema 读取)**")', 
                              'st.markdown("*(由 KnowledgeGraphEngine 实时推理)*")')
                              
    content = content.replace('st.markdown("###### 📊 系统状态")', 
                              'st.markdown("###### 📊 后端引擎监控")')
                              
    # Organize right column into tabs
    old_right_col = '''    # 展示组件列表
    st.markdown("###### 🧩 核心组件 (Components)")
    comps_df = pd.DataFrame.from_dict(kg_data['components'], orient='index')    
    st.dataframe(
        comps_df[['name', 'description']],
        hide_index=True,
        use_container_width=True
    )

    # 展示已知缺陷
    st.markdown("###### 🚑 已知缺陷库 (Defects)")
    defs_df = pd.DataFrame.from_dict(kg_data['defects'], orient='index')        
    # 增加颜色高亮
    def highlight_severity(val):
        color = 'red' if val == 'critical' or val == 'high' else 'orange'       
        return f'color: {color}'

    st.dataframe(
        defs_df[['name', 'severity']],
        hide_index=True,
        use_container_width=True
    )'''

    new_right_col = '''    # 定义选项卡来优化空间
    tab_comps, tab_defs = st.tabs(["🧩 核心部件", "🚑 缺陷标准体系"])
    
    with tab_comps:
        comps_df = pd.DataFrame.from_dict(kg_data['components'], orient='index')
        st.dataframe(
            comps_df[['name', 'description']],
            hide_index=True,
            use_container_width=True
        )

    with tab_defs:
        defs_df = pd.DataFrame.from_dict(kg_data['defects'], orient='index')
        def highlight_severity(val):
            color = 'red' if val == 'critical' or val == 'high' else 'orange'
            return f'color: {color}'
        st.dataframe(
            defs_df[['name', 'severity']],
            hide_index=True,
            use_container_width=True
        )'''
        
    content = content.replace(old_right_col, new_right_col)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    optimize_ui()