import os
import json 
from typing import Dict, Any, List
from pydantic import BaseModel
from langchain.tools import tool


class ArchLensConfig(BaseModel):
    name: str
    rootFolder: str
    views: Dict[str, Dict[str, List[Dict[str, Any]]]]
    saveLocation:str  = "./diagrams/"


REPOSITORY_FOLDER = "repositories"

@tool('run_archLens')
def run_archLens() -> str:
    """"Run archLens on the current directory (should be in a repository)."""
    current_dir = os.getcwd()
    
    if not os.path.exists("archlens.json"):
        return f"archlens.json does not exist in {current_dir}. Please make sure you're in a repository directory and run init_archLens first."

    try:
        exit_code = os.system("archlens render")
        if exit_code == 0:
            return f"Successfully ran archLens in {current_dir}"
        else:
            return f"archLens render failed with exit code {exit_code}"
    except Exception as e:
        return f"Error running archLens: {str(e)}"

@tool('init_archLens')
def init_archLens() -> str:
    """"Initialize archLens in the current directory (should be in a repository)."""
    current_dir = os.getcwd()
    
    # Check if we're in what looks like a repository directory
    if not (REPOSITORY_FOLDER in current_dir or os.path.exists(".git")):
        return f"Current directory ({current_dir}) doesn't appear to be a repository. Please navigate to a repository first."
    
    if os.path.exists("archlens.json"):
        return f"archlens.json already exists in {current_dir}, skipping initialization."
    else:
        try:
            exit_code = os.system("archlens init")
            if exit_code == 0:
                return f"Successfully initialized archLens in {current_dir}"
            else:
                return f"archLens init failed with exit code {exit_code}"
        except Exception as e:
            return f"Error initializing archLens: {str(e)}"

@tool('read_archLens_config_file')
def read_archLens_config_file() -> ArchLensConfig:
    """"Reads the content of the archlens.json file."""

    config_path = "archlens.json"
    if not os.path.exists(config_path):
        return "archlens.json does not exist. Please run init_archLens first."
    
    with open('archlens.json', 'r') as file:
        data = json.load(file)

    #print(json.dumps(data, indent=4))
    arch = ArchLensConfig(**data)
    return arch

@tool('write_archLens_config_file')
def write_archLens_config_file(arch: ArchLensConfig) -> str:
    """"Writes content to the archlens.json file.
        args: 
    """
    config_path = "archlens.json"
    with open(config_path, 'w') as file:
        json.dump(arch.__dict__, file)
    
    return "Wrote to config file"

@tool('create_ArchLensConfig_Object')
def create_archLens_config_object(packageName:str, path: str, depth: int) -> ArchLensConfig:
    """"Creates an ArchLensConfig object, which is used when writing to the archlens.json file. This is the structure of the ArchLensConfig object:
    viewsJson = {"top-level-view-depth-1": {
      "packages": [
        {
          "path": "*",
          "depth": 1
        }
      ]
    },
    "top-level-view-depth-2": {
      "packages": [
        {
          "path": "*",
          "depth": 2
        }
      ]
    }}
    """

    viewsJson = {packageName: {
      "packages": [
        {
          "path": path,
          "depth": depth
        }
      ]
    }
    }

    archlensObject = ArchLensConfig(name='testing' ,rootFolder='zeeguu', views=viewsJson)
    return archlensObject

##
@tool('add_view_to_ArchLensConfig_Object')
def add_view_to_archLens_config_object(archlensObject: ArchLensConfig, packageName:str, path:str, depth: int) -> ArchLensConfig:

  """"Adds a view to an existing ArchLensConfig object. 
          args: 
              archlensObject: The existing ArchLensConfig object.
              name: The name of the view to add.
  """

  archlensObject.views[packageName] = {
      "packages": [
        {
          "path": path,
          "depth": depth
        }
      ]
    }
  return archlensObject