/**
 * Project management service
 */

import fs from 'fs/promises';
import path from 'path';
import { execSync } from 'child_process';
import { buildProjectStructure, listDirectory, readFileContent } from '../utils/index.js';
import { ProjectStructure, FileSystemEntry } from '../types/index.js';

export class ProjectService {
  private projectsBasePath: string;

  constructor(projectsBasePath: string = '../GeneratedCode') {
    this.projectsBasePath = projectsBasePath;
    this.ensureProjectsDirectory();
  }

  /**
   * Ensure projects directory exists
   */
  private async ensureProjectsDirectory(): Promise<void> {
    try {
      await fs.access(this.projectsBasePath);
    } catch {
      await fs.mkdir(this.projectsBasePath, { recursive: true });
    }
  }

  /**
   * List all generated projects
   */
  async listGeneratedProjects(): Promise<any> {
    try {
      const projects = await listDirectory(this.projectsBasePath);
      const projectsWithDetails = await Promise.all(
        projects.filter(p => p.isDirectory).map(async (project) => {
          const projectPath = project.path;
          const structure = await buildProjectStructure(projectPath, 0, 3); // Limit depth for performance
          const stats = await this.getProjectStats(projectPath);
          
          return {
            name: project.name,
            path: projectPath,
            lastModified: project.lastModified,
            structure,
            stats
          };
        })
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              projects: projectsWithDetails,
              totalProjects: projectsWithDetails.length,
              basePath: this.projectsBasePath
            }, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to list projects: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Read file content from a project
   */
  async readFileContent(filePath: string): Promise<any> {
    try {
      const content = await readFileContent(filePath);
      const stats = await fs.stat(filePath);
      
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              filePath,
              content,
              size: stats.size,
              lastModified: stats.mtime,
              encoding: 'utf-8'
            }, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to read file content: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Analyze project structure
   */
  async analyzeProjectStructure(projectPath: string, maxDepth: number = 10): Promise<any> {
    try {
      const structure = await buildProjectStructure(projectPath, 0, maxDepth);
      const stats = await this.getProjectStats(projectPath);
      
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              structure,
              stats,
              analysis: {
                totalFiles: stats.fileCount,
                totalDirectories: stats.dirCount,
                languages: stats.languages,
                recommendations: this.getProjectRecommendations(structure, stats)
              }
            }, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to analyze project structure: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get project statistics
   */
  private async getProjectStats(projectPath: string): Promise<any> {
    let fileCount = 0;
    let dirCount = 0;
    let totalSize = 0;
    const languages = new Set<string>();
    const extensions = new Map<string, number>();

    const traverse = async (currentPath: string): Promise<void> => {
      try {
        const entries = await fs.readdir(currentPath);
        
        for (const entry of entries) {
          // Skip hidden files and common build directories
          if (entry.startsWith('.') || ['node_modules', 'target', 'dist', 'build'].includes(entry)) {
            continue;
          }
          
          const entryPath = path.join(currentPath, entry);
          const stats = await fs.stat(entryPath);
          
          if (stats.isDirectory()) {
            dirCount++;
            await traverse(entryPath);
          } else {
            fileCount++;
            totalSize += stats.size;
            
            const ext = path.extname(entry).toLowerCase();
            if (ext) {
              extensions.set(ext, (extensions.get(ext) || 0) + 1);
              
              // Map extensions to languages
              const languageMap: Record<string, string> = {
                '.java': 'Java',
                '.ts': 'TypeScript',
                '.js': 'JavaScript',
                '.py': 'Python',
                '.cpp': 'C++',
                '.c': 'C',
                '.cs': 'C#',
                '.go': 'Go',
                '.rs': 'Rust',
                '.php': 'PHP',
                '.rb': 'Ruby',
                '.swift': 'Swift',
                '.kt': 'Kotlin'
              };
              
              if (languageMap[ext]) {
                languages.add(languageMap[ext]);
              }
            }
          }
        }
      } catch {
        // Skip directories we can't read
      }
    };

    await traverse(projectPath);

    return {
      fileCount,
      dirCount,
      totalSize,
      languages: Array.from(languages),
      extensions: Object.fromEntries(extensions)
    };
  }

  /**
   * Get project recommendations based on structure and stats
   */
  private getProjectRecommendations(structure: ProjectStructure, stats: any): string[] {
    const recommendations: string[] = [];

    // Check for common project structure issues
    if (stats.fileCount > 1000) {
      recommendations.push("Large project detected. Consider breaking into smaller modules.");
    }

    if (stats.languages.length > 3) {
      recommendations.push("Multiple languages detected. Ensure proper build tool configuration.");
    }

    if (stats.languages.includes('Java') && !this.hasFileInStructure(structure, 'pom.xml') && !this.hasFileInStructure(structure, 'build.gradle')) {
      recommendations.push("Java project without Maven or Gradle detected. Consider adding a build tool.");
    }

    if (stats.languages.includes('TypeScript') && !this.hasFileInStructure(structure, 'package.json')) {
      recommendations.push("TypeScript project without package.json detected. Consider initializing npm project.");
    }

    return recommendations;
  }

  /**
   * Check if a file exists in the project structure
   */
  private hasFileInStructure(structure: ProjectStructure, fileName: string): boolean {
    if (structure.name === fileName) {
      return true;
    }
    
    if (structure.children) {
      return structure.children.some(child => this.hasFileInStructure(child, fileName));
    }
    
    return false;
  }
}
