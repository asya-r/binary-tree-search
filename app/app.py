from flask import Flask, render_template, make_response, request, redirect, url_for
import uuid
from db import create_new_token, Token, initialize_db
from datetime import datetime, timedelta
import time
import hashlib
import config

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return redirect(url_for('start'))


@app.route('/start', methods=['GET'])
def start(message=None, **kwargs):
    initialize_db()
    if 'delay' in kwargs:
        time.sleep(kwargs['delay'])
    return render_template('start.html')


@app.route('/start', methods=['POST'])
def set_cookie():
    c = str(uuid.uuid4())
    create_new_token(c)
    token = Token.get(Token.user_cookie == c)
    next_chl = children_for(token.secret, "start")

    print(request.path)
    resp = make_response(render_template('find_flag.html', chl=next_chl, path=request.path))
    resp.set_cookie('token', c, max_age=60)

    return resp


@app.route('/start/<path:many_routes>')
def find_flag(many_routes):
    time.sleep(1)
    cookie = request.cookies.get('token')
    if not cookie:
        return redirect(url_for('start'), code=403)

    token = Token.get(Token.user_cookie == cookie)
    if not token:
        return redirect(url_for('start'), code=403)

    dt_token = datetime.fromtimestamp(token.timestamp)
    if (datetime.now() - dt_token) > timedelta(seconds=60):
        token.delete_instance()
        return redirect(url_for('start'), code=403)

    secret = token.secret
    cur_path = ""
    routes = many_routes.split('/')
    for i in range(len(routes)-1):
        if i == 0:
            chl = children_for(secret, "start")
        else:
            chl = children_for(secret, routes[i-1])
        if routes[i] not in chl:
            return redirect(url_for('start'), code=403)
        ind = chl.index(routes[i])
        cur_path += str(ind)
    if cur_path == token.flag_path:
        start(message="CTF{}")
    else:
        next_chl = children_for(secret, routes[-1])
    print(request.path)
    resp = make_response(render_template('find_flag.html', chl=next_chl, path=request.path))
    return resp


def children_for(secret: bytes, path: str) -> [bytes]:
    prep_hsh = hashlib.sha256(bytes(secret) + bytes(path, encoding='utf8')).digest()
    hsh = hashlib.sha256(bytes(secret) + prep_hsh)
    fst = hsh.digest()[0:16].hex()
    snd = hsh.digest()[16:].hex()
    return [fst, snd]


if __name__ == '__main__':
    try:
        initialize_db()
    except:
        raise RuntimeError("Couldn't initialize db")
    else:
        app.run(host='0.0.0.0')
