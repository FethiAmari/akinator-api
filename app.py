import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from myaki_api import Akinator  # Replace this with your Akinator class import
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)  # Adjust level to DEBUG for more detailed logs
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS with your frontend domain (replace with your actual domain)
CORS(app, origins=["https://aki.sculptvid.com"])  # Replace with your frontend domain

# Store active Akinator sessions
akinator_sessions = {}

# Request logging before every request
@app.before_request
def log_request():
    logger.info(f"Request {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Body: {request.get_data(as_text=True)}")  # Logs the request body (if any)

# Response logging after every request
@app.after_request
def log_response(response):
    logger.info(f"Response status: {response.status}")
    logger.info(f"Response data: {response.get_data(as_text=True)}")
    return response

# Start the game route
@app.route('/api/start', methods=['POST'])
def start_game():
    try:
        # Get data from the request
        data = request.json
        lang = data.get('lang', 'en')  # Default to English
        child_mode = data.get('child_mode', "true")  # Default to True

        logger.info(f"Starting game with lang={lang}, child_mode={child_mode}")

        # Create a new Akinator instance (replace with your actual Akinator class)
        aki = Akinator(lang=lang, child_mode=child_mode)
        aki.start_game()

        # Generate a unique session ID
        session_id = str(uuid.uuid4())

        # Store the session
        akinator_sessions[session_id] = aki

        logger.info(f"Game started with session_id={session_id}")

        return jsonify({
            'session_id': session_id,
            'question': aki.question,
            'progression': aki.progression
        })
    except Exception as e:
        logger.error(f"Error in start_game: {e}")
        return jsonify({'error': str(e)}), 500

# Post answer route
@app.route('/api/answer', methods=['POST'])
def post_answer():
    try:
        # Get data from the request
        data = request.json
        session_id = data.get('session_id')
        answer = data.get('answer')

        logger.info(f"Received answer '{answer}' for session_id={session_id}")

        # Validate session_id and answer
        if not session_id or not answer or session_id not in akinator_sessions:
            logger.error(f"Invalid session_id={session_id} or missing answer")
            return jsonify({'error': 'Invalid session or answer'}), 400

        # Retrieve the session and post the answer
        aki = akinator_sessions[session_id]
        aki.post_answer(answer)

        # Prepare the response
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
                'picture': aki.picture if hasattr(aki, 'picture') else None
            }

        logger.info(f"Answered, new question: {aki.question}")

        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in post_answer: {e}")
        return jsonify({'error': str(e)}), 500

# Go back route
@app.route('/api/back', methods=['POST'])
def go_back():
    try:
        data = request.json
        session_id = data.get('session_id')

        logger.info(f"Going back for session_id={session_id}")

        if not session_id or session_id not in akinator_sessions:
            logger.error(f"Invalid session_id={session_id}")
            return jsonify({'error': 'Invalid session'}), 400

        aki = akinator_sessions[session_id]
        aki.go_back()

        return jsonify({
            'question': aki.question,
            'progression': aki.progression
        })
    except Exception as e:
        logger.error(f"Error in go_back: {e}")
        return jsonify({'error': str(e)}), 500

# Exclude guess route
@app.route('/api/exclude', methods=['POST'])
def exclude_guess():
    try:
        data = request.json
        session_id = data.get('session_id')

        logger.info(f"Excluding guess for session_id={session_id}")

        if not session_id or session_id not in akinator_sessions:
            logger.error(f"Invalid session_id={session_id}")
            return jsonify({'error': 'Invalid session'}), 400

        aki = akinator_sessions[session_id]
        aki.exclude_guess()

        return jsonify({
            'question': aki.question,
            'progression': aki.progression
        })
    except Exception as e:
        logger.error(f"Error in exclude_guess: {e}")
        return jsonify({'error': str(e)}), 500

# End game route
@app.route('/api/end', methods=['POST'])
def end_game():
    try:
        data = request.json
        session_id = data.get('session_id')

        logger.info(f"Ending game for session_id={session_id}")

        if not session_id or session_id not in akinator_sessions:
            logger.error(f"Invalid session_id={session_id}")
            return jsonify({'error': 'Invalid session'}), 400

        aki = akinator_sessions[session_id]
        aki.end_game()

        # Remove session from active sessions
        del akinator_sessions[session_id]

        return jsonify({'message': 'Game ended successfully'})
    except Exception as e:
        logger.error(f"Error in end_game: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
