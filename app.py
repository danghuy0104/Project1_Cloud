from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

tasks = []  # Lưu danh sách tasks
next_id = 1

# Lấy tất cả tasks (hỗ trợ lọc theo status, priority và tìm kiếm)
@app.route('/tasks', methods=['GET'])
def get_tasks():
    status = request.args.get('status')  # Lọc theo trạng thái
    priority = request.args.get('priority')  # Lọc theo priority
    search = request.args.get('search')  # Tìm kiếm theo từ khóa

    filtered_tasks = tasks

    # Lọc theo trạng thái
    if status:
        filtered_tasks = [task for task in filtered_tasks if task['status'] == status]

    # Lọc theo priority
    if priority:
        filtered_tasks = [task for task in filtered_tasks if task['priority'] == priority]

    # Tìm kiếm theo từ khóa (trong title hoặc description)
    if search:
        search = search.lower()
        filtered_tasks = [
            task for task in filtered_tasks
            if search in task['title'].lower() or search in task['description'].lower()
        ]

    return jsonify(filtered_tasks)

# Thêm task mới
@app.route('/tasks', methods=['POST'])
def add_task():
    global next_id
    data = request.json
    new_task = {
        "id": next_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "start_date": data.get("start_date", ""),
        "due_date": data.get("due_date", ""),
        "priority": data.get("priority", "low"),
        "status": data.get("status", "incomplete")
    }
    tasks.append(new_task)
    next_id += 1
    return jsonify(new_task), 201

# Cập nhật task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = data.get("title", task["title"])
            task["description"] = data.get("description", task["description"])
            task["start_date"] = data.get("start_date", task["start_date"])
            task["due_date"] = data.get("due_date", task["due_date"])
            task["priority"] = data.get("priority", task["priority"])
            task["status"] = data.get("status", task["status"])
            return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

# Cập nhật trạng thái nhanh
@app.route('/tasks/<int:task_id>/status', methods=['PATCH'])
def update_task_status(task_id):
    data = request.json
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = data.get("status", task["status"])
            return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

# Xóa task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return jsonify({"message": "Task deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)