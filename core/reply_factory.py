
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    
    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        session['user_answers'] = {}
       
    else:
        success, error = record_current_answer(message, current_question_id, session)
        if not success:
            return [error]

    next_question, options,next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
        bot_responses.append(options)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses

def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
   
    if current_question_id is None:
        return False, "Error: No current question"
    if answer.isdigit():
        if (int(answer)<1 or int(answer)>4):
            return False, "Error: Invalid Answer Submitted"
        
        user_answers = session.get('user_answers', {})
       
        # Fetching current question from question list
        current_question = PYTHON_QUESTION_LIST[current_question_id]
        options = current_question.get('options')
        correct_answer = current_question.get('answer')
        user_answer = options[int(answer)-1]

        is_correct = user_answer == correct_answer

        if 'user_answers' not in session:
            session['user_answers'] = {}

        session['user_answers'][int(current_question_id)] = is_correct

        session.save()
        
        return True, ""
    return False, "Error: Invalid Answer Submitted"


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        get_question = PYTHON_QUESTION_LIST[0]
        next_question = get_question.get('question_text')
        option =  get_question.get('options')
        i=1
        options = []
        for o in option:
            options.append(f'<br>({i}) {o}')
            i+=1
        return next_question,options, 0

    next_question_id = current_question_id + 1
    if next_question_id < len(PYTHON_QUESTION_LIST):
        get_question = PYTHON_QUESTION_LIST[next_question_id]
        next_question = get_question.get('question_text')
        option =  get_question.get('options')
        i=1
        options = []
        for o in option:
            options.append(f'<br>({i}) {o}')
            i+=1
        return next_question,options, next_question_id
    else:
        return None, None, -1

def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get('user_answers', {})
    print(user_answers)
    correct_answers = sum(1 for answer in user_answers.values() if answer)
    total_questions = len(PYTHON_QUESTION_LIST)
    score_percentage = (correct_answers / total_questions) * 100

    final_response = f"Your quiz result:<br>Total Questions: {total_questions}<br>Correct Answers: {correct_answers}<br>Score: {score_percentage:.2f}%"

    return final_response


