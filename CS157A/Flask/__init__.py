from flask import Flask
import os

cwd = os.getcwd()

templates_relative_path = "CS157A/Flask/templates"
static_relative_path = "CS157A/Flask/static"

templates_folder_location = os.path.join(cwd, templates_relative_path) 
static_folder_location = os.path.join(cwd, static_relative_path) 

flask_obj = Flask(__name__,
                  template_folder = templates_folder_location,
                  static_folder = static_folder_location)

from CS157A.Flask import routes