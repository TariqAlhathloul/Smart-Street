import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from Audio import Audio
import datetime as dt

load_dotenv()
OPENAI_API_KEY = ("")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

os.makedirs("./chat_history", exist_ok=True)
os.makedirs("./chat_history/voice_history", exist_ok=True)
os.makedirs("./chat_history/text_history", exist_ok=True)


embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
vector_store = PineconeVectorStore(index_name='violations-data-11',embedding=embeddings)

llm = ChatOpenAI(verbose=True, temperature=0.5, model="gpt-4")


template = """
 أنت مساعد ومحلل بيانات في قسم المرور، ومهمتك هي مساعدة القسم في إجراء التحليلات اللازمة على قاعدة البيانات والإجابة على الأسئلة المتعلقة بها. يُرجى استخدام قاعدة البيانات كمرجع للإجابة على الأسئلة التي تتلقاها.

مثال على سؤال:
كم عدد المخالفات المرورية في يوم 2024/09/22؟

مثال على إجابة:
عدد المخالفات المرورية   في يوم 2024/09/22 الموافق يوم الأحد كان 17 مخالفة. نوع المخالفة: تجاوز من الاكتاف

مثال على سؤال:
ما هي الطرق التي تم رصد المخالفات فيها؟

مثال على إجابة:
تم رصد المخالفات في الطرق التالية: طريق الملك فهد, طريق المطار , طريق الملك سلمان

مثال على سؤال:
ما هي الأوقات التي تم فيها رصد المخالفات؟

مثال على إجابة:
تم رصد اغلب المخالفات في الفتره بين الثامنه والعاشره صباحا

مثال على سؤال:
ما هو مجموع المخالفات المسجلة في النظام؟
مجموع المخالفات المسجلة في النظام هو خمسه وسبعون مخالفة


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

def query_docs(context, question):
    return vector_store.query(question, context)
    

chain = (
    {"context": vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 70, 'fetch_k': 50}) | format_docs, "question": RunnablePassthrough()}
    |prompt
    |llm
    |StrOutputParser()
)

#chat history
history = []

def start():
    
    #counter for the audio files
    counter = 0

    #initialize the audio class
    Au = Audio()
    #Au.play_sound("welcome.mp3")
    while True:
        #record question audio from user
        try:
            recording, _ = Au.record_audio()
        except Exception as e:
            print(f"Error recording audio: {e}")
            continue

        #save audio recorded to a file
        Au.write_audio(recording, f"./chat_history/voice_history/question{counter}.mp3")

        #convert saved audio to text
        question = Au.voice_to_text(f"./chat_history/voice_history/question{counter}.mp3")

        #print the question to the terminal and save it to the history
        Au.printAr(f"المستخدم: {question}")
        history.append(question)

        #invoke the model
        answer = chain.invoke(question)

        #print the model answer to the terminal and save it to the history
        Au.printAr(f"المساعد الذكي: {answer}")
        history.append(answer)

        #convert the answer to voice
        Au.text_to_voice(answer, f"./chat_history/voice_history/answer{counter}.mp3")

        #play the answer
        Au.play_sound(f"./chat_history/voice_history/answer{counter}.mp3")
        
        #end the loop
        if question == ["إنهاء", "انها", "انهاء", "خروج"]:
            break
        counter += 1

if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(f"./chat_history/text_history/history{now}.txt", "a") as file:
            file.write("\n".join(history))
    
