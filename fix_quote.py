content = open('app.py', encoding='utf-8').read()
old_str = "st.markdown('''\n            if 'active_session'"
new_str = "if 'active_session'"
content = content.replace(old_str, new_str)
open('app.py', 'w', encoding='utf-8').write(content)
