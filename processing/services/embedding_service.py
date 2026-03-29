"""
Embedding Service
Generates vector embeddings for content using Sentence Transformers
"""
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger
import asyncio
from concurrent.futures import ThreadPoolExecutor


class EmbeddingService:
    """
    Vector embedding service using Sentence Transformers

    Supports multiple models:
    - all-MiniLM-L6-v2 (default, 384 dimensions, fast)
    - paraphrase-multilingual-mpnet-base-v2 (768 dimensions, multilingual)
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        max_seq_length: int = 512,
        device: str = "cpu"
    ):
        """
        Initialize embedding service

        Args:
            model_name: Name of the sentence transformer model
            max_seq_length: Maximum sequence length
            device: Device to use (cpu, cuda, mps)
        """
        self.model_name = model_name
        self.device = device

        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        self.model.max_seq_length = max_seq_length

        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")

        # Thread pool for CPU-bound embedding generation
        self.executor = ThreadPoolExecutor(max_workers=4)

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            Embedding vector as list
        """
        try:
            if not text or len(text.strip()) == 0:
                return None

            # Generate embedding
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True  # Normalize for cosine similarity
            )

            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of input texts
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")

            # Filter empty texts
            valid_indices = []
            valid_texts = []
            for i, text in enumerate(texts):
                if text and len(text.strip()) > 0:
                    valid_indices.append(i)
                    valid_texts.append(text)

            # Generate embeddings
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=True,
                normalize_embeddings=True
            )

            # Build result list with None for empty texts
            result = [None] * len(texts)
            for idx, embedding in zip(valid_indices, embeddings):
                result[idx] = embedding.tolist()

            logger.success(f"Generated {len(valid_texts)} embeddings")
            return result

        except Exception as e:
            logger.error(f"Error in batch embedding generation: {e}")
            return [None] * len(texts)

    async def generate_embedding_async(self, text: str) -> Optional[List[float]]:
        """
        Async wrapper for embedding generation

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.generate_embedding,
            text
        )

    async def generate_embeddings_async(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Optional[List[float]]]:
        """
        Async wrapper for batch embedding generation

        Args:
            texts: List of texts
            batch_size: Batch size

        Returns:
            List of embeddings
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.generate_embeddings_batch,
            texts,
            batch_size
        )

    def similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score (0-1)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Cosine similarity
            similarity = np.dot(vec1, vec2) / (
                np.linalg.norm(vec1) * np.linalg.norm(vec2)
            )

            return float(similarity)

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def find_similar(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]],
        top_k: int = 10
    ) -> List[tuple]:
        """
        Find most similar embeddings

        Args:
            query_embedding: Query vector
            embeddings: List of vectors to search
            top_k: Number of results

        Returns:
            List of (index, similarity) tuples
        """
        try:
            query_vec = np.array(query_embedding)
            embedding_matrix = np.array(embeddings)

            # Calculate all similarities
            similarities = np.dot(embedding_matrix, query_vec)

            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = [
                (int(idx), float(similarities[idx]))
                for idx in top_indices
            ]

            return results

        except Exception as e:
            logger.error(f"Error finding similar embeddings: {e}")
            return []

    def get_model_info(self) -> dict:
        """
        Get model information

        Returns:
            Dictionary with model details
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "max_seq_length": self.model.max_seq_length,
            "device": self.device
        }


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(
    model_name: str = "all-MiniLM-L6-v2",
    device: str = "cpu"
) -> EmbeddingService:
    """
    Get or create embedding service singleton

    Args:
        model_name: Model name
        device: Device to use

    Returns:
        EmbeddingService instance
    """
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService(
            model_name=model_name,
            device=device
        )

    return _embedding_service
