#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time : 2021/10/11
# @Author : jiang.hu
# @File : app.py
from flask import Flask
from flasgger import Swagger

from main import blueprint

app = Flask(__name__)
Swagger(app)

app.register_blueprint(blueprint)

if __name__ == '__main__':
    env_port = 8888
    app.run(host='0.0.0.0', port=env_port, debug=False)
