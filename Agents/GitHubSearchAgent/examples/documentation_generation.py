"""
Example 4: Documentation Generation
"""

import asyncio
from src.github_search_agent import GitHubSearchSystem

async def documentation_example():
    """Demonstrate automated documentation generation."""
    
    system = GitHubSearchSystem()
    
    try:
        print("📚 Generating comprehensive documentation...")
        
        # Generate documentation for a repository
        repo_name = "microsoft/vscode"
        
        docs = await system.generate_comprehensive_docs(
            repository=repo_name,
            include_setup=True,
            include_examples=True,
            include_api=True
        )
        
        print(f"\n✅ Generated documentation for {repo_name}")
        
        # Display documentation sections
        print("\n📖 Documentation Overview:")
        print(f"   📋 Title: {docs.title}")
        print(f"   📝 Description: {docs.description[:200]}...")
        print(f"   🔧 Setup Instructions: {len(docs.setup_instructions)} steps")
        print(f"   💡 Usage Examples: {len(docs.usage_examples)} examples")
        print(f"   🔗 API Reference: {len(docs.api_reference)} endpoints")
        
        # Show setup instructions
        print("\n🚀 Setup Instructions:")
        for i, step in enumerate(docs.setup_instructions[:3], 1):
            print(f"   {i}. {step}")
        
        # Show usage examples
        print("\n💡 Usage Examples:")
        for i, example in enumerate(docs.usage_examples[:2], 1):
            print(f"\n   Example {i}: {example['title']}")
            print(f"   {example['description']}")
            if example['code']:
                print(f"   ```{example['language']}")
                print(f"   {example['code'][:100]}...")
                print(f"   ```")
        
        # Generate technology summary
        print("\n📊 Generating technology summary...")
        
        summary = await system.summarize_technology_landscape(
            technology="machine learning",
            focus_areas=["frameworks", "tools", "libraries"]
        )
        
        print(f"\n🎯 Technology Landscape: {summary.technology}")
        print(f"   📈 Market Share: {summary.market_share}")
        print(f"   📊 Adoption Rate: {summary.adoption_rate}")
        print(f"   🔮 Future Outlook: {summary.future_outlook}")
        
        print("\n🏆 Key Players:")
        for i, player in enumerate(summary.key_players[:3], 1):
            print(f"   {i}. {player['name']}: {player['description']}")
        
        print("\n📚 Learning Resources:")
        for i, resource in enumerate(summary.learning_resources[:3], 1):
            print(f"   {i}. {resource['title']}: {resource['url']}")
        
    except Exception as e:
        print(f"❌ Error during documentation generation: {str(e)}")
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(documentation_example())
