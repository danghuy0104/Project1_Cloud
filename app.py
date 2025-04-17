from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
CORS(app)

# Kết nối với DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Thay đổi region nếu cần
table = dynamodb.Table('Tasks')

# Lấy tất cả tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    status = request.args.get('status')
    priority = request.args.get('priority')
    search = request.args.get('search')

    try:
        response = table.scan()
        filtered_tasks = response['Items']

        if status:
            filtered_tasks = [task for task in filtered_tasks if task['status'] == status]
        if priority:
            filtered_tasks = [task for task in filtered_tasks if task['priority'] == priority]
        if search:
            search = search.lower()
            filtered_tasks = [
                task for task in filtered_tasks
                if search in task['title'].lower() or search in task['description'].lower()
            ]

        return jsonify(filtered_tasks)
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

# Thêm task mới
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.json
    try:
        # Lấy ID lớn nhất hiện tại để tạo ID mới
        response = table.scan()
        tasks = response['Items']
        next_id = max([task['id'] for task in tasks], default=0) + 1

        new_task = {
            "id": next_id,
            "title": data["title"],
            "description": data.get("description", ""),
            "start_date": data.get("start_date", ""),
            "due_date": data.get("due_date", ""),
            "priority": data.get("priority", "low"),
            "status": data.get("status", "incomplete")
        }
        table.put_item(Item=new_task)
        return jsonify(new_task), 201
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

# Cập nhật task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    try:
        response = table.get_item(Key={'id': task_id})
        if 'Item' not in response:
            return jsonify({"error": "Task not found"}), 404

        task = response['Item']
        task["title"] = data.get("title", task["title"])
        task["description"] = data.get("description", task["description"])
        task["start_date"] = data.get("start_date", task["start_date"])
        task["due_date"] = data.get("due_date", task["due_date"])
        task["priority"] = data.get("priority", task["priority"])
        task["status"] = data.get("status", task["status"])  # Thêm status vào update

        table.put_item(Item=task)
        return jsonify(task)
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

# Cập nhật trạng thái nhanh
@app.route('/tasks/<int:task_id>/status', methods=['PATCH'])
def update_task_status(task_id):
    data = request.json
    try:
        response = table.get_item(Key={'id': task_id})
        if 'Item' not in response:
            return jsonify({"error": "Task not found"}), 404

        task = response['Item']
        task["status"] = data.get("status", task["status"])
        table.put_item(Item=task)
        return jsonify(task)
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

# Xóa task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        response = table.get_item(Key={'id': task_id})
        if 'Item' not in response:
            return jsonify({"error": "Task not found"}), 404

        table.delete_item(Key={'id': task_id})
        return jsonify({"message": "Task deleted"}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)