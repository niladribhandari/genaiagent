"""
Example 2: Repository Analysis with Security Scanning
"""

import asyncio
from src.github_search_agent import GitHubSearchSystem

async def analysis_example():
    """Demonstrate repository analysis with security scanning."""
    
    system = GitHubSearchSystem()
    
    try:
        print("🔍 Searching for machine learning repositories with analysis...")
        
        # Search with analysis enabled
        results = await system.search_repositories(
            query="machine learning pytorch",
            max_results=5,
            language="python",
            include_analysis=True,
            include_security_scan=True
        )
        
        print(f"\n✅ Found {results.total_count} repositories")
        print(f"📊 Analyzed {len(results.analyses)} repositories")
        
        # Display analysis results
        for analysis in results.analyses:
            repo = analysis.repository
            print(f"\n📦 {repo.full_name}")
            print(f"   📊 Quality Score: {analysis.score:.1f}/100")
            print(f"   🔒 Security Issues: {len(analysis.security_issues)}")
            
            if analysis.security_issues:
                critical_issues = [issue for issue in analysis.security_issues 
                                 if issue.severity == "CRITICAL"]
                high_issues = [issue for issue in analysis.security_issues 
                              if issue.severity == "HIGH"]
                
                if critical_issues:
                    print(f"   🚨 Critical Issues: {len(critical_issues)}")
                if high_issues:
                    print(f"   ⚠️  High Issues: {len(high_issues)}")
            
            print(f"   📝 Summary: {analysis.summary}")
        
        # Detailed analysis of top repository
        if results.repositories:
            top_repo = results.repositories[0]
            print(f"\n🔬 Detailed analysis of {top_repo.full_name}...")
            
            detailed_analysis = await system.analyze_repository(
                top_repo.owner, 
                top_repo.name,
                include_security=True,
                include_trends=True
            )
            
            print(f"   📊 Overall Quality: {detailed_analysis.score:.1f}/100")
            print(f"   📁 Files Analyzed: {len(detailed_analysis.code_files)}")
            print(f"   🔒 Security Issues: {len(detailed_analysis.security_issues)}")
            
            # Show security issues by severity
            if detailed_analysis.security_issues:
                severity_counts = {}
                for issue in detailed_analysis.security_issues:
                    severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
                
                print("   🔒 Security Issues by Severity:")
                for severity, count in severity_counts.items():
                    print(f"      {severity}: {count}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(analysis_example())
