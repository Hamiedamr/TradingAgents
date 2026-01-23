import chromadb
from chromadb.config import Settings
import litellm
from fastembed import TextEmbedding


class FinancialSituationMemory:
    def __init__(self, name, config):
        if "model_cache" in config:
             cache_dir = config["model_cache"]
        else:
             cache_dir = "model_cache"
             
        self.embedding_model = TextEmbedding(
            model_name="intfloat/multilingual-e5-large", 
            cache_dir=cache_dir
        )
        
        self.config = config
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        
        try:
            self.chroma_client.delete_collection(name=name)
        except Exception:
            pass # Collection didn't exist, which is fine
        
        # Create collection
        # Note: We manage embeddings manually, so we don't pass an embedding function to Chroma
        self.situation_collection = self.chroma_client.get_or_create_collection(name=name)

    def get_embedding(self, text):
        """Get embedding for a text using FastEmbed"""
        try:
            # FastEmbed returns a generator of embeddings, we take the first one for the single text
            embeddings = list(self.embedding_model.embed([text]))
            return embeddings[0].tolist() if hasattr(embeddings[0], 'tolist') else list(embeddings[0])
        except Exception as e:
            raise RuntimeError(f"FastEmbed generation failed: {e}")
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
    # Example usage
    # Mock config
    config = {"backend_url": "http://localhost:11434/v1"}
    matcher = FinancialSituationMemory(name="debug_verification", config=config)

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
