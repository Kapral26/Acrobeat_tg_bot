from dishka import FromDishka, Provider, Scope, provide

from src.service.MinIO.client import MinIOClientFactory
from src.service.MinIO.service import MinIOService


class MinIOProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_minio(self) -> MinIOClientFactory:
        return MinIOClientFactory()

    @provide(scope=Scope.REQUEST)
    def get_service(self, minio_client: FromDishka[MinIOClientFactory]) -> MinIOService:
        return MinIOService(minio_client=minio_client)
