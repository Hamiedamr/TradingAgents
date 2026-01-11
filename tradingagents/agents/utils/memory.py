import chromadb
from chromadb.config import Settings
import litellm
from ollama import Client


class FinancialSituationMemory:
    def __init__(self, name, config):
        if config["backend_url"] == "http://localhost:11434/v1" or "127.0.0.1" in config["backend_url"]:
            self.embedding = "ollama/nomic-embed-text"
        else:
            self.embedding = "text-embedding-3-small"
        
        # litellm doesn't need a client instantiation for embeddings, 
        # but we might need config context if available. 
        self.config = config
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        
        # Initialize Ollama Client if needed
        if "ollama/" in self.embedding:
            base_url = self.config.get("backend_url").replace("/v1", "").replace("localhost", "127.0.0.1")
            self.ollama_client = Client(host=base_url)

        try:
            self.chroma_client.delete_collection(name=name)
        except Exception:
            pass # Collection didn't exist, which is fine
        
        self.situation_collection = self.chroma_client.create_collection(name=name)

    def get_embedding(self, text):
        """Get embedding for a text"""
        
        # 1. Ollama Path
        if "ollama/" in self.embedding:
            # Clean model name (e.g., 'ollama/nomic-embed-text' -> 'nomic-embed-text')
            model_name = self.embedding.replace("ollama/", "")
            
            try:
                # Use expected response object attribute
                response = self.ollama_client.embeddings(
                    model=model_name,
                    prompt=text
                )
                # The official python client returns an object with .embedding attribute in recent versions,
                # or a dictionary in older ones. Simple hasattr check is cleanest.
                if hasattr(response, 'embedding'):
                    return response.embedding
                return response['embedding']

            except Exception as e:
                # Clear error propagation
                if "404" in str(e):
                    raise ValueError(f"Model '{model_name}' not found. Run `uv run ollama pull {model_name}`.") from e
                raise ConnectionError(f"Ollama embedding failed: {e}") from e

        # 2. LiteLLM Path (OpenAI etc)
        try:
            response = litellm.embedding(
                model=self.embedding, 
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            raise RuntimeError(f"Embedding failed for {self.embedding}: {e}")
    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using OpenAI embeddings"""
        query_embedding = self.get_embedding(current_situation)

        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        matched_results = []
        for i in range(len(results["documents"][0])):
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": 1 - results["distances"][0][i],
                }
            )

        return matched_results


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory()

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
