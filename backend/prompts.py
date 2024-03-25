import sys

# sys.path.append("..")
from ollama_client import generate

DEFAULT_MODEL = "mistral-openorca:latest"


def create_hypothesis(
    question: str,
    model: str = DEFAULT_MODEL,
): 
    SYS_PROMPT = (
        "You will be provided with a 'question'."
        " Your task is to create a hypothesis on what information is required to answer the 'question'."
        " The hypothesis will be used to search a large document for context relevant to the question."
        " You can use the following chain of thoughts:\n"
        " \tThought 1: Concepts. What are the entities like subject, predicate, etc. mentioned in the question?\n"
        " \tThought 2: Context. What additional context may help you know more about these entities to answer the question?\n"
        " Do not use any prior knowledge. If it is not possible to make a hypothesis, return the original question."
        " Format your answer as the following: \n"
        " Concepts: \n"
        " Context: \n"
    )

    prompt = f"Question: ``` {question} ```\n Your response:"

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)
    return response
    

def retrieve_answer(
    question: str,
    context: str,
    model: str = DEFAULT_MODEL
):
    SYS_PROMPT = (
        "You will be provided with a 'question' and a list of 'excerpts' from a long document (delimited by ```)."
        " Your task is to answer the question based on information given documents excerpts."
        " Make sure the answer really reflects the question. "
        " Answer in a crisp, objective and business casual tone."
    )

    prompt = (
        f"Question:\n ``` {question} ```\n"
        f"Excerpts:\n ``` {context} ```\n"
        "Your response:"
    )
    # print("\n---\n", SYS_PROMPT, prompt, "\n---\n")
    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)

    return response



def create_questions(
    question: str,
    context: str,
    previous_questions: str,
    model: str = DEFAULT_MODEL,
    num_questions = 2,
):
    SYS_PROMPT = (
        "Your are a curious researcher. Your task is to ask questions that can help you answer the goal question. "
        "You will be given a 'goal question', a 'context' and some 'previously asked questions' as input (delimited by ```). "
        "Use the following chain of thoughts:\n"
        "Thought 1: Use only the given 'context' and the 'goal question', and no other previous knowledge."
        "Thought 2: Think about questions you can ask that can not be answered using the given context.\n"
        "Thought 3: Think about if these questions are directly relevant to your goal question. Discard the questions that are not relevant.\n"
        "Thought 4: Discard the questions that are semantically similar to the 'previously asked questions'.\n"
        f"Respond with at most {num_questions} questions. "
        "Format your response as a python list of questions like:\n "
        " ['First Question', 'Second Question', ...]"
    )

    prompt = (
        f"Goal Question: ``` {question} ```.\n\n"
        f"Context: \n ``` {context} ``` \n\n"
        f"Previously Asked Questions:  ``` {previous_questions} ```\n\n"
        "Your response:"
    )

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)

    return response

    
    

def create_questions(
    question: str,
    context: str,
    previous_questions: str,
    model: str = DEFAULT_MODEL,
    num_questions=2,
):
    SYS_PROMPT = (
        "Your are a curious researcher. Your task is to ask questions that can help you answer the goal question. "
        "You will be given a 'goal question', a 'context' and some 'previously asked questions' as input (delimited by ```). "
        "Use the following chain of thoughts:\n"
        "Thought 1: Use only the given 'context' and the 'goal question', and no other previous knowledge."
        "Thought 2: Think about questions you can ask that can not be answered using the given context.\n"
        "Thought 3: Think about if these questions are relevant to your goal question. Discard the questions that are not relevant.\n"
        "Thought 4: Discard the questions that are semantically similar to the 'previously asked questions'.\n"
        f"Respond with at most {num_questions} questions. "
        "Format your response as a python list of questions like:\n "
        " ['First Question', 'Second Question', ...]"
    )

    prompt = (
        f"Goal Question: ``` {question} ```.\n\n"
        f"Context: \n ``` {context} ``` \n\n"
        f"Previously Asked Questions:  ``` {previous_questions} ```\n\n"
        "Your response:"
    )

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)

    return response


def choose_best_question(
    question: str,
    unanswered_questions: str,
    model=DEFAULT_MODEL,
):
    SYS_PROMPT = (
        "You are a curious researcher. Your task is to choose one question "
        "from a given list of 'unanswered questions' (delimited by ```). "
        "You are provided with a 'goal question' and a numbered list of 'unanswered questions' as inputs. "
        "Think about which question out of the given list of questions can help you answer the 'goal question'. "
        "Don't choose a question that doesn't seem to relate to the 'goal question'."
        "Choose one and only one question from the list of 'unanswered questions'.\n"
        "Respond with the choosen question as it is, ditto without any edits."
        " Remember the format of the output should look like:\n"
        " question_id. question"
    )

    prompt = (
        f"Goal Question: ``` {question} ```.\n\n"
        f"Unanswered Questions:  ``` {unanswered_questions} ```\n\n"
        "Your response:"
    )

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)

    return response


def refine_answer(
    question: str,
    answer: str,
    context: str,
    model=DEFAULT_MODEL,
):
    SYS_PROMPT = (
        "You will be provided with a 'question', an 'existing answer', and some 'new context'"
        " You have the opportunity to improve upon the 'existing answer'"
        " Using the following chain of thought:\n"
        "\t - Is the 'new context' relevant to the 'question'?.\n"
        "\t - Is there any new information in the 'new context' that can be added to the 'existing answer'?\n"
        "\t - Are there any corrections needed to the 'existing answer' based on 'new context'\n"
        "\t - Can you augment or correct the 'existing answer' using the 'new context'?\n"
        " Refine the 'existing answer' only if needed. Use only the given context. Do not use any pre-existing knowledge.\n"
        " Respond with a new answer and get rid of any information that may not be especially relevant to the 'question'."
        " Use a descriptive style and a business casual language."
    )

    prompt = (
        f"Question: ``` {question} ```\n"
        f"Existing Answer: ``` {answer} ```\n"
        f"New Context: ``` {context} ```\n"
        "New Answer:"
    )

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)

    return response





# For when the robot asks question based on text, add complexity?
def create_questions_from_text(
    question_type: str,
    context: str,
    previous_questions: str,
    model=DEFAULT_MODEL,
):
    SYS_PROMPT = (
        "Your are a test administrator. "
        "Your task is to ask questions that fits the 'question type' if it is not an empty string that can test takers could answer based on the 'context'. "
        "You will be given a 'question type', a 'context' and some 'previous questions' as input (delimited by ```). "
        "Use the following chain of thoughts:\n"
        "Thought 1: ."
        "Thought 2: Think about questions you can ask that a student could answer using the given context.\n"
        "Thought 3: Discard the questions that are semantically similar to the 'previous questions'.\n"
        "Thought 4: If the question type is not empty, does the question fit the 'question type'?\n"
         " Respond with a new answer and get rid of any information that may not be especially relevant to the 'question'."
        " Use a descriptive style and a business casual language."
    )

    prompt = (
        f"Question type: ``` {question_type} ```.\n\n"
        f"Context: \n ``` {context} ``` \n\n"
        f"Previously Asked Questions:  ``` {previous_questions} ```\n\n"
        "Your response:"
    )

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)

    return response



# Answer if the student answer correctly answers the question? or
def create_questions_from_text(
    question_type: str,
    context: str,
    previous_questions: str,
    model: str = DEFAULT_MODEL,
):
    SYS_PROMPT = (
        "Your are a test administrator. "
        "Your task is to ask questions that fits the 'question type' if it is not an empty string that can test takers could answer based on the 'context'. "
        "You will be given a 'question type', a 'context' and some 'previous questions' as input (delimited by ```). "
        "Use the following chain of thoughts:\n"
        "Thought 1: ."
        "Thought 2: Think about questions you can ask that a student could answer using the given context.\n"
        "Thought 3: Discard the questions that are semantically similar to the 'previous questions'.\n"
        "Thought 4: If the question type is not empty, does the question fit the 'question type'?\n"
         " Respond with a new answer and get rid of any information that may not be especially relevant to the 'question'."
        " Use a descriptive style and a business casual language."
    )

    prompt = (
        f"Question type: ``` {question_type} ```.\n\n"
        f"Context: \n ``` {context} ``` \n\n"
        f"Previously Asked Questions:  ``` {previous_questions} ```\n\n"
        "Your response:"
    )
    print(context)

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)

    return response
