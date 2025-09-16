"""
Example 3: Technology Trend Analysis
"""

import asyncio
from src.github_search_agent import GitHubSearchSystem

async def trend_analysis_example():
    """Demonstrate technology trend analysis."""
    
    system = GitHubSearchSystem()
    
    try:
        print("📈 Analyzing technology trends...")
        
        # Discover trending technologies
        trends = await system.discover_trending_technologies(
            time_period="6months",
            max_technologies=10
        )
        
        print(f"\n✅ Analyzed {len(trends)} trending technologies")
        
        # Display trend results
        print("\n🏆 Top Trending Technologies:")
        for i, trend in enumerate(trends[:5], 1):
            print(f"\n{i}. {trend.technology}")
            print(f"   📊 Popularity Score: {trend.popularity_score:.1f}")
            print(f"   📈 Growth Rate: {trend.growth_rate:.1f}%")
            print(f"   👥 Community Activity: {trend.community_activity:.1f}%")
            
            if trend.recent_projects:
                print(f"   🔥 Recent Projects: {', '.join(trend.recent_projects[:3])}")
        
        # Compare specific technologies
        print("\n🔬 Comparing Web Frameworks...")
        
        comparison = await system.compare_repositories([
            "django/django",
            "pallets/flask",
            "encode/django-rest-framework"
        ])
        
        print("\n📊 Framework Comparison Results:")
        for repo_name, data in comparison["comparison_data"].items():
            repo = data["repository"]
            print(f"\n📦 {repo_name}")
            print(f"   ⭐ Stars: {repo.stars:,}")
            print(f"   📊 Quality Score: {data['quality_score']:.1f}/100")
            print(f"   🔒 Security Issues: {data['security_issues']}")
            print(f"   📝 {data['summary']}")
        
        print("\n💡 Comparison Insights:")
        for insight in comparison["insights"]:
            print(f"   • {insight}")
        
    except Exception as e:
        print(f"❌ Error during trend analysis: {str(e)}")
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(trend_analysis_example())
