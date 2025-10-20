import os
import sys 
from dotenv import load_dotenv
from langchain_core import embeddings
from multi_doc_chat.utils.config_loader import load_config 
from multi_doc_chat.logger import GLOBAL_LOGGER as log 
from multi_doc_chat.exceptions.custom_exception import CustomException 
from langchain_openai import ChatOpenAI, OpenAIEmbeddings 
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

class APIKeyManager:
    REQUIRED_KEYS = ["OPENAI_API_KEY"] 
    
    def __init__(self):
        load_dotenv()
        self.api_keys = {}

        for key in self.REQUIRED_KEYS:
            env_val = os.getenv(key)
            if env_val:
                self.api_keys[key] = env_val
                log.info(f"Loaded {key} from individual env var")

        # Final Check
        missing = [k for k in self.REQUIRED_KEYS if not self.api_keys.get(k)]
        if missing:
            log.error("Missing Required API Key", missing_keys = missing)
            raise CustomException("Missing API Key")
        
        log.info("API Key loaded", keys = {k: v[:5] + "-----" for k, v in self.api_keys.items()})
    
    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            raise KeyError(f"API key for {key} is missing.")
        return val

class ModelLoader:
    """
    Loads embedding models and LLMs based on config and environment.
    """
    def __init__(self):
        self.api_key_mgr = APIKeyManager() 
        self.config = load_config() 
    
    def load_embeddings(self):
        """
        Load and return embedding model from OpenAI.
        """
        try:
            model_name = self.config["embedding_model"]["model_name"]
            log.info("Loading Embedding model: ", model = model_name)
            return OpenAIEmbeddings(model = model_name, api_key=self.api_key_mgr.get("OPENAI_API_KEY"))
        except Exception as e:
            log.error("Error Loading embedding model: ", error = str(e)) 
            raise CustomException("Failed to load embedding model", e)

    def load_llm(self):
        """
        Load and return the configured LLM model.
        """
        llm_block = self.config["llm"]

        provider = llm_block.get("provider")
        model_name = llm_block.get("model_name")
        temperature = llm_block.get("temperature", 0.2)
        max_tokens = llm_block.get("max_output_tokens", 2048)

        log.info("Loading LLM", provider = provider, model = model_name)

        if provider == "google":
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=self.api_key_mgr.get("GOOGLE_API_KEY"),
                temperature=temperature,
                max_output_tokens=max_tokens
            )

        elif provider == "openai":
            return ChatOpenAI(
                model=model_name,
                api_key=self.api_key_mgr.get("OPENAI_API_KEY"),
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            log.error("Unsupported LLM Provider", provider = provider) 
            raise ValueError(f"Unsupported LLM Provider: {provider}")

if __name__ == "__main__":
    api = APIKeyManager()
    # print(f"API Loaded: {api.get(key='OPENAI_API_KEY')[:5]}-----")'
    model = ModelLoader() 
    print(model.load_embeddings())
    embeddings = model.load_embeddings()
    # print(embeddings.embed_query("Hello world"))

    llm = model.load_llm()
    print(llm.invoke("what is Artificial Intelligence"))