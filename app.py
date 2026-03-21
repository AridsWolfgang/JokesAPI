from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# ===========================================[Jokes Data]================================================
# Sample Data but will use a database for large data (will soon get to that point)
jokes = [
    {
        "id": 1,
        "category": "technology",
        "joke": "Why did the computer go to therapy? It had a virus.",
    },
    {
        "id": 2,
        "category": "puns",
        "joke": "Why did scarecrow win an award? Because, he was outstanding in his field!.",
    },
    {
        "id": 3,
        "category": "one-liners",
        "joke": "I'm reading a book on anti-gravity. It's impossible to put down!.",
    },
    {
        "id": 4,
        "category": "knock-knock",
        "joke": "Knock, knock! Who's there? Cows go. Cows go who? No, cows go 'moo'.",
    },
    {
        "id": 5,
        "category": "play-on-words",
        "joke": "Why did the baker go to the bank? He needed dough!.",
    },
    {
        "id": 6,
        "category": "sarcastic",
        "joke": "Oh great, just what i needed, another thing to worry about... said no one ever.",
    },
    {
        "id": 7,
        "category": "observational",
        "joke": "You know what's weird? We spend the first year of a child's life teaching them to walk and talk, and the rest of their lives telling them to shut up and sit down",
    },
    {
        "id": 8,
        "category": "dads",
        "joke": "Why did the mushroom go to the party? Because he was a fun-gi.",
    },
    {
        "id": 9,
        "category": "dark",
        "joke": "Why did the morgue employee quit? He couldn't handle the dead-end job.",
    },
    {
        "id": 10,
        "category": "parody",
        "joke": "I'm not lazy, i'm just on energy-saving mode.",
    },
    {
        "id": 11,
        "category": "lightbulb",
        "joke": "How many programmers does it take to screw in a lightbulb? None, it's a hardware problem.",
    },
    {
        "id": 12,
        "category": "animals",
        "joke": "Why did the cat join a band? Because it wanted to be a purr-cussionist.",
    },
    {
        "id": 13,
        "category": "food",
        "joke": "Why was the pizza in a bad mood? It was feeling crusty.",
    },
    {
        "id": 14,
        "category": "travel",
        "joke": "Why did the tourist bring a ladder to Paris? He wanted to elevate his experience.",
    },
    {
        "id": 15,
        "category": "school",
        "joke": "Why did the student bring a ladder to school? He wanted to reach his full potential.",
    },
]


# Still don't understand what this function does but will catch it in action
def next_id():
    return max(joke["id"] for joke in jokes) + 1 if jokes else 1


# ===========================================[Routes]================================================


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Welcome to the JokeAPI! Try /jokes or /jokes/random for the best of jokes"
        }
    )


@app.route("/jokes", methods=["GET"])
def get_jokes():
    category = request.args.get("category")
    if category:
        filtered = [j for j in jokes if j["category"].lower() == category.lower()]
        return jsonify(filtered)
    return jsonify(jokes)


@app.route("/jokes/<int:id>", methods=["GET"])
def get_joke(id):
    joke = next((j for j in jokes if j["id"] == id), None)
    if joke is None:
        return jsonify({"error": "Joke not found"}), 404
    return jsonify(joke)


@app.route("/jokes/random", methods=["GET"])
def random_jokes():
    category = request.args.get("category")
    if category:
        filtered = [j for j in jokes if j["category"].lower() == category.lower()]
        if not filtered:
            return jsonify({"error": "No jokes found for that category"}), 404
        return jsonify(random.choice(filtered))
    return jsonify(random.choice(jokes))


@app.route("/jokes", methods=["POST"])
def add_joke():
    data = request.get_json()
    if not data or "joke" not in data or "category" not in data:
        return jsonify({"error": "Missing 'joke' or 'category' in JSON body"}), 400

    new_joke = {"id": next_id(), "category": data["category"], "joke": data["joke"]}
    jokes.append(new_joke)
    return jsonify(new_joke), 201


# ===========================================[Run]================================================
if __name__ == "__main__":
    app.run(debug=True)
