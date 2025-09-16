"""
Example 1: Basic Web Search with AI Analysis
"""

import asyncio
from src.web_search_system import WebSearchSystem

async def basic_search_example():
    """Demonstrate basic web search with AI analysis."""
    
    system = WebSearchSystem()
    
    try:
        print("🔍 Starting basic web search with AI analysis...")
        
        # Perform intelligent search
        query = "artificial intelligence latest developments 2024"
        results = await system.intelligent_search(
            query=query,
            search_type="comprehensive",
            max_results=10,
            include_analysis=True,
            include_summary=True
        )
        
        print(f"\n✅ Search completed for: '{query}'")
        print(f"📊 Status: {results.get('status', 'unknown')}")
        
        # Display orchestrator results
        if "orchestrator_results" in results:
            orch_results = results["orchestrator_results"]
            print(f"\n🤖 Agents involved: {', '.join(orch_results.get('agents_involved', []))}")
            print(f"🎯 Confidence score: {orch_results.get('confidence_score', 0):.1%}")
            
            # Show agent contributions
            if "results_by_agent" in orch_results:
                print("\n📋 Agent Contributions:")
                for agent_name, agent_results in orch_results["results_by_agent"].items():
                    print(f"   • {agent_name}: {len(agent_results)} result(s)")
        
        # Display search metadata
        if "search_metadata" in results:
            metadata = results["search_metadata"]
            print(f"\n📈 Search Type: {metadata.get('search_type')}")
            print(f"⏰ Timestamp: {metadata.get('timestamp')}")
        
        # Show sample search results
        if "processed_results" in results:
            search_results = results["processed_results"]
            print(f"\n🔗 Found {len(search_results)} results:")
            
            for i, result in enumerate(search_results[:5], 1):
                print(f"\n{i}. {result.title}")
                print(f"   🌐 {result.url}")
                print(f"   📝 {result.description[:100]}...")
                if hasattr(result, 'relevance_score') and result.relevance_score:
                    print(f"   ⭐ Relevance: {result.relevance_score:.1%}")
        
        print("\n✅ Basic search example completed!")
        
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(basic_search_example())
