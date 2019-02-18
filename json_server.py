from werkzeug.wrappers import Request, Response 
from jsonrpc import JSONRPCResponseManager, dispatcher
from process_manager import ProcessManager

@Request.application
def application(request: Request):

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher
    )

    return Response(response.json, mimetype='application/json')

if __name__ == '__main__':
    from werkzeug.serving import run_simple

    process_manager = ProcessManager('processes.json')

    dispatcher['list_processes'] = process_manager.list_processes
    dispatcher['get_metrics'] = process_manager.get_metrics
    dispatcher['start_process'] = process_manager.start_process
    dispatcher['kill'] = process_manager.kill 
    dispatcher['terminate'] = process_manager.terminate
    dispatcher['restart_process'] = process_manager.restart_process


    run_simple('localhost', 8000, application)