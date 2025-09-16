"""
Example 4: Multi-Query Research Workflow
"""

import asyncio
from src.web_search_system import WebSearchSystem

async def research_workflow_example():
    """Demonstrate multi-query research workflow with fact-checking."""
    
    system = WebSearchSystem()
    
    try:
        print("🔬 Starting multi-query research workflow...")
        
        # Define research topic with multiple aspects
        main_topic = "Electric Vehicle Adoption"
        research_queries = [
            "electric vehicle sales statistics 2024",
            "EV charging infrastructure development",
            "electric car battery technology advances",
            "government electric vehicle incentives",
            "environmental impact electric vehicles"
        ]
        
        research_results = {}
        
        print(f"\n📚 Researching: {main_topic}")
        print(f"📋 Query plan: {len(research_queries)} targeted searches")
        
        # Execute research queries
        for i, query in enumerate(research_queries, 1):
            print(f"\n🔍 Query {i}/{len(research_queries)}: {query}")
            
            try:
                # Perform intelligent search
                results = await system.intelligent_search(
                    query=query,
                    max_results=8
                )
                
                if results and results.get("status") == "success":
                    search_data = results.get("search_results", {})
                    
                    # Extract and analyze content
                    content_items = []
                    for result in search_data.get("results", []):
                        content_items.append({
                            "title": result.get("title", ""),
                            "content": result.get("snippet", ""),
                            "url": result.get("link", ""),
                            "domain": result.get("link", "").split("//")[-1].split("/")[0] if result.get("link") else ""
                        })
                    
                    # Perform fact-checking on the content
                    fact_check = await system.fact_check_content(
                        query=query,
                        content_items=content_items
                    )
                    
                    # Generate summary
                    summary = await system.summarize_content(
                        content_items=content_items,
                        summary_type="bullet_points"
                    )
                    
                    research_results[query] = {
                        "search_results": search_data,
                        "fact_check": fact_check,
                        "summary": summary,
                        "content_count": len(content_items)
                    }
                    
                    # Display immediate results
                    credibility = fact_check.get("overall_credibility", 0)
                    result_count = len(search_data.get("results", []))
                    
                    print(f"   ✅ Found {result_count} results")
                    print(f"   🛡️ Credibility: {credibility:.1%}")
                    
                    if summary and "summary" in summary:
                        summary_text = summary["summary"].get("text", "")
                        if summary_text:
                            print(f"   📄 Summary: {summary_text[:100]}...")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error with query '{query}': {str(e)}")
                continue
        
        # Generate comprehensive research report
        print(f"\n📊 Research Report: {main_topic}")
        print("=" * 60)
        
        total_results = sum(
            result.get("content_count", 0) 
            for result in research_results.values()
        )
        
        avg_credibility = sum(
            result.get("fact_check", {}).get("overall_credibility", 0)
            for result in research_results.values()
        ) / len(research_results) if research_results else 0
        
        print(f"📈 Research Summary:")
        print(f"   🔍 Queries executed: {len(research_results)}")
        print(f"   📄 Total sources: {total_results}")
        print(f"   🛡️ Average credibility: {avg_credibility:.1%}")
        
        # Detailed findings per query
        print(f"\n📋 Detailed Findings:")
        
        for i, (query, data) in enumerate(research_results.items(), 1):
            print(f"\n{i}. {query}")
            
            fact_check = data.get("fact_check", {})
            credibility = fact_check.get("overall_credibility", 0)
            
            # Credibility indicator
            if credibility > 0.8:
                cred_indicator = "🟢 HIGH"
            elif credibility > 0.6:
                cred_indicator = "🟡 MEDIUM"
            else:
                cred_indicator = "🔴 LOW"
            
            print(f"   Credibility: {cred_indicator} ({credibility:.1%})")
            
            # Key findings from summary
            summary = data.get("summary", {})
            if summary and "summary" in summary:
                summary_text = summary["summary"].get("text", "")
                if summary_text:
                    # Split into bullet points if formatted that way
                    if "•" in summary_text:
                        points = [p.strip() for p in summary_text.split("•") if p.strip()]
                        print(f"   Key findings:")
                        for point in points[:3]:
                            print(f"      • {point}")
                    else:
                        print(f"   Key finding: {summary_text[:200]}...")
            
            # Source diversity
            search_data = data.get("search_results", {})
            domains = list(set([
                result.get("link", "").split("//")[-1].split("/")[0]
                for result in search_data.get("results", [])
                if result.get("link")
            ]))
            
            if domains:
                print(f"   Sources: {len(domains)} unique domains")
                if len(domains) <= 3:
                    print(f"            {', '.join(domains)}")
        
        # Research quality assessment
        print(f"\n🎯 Research Quality Assessment:")
        
        high_quality_queries = [
            query for query, data in research_results.items()
            if data.get("fact_check", {}).get("overall_credibility", 0) > 0.7
        ]
        
        if high_quality_queries:
            print(f"   ✅ High-quality research areas ({len(high_quality_queries)}):")
            for query in high_quality_queries:
                print(f"      • {query}")
        
        low_quality_queries = [
            query for query, data in research_results.items()
            if data.get("fact_check", {}).get("overall_credibility", 0) < 0.5
        ]
        
        if low_quality_queries:
            print(f"   ⚠️ Areas needing additional verification ({len(low_quality_queries)}):")
            for query in low_quality_queries:
                print(f"      • {query}")
        
        # Recommendations
        print(f"\n💡 Research Recommendations:")
        
        if avg_credibility > 0.7:
            print("   ✅ Strong overall research foundation")
        elif avg_credibility > 0.5:
            print("   📊 Moderate research quality - consider additional sources")
        else:
            print("   ⚠️ Research quality concerns - verify with authoritative sources")
        
        if total_results < 20:
            print("   📈 Consider expanding search scope for more comprehensive coverage")
        
        if len(set([
            result.get("search_results", {}).get("results", [{}])[0].get("link", "").split("//")[-1].split("/")[0]
            for result in research_results.values()
        ])) < 5:
            print("   🔄 Diversify source types for broader perspective")
        
        print("\n✅ Multi-query research workflow completed!")
        
    except Exception as e:
        print(f"❌ Error during research workflow: {str(e)}")
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(research_workflow_example())
