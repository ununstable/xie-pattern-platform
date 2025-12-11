# pattern_matcher.py
import json
import random
from itertools import product


class PatternMatcher:
    def __init__(self, patterns, herbs):
        self.patterns = patterns
        self.herbs = herbs

        # Define matching rules
        # 在 pattern_matcher.py 的 __init__ 方法中，更新 matching_rules

        self.matching_rules = {
            'cultural': {
                'chinese': ['Ginseng', 'Goji Berry', 'Chinese Angelica', 'Astragalus', 'Chrysanthemum'],
                'muslim': ['Frankincense', 'Myrrh', 'Saffron', 'Clove', 'Cardamom', 'Cinnamon', 'Nutmeg']
                # 添加更多适合穆斯林/印尼文化的中草药
            },
            'color_themes': {
                'Red': ['Ginseng', 'Goji Berry', 'Safflower'],
                'Green': ['Mint', 'Green Tea', 'Lotus Leaf'],
                'Gold': ['Turmeric', 'Honeysuckle', 'Licorice'],
                'Blue': ['Isatis Root', 'Gromwell', 'Seaweed'],
                'Purple': ['Lavender', 'Echinacea', 'Bilberry'],
                'White': ['Chrysanthemum', 'White Peony', 'Pearl']
            },
            'meaning_matches': {
                'Auspicious': ['Ginseng', 'Lingzhi Mushroom'],
                'Health': ['Goji Berry', 'Astragalus'],
                'Harmony': ['Licorice', 'Chrysanthemum'],
                'Strength': ['Chinese Angelica', 'Codonopsis'],
                'Prosperity': ['Ginseng', 'Goji Berry'],
                'Balance': ['Licorice', 'Schisandra'],
                'Purity': ['Chrysanthemum', 'White Peony']
            }
        }

    def find_all_combinations(self, max_results=50):
        """Generate all possible pattern + herb combinations - optimized for deduplication"""
        all_combinations = []
        seen_combinations = set()  # For deduplication

        for pattern in self.patterns:
            for herb in self.herbs:
                # Create unique identifier
                combination_key = f"{pattern.get('id', '')}_{herb.get('id', '')}"

                # Skip duplicate combinations
                if combination_key in seen_combinations:
                    continue

                # Calculate match score
                score = self.calculate_match_score(pattern, herb)

                # Generate story
                story = self.generate_story(pattern, herb)

                # Add combination
                all_combinations.append({
                    'pattern': pattern,
                    'herb': herb,
                    'score': score,
                    'story': story,
                    'combination_name': f"{pattern['name']}·{herb['name']} Series",
                    'combination_id': combination_key  # Add unique ID
                })

                seen_combinations.add(combination_key)

        # Sort by match score
        all_combinations.sort(key=lambda x: x['score'], reverse=True)

        # Limit number of results
        return all_combinations[:max_results]

    def calculate_match_score(self, pattern, herb):
        """Calculate matching score between pattern and herb"""
        score = 0

        # 1. Cultural match
        pattern_culture = pattern.get('culture', 'chinese')
        herb_name = herb.get('name', '')

        if pattern_culture == 'chinese' and herb_name in self.matching_rules['cultural']['chinese']:
            score += 30
        elif pattern_culture == 'muslim' and herb_name in self.matching_rules['cultural']['muslim']:
            score += 30
        else:
            score += 10  # Base score

        # 2. Color match
        pattern_colors = pattern.get('colors', [])
        for color in pattern_colors:
            if color in self.matching_rules['color_themes']:
                if herb_name in self.matching_rules['color_themes'][color]:
                    score += 20

        # 3. Meaning match
        pattern_meaning = pattern.get('meaning', '')
        for keyword, herbs_list in self.matching_rules['meaning_matches'].items():
            if keyword in pattern_meaning and herb_name in herbs_list:
                score += 25

        # 4. Tag match (if there are common tags)
        pattern_tags = set(pattern.get('style_tags', []))
        herb_tags = set(herb.get('tags', []))
        common_tags = pattern_tags.intersection(herb_tags)
        score += len(common_tags) * 5

        return min(score, 100)  # Ensure score doesn't exceed 100

    def generate_story(self, pattern, herb):
        """Generate combination story"""
        pattern_name = pattern.get('name', '')
        herb_name = herb.get('name', '')
        pattern_meaning = pattern.get('meaning', '')
        herb_effect = herb.get('effect', '')

        # Select different story templates based on match score
        score = self.calculate_match_score(pattern, herb)

        if score >= 70:
            story_type = "Perfect Match"
            intro = f"✨【{story_type}】"
            connection = "perfectly complements"
        elif score >= 50:
            story_type = "Excellent Combination"
            intro = f"👍【{story_type}】"
            connection = "harmoniously combines with"
        else:
            story_type = "Innovative Experiment"
            intro = f"💡【{story_type}】"
            connection = "innovatively fuses with"

        stories = [
            f"{intro} The 「{pattern_name}」 pattern {connection} {herb_name}, "
            f"embodying the cultural significance of {pattern_meaning}, "
            f"while integrating the health benefits of {herb_name} ({herb_effect}), "
            f"infusing traditional wisdom into modern design.",

            f"{intro} The {pattern_meaning} symbolism of {pattern_name} "
            f"and the {herb_effect} properties of {herb_name} complement each other, "
            f"creating culturally rich and practical design products.",

            f"{intro} Merging the visual aesthetics of {pattern_name} "
            f"with the natural attributes of {herb_name} "
            f"forms a unique cultural IP suitable for home decor, fashion, and other fields."
        ]

        return random.choice(stories)

    def find_similar_patterns(self, pattern_id, top_n=5):
        """Find similar patterns"""
        target_pattern = None
        for pattern in self.patterns:
            if pattern.get('id') == pattern_id:
                target_pattern = pattern
                break

        if not target_pattern:
            return []

        similar_patterns = []
        for pattern in self.patterns:
            if pattern.get('id') != pattern_id:
                # Calculate similarity
                similarity = self.calculate_pattern_similarity(target_pattern, pattern)
                if similarity > 0.3:
                    similar_patterns.append({
                        **pattern,
                        'similarity': round(similarity, 2)
                    })

        # Sort by similarity
        similar_patterns.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_patterns[:top_n]

    def calculate_pattern_similarity(self, pattern1, pattern2):
        """Calculate similarity between two patterns"""
        score = 0

        # 1. Same culture
        if pattern1.get('culture') == pattern2.get('culture'):
            score += 20

        # 2. Same type
        if pattern1.get('type') == pattern2.get('type'):
            score += 20

        # 3. Color similarity
        colors1 = set(pattern1.get('colors', []))
        colors2 = set(pattern2.get('colors', []))
        color_similarity = len(colors1.intersection(colors2)) / max(len(colors1), 1)
        score += color_similarity * 30

        # 4. Tag similarity
        tags1 = set(pattern1.get('style_tags', []))
        tags2 = set(pattern2.get('style_tags', []))
        tag_similarity = len(tags1.intersection(tags2)) / max(len(tags1), 1)
        score += tag_similarity * 30

        return min(score, 100) / 100  # Normalize to 0-1