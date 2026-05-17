with open('review_response_system.py', 'r', encoding='utf-8') as f:
    text = f.read()

second_call_idx = text.rfind('    def call_real_llm')
if second_call_idx != -1 and second_call_idx > text.find('    def call_real_llm') + 10:
    end_of_func = text.find('\nclass ReviewResponseSystem', second_call_idx)
    if end_of_func != -1:
        text = text[:second_call_idx] + text[end_of_func:]
    
with open('review_response_system.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("dup fixed")
