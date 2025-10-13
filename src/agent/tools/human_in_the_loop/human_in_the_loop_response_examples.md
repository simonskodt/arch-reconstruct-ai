# Human-in-the-loop (HITL) response guide

This document shows the exact response shapes the `HumanInTheLoopMiddleware` (and compatible HITL handlers) expect when your UI or manual process returns decisions for interrupts. The middleware expects a single object with a `decisions` key whose value is a list. The list length and order must match the `action_requests` you sent in the original `HITLRequest`.

Summary rules
- The root object MUST be a dict with a `decisions` key.
- `decisions` is a list with one entry per requested action (same order).
- Each entry must be one of:
    - ApproveDecision: `{ "type": "approve" }`
    - EditDecision: `{ "type": "edit", "edited_action": {"name": <str>, "arguments": <dict>} }`
    - RejectDecision: `{ "type": "reject", "message": <optional str> }`

Why order matters
- The middleware maps each decision to the corresponding `action_request` by index. If lengths differ you'll get a validation error.

Examples

1) Approve a single tool call

```json
{
    "decisions": [
        { "type": "approve" }
    ]
}
```

2) Edit the arguments for a tool call (change values or even tool name)

```json
{
    "decisions": [
        {
            "type": "edit",
            "edited_action": {
                "name": "weather_tool",
                "arguments": { "location": "London" }
            }
        }
    ]
}
```

3) Reject with a message (human feedback sent back to the LLM)

```json
{
    "decisions": [
        {
            "type": "reject",
            "message": "Do not call external APIs now"
        }
    ]
}
```

4) Multiple actions (example with three interrupts)

```json
{
    "decisions": [
        { "type": "approve" },
        {
            "type": "edit",
            "edited_action":
            {
                "name": "different_tool",
                "arguments":
                { "data":
                    {
                    "text": "corrected" }
                    }
                }
        },
        { "type": "reject", "message": "Skip this one" }
    ]
}
```

Best practices and tips

- Always validate the **Response**: If an exception is raised during the interrupt for human-in-the-loop due to the reponse the remaining run will fault
- For `edit`: the `edited_action` must include `name` (string) and `arguments` (object/dict). If you only want to change a single field, include the full `arguments` object as expected by the tool.
- For `reject`, the message appears to the model as tool feedback.

Debugging & validation

- If you see errors like `Number of human decisions (...) does not match number of hanging tool calls`, inspect the original `HITLRequest.action_requests` array and ensure your `decisions` list matches in order and length.


Integrating with LangGraph Studio (or other UIs)

- The flow is:
    1. Graph interrupts and emits a `HITLRequest` (list of `action_requests`).
    2. The UI shows the requests and provides controls to Approve / Edit / Reject.
    3. UI translates selections into the HITLResponse JSON above and returns it to the runtime.

Small checklist for UI implementation

- [ ] Display each `action_request` with its `description` and `arguments`.
- [ ] Provide three actions: Approve, Edit, Reject.
- [ ] When Edit is used, capture the edited `arguments` and return them in `edited_action.arguments`.
- [ ] Return a single JSON object with `decisions` (same order as requests).
