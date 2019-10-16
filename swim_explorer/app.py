"""
Copyright 2019 EUROCONTROL
==========================================

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the 
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following 
   disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following 
   disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products 
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==========================================

Editorial note: this license is an instance of the BSD license template as provided by the Open Source Initiative: 
http://opensource.org/licenses/BSD-3-Clause

Details on EUROCONTROL: http://www.eurocontrol.int
"""
import os
from functools import partial

from flask import Flask
from flask_socketio import SocketIO
from swim_pubsub.subscriber import SubApp

from swim_explorer.web_app.views import explorer_blueprint
from swim_explorer.socketio_handlers import on_subscribe, on_unsubscribe, on_connect, on_disconnect, on_pause, on_resume

__author__ = "EUROCONTROL (SWIM)"


def _get_config_path():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, 'config.yml')


# the subscriber app and the subscriber that receives data from the broker and interacts with subscription manager
sub_app = SubApp.create_from_config(_get_config_path())
# start the subscriber app in the background
sub_app.run(threaded=True)
subscriber = sub_app.register_subscriber(username=sub_app.config['SWIM_EXPLORER_SM_USER'],
                                         password=sub_app.config['SWIM_EXPLORER_SM_PASS'])


# the web app that renders the frontend
flask_app = Flask(__name__)
flask_app.register_blueprint(explorer_blueprint)

# the SocketIO that sits in between the frontend and backend and redirects the data coming from the broker to the
# frontend via socket.io
sio = SocketIO(flask_app)
sio.on_event('subscribe', partial(on_subscribe, sio=sio, subscriber=subscriber))
sio.on_event('unsubscribe', partial(on_unsubscribe, subscriber=subscriber))
sio.on_event('pause', partial(on_pause, subscriber=subscriber))
sio.on_event("resume", partial(on_resume, subscriber=subscriber))
sio.on_event('connect', partial(on_connect, sio=sio, subscriber=subscriber))
sio.on_event('disconnect', partial(on_disconnect, subscriber=subscriber))


def main():

    # start the flask_socketio app
    sio.run(flask_app, host="0.0.0.0")


if __name__ == '__main__':
    main()
