import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from chatbot.Audio import Audio

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")


embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
vector_store = PineconeVectorStore(index_name='violations-data-10',embedding=embeddings)

llm = ChatOpenAI(verbose=True, temperature=0.5, model="gpt-4")


template = """
 أنت مساعد ومحلل بيانات في قسم المرور، ومهمتك هي مساعدة القسم في إجراء التحليلات اللازمة على قاعدة البيانات والإجابة على الأسئلة المتعلقة بها. يُرجى استخدام قاعدة البيانات كمرجع للإجابة على الأسئلة التي تتلقاها.

مثال على سؤال:
كم عدد المخالفات المرورية في يوم 2024/09/22؟

مثال على إجابة:
عدد المخالفات المرورية   في يوم 2024/09/22 الموافق يوم الأحد كان 17 مخالفة. نوع المخالفة: تجاوز من الاكتاف

مثال على سؤال:
ما هي الأماكن التي تم رصد المخالفات فيها؟

مثال على إجابة:
تم رصد المخالفات في الطرق التالية: طريق الملك فهد, طريق المطار , طريق الملك سلمان
"إذا كنت لا تعرف الإجابة، ببساطة قل: "لا أعرف.
context: {context}

question: {question}

answer:
"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=template,
)



def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])


chain = (
    {"context": vector_store.as_retriever() | format_docs, "question": RunnablePassthrough()}
    |prompt
    |llm
    |StrOutputParser()
)

#chat history
history = []

#counter for the audio files
counter = 0

#initialize the audio class
Au = Audio()

def start():
    while True:
        #record question audio from user
        recording, _ = Au.record_audio()

        #save audio recorded to a file
        Au.write_audio(recording, f"voice_records/question{counter}.mp3")

        #convert saved audio to text
        question = Au.voice_to_text(f"./voice_records/question{counter}.mp3")

        #print the question to the terminal and save it to the history
        Au.printAr(f"المستخدم: {question}")
        history.append(question)

        #invoke the model
        answer = chain.invoke(question)

        #print the model answer to the terminal and save it to the history
        Au.printAr(f"المساعد الذكي: {answer}")
        history.append(answer)

        #convert the answer to voice
        Au.text_to_voice(answer, f"./voice_records/answer{counter}.mp3")

        #play the answer
        Au.play_sound(f"./voice_records/answer{counter}.mp3")
        counter += 1

if __name__ == "__main__":
    start()
    with open("./history.txt", "a") as f:
        f.write("\n".join(history))
    
