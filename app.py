from flask import Flask, request, jsonify, session
from flask_cors import CORS
from akinator.akinator import Akinator
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # Secure random key for production
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["https://mind-reader.sculptvid.com"],
            "supports_credentials": True
        }
    }
)

@app.route('/api/start', methods=['POST'])
def start_game():
    try:
        data = request.json
        lang = data.get('lang', 'en')
        child_mode = data.get('child_mode', "true") == "true"  # Convert string to boolean

        # Create new Akinator game
        aki = Akinator(lang=lang, child_mode=child_mode)
        aki.start_game()

        # Save game state to session
        session['akinator_state'] = json.dumps(aki.json)

        return jsonify({
            'question': aki.question,
            'progression': aki.progression,
            'step': aki.step
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/answer', methods=['POST'])
def post_answer():
    try:
        data = request.json
        answer = data.get('answer')

        if 'akinator_state' not in session:
            return jsonify({'error': 'Invalid session'}), 400

        aki = Akinator()
        aki.json = json.loads(session['akinator_state'])

        aki.post_answer(answer)

        # Save updated game state
        session['akinator_state'] = json.dumps(aki.json)

        response = {
            'question': aki.question,
            'progression': aki.progression,
            'step': aki.step
        }

        if aki.answer_id:
            response['guess'] = {
                'id': aki.answer_id,
                'name': aki.name,
                'description': aki.description,
                'picture': aki.photo if hasattr(aki, 'photo') else None
            }

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/back', methods=['POST'])
def go_back():
    try:
        if 'akinator_state' not in session:
            return jsonify({'error': 'Invalid session'}), 400

        aki = Akinator()
        aki.json = json.loads(session['akinator_state'])

        aki.go_back()

        session['akinator_state'] = json.dumps(aki.json)

        return jsonify({
            'question': aki.question,
            'progression': aki.progression,
            'step': aki.step
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exclude', methods=['POST'])
def exclude_guess():
    try:
        if 'akinator_state' not in session:
            return jsonify({'error': 'Invalid session'}), 400

        aki = Akinator()
        aki.json = json.loads(session['akinator_state'])

        aki.exclude()

        session['akinator_state'] = json.dumps(aki.json)

        return jsonify({
            'question': aki.question,
            'progression': aki.progression,
            'step': aki.step
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/end', methods=['POST'])
def end_game():
    try:
        session.pop('akinator_state', None)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
