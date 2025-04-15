# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from aki1_api import Akinator
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store active Akinator sessions
akinator_sessions = {}


@app.route('/api/start', methods=['POST'])
def start_game():
    try:
        data = request.json
        lang = data.get('lang', 'en')
        child_mode = data.get('child_mode', "true")

        # Create a new Akinator instance
        aki = Akinator(lang=lang, child_mode=child_mode)
        aki.start_game()

        # Generate a unique session ID
        session_id = str(uuid.uuid4())

        # Store the session
        akinator_sessions[session_id] = aki

        return jsonify({
            'session_id': session_id,
            'question': aki.question,
            'progression': aki.progression
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/answer', methods=['POST'])
def post_answer():
    try:
        data = request.json
        session_id = data.get('session_id')
        answer = data.get('answer')

        if not session_id or not answer or session_id not in akinator_sessions:
            return jsonify({'error': 'Invalid session or answer'}), 400

        aki = akinator_sessions[session_id]
        aki.post_answer(answer)

        response = {
            'question': aki.question,
            'progression': aki.progression,
            'step': aki.step
        }

        # Check if Akinator has a guess
        if aki.answer_id:
            response['guess'] = {
                'id': aki.answer_id,
                'name': aki.name,
                'description': aki.description,
                'picture': aki.picture if hasattr(aki, 'picture') else None
            }

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/back', methods=['POST'])
def go_back():
    try:
        data = request.json
        session_id = data.get('session_id')

        if not session_id or session_id not in akinator_sessions:
            return jsonify({'error': 'Invalid session'}), 400

        aki = akinator_sessions[session_id]
        aki.go_back()

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
        data = request.json
        session_id = data.get('session_id')

        if not session_id or session_id not in akinator_sessions:
            return jsonify({'error': 'Invalid session'}), 400

        aki = akinator_sessions[session_id]
        aki.exclude()

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
        data = request.json
        session_id = data.get('session_id')

        if session_id and session_id in akinator_sessions:
            # Clean up the session
            del akinator_sessions[session_id]

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
