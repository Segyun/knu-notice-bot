from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


class AzureBlob:
    def __init__(self, account_url: str, container_name: str):
        self.account_url = account_url
        self.credential = DefaultAzureCredential()

        self.blob_service_client = BlobServiceClient(
            self.account_url, credential=self.credential
        )
        self.container_name = container_name

    def upload_blob(self, file_name: str, content: str):
        container_client = self.blob_service_client.get_container_client(
            container=self.container_name
        )
        container_client.upload_blob(name=file_name, data=content, overwrite=True)

    def download_blob_to_str(self, file_name: str) -> str:
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=file_name
        )
        download_stream = blob_client.download_blob()
        return download_stream.readall().decode("utf-8")
