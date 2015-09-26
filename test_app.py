# coding:utf-8



if __name__ == '__main__':
    from werkzeug.wsgi import DispatcherMiddleware
    from werkzeug.serving import run_simple
    from sz_webapp.frontend import create_app
    application = create_app()

    # application = DispatcherMiddleware(None, {
    #     '/backend': create_app(),
    # })
    run_simple("0.0.0.0", 5000, application, use_debugger=True, use_reloader=False)
