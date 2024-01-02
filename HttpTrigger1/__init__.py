import logging
import azure.functions as func
from ..src.server import app  # Adjust the import path as needed

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Azure Function processed a request for the Dash app.')

    # You can add any logic here to handle the request, if needed.

    # Run the Dash app
    app.run_server(debug=True, port=8000)

    # Since the app.run_server() is blocking, the code below might not be reached.
    # You may need to handle your response logic within your Dash app callbacks.

    return func.HttpResponse(
        "Dash app is running. This HTTP triggered function executed successfully.",
        status_code=200
    )
