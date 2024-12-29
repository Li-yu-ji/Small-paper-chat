from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)

# 存储在线用户信息
users = {}

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='online')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

# 消息模型
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    receiver = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_recalled = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    users[request.sid] = {'username': None, 'status': 'offline'}
    emit('user_list', {'users': [{'username': user['username'], 'status': user['status']} 
                                for user in users.values() if user['username']]})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    if request.sid in users:
        username = users[request.sid].get('username')
        if username:
            print(f"User {username} disconnected")
            user = User.query.filter_by(username=username).first()
            if user:
                user.status = 'offline'
                user.last_seen = datetime.utcnow()
                db.session.commit()
            
            emit('user_left', {'username': username}, broadcast=True)
        
        del users[request.sid]
        emit('user_list', {'users': [{'username': user['username'], 'status': user['status']} 
                                    for user in users.values() if user['username']]}, broadcast=True)

@socketio.on('register')
def handle_register(data):
    print(f"Register attempt with data: {data}")
    username = data.get('username', '').strip()
    if not username:
        print("Username is empty")
        emit('register_response', {'success': False, 'message': '用户名不能为空'})
        return
    
    # 检查用户名是否已经被使用
    for sid, user in users.items():
        if user.get('username') == username:
            print(f"Username {username} is already in use")
            emit('register_response', {'success': False, 'message': '用户名已被使用'})
            return
    
    # 创建或获取用户
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, status='online')
        db.session.add(user)
        db.session.commit()
    else:
        user.status = 'online'
        user.last_seen = datetime.utcnow()
        db.session.commit()
    
    users[request.sid] = {'username': username, 'status': 'online'}
    print(f"User {username} registered successfully")
    
    # 发送注册成功响应
    emit('register_response', {'success': True, 'username': username})
    
    # 广播用户加入消息
    emit('user_joined', {'username': username}, broadcast=True)
    
    # 更新用户列表
    emit('user_list', {'users': [{'username': user['username'], 'status': user['status']} 
                                for user in users.values() if user['username']]}, broadcast=True)
    
    # 加载历史消息
    history = Message.query.filter_by(type='public', is_recalled=False).order_by(Message.timestamp).all()
    messages_history = [{
        'id': msg.id,
        'type': msg.type,
        'sender': msg.sender,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'is_recalled': msg.is_recalled
    } for msg in history]
    emit('load_history', messages_history)

@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")
    
    if request.sid not in users or not users[request.sid].get('username'):
        print("User not found or not registered")
        return
        
    content = data.get('content', '').strip()
    if not content:
        print("Message content is empty")
        return

    message_type = data.get('type', 'public')
    sender = users[request.sid]['username']
    receiver = data.get('receiver')
    
    # 创建消息记录
    message = Message(
        type=message_type,
        sender=sender,
        receiver=receiver,
        content=content,
        timestamp=datetime.utcnow(),
        is_recalled=False
    )
    db.session.add(message)
    db.session.commit()
    
    # 准备发送的消息数据
    message_data = {
        'id': message.id,
        'type': message_type,
        'sender': sender,
        'content': content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'is_recalled': False
    }
    
    print(f"Sending message data: {message_data}")
    
    if message_type == 'public':
        # 公共消息广播给所有用户
        emit('message', message_data, broadcast=True)
        
        # 处理@提醒
        mentions = re.findall(r'@(\w+)', content)
        for mentioned_user in mentions:
            for sid, user in users.items():
                if user.get('username') == mentioned_user:
                    emit('mentioned', {
                        'from': sender,
                        'content': content
                    }, room=sid)
    else:
        # 私聊消息只发送给发送者和接收者
        message_data['receiver'] = receiver
        for sid, user in users.items():
            if user.get('username') in [sender, receiver]:
                emit('private_message', message_data, room=sid)

@socketio.on('update_status')
def handle_status_update(data):
    print(f"Status update request: {data}")
    if request.sid in users and users[request.sid]['username']:
        status = data.get('status', 'online')
        username = users[request.sid]['username']
        
        # 更新内存中的状态
        users[request.sid]['status'] = status
        
        # 更新数据库中的状态
        user = User.query.filter_by(username=username).first()
        if user:
            user.status = status
            user.last_seen = datetime.utcnow()
            db.session.commit()
        
        # 广播更新后的用户列表
        emit('user_list', {'users': [{'username': user['username'], 'status': user['status']} 
                                    for user in users.values() if user['username']]}, broadcast=True)

@socketio.on('delete_message')
def handle_delete_message(data):
    print(f"Deleting message: {data}")
    message_id = data.get('message_id')
    if message_id and request.sid in users:
        username = users[request.sid]['username']
        message = Message.query.get(message_id)
        if message and message.sender == username:
            print(f"Deleting message {message_id} from {username}")
            db.session.delete(message)
            db.session.commit()
            emit('message_deleted', {'message_id': message_id}, broadcast=True)
        else:
            print(f"Message not found or not authorized: {message_id}")

@socketio.on('recall_message')
def handle_recall_message(data):
    print(f"Recalling message: {data}")
    message_id = data.get('message_id')
    if message_id and request.sid in users:
        username = users[request.sid]['username']
        message = Message.query.get(message_id)
        if message and message.sender == username:
            if (datetime.utcnow() - message.timestamp).total_seconds() <= 120:
                print(f"Recalling message {message_id} from {username}")
                message.is_recalled = True
                message.content = "此消息已被撤回"
                db.session.commit()
                emit('message_recalled', {
                    'message_id': message_id,
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }, broadcast=True)
            else:
                emit('recall_error', {'message': '只能撤回2分钟内的消息'})
        else:
            print(f"Message not found or not authorized: {message_id}")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=4545)
