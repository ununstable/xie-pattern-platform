# database.py
import json


class PatternDatabase:
    def __init__(self):
        self.patterns = []
        self.herbs = []
        self.load_data()

    def load_data(self):
        try:
            with open('data/patterns/patterns.json', 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)

            with open('data/herbs.json', 'r', encoding='utf-8') as f:
                self.herbs = json.load(f)
        except Exception as e:
            print(f"加载数据失败: {e}")

    def get_all_patterns(self):
        return self.patterns

    def get_all_herbs(self):
        return self.herbs

    def get_pattern(self, pattern_id):
        for pattern in self.patterns:
            if pattern.get('id') == pattern_id:
                return pattern
        return None

    def get_herb(self, herb_id):
        for herb in self.herbs:
            if herb.get('id') == herb_id:
                return herb
        return None

    def search_patterns(self, keyword, culture):
        results = []
        for pattern in self.patterns:
            match = True

            if keyword:
                keyword_lower = keyword.lower()
                if not (keyword_lower in pattern.get('name', '').lower() or
                        keyword_lower in pattern.get('meaning', '').lower()):
                    match = False

            if culture and pattern.get('culture') != culture:
                match = False

            if match:
                results.append(pattern)

        return results