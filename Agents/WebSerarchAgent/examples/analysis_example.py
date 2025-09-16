"""
Example 2: Comprehensive Analysis Workflow
"""

import asyncio
from src.web_search_system import WebSearchSystem

async def analysis_workflow_example():
    """Demonstrate comprehensive search analysis workflow."""
    
    system = WebSearchSystem()
    
    try:
        print("🔬 Starting comprehensive analysis workflow...")
        
        # Perform comprehensive search analysis
        query = "climate change renewable energy solutions"
        analysis = await system.comprehensive_search_analysis(
            query=query,
            max_results=15
        )
        
        print(f"\n✅ Comprehensive analysis completed for: '{query}'")
        print(f"📊 Status: {analysis.get('status', 'unknown')}")
        
        # Display search results summary
        if "search_results" in analysis:
            search_info = analysis["search_results"]
            print(f"\n🔍 Search Results Summary:")
            print(f"   📊 Total found: {search_info.get('total_found', 0)}")
            print(f"   🌐 Unique domains: {len(search_info.get('domains', []))}")
            print(f"   🔗 Top domains: {', '.join(search_info.get('domains', [])[:5])}")
        
        # Display content analysis
        if "content_analysis" in analysis:
            content = analysis["content_analysis"]
            if "analyses" in content:
                print(f"\n📝 Content Analysis:")
                
                # Sentiment analysis
                if "sentiment" in content["analyses"]:
                    sentiment = content["analyses"]["sentiment"]
                    print(f"   😊 Sentiment: {sentiment.get('label', 'unknown')} "
                          f"({sentiment.get('confidence', 0):.1%} confidence)")
                
                # Keywords
                if "keywords" in content["analyses"]:
                    keywords = content["analyses"]["keywords"]
                    if keywords.get("keywords"):
                        top_keywords = [kw["word"] for kw in keywords["keywords"][:5]]
                        print(f"   🔑 Top keywords: {', '.join(top_keywords)}")
                
                # Language detection
                if "language" in content["analyses"]:
                    language = content["analyses"]["language"]
                    print(f"   🌍 Language: {language.get('language', 'unknown')} "
                          f"({language.get('confidence', 0):.1%} confidence)")
        
        # Display fact-checking results
        if "fact_check" in analysis:
            fact_check = analysis["fact_check"]
            if "overall_credibility" in fact_check:
                credibility = fact_check["overall_credibility"]
                print(f"\n🛡️ Fact Check:")
                print(f"   📊 Overall credibility: {credibility:.1%}")
                
                if "fact_check_summary" in fact_check:
                    print("   📋 Summary:")
                    for summary_point in fact_check["fact_check_summary"][:3]:
                        print(f"      • {summary_point}")
        
        # Display summary
        if "summary" in analysis:
            summary = analysis["summary"]
            if "summary" in summary and "text" in summary["summary"]:
                summary_text = summary["summary"]["text"]
                print(f"\n📄 Executive Summary:")
                print(f"   {summary_text[:300]}...")
                
                if "compression_ratio" in summary:
                    ratio = summary["compression_ratio"]
                    print(f"   📊 Compression ratio: {ratio:.1%}")
        
        # Display trends
        if "trends" in analysis:
            trends = analysis["trends"]
            if "trending_score" in trends:
                trending_score = trends["trending_score"]
                print(f"\n📈 Trend Analysis:")
                print(f"   📊 Trending score: {trending_score:.1%}")
                
                if "trend_insights" in trends:
                    print("   💡 Insights:")
                    for insight in trends["trend_insights"][:3]:
                        print(f"      • {insight}")
        
        # Display comprehensive insights
        if "insights" in analysis:
            insights = analysis["insights"]
            print(f"\n🧠 Comprehensive Insights:")
            for insight in insights:
                print(f"   • {insight}")
        
        print("\n✅ Comprehensive analysis workflow completed!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(analysis_workflow_example())
