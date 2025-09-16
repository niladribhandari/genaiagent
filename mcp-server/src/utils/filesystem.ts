/**
 * File system utilities
 */

import fs from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import { ProjectStructure, FileSystemEntry } from '../types/index.js';

/**
 * Check if a path exists
 */
export async function pathExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Get file stats safely
 */
export async function getFileStats(filePath: string) {
  try {
    return await fs.stat(filePath);
  } catch {
    return null;
  }
}

/**
 * Read file content safely
 */
export async function readFileContent(filePath: string): Promise<string> {
  try {
    return await fs.readFile(filePath, 'utf-8');
  } catch (error) {
    throw new Error(`Failed to read file ${filePath}: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Write file content safely
 */
export async function writeFileContent(filePath: string, content: string): Promise<void> {
  try {
    await fs.mkdir(path.dirname(filePath), { recursive: true });
    await fs.writeFile(filePath, content, 'utf-8');
  } catch (error) {
    throw new Error(`Failed to write file ${filePath}: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Build project structure recursively
 */
export async function buildProjectStructure(
  dirPath: string,
  currentDepth: number = 0,
  maxDepth: number = 10
): Promise<ProjectStructure> {
  const stats = await fs.stat(dirPath);
  const name = path.basename(dirPath);
  
  const structure: ProjectStructure = {
    name,
    type: stats.isDirectory() ? 'directory' : 'file',
    path: dirPath,
    size: stats.size,
    lastModified: stats.mtime,
  };
  
  if (stats.isDirectory() && currentDepth < maxDepth) {
    try {
      const entries = await fs.readdir(dirPath);
      structure.children = [];
      
      for (const entry of entries) {
        // Skip hidden files and common build directories
        if (entry.startsWith('.') || ['node_modules', 'target', 'dist', 'build'].includes(entry)) {
          continue;
        }
        
        const entryPath = path.join(dirPath, entry);
        try {
          const childStructure = await buildProjectStructure(entryPath, currentDepth + 1, maxDepth);
          structure.children.push(childStructure);
        } catch {
          // Skip entries we can't read
          continue;
        }
      }
      
      // Sort children: directories first, then files, both alphabetically
      structure.children.sort((a, b) => {
        if (a.type !== b.type) {
          return a.type === 'directory' ? -1 : 1;
        }
        return a.name.localeCompare(b.name);
      });
    } catch {
      // If we can't read the directory, just return it as a directory without children
    }
  }
  
  return structure;
}

/**
 * List directory contents
 */
export async function listDirectory(dirPath: string): Promise<FileSystemEntry[]> {
  try {
    const entries = await fs.readdir(dirPath);
    const result: FileSystemEntry[] = [];
    
    for (const entry of entries) {
      const entryPath = path.join(dirPath, entry);
      const stats = await getFileStats(entryPath);
      
      if (stats) {
        result.push({
          name: entry,
          path: entryPath,
          isDirectory: stats.isDirectory(),
          size: stats.size,
          lastModified: stats.mtime,
        });
      }
    }
    
    return result.sort((a, b) => {
      if (a.isDirectory !== b.isDirectory) {
        return a.isDirectory ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });
  } catch (error) {
    throw new Error(`Failed to list directory ${dirPath}: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}
