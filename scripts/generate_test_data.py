#!/usr/bin/env python3
"""
Generate Test Data for AI Frontiers
Generate AI Frontiers test data (simplified version without embedding)
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import random

# Setup path for both local and container environments
script_dir = Path(__file__).parent.resolve()
project_root = script_dir.parent
api_dir = project_root / "api"

if api_dir.exists():
    # Local development
    sys.path.insert(0, str(api_dir))
elif (project_root / "core").exists():
    # Container environment
    sys.path.insert(0, str(project_root))
else:
    sys.path.insert(0, str(project_root))

from loguru import logger
from core.database import AsyncSessionLocal
from models.models import Content


# Test data
TEST_PAPERS = [
    {
        "title": "Attention Is All You Need",
        "summary": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
        "source": "arxiv",
        "category": "deep_learning",
        "tags": ["transformer", "attention", "nlp"],
        "views": 5000,
        "likes": 450,
    },
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers",
        "summary": "We introduce BERT, which stands for Bidirectional Encoder Representations from Transformers. BERT is designed to pre-train deep bidirectional representations from unlabeled text.",
        "source": "arxiv",
        "category": "natural_language",
        "tags": ["bert", "transformer", "pre-training"],
        "views": 4500,
        "likes": 420,
    },
    {
        "title": "GPT-4 Technical Report",
        "summary": "We report the development of GPT-4, a large-scale, multimodal model which can accept image and text inputs and produce text outputs. GPT-4 exhibits human-level performance on various benchmarks.",
        "source": "arxiv",
        "category": "generative_ai",
        "tags": ["gpt", "llm", "multimodal"],
        "views": 8000,
        "likes": 800,
    },
    {
        "title": "Language Models are Few-Shot Learners",
        "summary": "We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance. GPT-3 achieves strong performance on many NLP datasets with no gradient updates.",
        "source": "arxiv",
        "category": "natural_language",
        "tags": ["gpt-3", "few-shot", "language-model"],
        "views": 6500,
        "likes": 600,
    },
    {
        "title": "Deep Residual Learning for Image Recognition",
        "summary": "We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. ResNet won the ImageNet competition.",
        "source": "arxiv",
        "category": "computer_vision",
        "tags": ["resnet", "deep-learning", "residual-learning"],
        "views": 7000,
        "likes": 650,
    },
    {
        "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition",
        "summary": "We show that a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks. ViT achieves state-of-the-art results.",
        "source": "arxiv",
        "category": "computer_vision",
        "tags": ["vit", "vision-transformer", "image-classification"],
        "views": 5500,
        "likes": 500,
    },
    {
        "title": "Generative Adversarial Networks",
        "summary": "We propose a new framework for estimating generative models via an adversarial process. GANs have become fundamental to generative AI applications.",
        "source": "arxiv",
        "category": "generative_ai",
        "tags": ["gan", "generative", "adversarial"],
        "views": 9000,
        "likes": 850,
    },
    {
        "title": "Denoising Diffusion Probabilistic Models",
        "summary": "We present high quality image synthesis results using diffusion probabilistic models. Diffusion models achieve state-of-the-art synthesis results.",
        "source": "arxiv",
        "category": "generative_ai",
        "tags": ["diffusion", "ddpm", "generative"],
        "views": 6000,
        "likes": 580,
    },
    {
        "title": "High-Resolution Image Synthesis with Latent Diffusion Models",
        "summary": "We present latent diffusion models for high-resolution image synthesis. This is the foundation of Stable Diffusion, enabling efficient text-to-image generation.",
        "source": "arxiv",
        "category": "generative_ai",
        "tags": ["stable-diffusion", "latent-diffusion", "text-to-image"],
        "views": 7500,
        "likes": 720,
    },
    {
        "title": "Mastering the game of Go with deep neural networks",
        "summary": "We introduce AlphaGo, which uses value networks and policy networks to evaluate board positions and select moves. AlphaGo defeated the world champion.",
        "source": "arxiv",
        "category": "reinforcement_learning",
        "tags": ["alphago", "deep-learning", "game-ai"],
        "views": 10000,
        "likes": 950,
    },
    {
        "title": "Proximal Policy Optimization Algorithms",
        "summary": "We propose PPO, a family of policy gradient methods for reinforcement learning. PPO has become the standard algorithm for training RL agents.",
        "source": "arxiv",
        "category": "reinforcement_learning",
        "tags": ["ppo", "policy-gradient", "rl"],
        "views": 5500,
        "likes": 520,
    },
    {
        "title": "Adam: A Method for Stochastic Optimization",
        "summary": "We introduce Adam, an algorithm for first-order gradient-based optimization. Adam has become the default optimizer for training deep neural networks.",
        "source": "arxiv",
        "category": "machine_learning",
        "tags": ["adam", "optimization", "gradient-descent"],
        "views": 8500,
        "likes": 800,
    },
    {
        "title": "Dropout: A Simple Way to Prevent Overfitting",
        "summary": "We propose dropout, where we randomly drop units from the neural network during training. Dropout is a key regularization technique in deep learning.",
        "source": "arxiv",
        "category": "machine_learning",
        "tags": ["dropout", "regularization", "overfitting"],
        "views": 6000,
        "likes": 550,
    },
    {
        "title": "Batch Normalization: Accelerating Deep Network Training",
        "summary": "We present batch normalization to reduce internal covariate shift. This technique enables faster training and higher learning rates.",
        "source": "arxiv",
        "category": "machine_learning",
        "tags": ["batch-normalization", "training", "optimization"],
        "views": 5500,
        "likes": 500,
    },
    {
        "title": "LLaMA: Open and Efficient Foundation Language Models",
        "summary": "We introduce LLaMA, a collection of foundation language models ranging from 7B to 65B parameters. LLaMA enables open-source LLM research.",
        "source": "arxiv",
        "category": "natural_language",
        "tags": ["llama", "llm", "open-source"],
        "views": 7000,
        "likes": 680,
    },
    {
        "title": "Constitutional AI: Harmlessness from AI Feedback",
        "summary": "We experiment with methods for training harmless AI assistants through self-improvement. Constitutional AI provides a framework for AI alignment.",
        "source": "arxiv",
        "category": "natural_language",
        "tags": ["constitutional-ai", "rlhf", "alignment"],
        "views": 4500,
        "likes": 420,
    },
    {
        "title": "Training language models to follow instructions",
        "summary": "We show methods for aligning language models with user intent on a wide range of tasks. InstructGPT demonstrates improved instruction following.",
        "source": "arxiv",
        "category": "natural_language",
        "tags": ["instructgpt", "rlhf", "alignment"],
        "views": 6000,
        "likes": 580,
    },
    {
        "title": "U-Net: Convolutional Networks for Image Segmentation",
        "summary": "We present U-Net, a network architecture for biomedical image segmentation. U-Net has become the standard for image segmentation tasks.",
        "source": "arxiv",
        "category": "computer_vision",
        "tags": ["unet", "segmentation", "medical-imaging"],
        "views": 4500,
        "likes": 400,
    },
    {
        "title": "Human-level control through deep reinforcement learning",
        "summary": "We develop a deep Q-network (DQN) that achieves human-level control in Atari games. DQN combines reinforcement learning with deep neural networks.",
        "source": "arxiv",
        "category": "reinforcement_learning",
        "tags": ["dqn", "deep-rl", "q-learning"],
        "views": 6500,
        "likes": 620,
    },
    {
        "title": "End-to-End Training of Deep Visuomotor Policies",
        "summary": "We describe a method for learning deep visuomotor policies for manipulation tasks. This enables robots to learn from visual input.",
        "source": "arxiv",
        "category": "robotics",
        "tags": ["visuomotor", "robotics", "manipulation"],
        "views": 3500,
        "likes": 320,
    },
]


async def generate_data():
    """Generate test data"""
    logger.info("=" * 60)
    logger.info("Generating test data...")
    logger.info("=" * 60)

    created = 0

    async with AsyncSessionLocal() as session:
        from sqlalchemy import text

        # Check existing
        result = await session.execute(text("SELECT COUNT(*) FROM contents"))
        existing = result.scalar()

        if existing > 10:
            logger.info(f"Database already has {existing} records, skipping")
            return existing

        # Generate data with random dates
        for i, paper in enumerate(TEST_PAPERS):
            # Random date in last 60 days
            days_ago = random.randint(1, 60)
            pub_date = datetime.now() - timedelta(days=days_ago)

            # Create content (without embedding for simplified deployment)
            content = Content(
                title=paper["title"],
                summary=paper["summary"],
                content=paper["summary"],
                source=paper["source"],
                category=paper["category"],
                tags=paper["tags"],
                original_url=f"https://arxiv.org/abs/2024.{10000 + i}",
                is_processed=True,
                view_count=paper["views"] + random.randint(-100, 100),
                like_count=paper["likes"] + random.randint(-20, 20),
                published_at=pub_date,
            )
            session.add(content)
            created += 1

            if created % 5 == 0:
                logger.info(f"  Generated {created}/{len(TEST_PAPERS)} records...")

        await session.commit()
        logger.success(f"Successfully generated {created} test records")

        return created


async def main():
    """Main function"""
    logger.info("AI Frontiers Test Data Generator")
    logger.info("=" * 60)

    count = await generate_data()

    logger.info("\n" + "=" * 60)
    logger.info("Done!")
    logger.info("=" * 60)
    logger.info(f"Database now has {count} test records")
    logger.info("\nYou can now test the frontend!")


if __name__ == "__main__":
    asyncio.run(main())
