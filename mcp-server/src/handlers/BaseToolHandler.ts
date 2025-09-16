/**
 * Base tool handler interface and implementation
 */

import { ServerContext, ToolResult } from '../types/index.js';

export interface ToolHandler {
  handle(args: any, context: ServerContext): Promise<ToolResult>;
}

export abstract class BaseToolHandler implements ToolHandler {
  protected context: ServerContext;

  constructor(context: ServerContext) {
    this.context = context;
  }

  abstract handle(args: any, context: ServerContext): Promise<ToolResult>;

  protected createTextResult(text: string): ToolResult {
    return {
      content: [
        {
          type: "text",
          text: text
        }
      ]
    };
  }

  protected createJsonResult(data: any): ToolResult {
    return this.createTextResult(JSON.stringify(data, null, 2));
  }
}
