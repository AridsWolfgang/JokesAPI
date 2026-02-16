from flask import Flask, jsonify, request
import random

app = Flask(__name__)

jokes = {
    "programming": [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the programmer quit his job? Because he didn't get arrays!",
        "A SQL query goes into a bar, walks up to two tables and asks: 'Can I join you?'",
        "Why do Java developers wear glasses? Because they can't C#!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem!"
    ],
    "dad": [
        "Why don't eggs tell jokes? They'd crack each other up!",
        "I'm reading a book on anti-gravity. It's impossible to put down!",
        "What do you call a fake noodle? An impasta!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "What do you call a fish with no eyes? A fsh!"
    ],
    "punny": [
        "I used to be a baker, but I couldn't make enough dough.",
        "I'm reading a book about mazes. I got lost in it.",
        "I told my wife she should embrace her mistakes. She gave me a hug.",
        "What's the best thing about Switzerland? I don't know, but the flag is a big plus.",
        "I don't trust stairs. They're always up to something."
    ],
    "knock-knock": [
        "Knock knock. Who's there? Lettuce. Lettuce who? Lettuce in, it's cold out here!",
        "Knock knock. Who's there? Atch. Atch who? Bless you!",
        "Knock knock. Who's there? Interrupting cow. Interrupting cow wh- MOO!",
        "Knock knock. Who's there? Tank. Tank who? You're welcome!",
        "Knock knock. Who's there? Opportunity. That's impossible. Opportunity doesn't come knocking twice!"
    ],
    "general": [
        "Why don't skeletons fight each other? They don't have the guts!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why did the bicycle fall over? Because it was two-tired!",
        "What do you call a sleeping bull? A bulldozer!",
        "How does a penguin build its house? Igloos it together!"
    ]
}

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Joke Generator API! 🎭",
        "endpoints": {
            "/joke": "Get a random joke (any category)",
            "/joke?type=programming": "Get a random programming joke",
            "/joke?type=dad": "Get a random dad joke",
            "/categories": "See all available joke categories",
            "/jokes/all": "See all jokes (all categories)"
        }
    })

@app.route('/joke')
def get_joke():
    category = request.args.get('type', 'any').lower()
    
    if category == 'any' or category not in jokes:
        random_category = random.choice(list(jokes.keys()))
        category_jokes = jokes[random_category]
        category_name = random_category
    else:
        category_jokes = jokes[category]
        category_name = category
    
    selected_joke = random.choice(category_jokes)
    
    return jsonify({
        "joke": selected_joke,
        "category": category_name,
        "id": jokes[category_name].index(selected_joke) + 1  
    })

@app.route('/categories')
def get_categories():
    return jsonify({
        "categories": list(jokes.keys()),
        "count": len(jokes)
    })

@app.route('/jokes/all')
def get_all_jokes():
    return jsonify(jokes)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=3000)