content = open('app.py', encoding='utf-8').read()

part1 = '''                    if service_agent_name:
                        response += f"\\n\\n—— {shop_name} 售后顾问：{service_agent_name}"

                    # 把 state 存入 session_state
                    st.session_state['last_response'] = response
                    st.session_state['last_analysis'] = analysis_result
                    st.session_state['last_prompt'] = prompt

                    # ===== 真实数据落库 ====='''

repl1 = '''                    if service_agent_name:
                        response += f"\\n\\n—— {shop_name} 售后顾问：{service_agent_name}"

                    # 解析 Tool Calling
                    import json
                    import re
                    tool_action = None
                    json_str_match = re.search(r'`json\\s*(\\{.*?\\})\\s*`', response, re.DOTALL)
                    if json_str_match:
                        try:
                            tool_action_data = json.loads(json_str_match.group(1))
                            if tool_action_data.get("action"):
                                tool_action = tool_action_data
                                # 从显示给用户的回复中移除 json 块
                                response = response[:json_str_match.start()].strip()
                        except:
                            pass

                    # 把 state 存入 session_state
                    st.session_state['last_response'] = response
                    st.session_state['last_analysis'] = analysis_result
                    st.session_state['last_prompt'] = prompt
                    st.session_state['tool_action'] = tool_action

                    # ===== 真实数据落库 ====='''

content = content.replace(part1, repl1)

part2 = '''            # 如果有渲染历史结果，显示 AI 回复
            if 'last_response' in st.session_state:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(st.session_state['last_response'])'''

repl2 = '''            # 如果有渲染历史结果，显示 AI 回复
            if 'last_response' in st.session_state:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(st.session_state['last_response'])
                    
                    # 渲染 Tool Calling 结果卡片
                    if st.session_state.get('tool_action'):
                        action_data = st.session_state['tool_action']
                        action_name = action_data.get("action", "")
                        action_emoji = "🎟️" if "coupon" in action_name else "📦"
                        action_desc = "发放优惠券" if "coupon" in action_name else ("创建退换货工单" if "return" in action_name else action_name)
                        st.markdown(f"""
                        <div style='margin-top:10px; padding:10px; background-color:#e0f2fe; border-left:4px solid #3b82f6; border-radius:4px;'>
                            <div style='font-size:12px; color:#1e40af; font-weight:bold;'>⚡ Agent 自动执行动作指令：</div>
                            <div style='font-size:14px; color:#1e3a8a; margin-top:5px;'>
                                {action_emoji} <b>{action_desc}</b><br>
                                <span style='font-size:12px;'>🏷️ {action_data.get('reason', '系统判定执行')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)'''

content = content.replace(part2, repl2)

open('app.py', 'w', encoding='utf-8').write(content)
