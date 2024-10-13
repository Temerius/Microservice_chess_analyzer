from flask import Flask, request, jsonify
from sql import init_db, register_user, login_user, change_username, change_password, change_figure_style, \
    change_board_style, change_bg_style

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    msg, styles = register_user(username, password)
    return jsonify({'msg': msg, 'styles': styles})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    msg, styles = login_user(username, password)
    return jsonify({'msg': msg, 'styles': styles})


@app.route('/change_name', methods=['POST'])
def chg_name():
    data = request.get_json()
    new_username = data.get('new_name')
    old_username = data.get('old_name')
    success, msg = change_username(new_username, old_username)
    return jsonify({'success': success, 'msg': msg})


@app.route('/change_pwd', methods=['POST'])
def chg_pwd():
    data = request.get_json()
    new_password = data.get('new_pwd')
    username = data.get('name')
    success, msg = change_password(new_password, username)
    return jsonify({'success': success, 'msg': msg})


@app.route('/change_figure_style', methods=['POST'])
def chg_figure_style():
    data = request.get_json()
    new_style = data.get('new_style')
    username = data.get('name')
    success, msg = change_figure_style(new_style, username)
    return jsonify({'success': success, 'msg': msg})


@app.route('/change_board_style', methods=['POST'])
def chg_board_style():
    data = request.get_json()
    new_style = data.get('new_style')
    username = data.get('name')
    success, msg = change_board_style(new_style, username)
    return jsonify({'success': success, 'msg': msg})


@app.route('/change_bg_style', methods=['POST'])
def chg_bg_style():
    data = request.get_json()
    new_style = data.get('new_style')
    username = data.get('name')
    success, msg = change_bg_style(new_style, username)
    return jsonify({'success': success, 'msg': msg})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=54321)
