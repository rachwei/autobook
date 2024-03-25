import ast
from typing import Optional
from prompts import create_hypothesis, retrieve_answer, create_questions, choose_best_question, refine_answer
from prompts import create_questions_from_text
from vector_retriever import VectorRetriever
from helpers import get_postgre_database


# https://github.com/rahulnyk/research_agent


# add way to connect an answer to a question
class Answer:
    def __init__(self, answer: str, id: int, question_id = None, docs = None):
        self.answer = answer
        self.id = id
        self.question_id = question_id
        self.docs = docs

class Question:
    def __init__(self, question: str, id: int, parent_id: int = None):
        self.question = question
        self.id = id
        self.parent_id = parent_id if parent_id != None else id
        self.status = "unanswered"


class Notepad:
    def __init__(self, initial_question: Optional[str] = None):
        self.current_question_id = 0
        self.answers = []
        self.questions = [Question(question=initial_question, id=0)] if initial_question else []

        self.next_question_id = len(self.questions)
        self.next_answer_id = 0
        self.initial_question_id = 0
        self.initial_answer_id = 0
    
    # also have to add status of the question
    def add_question_to_notepad(self, question: str, parent_id: int = None, initial: bool = False):
        print("Adding question: ", question)
        self.questions.append(Question(question=question, id=self.next_question_id, parent_id=parent_id))

        if initial:
            self.initial_question_id = self.next_question_id

        self.next_question_id += 1
    
    def add_answer_to_notepad(self, answer: str, question_id: int = None, docs = None, initial = False):
        # print("Adding answer: ", answer)
        self.answers.append(Answer(answer=answer, id=self.next_question_id, question_id=question_id, docs=docs))

        if initial:
            self.initial_answer_id = self.next_answer_id
        
        if question_id is not None:
            question = self.get_question_from_id(question_id)
            question.status = "solved"

        self.next_answer_id += 1
    
    def get_question_from_id(self, question_id: int):
        potent = list(filter(lambda x: x.id == question_id, self.questions))
        return potent[0] if potent else None

    def get_all_questions(self):
        return [question.question for question in self.questions]

    def get_last_answer(self):
        return self.answers[-1].answer

    def get_unanswered_questions(self):
        return [question for question in self.questions if question.status == "unanswered"]

    def get_most_revised_answer(self):
        return next((answer.answer for answer in reversed(self.answers) 
                     if answer.question_id == self.initial_question_id), None)


class Agent:
    def __init__(self, model: str, vector_retriever: VectorRetriever):
        self.model = model
        self.notepad = Notepad()
        self.vector_retriever = vector_retriever
    
    def create_initial_hypothesis(self, question: str):
        response = create_hypothesis(question, self.model)
        self.notepad.add_answer_to_notepad(response)
        return response

    def generate_answer(self, question_id: int, docs, initial = False):
        question = self.notepad.get_question_from_id(question_id)
        if question:
            context = "\n----\n".join(
                [f"Excerpt:\n {doc.page_content}\n- Source: {doc.metadata}" for doc in docs]
            )
            response = retrieve_answer(question.question, context, self.model)
            self.notepad.add_answer_to_notepad(response, question_id, docs, initial)
            return response
        
        return None

    def generate_questions(self, parent_id: int, num_questions = 2):
        previous_questions = self.notepad.get_all_questions()
        goal = self.notepad.get_question_from_id(self.notepad.initial_question_id)
        context = self.notepad.get_last_answer()

        # print("Previous questions: ", previous_questions)
        generated = []
        max_tries = 5

        while goal is not None and len(generated) < num_questions and max_tries > 0:
            response = create_questions(goal.question, context, previous_questions, self.model, num_questions)
            print("Response ", response)
            # might have some issues if there are commas in each question
            generated.extend([s.strip().strip("'") for s in response.strip().strip("[]").split(',')])

            max_tries -= 1

        for new_question in generated:
            print("question in generated", new_question)
            self.notepad.add_question_to_notepad(new_question, parent_id)

        return generated

    def choose_question(self):
        goal = self.notepad.get_question_from_id(self.notepad.initial_question_id)
        unanswered_questions = self.notepad.get_unanswered_questions()
        q_list = [f"{q.id}. '{q.question}'" for q in unanswered_questions]
        q_string_list = "[\n" + ",\n".join(q_list) + "\n]"

        max_tries = 5

        while max_tries > 0 and goal is not None:
            result = choose_best_question(goal.question, q_string_list, self.model)
            print("Preliminary best question: ", result)

            try:
                split = result.strip(" '\"").split(".", 1)
                question_id = int(split[0])
                question = split[-1].strip()
                
                return question_id, question
            except:
                max_tries -= 1
        
        return None

    def refine_answer(self, new_context):
        goal = self.notepad.get_question_from_id(self.notepad.initial_question_id)
        most_recent_answer = self.notepad.get_most_revised_answer()

        if most_recent_answer is not None and goal is not None:
            new_answer = refine_answer(goal.question, most_recent_answer, new_context, self.model)
            self.notepad.add_answer_to_notepad(new_answer, self.notepad.initial_question_id)
            return new_answer
    
        return None

    # def get_relevant_documents(self, ):
        

    def answer_question(self, question: str, max_iter: int = 2):
        print("Initial question: ", question)
        self.notepad.add_question_to_notepad(question, initial=True)

        #1. CREATE HYPOTHESIS
        initial_hyp = self.create_initial_hypothesis(question)
        hypothesis = f"{question}\n{initial_hyp}"
        docs = self.vector_retriever.get_docs(question)

        print("Hypothesis: ", hypothesis)
        print("\n\n\n")
        print("Retrieved docs: ", docs)

        # way to check if the retrieved docs are relevant?

        #2: GET INITIAL ANSWER
        initial_answer = self.generate_answer(self.notepad.initial_question_id, docs=docs, initial=True)
        print("Initial answer: ", initial_answer)
        parent_id = self.notepad.initial_question_id
        
        for i in range(max_iter):
            print("Iteration: ", i)
            # generate a bunch of questions
            new_questions = self.generate_questions(parent_id)
            print("Create questions response: ", new_questions)
            if not len(new_questions): 
                break
            
            # pick one question
            chosen_question_id, chosen_question = self.choose_question()
            parent_id = chosen_question_id
            print("Chosen question: ", chosen_question)

            # answer current question
            docs = self.vector_retriever.get_docs(chosen_question)
            int_answer = self.generate_answer(chosen_question_id, docs=docs, initial=True)
            print("Intermediate answer: ", int_answer)

            # refine answer?
            new_result = self.refine_answer(
                new_context=int_answer
            )
            print("New revised answer: ", new_result)
            print("\n\n\n")
    
        result = self.notepad.get_most_revised_answer()
        print("Final answer!!!!")
        print(result)
        return result
    

    async def generate_questions_from_text(self, question_type = "Anything", context = "", previous_questions = []):
        # get context here! and then you're done
        docs = self.vector_retriever.get_context()
        context = ''.join(doc[0] for doc in docs)
        new_answer = create_questions_from_text(question_type, context, previous_questions, self.model)
        print("new answer: ", new_answer)
        return new_answer


if __name__ == '__main__':
    connection_string = get_postgre_database("legal_docs")
    collection = "legal_docs_embeddings"
    vector_retriever = VectorRetriever(conn_string=connection_string, collection=collection)

    agent = Agent(model="mistral-openorca:latest", vector_retriever=vector_retriever)
    agent.answer_question("what is AL?")


# would adding a context to the thing be helpful?
# seeing how the machine sees the text
# does the question relate to the original question?