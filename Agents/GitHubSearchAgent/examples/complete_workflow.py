"""
Example 5: Complete Search Workflow
"""

import asyncio
from src.github_search_agent import GitHubSearchSystem

async def complete_workflow_example():
    """Demonstrate complete search and analysis workflow."""
    
    system = GitHubSearchSystem()
    
    try:
        print("🔍 Starting complete GitHub search workflow...")
        
        # 1. Search for repositories
        print("\n1️⃣ Searching for repositories...")
        search_results = await system.smart_search(
            query="python machine learning",
            search_type="repositories",
            max_results=5
        )
        
        print(f"   Found {len(search_results)} repositories")
        
        # 2. Analyze each repository
        print("\n2️⃣ Analyzing repositories...")
        analysis_results = []
        
        for repo in search_results:
            print(f"   Analyzing {repo.name}...")
            
            # Basic analysis
            analysis = await system.analyze_repository(repo.name)
            
            # Security scan
            security = await system.scan_repository_security(repo.name)
            
            # Code quality assessment
            quality = await system.assess_code_quality(repo.name)
            
            analysis_results.append({
                'repository': repo,
                'analysis': analysis,
                'security': security,
                'quality': quality
            })
        
        # 3. Generate comprehensive report
        print("\n3️⃣ Generating comprehensive report...")
        
        report = {
            'search_query': "python machine learning",
            'total_repositories': len(search_results),
            'analysis_date': "2024-12-30",
            'repositories': []
        }
        
        for result in analysis_results:
            repo = result['repository']
            analysis = result['analysis']
            security = result['security']
            quality = result['quality']
            
            repo_report = {
                'name': repo.name,
                'description': repo.description,
                'stars': repo.stars,
                'forks': repo.forks,
                'language': repo.language,
                'last_updated': repo.last_updated.isoformat() if repo.last_updated else None,
                'quality_score': quality.overall_score,
                'security_score': 100 - len(security.vulnerabilities),
                'complexity_score': analysis.complexity_score,
                'maintainability': quality.maintainability_score,
                'documentation_quality': quality.documentation_score,
                'test_coverage': quality.test_coverage,
                'security_issues': len(security.vulnerabilities),
                'performance_score': quality.performance_score
            }
            
            report['repositories'].append(repo_report)
        
        # 4. Display results
        print("\n📊 COMPREHENSIVE ANALYSIS REPORT")
        print("=" * 50)
        
        print(f"\n🔍 Search Query: {report['search_query']}")
        print(f"📅 Analysis Date: {report['analysis_date']}")
        print(f"📦 Repositories Analyzed: {report['total_repositories']}")
        
        print("\n🏆 TOP REPOSITORIES BY OVERALL SCORE:")
        
        # Sort by composite score
        sorted_repos = sorted(
            report['repositories'],
            key=lambda x: (x['quality_score'] + x['security_score']) / 2,
            reverse=True
        )
        
        for i, repo in enumerate(sorted_repos, 1):
            print(f"\n{i}. {repo['name']}")
            print(f"   ⭐ Stars: {repo['stars']:,}")
            print(f"   📊 Quality: {repo['quality_score']:.1f}/100")
            print(f"   🔒 Security: {repo['security_score']:.1f}/100")
            print(f"   🧪 Test Coverage: {repo['test_coverage']:.1f}%")
            print(f"   📚 Documentation: {repo['documentation_quality']:.1f}/100")
            print(f"   🚨 Security Issues: {repo['security_issues']}")
            print(f"   📝 {repo['description'][:100]}...")
        
        # 5. Generate recommendations
        print("\n💡 RECOMMENDATIONS:")
        
        best_repo = sorted_repos[0]
        print(f"   🥇 Best Overall: {best_repo['name']}")
        print(f"      Excellent balance of quality, security, and features")
        
        most_popular = max(sorted_repos, key=lambda x: x['stars'])
        print(f"   👥 Most Popular: {most_popular['name']}")
        print(f"      {most_popular['stars']:,} stars - strong community support")
        
        best_maintained = max(sorted_repos, key=lambda x: x['maintainability'])
        print(f"   🔧 Best Maintained: {best_maintained['name']}")
        print(f"      {best_maintained['maintainability']:.1f}/100 maintainability score")
        
        most_secure = max(sorted_repos, key=lambda x: x['security_score'])
        print(f"   🛡️ Most Secure: {most_secure['name']}")
        print(f"      {most_secure['security_score']:.1f}/100 security score")
        
        print("\n✅ Analysis complete! Use these insights to make informed decisions.")
        
    except Exception as e:
        print(f"❌ Error during workflow: {str(e)}")
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(complete_workflow_example())
