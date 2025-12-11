from flask import Flask, request, jsonify, render_template, send_from_directory
import json
import os
import urllib.parse
from pattern_matcher import PatternMatcher

app = Flask(__name__)


# ========== Data Loading Functions ==========
def load_patterns():
    """Load pattern data from patterns.json"""
    try:
        with open('data/patterns/patterns.json', 'r', encoding='utf-8') as f:
            patterns = json.load(f)

        # Add data validation for each pattern
        for pattern in patterns:
            # Ensure required fields exist
            if 'id' not in pattern:
                pattern['id'] = f"pattern_{patterns.index(pattern) + 1}"
            if 'style_tags' not in pattern:
                pattern['style_tags'] = []
            if 'elements' not in pattern:
                pattern['elements'] = []
            if 'colors' not in pattern:
                pattern['colors'] = []

        return patterns
    except Exception as e:
        print(f"Failed to load pattern data: {e}")
        return []


def load_herbs():
    """Load herbal medicine data from herbs.json"""
    try:
        with open('data/herbs.json', 'r', encoding='utf-8') as f:
            herbs = json.load(f)
        return herbs
    except Exception as e:
        print(f"Failed to load herbal medicine data: {e}")
        return []

def load_products():
    """Load product data from products.json"""
    try:
        with open('data/products/products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        return products
    except Exception as e:
        print(f"Failed to load product data: {e}")
        return []


# ========== Load Data ==========
patterns_data = load_patterns()
herbs_data = load_herbs()
products_data = load_products()


# ========== Basic Routes ==========
@app.route('/')
def home():
    """Home page - Platform introduction"""
    # 只获取前6个图案和产品作为特色展示
    featured_patterns = patterns_data[:6]
    featured_products = products_data[:6]

    return render_template('index.html',
                           featured_patterns=featured_patterns,
                           featured_products=featured_products,
                           total_patterns=len(patterns_data),
                           total_products=len(products_data),
                           total_herbs=len(herbs_data),
                           total_combinations=len(patterns_data) * len(herbs_data))


@app.route('/patterns')
def get_patterns_page():
    """Render HTML page showing all patterns"""
    return render_template('patterns.html', patterns=patterns_data)


@app.route('/combinations')
def combinations_page():
    """Pattern + Herbal Medicine combination matching page"""
    return render_template('combinations.html')

@app.route('/products')
def get_products_page():
    """Render HTML page showing all products"""
    return render_template('products.html', products=products_data)


# ========== API Routes ==========
@app.route('/api/patterns')
def get_patterns():
    """Get all patterns"""
    return jsonify(patterns_data)


@app.route('/api/herbs')
def get_herbs():
    """Get all herbal medicines"""
    return jsonify(herbs_data)

@app.route('/api/products')
def get_products():
    """Get all products"""
    return jsonify(products_data)


@app.route('/api/search/patterns')
def search_patterns():
    """Search patterns by keyword"""
    keyword = request.args.get('q', '').lower()
    culture = request.args.get('culture', '')

    filtered_patterns = []
    for pattern in patterns_data:
        match = False

        # Search logic
        if keyword:
            search_fields = [
                pattern.get('name', ''),
                pattern.get('meaning', ''),
                pattern.get('description', '')
            ] + pattern.get('style_tags', []) + pattern.get('elements', [])

            if any(keyword in str(field).lower() for field in search_fields):
                match = True
        else:
            match = True

        # Culture filter
        if culture and pattern.get('culture') != culture:
            match = False

        if match:
            filtered_patterns.append(pattern)

    return jsonify(filtered_patterns)


@app.route('/api/match/patterns', methods=['POST'])
def match_patterns():
    """Simple pattern matching"""
    data = request.json
    pattern_id = data.get('pattern_id')

    if not pattern_id:
        return jsonify({'error': 'pattern_id is required'}), 400

    # Create matcher
    matcher = PatternMatcher(patterns_data, herbs_data)

    # Find similar patterns
    similar_patterns = matcher.find_similar_patterns(pattern_id)

    return jsonify(similar_patterns)


# ========== Combination Matching API Routes ==========
@app.route('/api/combine/story', methods=['POST'])
def create_story():
    """Create pattern + herbal medicine narrative combination"""
    data = request.json
    pattern_id = data.get('pattern_id')
    herb_id = data.get('herb_id')

    if not pattern_id or not herb_id:
        return jsonify({'error': 'pattern_id and herb_id are required'}), 400

    # Find pattern
    pattern = None
    herb = None

    for p in patterns_data:
        if p.get('id') == pattern_id:
            pattern = p
            break

    for h in herbs_data:
        if h.get('id') == herb_id:
            herb = h
            break

    if not pattern or not herb:
        return jsonify({'error': 'Pattern or herbal medicine not found'}), 404

    # Create matcher and generate story
    matcher = PatternMatcher(patterns_data, herbs_data)
    story = matcher.generate_story(pattern, herb)

    return jsonify({
        'pattern': pattern,
        'herb': herb,
        'story': story,
        'combination_name': f"{pattern['name']}·{herb['name']} Series",
        'match_score': matcher.calculate_match_score(pattern, herb)
    })


@app.route('/api/combinations/all')
def get_all_combinations():
    """Get all pattern + herbal medicine combinations (sorted by match score)"""
    # Create matcher
    matcher = PatternMatcher(patterns_data, herbs_data)

    # Get all combinations
    combinations = matcher.find_all_combinations(max_results=50)

    # Group by match score
    excellent = [c for c in combinations if c['score'] >= 70]
    good = [c for c in combinations if 50 <= c['score'] < 70]
    experimental = [c for c in combinations if c['score'] < 50]

    return jsonify({
        'total_combinations': len(combinations),
        'excellent_matches': excellent,
        'good_matches': good,
        'experimental_matches': experimental,
        'summary': {
            'excellent_count': len(excellent),
            'good_count': len(good),
            'experimental_count': len(experimental),
            'best_match': combinations[0] if combinations else None
        }
    })


@app.route('/api/combinations/cultural')
def get_cultural_combinations():
    """Get combinations by cultural matching"""
    # Group by culture
    chinese_patterns = [p for p in patterns_data if p.get('culture') == 'chinese']
    muslim_patterns = [p for p in patterns_data if p.get('culture') == 'muslim']

    matcher = PatternMatcher(patterns_data, herbs_data)

    results = []

    # Chinese patterns + herbal medicines
    for pattern in chinese_patterns[:3]:
        for herb in herbs_data[:2]:
            score = matcher.calculate_match_score(pattern, herb)
            story = matcher.generate_story(pattern, herb)
            results.append({
                'type': 'Cultural Match (Chinese)',
                'pattern': pattern,
                'herb': herb,
                'score': score,
                'story': story
            })

    # Muslim patterns + herbal medicines
    if muslim_patterns:
        for pattern in muslim_patterns[:2]:
            for herb in herbs_data[:2]:
                score = matcher.calculate_match_score(pattern, herb)
                story = matcher.generate_story(pattern, herb)
                results.append({
                    'type': 'Cultural Match (Muslim)',
                    'pattern': pattern,
                    'herb': herb,
                    'score': score,
                    'story': story
                })

    return jsonify(results)


@app.route('/api/combinations/random')
def get_random_combinations():
    """Get random combinations (for inspiration)"""
    import random

    count = request.args.get('count', default=10, type=int)

    random_combinations = []
    matcher = PatternMatcher(patterns_data, herbs_data)

    for _ in range(min(count, 20)):
        pattern = random.choice(patterns_data)
        herb = random.choice(herbs_data)

        score = matcher.calculate_match_score(pattern, herb)
        story = matcher.generate_story(pattern, herb)

        random_combinations.append({
            'pattern': pattern,
            'herb': herb,
            'score': score,
            'story': story,
            'combination_name': f"{pattern['name']}·{herb['name']}"
        })

    return jsonify(random_combinations)


@app.route('/api/combinations/by-color/<color>')
def get_combinations_by_color(color):
    """Get combinations by color theme"""
    # Find patterns containing this color
    matching_patterns = []
    for pattern in patterns_data:
        pattern_colors = [c.lower() for c in pattern.get('colors', [])]
        if color.lower() in pattern_colors:
            matching_patterns.append(pattern)

    if not matching_patterns:
        return jsonify({'error': f'No patterns found with {color} color'}), 404

    # Generate combinations
    combinations = []
    matcher = PatternMatcher(patterns_data, herbs_data)

    for pattern in matching_patterns[:5]:
        for herb in herbs_data[:3]:
            score = matcher.calculate_match_score(pattern, herb)
            story = matcher.generate_story(pattern, herb)

            combinations.append({
                'color_theme': color,
                'pattern': pattern,
                'herb': herb,
                'score': score,
                'story': story
            })

    # Sort by score
    combinations.sort(key=lambda x: x['score'], reverse=True)

    return jsonify({
        'color_theme': color,
        'total_combinations': len(combinations),
        'combinations': combinations[:10]
    })


@app.route('/api/combinations/recommended')
def get_recommended_combinations():
    """Get recommended combinations (algorithm-based)"""
    matcher = PatternMatcher(patterns_data, herbs_data)

    # Get all combinations and sort
    all_combinations = matcher.find_all_combinations(max_results=30)

    # Categorized recommendations
    recommendations = {
        'top_picks': all_combinations[:3],
        'cultural_matches': [],
        'color_matches': [],
        'meaning_matches': []
    }

    # Cultural match recommendations
    for combo in all_combinations:
        pattern_culture = combo['pattern'].get('culture', '')
        herb_name = combo['herb'].get('name', '')

        if pattern_culture == 'chinese' and herb_name in ['Ginseng', 'Goji Berry', 'Angelica', 'Astragalus', 'Chrysanthemum']:
            if len(recommendations['cultural_matches']) < 3:
                recommendations['cultural_matches'].append(combo)
        elif pattern_culture == 'muslim' and herb_name not in ['Ginseng', 'Goji Berry', 'Angelica', 'Astragalus', 'Chrysanthemum']:
            if len(recommendations['cultural_matches']) < 3:
                recommendations['cultural_matches'].append(combo)

    # Color theme recommendations
    color_groups = {}
    for combo in all_combinations:
        colors = combo['pattern'].get('colors', [])
        if colors:
            main_color = colors[0]
            if main_color not in color_groups:
                color_groups[main_color] = []
            if len(color_groups[main_color]) < 2:
                color_groups[main_color].append(combo)

    recommendations['color_matches'] = []
    for color, combos in color_groups.items():
        recommendations['color_matches'].extend(combos)

    return jsonify(recommendations)


@app.route('/api/stats')
def get_stats():
    """Get platform statistics"""
    total_patterns = len(patterns_data)
    total_herbs = len(herbs_data)

    # Calculate possible combinations
    total_possible_combinations = total_patterns * total_herbs

    # Calculate generated combinations
    matcher = PatternMatcher(patterns_data, herbs_data)
    generated_combinations = matcher.find_all_combinations(max_results=100)

    return jsonify({
        'total_patterns': total_patterns,
        'total_herbs': total_herbs,
        'total_combinations': total_possible_combinations,
        'generated_combinations': len(generated_combinations),
        'matching_algorithms': ['Cultural Match', 'Color Match', 'Meaning Match', 'Random Innovation']
    })


# ========== Image Serving Routes ==========
@app.route('/data/patterns/<path:filename>')
def serve_pattern_image(filename):
    """Serve pattern images, supporting Chinese filenames"""
    try:
        # Decode URL-encoded Chinese filenames
        decoded_filename = urllib.parse.unquote(filename)
        # Ensure directory exists
        image_directory = os.path.join('data', 'patterns')

        # Check if file exists
        file_path = os.path.join(image_directory, decoded_filename)
        if not os.path.exists(file_path):
            print(f"Image not found: {file_path}")
            # Return placeholder image
            return send_from_directory('static', 'placeholder.jpg')

        return send_from_directory(image_directory, decoded_filename)
    except Exception as e:
        print(f"Cannot serve image {filename}: {e}")
        # Return placeholder image
        return send_from_directory('static', 'placeholder.jpg')


@app.route('/data/products/<path:filename>')
def serve_product_image(filename):
    """Serve product images"""
    try:
        # Decode URL-encoded Chinese filenames
        decoded_filename = urllib.parse.unquote(filename)
        # Ensure directory exists
        image_directory = os.path.join('data', 'products')

        # Check if file exists
        file_path = os.path.join(image_directory, decoded_filename)
        if not os.path.exists(file_path):
            print(f"Product image not found: {file_path}")
            # Return placeholder image
            return send_from_directory('static', 'placeholder.jpg')

        return send_from_directory(image_directory, decoded_filename)
    except Exception as e:
        print(f"Cannot serve product image {filename}: {e}")
        # Return placeholder image
        return send_from_directory('static', 'placeholder.jpg')


# ========== Main Program Entry ==========
if __name__ == '__main__':
    # Ensure necessary directories exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('data/patterns', exist_ok=True)
    os.makedirs('data/products', exist_ok=True)  # 添加这行

    # Run application
    app.run(debug=True, host='0.0.0.0', port=5000)