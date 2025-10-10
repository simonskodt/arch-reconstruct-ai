![Header](docs/img/cover.png)

[![Pylint](https://github.com/simonskodt/arch-reconstruct-ai/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/simonskodt/arch-reconstruct-ai/actions/workflows/pylint.yml)
[![Check LangChain Dependencies Updates](https://github.com/simonskodt/arch-reconstruct-ai/actions/workflows/Langchain_dependencies.yml/badge.svg)](https://github.com/simonskodt/arch-reconstruct-ai/actions/workflows/Langchain_dependencies.yml)
[![License: MIT](https://cdn.prod.website-files.com/5e0f1144930a8bc8aace526c/65dd9eb5aaca434fac4f1c34_License-MIT-blue.svg)](/LICENSE)
[![Deps](https://cdn.prod.website-files.com/5e0f1144930a8bc8aace526c/65dd9eb5aaca434fac4f1c9e_Deps-Up--to--date-brightgreen.svg)]()

ArchReconstructAI is an **agentic AI system** that helps users understand codebases by reconstructing its architecture.

> [!WARNING]
> The project is under development; therefore currently not working.

## Motivation Behind This Repository

Our thesis focuses on agentic AI systems. After exploring various frameworks for developing agentic AI (LangGraph, CrewAI, AutoGen, Semantic Kernel, SmolAgents, Pydantic AI, Agno, n8n, etc.), we decided to build our own agentic AI system. We have all completed the Software Architecture course which introduced us to architectural reconstruction. This process requires running several different tools and possessing substantial knowledge to obtain an architectural view of the system. Therefore, we considered the processes of architectural reconstruction as an ideal challenge to be solved by an agentic AI system.

## How Does It Work?

Users can run our application against a repository, and the agentic AI system will collaborate with the human driver to develop an understanding of the codebase. The system collects general data, leverages domain-specific knowledge on architectural reconstruction, and invokes relevant tools to generate comprehensive documentation describing the system's architecture from multiple viewpoints. The views we initially aim to provide are described in "The 3+1 Approach to Software Architecture Description Using UML," namely:

- "A **Module viewpoint** concerned with how functionality of the system maps
to static development units,
- a **Component & Connector** viewpoint concerned with the runtime mapping
of functionality to components of the architecture, and
- an **Allocation viewpoint** concerned with how software entities are mapped
to environmental entities"

(Christensen, Henrik & Corry, Aino & Hansen, Klaus. (2004). An Approach to Software Architecture Description Using UML.).

## What Is?

<details>
    <summary><b>Architectural Reconstruction</b></summary>
    Architectural reconstruction is the process of recovering, documenting, and understanding the architectural design of an existing software system. This technique helps developers comprehend how different components of a codebase interact with each other by recreating architectural models from source code and other artifacts.
</details>

<details>
    <summary><b>Agentic AI</b></summary>
    Agentic AI refers to artificial intelligence systems that act as agents with some degree of autonomy, purpose-directedness, and the ability to perform tasks on behalf of users.
    Microsoft defines it as:
    <blockquote>
    AI Agents are <b>systems</b> that enable <b>Large Language Models (LLMs)</b> to <b>perform actions</b> by extending their capabilities by giving LLMs <b>access to tools</b> and <b>knowledge</b>.
    </blockquote>
</details>

## Installation

To install ArchReconstructAI:

> [!IMPORTANT]
> To run the program, we use the package manager *uv*. [Guide to installation.](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/simonskodt/arch-reconstruct-ai
cd ArchReconstructAI
uv run main.py
```

## Usage

You can run ArchReconstructAI against a repository using:

```bash
uv run main.py # TBD
```

## Output Examples

Under development.

## License

This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details.


## Run LangGraph Studio

LangGraph studio can be used to visualize, interact, and debug your agent locally.
1. Add LANGSMITH_API_KEY to your own local .env file. https://smith.langchain.com/o/e7bcbe7e-b691-491f-a1d0-f77247fd57df/settings/apikeys
2. Add agent to langgraph.json file. 
3. To start LangGraph Studio run: `uv run langgraph dev`

## Run Deepagents UI 

1. Clone the repository [github repository](https://github.com/langchain-ai/deep-agents-ui)
2. create or copy the .env.local into the repository
    ```
    NEXT_PUBLIC_DEPLOYMENT_URL="http://127.0.0.1:2024" # Or your server URL
    NEXT_PUBLIC_AGENT_ID=<your agent ID from langgraph.json>
    ```
3. `npm install`
4. `npm run dev`

## Environment Variables for MCP Servers

When adding an MCP server, if the connection requires a token or API key, set the corresponding environment variable in a `.env` file. It will be loaded automatically:

```bash
MCP1_API_KEY=secret
```

Example `mcp_servers_config.json`:

```json
{
    "mcp1": {
        "url": "https://mcp1.com/mcp",
        "transport": "streamable_http",
        "headers": {
            "Authorization": "Bearer MCP1_API_KEY"
        }
    },
    "mcp2": {
        "url": "..",
        "transport": ".."
    }
}
```