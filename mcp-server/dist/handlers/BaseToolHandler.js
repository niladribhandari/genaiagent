/**
 * Base tool handler interface and implementation
 */
export class BaseToolHandler {
    context;
    constructor(context) {
        this.context = context;
    }
    createTextResult(text) {
        return {
            content: [
                {
                    type: "text",
                    text: text
                }
            ]
        };
    }
    createJsonResult(data) {
        return this.createTextResult(JSON.stringify(data, null, 2));
    }
}
