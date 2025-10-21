# Drawing Tools Module
This module defines the prerequisites for the agent to generate and render diagrams using PlantUML. Ensure Docker is installed and running on your system to host the PlantUML server locally.
## Quick Start

### PlantUML Setup

#### Setup server for Agent
```bash
# Pull the PlantUML server image
docker pull plantuml/plantuml-server:jetty

# Run the PlantUML server
docker run -d -p 8080:8080 --name plantumlserver plantuml/plantuml-server:jetty
```

#### Local testing and inspection of UML diagrams in VS code
1. Install the PlantUML VS Code extension:
   - Visit: https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml
   - Or search for "PlantUML" in VS Code extensions

2. VS Code will automatically install PlantUML locally
3. Access any plantuml file and use th VS code preview

#### Optional VS Code Configuration to use local server
Update VS Code `settings.json`:

```json
{
  "plantuml.server": "http://localhost:8080/",
  "plantuml.render": "PlantUMLServer",
  "plantuml.exportOutDir": "/diagrams/out"
}
```
