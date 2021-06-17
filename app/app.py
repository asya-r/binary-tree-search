from flask import Flask, render_template, make_response, request, redirect, url_for
import uuid
from db import create_new_token, Token, initialize_db
from datetime import datetime, timedelta
import time
import hashlib

app = Flask(__name__)


FLAG = "SPYCTF{}"


@app.route('/', methods=['GET'])
def hello():
    return redirect(url_for('start'))


@app.route('/start', methods=['GET'])
def start():
    initialize_db()
    return render_template('start.html', message=request.args.get('message'))


@app.route('/start', methods=['POST'])
def set_cookie():
    c = str(uuid.uuid4())
    create_new_token(c)
    token = Token.get(Token.user_cookie == c)
    next_chl = children_for(token.secret, "start")

    resp = make_response(render_template('find_flag.html', chl=next_chl, path=request.path))
    resp.set_cookie('token', c, max_age=60)

    return resp


@app.route('/start/<path:many_routes>')
def find_flag(many_routes):
    time.sleep(1)
    cookie = request.cookies.get('token')
    if not cookie:
        return redirect(url_for('start', message="You`re late! (no cookie)"), code=301)

    token = Token.get_or_none(Token.user_cookie == cookie)
    if token is None:
        return redirect(url_for('start', message="You`re late! (no token)"), code=301)

    app.logger.warning('%s token time for cookie %s', (datetime.now() - token.timestamp), token.user_cookie)
    if (datetime.now() - token.timestamp) > timedelta(seconds=60):
        token.delete_instance()
        return redirect(url_for('start', message="You`re late! (token is outdated)"), code=301)

    secret = token.secret
    cur_path = ""
    routes = many_routes.split('/')
    for i in range(len(routes)):
        if i == 0:
            chl = children_for(secret, "start")
        else:
            chl = children_for(secret, routes[i-1])
        if routes[i] not in chl:
            return redirect(url_for('start', message="Invalid route"), code=301)
        ind = chl.index(routes[i])
        cur_path += str(ind)
    if cur_path == token.flag_path:
        resp = make_response(render_template('find_flag.html', flag=FLAG, path=request.path))
        token.delete_instance()
    else:
        next_chl = children_for(secret, routes[-1])
        resp = make_response(render_template('find_flag.html', chl=next_chl, path=request.path))
    return resp


def children_for(secret: bytes, path: str) -> [bytes]:
    prep_hsh = hashlib.sha256(bytes(secret) + bytes(path, encoding='utf8')).digest()
    hsh = hashlib.sha256(bytes(secret) + prep_hsh)
    fst = hsh.digest()[0:8].hex()
    snd = hsh.digest()[16:24].hex()
    return [fst, snd]


if __name__ == '__main__':
    try:
        initialize_db()
    except:
        raise RuntimeError("Couldn't initialize db")
    else:
        app.run(host='0.0.0.0')

#TODO: проверить, что нет инъекции в request.path