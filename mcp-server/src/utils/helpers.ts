/**
 * Utility functions for error handling and transformation
 */

import { ErrorTransformResult } from '../types/index.js';

/**
 * Extract file name from error message
 */
export function extractFileNameFromMessage(message: string): string | undefined {
  // Pattern 1: /path/to/file.java:[line]:[column]: error
  const pathMatch = message.match(/([\/\\][\w\-\/\\\.]+\.java):\d+:\d+:/);
  if (pathMatch) {
    return pathMatch[1];
  }
  
  // Pattern 2: [ERROR] /path/to/file.java:[line,column]
  const errorMatch = message.match(/\[ERROR\]\s+([\/\\][\w\-\/\\\.]+\.java):\[\d+,\d+\]/);
  if (errorMatch) {
    return errorMatch[1];
  }
  
  // Pattern 3: file.java: error description
  const simpleMatch = message.match(/([\w\-]+\.java):/);
  if (simpleMatch) {
    return simpleMatch[1];
  }
  
  return undefined;
}

/**
 * Extract line number from error message
 */
export function extractLineFromMessage(message: string): number | undefined {
  // Pattern 1: file.java:[line]:[column]:
  const colonMatch = message.match(/:(\d+):\d+:/);
  if (colonMatch) {
    return parseInt(colonMatch[1], 10);
  }
  
  // Pattern 2: [ERROR] file.java:[line,column]
  const bracketMatch = message.match(/:\[(\d+),\d+\]/);
  if (bracketMatch) {
    return parseInt(bracketMatch[1], 10);
  }
  
  // Pattern 3: line number in parentheses
  const parenMatch = message.match(/line\s*(\d+)/i);
  if (parenMatch) {
    return parseInt(parenMatch[1], 10);
  }
  
  return undefined;
}

/**
 * Extract column number from error message
 */
export function extractColumnFromMessage(message: string): number | undefined {
  // Pattern 1: file.java:[line]:[column]:
  const colonMatch = message.match(/:(\d+):(\d+):/);
  if (colonMatch) {
    return parseInt(colonMatch[2], 10);
  }
  
  // Pattern 2: [ERROR] file.java:[line,column]
  const bracketMatch = message.match(/:\[\d+,(\d+)\]/);
  if (bracketMatch) {
    return parseInt(bracketMatch[1], 10);
  }
  
  return undefined;
}

/**
 * Clean error message by removing file paths and line numbers
 */
export function cleanErrorMessage(message: string): string {
  // Remove file paths with line/column info
  let cleaned = message.replace(/[\/\\][\w\-\/\\\.]+\.java:\d+:\d+:\s*/, '');
  
  // Remove [ERROR] prefixes
  cleaned = cleaned.replace(/^\[ERROR\]\s*/, '');
  
  // Remove file:line,column patterns
  cleaned = cleaned.replace(/[\w\-]+\.java:\[\d+,\d+\]\s*/, '');
  
  // Remove leading/trailing whitespace and redundant spaces
  cleaned = cleaned.trim().replace(/\s+/g, ' ');
  
  return cleaned;
}

/**
 * Transform Maven/compilation errors into structured format
 */
export function transformCompilationError(errorMessage: string): ErrorTransformResult {
  const file = extractFileNameFromMessage(errorMessage);
  const line = extractLineFromMessage(errorMessage);
  const column = extractColumnFromMessage(errorMessage);
  const message = cleanErrorMessage(errorMessage);
  
  // Determine severity based on message content
  let severity: 'error' | 'warning' | 'info' = 'error';
  if (errorMessage.toLowerCase().includes('warning')) {
    severity = 'warning';
  } else if (errorMessage.toLowerCase().includes('info')) {
    severity = 'info';
  }
  
  return {
    file,
    line,
    column,
    message,
    severity
  };
}

/**
 * Generate unique identifier
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Validate file path
 */
export function isValidPath(filePath: string): boolean {
  try {
    // Basic validation - no null bytes, reasonable length
    return (
      typeof filePath === 'string' &&
      filePath.length > 0 &&
      filePath.length < 4096 &&
      !filePath.includes('\0') &&
      !filePath.includes('..')
    );
  } catch {
    return false;
  }
}

/**
 * Safe JSON parse with fallback
 */
export function safeJsonParse<T>(jsonString: string, fallback: T): T {
  try {
    return JSON.parse(jsonString);
  } catch {
    return fallback;
  }
}
