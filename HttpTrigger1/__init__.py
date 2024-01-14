#AZURE FUNCTION to paste in VS CODE , Include __init__.py , deploy it in your Azure account and ready!
#VARIABLES that you need to change :  "connection_string" , "container_name" and line 38 -> "if filename.endswith(".F18")"

import azure.functions as func
import io
import zipfile
from azure.storage.blob import BlobServiceClient, BlobClient

def main(req: func.HttpRequest) -> func.HttpResponse:

     # Put the account key and container of the Blob Storage in "connection_string" and "container_name" so the script can make the connection:
    
    connection_string = "DefaultEndpointsProtocol=https;AccountName=upwrokblobstorage;AccountKey=e2WrALZwO7uYf5iIRNt+LEbJSMHAKqQ8YtjHt4FgqsP6MMnljsUqgHvHtKQujCfG4INiRfFj7PM3+AStqcKcow==;EndpointSuffix=core.windows.net"

    container_name = "executable"

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()

    for blob in blob_list:
        if blob.name.endswith('.exe'):
            blob_name = blob.name
            blob_client = blob_service_client.get_blob_client(container_name, blob_name)
            print(f"\nDownloading {blob_name}...")

            # download blob to in-memory byte stream
            blob_data = blob_client.download_blob().readall()
            blob_stream = io.BytesIO(blob_data)

            # NOTE: Depending on the nature of the .exe files and their execution requirements, running .exe file directly from memory might not be possible

            # upload the extracted files to Azure Blob Storage
            with zipfile.ZipFile(blob_stream, 'r') as zip_ref:
                for filename in zip_ref.namelist():

                    # In my case the file within the executable ends with .F18 , so put the ending for your case
                    if filename.endswith(".F18"):
                        file_data = zip_ref.read(filename)
                        file_stream = io.BytesIO(file_data)
                        blob_client = blob_service_client.get_blob_client(container_name, filename)
                        blob_client.upload_blob(file_stream, overwrite=True)
            print(f"Files extracted from {blob_name} uploaded successfully.")

    return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
