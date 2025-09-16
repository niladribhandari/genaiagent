"""
Example 3: Trend Monitoring and Alerting
"""

import asyncio
from src.web_search_system import WebSearchSystem

async def trend_monitoring_example():
    """Demonstrate trend monitoring and alerting capabilities."""
    
    system = WebSearchSystem()
    
    try:
        print("📈 Starting trend monitoring example...")
        
        # Monitor multiple trending topics
        trending_topics = [
            "artificial intelligence", 
            "machine learning", 
            "quantum computing",
            "blockchain technology",
            "sustainable energy"
        ]
        
        trend_reports = {}
        
        for topic in trending_topics:
            print(f"\n🔍 Analyzing trends for: '{topic}'")
            
            # Perform intelligent search with trend focus
            results = await system.intelligent_search(
                query=f"{topic} trends 2024",
                max_results=10
            )
            
            if results and "status" in results and results["status"] == "success":
                search_data = results.get("search_results", {})
                
                # Analyze trends specifically
                trend_analysis = await system.analyze_trends(
                    query=topic,
                    content_items=[{
                        "title": item.get("title", ""),
                        "content": item.get("snippet", ""),
                        "url": item.get("link", "")
                    } for item in search_data.get("results", [])]
                )
                
                trend_reports[topic] = trend_analysis
                
                # Display trend metrics
                if "trending_score" in trend_analysis:
                    score = trend_analysis["trending_score"]
                    print(f"   📊 Trending score: {score:.1%}")
                
                if "trend_insights" in trend_analysis:
                    insights = trend_analysis["trend_insights"]
                    print(f"   💡 Key insights:")
                    for insight in insights[:2]:
                        print(f"      • {insight}")
                
                if "momentum" in trend_analysis:
                    momentum = trend_analysis["momentum"]
                    print(f"   🚀 Momentum: {momentum}")
            
            # Add small delay to respect rate limits
            await asyncio.sleep(1)
        
        # Generate comparative trend report
        print(f"\n📊 Comparative Trend Analysis:")
        print("=" * 50)
        
        sorted_trends = sorted(
            trend_reports.items(),
            key=lambda x: x[1].get("trending_score", 0),
            reverse=True
        )
        
        for i, (topic, analysis) in enumerate(sorted_trends, 1):
            score = analysis.get("trending_score", 0)
            momentum = analysis.get("momentum", "stable")
            
            # Trend indicators
            if score > 0.7:
                indicator = "🔥 HOT"
            elif score > 0.5:
                indicator = "📈 RISING"
            elif score > 0.3:
                indicator = "📊 STABLE"
            else:
                indicator = "📉 DECLINING"
            
            print(f"#{i}. {topic.title()}")
            print(f"    {indicator} | Score: {score:.1%} | Momentum: {momentum}")
            
            # Show top insight
            if "trend_insights" in analysis and analysis["trend_insights"]:
                print(f"    💡 {analysis['trend_insights'][0]}")
            print()
        
        # Alert on high-trending topics
        high_trending = [
            topic for topic, analysis in trend_reports.items()
            if analysis.get("trending_score", 0) > 0.6
        ]
        
        if high_trending:
            print("🚨 High-Trending Alert:")
            print(f"   The following topics are showing high trend activity:")
            for topic in high_trending:
                score = trend_reports[topic].get("trending_score", 0)
                print(f"   • {topic.title()}: {score:.1%}")
        
        print("\n✅ Trend monitoring completed!")
        
    except Exception as e:
        print(f"❌ Error during trend monitoring: {str(e)}")
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(trend_monitoring_example())
