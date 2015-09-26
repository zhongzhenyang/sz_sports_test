import os
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.contrib.fixers import ProxyFix
from sz_webapp import frontend


frontend_app = frontend.create_app()

application = ProxyFix(DispatcherMiddleware(None,
                                            {
                                                '/app': frontend_app,
                                            }))

if __name__ == "__main__":
    run_simple("0.0.0.0", 7100, application, use_debugger=True)
