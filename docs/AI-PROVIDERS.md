# AI Providers and Web Search

Nila supports a switchable cloud-chat adapter plus a permission-gated web-search adapter.

## Ollama Cloud

The backend reads the API key from the process environment only. The browser UI never receives or displays the secret value.

Environment variables:

```text
OLLAMA_API_KEY=<your key>
NVC_OLLAMA_CLOUD_BASE=https://ollama.com
NVC_OLLAMA_CLOUD_MODEL=gpt-oss:20b-cloud
```

The Nila AI desktop app exposes an `Ollama Cloud ON/OFF` switch. Cloud requests also require the Security Center `network` capability and are blocked by Local-only mode.

Do not commit API keys to Git, `.env` files tracked by Git, frontend variables, screenshots or logs.

## Web Search

Web search is independently switchable and requires the network capability. Configure a trusted SearXNG-compatible JSON endpoint:

```text
NVC_SEARCH_ENDPOINT=http://127.0.0.1:8888
```

The AI runtime passes search snippets and source URLs as context when Web Search is ON. A production build must add URL/destination validation and SSRF protection before accepting arbitrary remote search endpoints.

## Chat rendering

AI responses are rendered with `react-markdown` + `remark-gfm`, so Markdown control characters such as `#`, `*`, and list markers are interpreted as formatting rather than displayed as raw syntax. Bold, italic, headings, lists, links and code are supported. Raw HTML is intentionally not enabled to avoid script/HTML injection.

## Task assignment

`Assign Task` is separate from conversational chat. When enabled, a chat request also creates a controlled task workspace. A model response alone never marks a system task complete; deterministic execution and verification remain authoritative.
