content = open('review_response_system.py', encoding='utf-8').read()

missing_class = '''

class ReviewResponseSystem:
    def __init__(self, kg: Dict, api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = ""):
        self.analyzer = ReviewAnalyzer(kg)
        self.generator = DynamicResponseGenerator(api_key=api_key, base_url=base_url, model=model)
'''

if 'class ReviewResponseSystem' not in content:
    open('review_response_system.py', 'a', encoding='utf-8').write(missing_class)
