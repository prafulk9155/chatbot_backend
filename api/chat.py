import json
import os
import logging
import warnings
from utils.embedding import *
from utils.pineconedb import *
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
import pinecone
from langchain.vectorstores import Pinecone
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)

class ConversationalRAGChatbot:
    def __init__(self, history_file="./chat_storage/chat_history.json"):
        logging.info("Initializing ConversationalRAGChatbot")

        # Initialize model and retriever
        self.vector_store = self.initialize_vector_store()
        self.retriever = self.initialize_retriever()
        self.model = self.initialize_model()

        # Set up prompts and chains
        self.setup_prompts_and_chains()

        # Chat history storage
        self.history_file = history_file
        self.store = self.load_chat_history()
        logging.info("Chat history loaded successfully")

    def initialize_vector_store(self):
        """Initialize the Pinecone vector store."""
        try:
            vector_store = Pinecone.from_existing_index(index_name, embeddings)
            logging.info("PineconeVectorStore initialized successfully")
            return vector_store
        except Exception as e:
            logging.error(f"Failed to initialize PineconeVectorStore: {e}")
            raise

    def initialize_retriever(self):
        """Create and return the retriever."""
        try:
            retriever = self.vector_store.as_retriever()
            # Log the type of the retriever
            logging.info(f"Retriever type: {type(retriever)}")  # Confirm it's a retriever

            # # Log a dummy query to test the retriever
            # dummy_question = "What is a car?"
            # response = retriever.get_relevant_documents(dummy_question)  # Use get_relevant_documents
            # logging.info(f"Dummy query response: {response}")  # Check response

            logging.info("Retriever created successfully")
            return retriever
        except Exception as e:
            logging.error(f"Failed to create retriever: {e}")
            raise




    def initialize_model(self):
        """Initialize the ChatGoogleGenerativeAI model."""
        try:
            model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", convert_system_message_to_human=True)
            logging.info("ChatGoogleGenerativeAI model initialized successfully")
            return model
        except Exception as e:
            logging.error(f"Failed to initialize ChatGoogleGenerativeAI: {e}")
            raise

    def setup_prompts_and_chains(self):
        """Set up prompts and chains for the chatbot."""
        try:
            # System and retriever prompts
            self.system_prompt = (
                "You are an assistant for question-answering tasks. "
                "Use the following pieces of retrieved context to answer the question. "
                "If you don't know the answer, say that you don't know. "
                "Use three sentences maximum and keep the answer concise."
                "\n\n{context}"
            )

            self.chat_prompt = ChatPromptTemplate.from_messages(
                [("system", self.system_prompt), ("human", "{input}")]
            )
            logging.info("Chat prompts initialized successfully")

            self.retriever_prompt = (
                "Given a chat history and the latest user question which might reference context in the chat history, "
                "formulate a standalone question which can be understood without the chat history. "
                "Do NOT answer the question, just reformulate it if needed and otherwise return it as is."
            )

            self.contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [("system", self.retriever_prompt), MessagesPlaceholder(variable_name="chat_history"), ("human", "{input}")]
            )

            self.history_aware_retriever = create_history_aware_retriever(self.model, self.retriever, self.contextualize_q_prompt)

            self.qa_prompt = ChatPromptTemplate.from_messages(
                [("system", self.system_prompt), MessagesPlaceholder("chat_history"), ("human", "{input}")]
            )

            self.question_answer_chain = create_stuff_documents_chain(self.model, self.qa_prompt)
            self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.question_answer_chain)

            logging.info("Retrieval and QA chains set up successfully")
        except Exception as e:
            logging.error(f"Error setting up prompts and chains: {e}")
            raise

    def load_chat_history(self):
        """Load chat history from a JSON file."""
        if os.path.exists(self.history_file):
            try:
                # Check if the file is empty
                if os.stat(self.history_file).st_size == 0:
                    logging.info("Chat history file is empty, returning an empty dictionary")
                    return {}
                
                # If the file is not empty, load the content
                with open(self.history_file, "r") as f:
                    chat_history = json.load(f)
                    logging.info("Chat history loaded from file")
                    return chat_history
            
            except json.JSONDecodeError:
                logging.error("Failed to decode chat history, file may be corrupted or improperly formatted.")
                return {}

        logging.info("No chat history file found, starting with an empty history")
        return {}

    def save_chat_history(self):
        """Save chat history to a JSON file, handling potential serialization issues."""
        try:
            # Convert the chat history (self.store) to a serializable format
            serializable_store = self._make_serializable(self.store)

            # Write the serializable history to the file
            with open(self.history_file, "w") as f:
                json.dump(serializable_store, f, indent=4)
                logging.info("Chat history saved to file")
        except (TypeError, json.JSONDecodeError) as e:
            logging.error(f"Failed to save chat history: {e}")
            # Optionally, you could raise the error or simply log it depending on what you want to do.
            raise

    def _make_serializable(self, data):
        """
        Recursively process the data structure to ensure it's serializable.
        Convert objects like `ChatMessageHistory` to basic serializable types (e.g., lists of dictionaries).
        """
        if isinstance(data, ChatMessageHistory):
            # Convert ChatMessageHistory to a list of dicts (e.g., messages)
            return [message.to_dict() for message in data.messages]

        if isinstance(data, dict):
            # If it's a dict, recursively process each key-value pair
            return {key: self._make_serializable(value) for key, value in data.items()}

        if isinstance(data, list):
            # If it's a list, recursively process each element
            return [self._make_serializable(item) for item in data]

        # For any other data types (primitives like str, int, etc.), return as is
        return data

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat history for a session."""
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
            logging.info(f"New session history created for session_id: {session_id}")
        return self.store[session_id]

    def chat_with_llm(self, session_id: str, user_input: str):
        """Run the chat conversation with the LLM, storing history."""
        logging.info(f"Processing chat with session_id: {session_id} and user_input: {user_input}")

        # Create a callable to return chat history
        history_callable = lambda: self.get_session_history(session_id)

        conversational_rag_chain = RunnableWithMessageHistory(
            self.rag_chain,
            history_callable,  # Pass callable for history
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        try:
            logging.info("conversational_rag_chain invoke started")
            response = conversational_rag_chain.invoke({"input": user_input},
                config={
                    "configurable": {"session_id": session_id}
                })
            logging.info(f"Response from LLM: {response['answer']}")

            # Ensure to correctly access the response content
            # Check if response is a dictionary and contains 'answer'
            if isinstance(response, dict) and 'answer' in response:
                answer_content = response['answer']
            else:
                logging.error(f"Unexpected response format: {response}")
                answer_content = "Sorry, an error occurred while processing your request."
            logging.info(f"Response generated: {answer_content}")

            # self.save_chat_history()  # Save history after response
            return answer_content

        except Exception as e:
            logging.error(f"Error during chat: {e}")
            return "Sorry, an error occurred while processing your request."
        
