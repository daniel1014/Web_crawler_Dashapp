import azure.functions as func
from src.server import app

def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.WsgiMiddleware(app).handle(req)
