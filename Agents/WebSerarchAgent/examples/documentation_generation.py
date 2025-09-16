"""
README Example: Documentation Generation
"""

import asyncio
from src.web_search_system import WebSearchSystem

async def documentation_generation_example():
    """Generate documentation for a technical topic using web search."""
    
    system = WebSearchSystem()
    
    try:
        print("📖 Starting documentation generation example...")
        
        # Topic for documentation
        topic = "RESTful API best practices"
        
        # Define documentation sections to research
        doc_sections = {
            "introduction": f"{topic} introduction overview",
            "principles": f"{topic} core principles guidelines",
            "implementation": f"{topic} implementation examples",
            "security": f"{topic} security considerations",
            "testing": f"{topic} testing strategies",
            "performance": f"{topic} performance optimization"
        }
        
        documentation = {
            "title": f"Comprehensive Guide: {topic.title()}",
            "sections": {}
        }
        
        print(f"📚 Generating documentation for: {topic}")
        print(f"📋 Sections to research: {len(doc_sections)}")
        
        # Research each section
        for section_name, search_query in doc_sections.items():
            print(f"\n🔍 Researching section: {section_name}")
            
            try:
                # Perform comprehensive search analysis
                analysis = await system.comprehensive_search_analysis(
                    query=search_query,
                    max_results=10
                )
                
                if analysis.get("status") == "success":
                    # Extract relevant information
                    section_data = {
                        "search_summary": {},
                        "content": "",
                        "sources": [],
                        "credibility": 0
                    }
                    
                    # Search results summary
                    if "search_results" in analysis:
                        search_info = analysis["search_results"]
                        section_data["search_summary"] = {
                            "total_found": search_info.get("total_found", 0),
                            "domains": search_info.get("domains", [])[:5]
                        }
                        
                        # Extract source URLs
                        for result in search_info.get("results", []):
                            if result.get("link"):
                                section_data["sources"].append({
                                    "title": result.get("title", ""),
                                    "url": result.get("link", ""),
                                    "domain": result.get("link", "").split("//")[-1].split("/")[0]
                                })
                    
                    # Content summary
                    if "summary" in analysis and "summary" in analysis["summary"]:
                        summary_data = analysis["summary"]["summary"]
                        section_data["content"] = summary_data.get("text", "")
                    
                    # Fact-check credibility
                    if "fact_check" in analysis:
                        fact_check = analysis["fact_check"]
                        section_data["credibility"] = fact_check.get("overall_credibility", 0)
                    
                    documentation["sections"][section_name] = section_data
                    
                    # Display progress
                    credibility = section_data["credibility"]
                    source_count = len(section_data["sources"])
                    content_length = len(section_data["content"])
                    
                    print(f"   ✅ Sources found: {source_count}")
                    print(f"   🛡️ Credibility: {credibility:.1%}")
                    print(f"   📄 Content: {content_length} characters")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error researching {section_name}: {str(e)}")
                continue
        
        # Generate final documentation
        print(f"\n📖 Generated Documentation: {documentation['title']}")
        print("=" * 70)
        
        # Documentation statistics
        total_sources = sum(len(section.get("sources", [])) for section in documentation["sections"].values())
        avg_credibility = sum(
            section.get("credibility", 0) for section in documentation["sections"].values()
        ) / len(documentation["sections"]) if documentation["sections"] else 0
        
        total_content = sum(len(section.get("content", "")) for section in documentation["sections"].values())
        
        print(f"📊 Documentation Statistics:")
        print(f"   📑 Sections: {len(documentation['sections'])}")
        print(f"   📄 Total sources: {total_sources}")
        print(f"   🛡️ Average credibility: {avg_credibility:.1%}")
        print(f"   📝 Total content: {total_content:,} characters")
        
        # Generate table of contents
        print(f"\n📋 Table of Contents:")
        for i, section_name in enumerate(documentation["sections"].keys(), 1):
            section_title = section_name.replace("_", " ").title()
            print(f"   {i}. {section_title}")
        
        # Display each section
        for section_name, section_data in documentation["sections"].items():
            section_title = section_name.replace("_", " ").title()
            credibility = section_data.get("credibility", 0)
            content = section_data.get("content", "")
            sources = section_data.get("sources", [])
            
            print(f"\n{section_title}")
            print("-" * len(section_title))
            
            # Credibility indicator
            if credibility > 0.8:
                cred_indicator = "🟢 HIGH CONFIDENCE"
            elif credibility > 0.6:
                cred_indicator = "🟡 MEDIUM CONFIDENCE"
            else:
                cred_indicator = "🔴 LOW CONFIDENCE"
            
            print(f"Credibility: {cred_indicator} ({credibility:.1%})")
            
            # Content
            if content:
                print(f"\nContent:")
                # Format content nicely
                if len(content) > 300:
                    print(f"{content[:300]}...")
                    print(f"[Content truncated - full length: {len(content)} characters]")
                else:
                    print(content)
            
            # Sources
            if sources:
                print(f"\nSources ({len(sources)}):")
                for i, source in enumerate(sources[:5], 1):
                    domain = source.get("domain", "unknown")
                    title = source.get("title", "Untitled")[:50]
                    print(f"   {i}. {title} ({domain})")
                
                if len(sources) > 5:
                    print(f"   ... and {len(sources) - 5} more sources")
        
        # Quality assessment
        print(f"\n🎯 Documentation Quality Assessment:")
        
        high_quality_sections = [
            name for name, data in documentation["sections"].items()
            if data.get("credibility", 0) > 0.7
        ]
        
        if high_quality_sections:
            print(f"   ✅ High-quality sections ({len(high_quality_sections)}):")
            for section in high_quality_sections:
                print(f"      • {section.replace('_', ' ').title()}")
        
        needs_review = [
            name for name, data in documentation["sections"].items()
            if data.get("credibility", 0) < 0.5
        ]
        
        if needs_review:
            print(f"   ⚠️ Sections needing review ({len(needs_review)}):")
            for section in needs_review:
                print(f"      • {section.replace('_', ' ').title()}")
        
        # Recommendations
        print(f"\n💡 Documentation Recommendations:")
        
        if avg_credibility > 0.7:
            print("   ✅ Strong documentation foundation with reliable sources")
        else:
            print("   📚 Consider additional authoritative sources for better credibility")
        
        if total_sources < 20:
            print("   📈 Expand source diversity for more comprehensive coverage")
        
        # Domain diversity check
        all_domains = set()
        for section in documentation["sections"].values():
            for source in section.get("sources", []):
                all_domains.add(source.get("domain", ""))
        
        if len(all_domains) < 10:
            print("   🔄 Include more diverse source types (academic, industry, official docs)")
        
        print("\n✅ Documentation generation completed!")
        
    except Exception as e:
        print(f"❌ Error during documentation generation: {str(e)}")
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(documentation_generation_example())
