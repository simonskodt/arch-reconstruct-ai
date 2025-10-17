# Drawing Tools Module

## Features

## Quick Start

### PlantUML Setup

#### Option 1: Local Installation (Recommended)
1. Install the PlantUML VS Code extension:
   - Visit: https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml
   - Or search for "PlantUML" in VS Code extensions

2. VS Code will automatically install PlantUML locally

#### Option 2: Docker Setup
```bash
# Pull the PlantUML server image
docker pull plantuml/plantuml-server:jetty

# Run the PlantUML server
docker run -d -p 8080:8080 --name plantumlserver plantuml/plantuml-server:jetty
```


#### VS Code Configuration
Update your VS Code `settings.json`:

```json
{
  "plantuml.server": "http://localhost:8080/",
  "plantuml.render": "PlantUMLServer",
  "plantuml.exportOutDir": "/diagrams/out"
}
```
Test the setup at: http://localhost:8080/
