"""
Tasks API

RESTful API for direct tasks operations using GoogleTasksRepository.
Provides endpoints for managing task lists and tasks.
"""

import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from googleapiclient.errors import HttpError
from flasgger import Swagger

# Add src directory to path to import modules
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from tasks_repository import GoogleTasksRepository


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api-docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Tasks API",
        "description": "RESTful API for direct tasks operations using Google Tasks",
        "version": "1.0.0",
        "contact": {
            "name": "API Support"
        }
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "Health",
            "description": "Health check endpoints"
        },
        {
            "name": "Task Lists",
            "description": "Task list management endpoints"
        },
        {
            "name": "Tasks",
            "description": "Task management endpoints"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Initialize tasks repository
tasks_repo = GoogleTasksRepository()


@app.route('/tasks/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---
    tags:
      - Health
    summary: Check API health status
    description: Returns the health status of the Tasks API service
    responses:
      200:
        description: API is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            service:
              type: string
              example: tasks-api
    """
    return jsonify({
        "status": "healthy",
        "service": "tasks-api"
    }), 200


@app.route('/tasks/lists', methods=['GET'])
def list_task_lists():
    """
    List All Task Lists
    ---
    tags:
      - Task Lists
    summary: List all task lists accessible by the user
    description: Retrieves a list of all task lists that the authenticated user has access to
    responses:
      200:
        description: Successfully retrieved task lists
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            task_lists:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: "@default"
                  title:
                    type: string
                    example: "My Tasks"
            count:
              type: integer
              example: 1
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to list task lists: ..."
    """
    try:
        task_lists = tasks_repo.list_task_lists()
        return jsonify({
            "success": True,
            "task_lists": task_lists,
            "count": len(task_lists)
        }), 200
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list task lists: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/tasks/lists/<task_list_id>', methods=['GET'])
def get_task_list(task_list_id: str):
    """
    Get Task List by ID
    ---
    tags:
      - Task Lists
    summary: Get a specific task list by ID
    description: Retrieves detailed information about a specific task list
    parameters:
      - name: task_list_id
        in: path
        type: string
        required: true
        description: The ID of the task list to retrieve
        example: "@default"
    responses:
      200:
        description: Successfully retrieved task list
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            task_list:
              type: object
              properties:
                id:
                  type: string
                  example: "@default"
                title:
                  type: string
                  example: "My Tasks"
      404:
        description: Task list not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to get task list: ..."
      500:
        description: Server error
    """
    try:
        task_list = tasks_repo.get_task_list(task_list_id)
        return jsonify({
            "success": True,
            "task_list": task_list
        }), 200
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get task list: {str(e)}"
        }), 404 if e.resp.status == 404 else 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/tasks/lists/<task_list_id>/tasks', methods=['GET'])
def list_tasks(task_list_id: str):
    """
    List Tasks
    ---
    tags:
      - Tasks
    summary: List tasks from a task list
    description: Retrieves a list of tasks from the specified task list with optional filtering
    parameters:
      - name: task_list_id
        in: path
        type: string
        required: true
        description: Task list identifier
        example: "@default"
      - name: show_completed
        in: query
        type: boolean
        required: false
        default: false
        description: Whether to show completed tasks
      - name: show_deleted
        in: query
        type: boolean
        required: false
        default: false
        description: Whether to show deleted tasks
      - name: max_results
        in: query
        type: integer
        required: false
        description: Maximum number of tasks to return
    responses:
      200:
        description: Successfully retrieved tasks
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            tasks:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: "task123"
                  title:
                    type: string
                    example: "Complete project"
                  status:
                    type: string
                    example: "needsAction"
            count:
              type: integer
              example: 5
      500:
        description: Server error
    """
    try:
        show_completed = request.args.get('show_completed', 'false').lower() == 'true'
        show_deleted = request.args.get('show_deleted', 'false').lower() == 'true'
        max_results = request.args.get('max_results', type=int)
        
        tasks = tasks_repo.list_tasks(
            task_list_id=task_list_id,
            show_completed=show_completed,
            show_deleted=show_deleted,
            max_results=max_results
        )
        
        return jsonify({
            "success": True,
            "tasks": tasks,
            "count": len(tasks)
        }), 200
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list tasks: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/tasks/lists/<task_list_id>/tasks/<task_id>', methods=['GET'])
def get_task(task_list_id: str, task_id: str):
    """
    Get Task by ID
    ---
    tags:
      - Tasks
    summary: Get a specific task by ID
    description: Retrieves detailed information about a specific task
    parameters:
      - name: task_list_id
        in: path
        type: string
        required: true
        description: Task list identifier
        example: "@default"
      - name: task_id
        in: path
        type: string
        required: true
        description: The ID of the task to retrieve
        example: "task123"
    responses:
      200:
        description: Successfully retrieved task
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            task:
              type: object
              properties:
                id:
                  type: string
                  example: "task123"
                title:
                  type: string
                  example: "Complete project"
                status:
                  type: string
                  example: "needsAction"
      404:
        description: Task not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to get task: ..."
      500:
        description: Server error
    """
    try:
        task = tasks_repo.get_task(task_id, task_list_id=task_list_id)
        return jsonify({
            "success": True,
            "task": task
        }), 200
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get task: {str(e)}"
        }), 404 if e.resp.status == 404 else 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/tasks/lists/<task_list_id>/tasks', methods=['POST'])
def create_task(task_list_id: str):
    """
    Create Task
    ---
    tags:
      - Tasks
    summary: Create a new task
    description: Creates a new task in the specified task list
    parameters:
      - name: task_list_id
        in: path
        type: string
        required: true
        description: Task list identifier
        example: "@default"
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              description: Title of the task
              example: "Complete project"
            notes:
              type: string
              description: Notes/description for the task
              example: "Finish the project documentation"
            due:
              type: string
              description: Due date in RFC3339 format
              example: "2024-12-31T23:59:59Z"
    responses:
      201:
        description: Successfully created task
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            task:
              type: object
              properties:
                id:
                  type: string
                  example: "task123"
                title:
                  type: string
                  example: "Complete project"
      400:
        description: Bad request (missing required fields)
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Title is required"
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        title = data.get('title')
        if not title:
            return jsonify({
                "success": False,
                "error": "Title is required"
            }), 400
        
        task = tasks_repo.create_task(
            title=title,
            task_list_id=task_list_id,
            notes=data.get('notes'),
            due=data.get('due'),
            **{k: v for k, v in data.items() if k not in ['title', 'notes', 'due']}
        )
        
        return jsonify({
            "success": True,
            "task": task
        }), 201
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/tasks/lists/<task_list_id>/tasks/<task_id>', methods=['PUT'])
def update_task(task_list_id: str, task_id: str):
    """
    Update Task
    ---
    tags:
      - Tasks
    summary: Update an existing task
    description: Updates an existing task in the specified task list
    parameters:
      - name: task_list_id
        in: path
        type: string
        required: true
        description: Task list identifier
        example: "@default"
      - name: task_id
        in: path
        type: string
        required: true
        description: The ID of the task to update
        example: "task123"
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: New title of the task
              example: "Updated task title"
            notes:
              type: string
              description: New notes/description for the task
              example: "Updated notes"
            due:
              type: string
              description: New due date in RFC3339 format
              example: "2024-12-31T23:59:59Z"
            status:
              type: string
              description: Task status ("needsAction" or "completed")
              example: "completed"
    responses:
      200:
        description: Successfully updated task
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            task:
              type: object
              properties:
                id:
                  type: string
                  example: "task123"
                title:
                  type: string
                  example: "Updated task title"
      404:
        description: Task not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to update task: ..."
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        task = tasks_repo.update_task(
            task_id=task_id,
            task_list_id=task_list_id,
            title=data.get('title'),
            notes=data.get('notes'),
            due=data.get('due'),
            status=data.get('status'),
            **{k: v for k, v in data.items() if k not in ['title', 'notes', 'due', 'status']}
        )
        
        return jsonify({
            "success": True,
            "task": task
        }), 200
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to update task: {str(e)}"
        }), 404 if e.resp.status == 404 else 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/tasks/lists/<task_list_id>/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_list_id: str, task_id: str):
    """
    Delete Task
    ---
    tags:
      - Tasks
    summary: Delete a task
    description: Deletes a task from the specified task list
    parameters:
      - name: task_list_id
        in: path
        type: string
        required: true
        description: Task list identifier
        example: "@default"
      - name: task_id
        in: path
        type: string
        required: true
        description: The ID of the task to delete
        example: "task123"
    responses:
      200:
        description: Successfully deleted task
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Task deleted successfully"
      404:
        description: Task not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to delete task: ..."
      500:
        description: Server error
    """
    try:
        tasks_repo.delete_task(task_id, task_list_id=task_list_id)
        return jsonify({
            "success": True,
            "message": "Task deleted successfully"
        }), 200
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to delete task: {str(e)}"
        }), 404 if e.resp.status == 404 else 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)

