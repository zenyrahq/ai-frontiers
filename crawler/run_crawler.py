#!/usr/bin/env python3
"""
Run arXiv Crawler - Fixed Version
运行 arXiv 爬虫
"""
import sys
import asyncio
import os
from pathlib import Path

# Add paths
base_dir = Path(__file__).parent.parent
crawler_dir = base_dir / "crawler"
api_dir = base_dir / "api"
sys.path.insert(0, str(crawler_dir))
sys.path.insert(0, str(api_dir))

# Set PYTHONPATH
os.environ['PYTHONPATH'] = f"{crawler_dir}:{api_dir}"

from loguru import logger

# Import directly
import importlib.util

# Load arxiv service
spec = importlib.util.spec_from_file_location(
    "arxiv_service",
    crawler_dir / "services" / "arxiv_service.py"
)
arxiv_module = importlib.util.module_from_spec(spec)
sys.modules['arxiv_service'] = arxiv_module
spec.loader.exec_module(arxiv_module)

# Load database service
spec = importlib.util.spec_from_file_location(
    "database_service",
    crawler_dir / "services" / "database_service.py"
)
db_module = importlib.util.module_from_spec(spec)
sys.modules['database_service'] = db_module
spec.loader.exec_module(db_module)

ArxivService = arxiv_module.ArxivService
DatabaseService = db_module.DatabaseService


async def main():
    """Main crawler function"""
    logger.info("=" * 60)
    logger.info("🚀 arXiv 爬虫启动")
    logger.info("=" * 60)

    arxiv = ArxivService()
    db = DatabaseService()

    # Fetch recent papers
    logger.info("\n📡 从 arXiv 获取最近 7 天的 AI 论文...")
    logger.info("   分类: cs.AI, cs.LG, cs.CL, cs.CV")
    logger.info("   最大数量: 100 篇")

    try:
        papers = await arxiv.fetch_recent_papers(days=7, max_results=100)
        logger.info(f"\n✅ 获取到 {len(papers)} 篇论文")

        if papers:
            # Show first few papers
            logger.info("\n📄 前 5 篇论文:")
            for i, paper in enumerate(papers[:5], 1):
                logger.info(f"   {i}. {paper['title'][:60]}...")

            # Save to database
            logger.info(f"\n💾 保存到数据库...")
            saved = await db.save_contents(papers)
            logger.success(f"✅ 成功保存 {saved} 篇论文到数据库")
        else:
            logger.warning("⚠️ 没有获取到论文")

        return len(papers) if papers else 0

    except Exception as e:
        logger.error(f"❌ 爬虫运行失败: {e}")
        logger.info("\n" + "=" * 60)
        logger.info("可能的解决方案:")
        logger.info("1. 检查网络连接，确保可以访问 export.arxiv.org")
        logger.info("2. 如果在中国大陆，可能需要使用代理")
        logger.info("3. 尝试部署到云服务器（如 AWS、GCP、Vercel）")
        logger.info("=" * 60)
        return 0


if __name__ == "__main__":
    asyncio.run(main())
