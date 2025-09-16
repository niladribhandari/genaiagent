"""
Example 1: Basic Repository Search
"""

import asyncio
import os
from dotenv import load_dotenv
from src.github_search_agent import GitHubSearchSystem

load_dotenv()

async def basic_search_example():
    """Demonstrate basic repository search functionality."""
    
    # Initialize the search system
    system = GitHubSearchSystem()
    
    try:
        print("🔍 Searching for Python web frameworks...")
        
        # Search for repositories
        results = await system.search_repositories(
            query="python web framework",
            max_results=10,
            language="python",
            min_stars=100
        )
        
        print(f"\n✅ Found {results.total_count} repositories")
        print(f"⏱️  Search took {results.search_time:.2f} seconds")
        
        # Display results
        for i, repo in enumerate(results.repositories[:5], 1):
            print(f"\n{i}. {repo.full_name}")
            print(f"   ⭐ Stars: {repo.stars:,}")
            print(f"   🔧 Language: {repo.language}")
            print(f"   📝 Description: {repo.description[:100]}..." if repo.description else "   📝 No description")
            print(f"   🔗 URL: {repo.html_url}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(basic_search_example())
