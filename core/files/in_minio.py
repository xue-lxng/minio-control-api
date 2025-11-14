from contextlib import AsyncExitStack
from typing import Optional, BinaryIO, AsyncIterator, Dict, Any, List

from aiobotocore.session import AioSession
from botocore.exceptions import ClientError


class AsyncMinIOClient:
    """Асинхронный клиент для работы с MinIO с поддержкой множественных бакетов"""

    def __init__(
            self,
            endpoint_url: str,
            access_key: str,
            secret_key: str,
            bucket_name: Optional[str] = None,
            region: str = "us-east-1",
            secure: bool = True
    ):
        """
        Инициализация клиента MinIO

        Args:
            endpoint_url: URL MinIO сервера (например, 'http://localhost:9000')
            access_key: Access key для подключения
            secret_key: Secret key для подключения
            bucket_name: Имя бакета по умолчанию (опционально)
            region: Регион (для MinIO обычно 'us-east-1')
            secure: Использовать ли HTTPS
        """
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.region = region
        self.secure = secure

        self._session: Optional[AioSession] = None
        self._client = None
        self._exit_stack: Optional[AsyncExitStack] = None

    async def __aenter__(self):
        """Вход в контекстный менеджер"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера"""
        await self.close()

    async def connect(self):
        """Создание подключения к MinIO"""
        self._session = AioSession()
        self._exit_stack = AsyncExitStack()

        self._client = await self._exit_stack.enter_async_context(
            self._session.create_client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                use_ssl=self.secure
            )
        )

    async def close(self):
        """Закрытие подключения"""
        if self._exit_stack:
            await self._exit_stack.__aexit__(None, None, None)
            self._exit_stack = None
        self._client = None
        self._session = None

    def _get_bucket(self, bucket: Optional[str] = None) -> str:
        """
        Получение имени бакета

        Args:
            bucket: Имя бакета (если None, используется дефолтный)

        Returns:
            Имя бакета

        Raises:
            ValueError: Если бакет не указан и нет дефолтного
        """
        result = bucket or self.bucket_name
        if not result:
            raise ValueError("Bucket name must be specified either in method call or during initialization")
        return result

    # === Методы для управления бакетами ===

    async def create_bucket(self, bucket: str) -> Dict[str, Any]:
        """
        Создание нового бакета

        Args:
            bucket: Имя бакета

        Returns:
            Ответ от MinIO
        """
        response = await self._client.create_bucket(Bucket=bucket)
        return response

    async def delete_bucket(self, bucket: str) -> Dict[str, Any]:
        """
        Удаление бакета (должен быть пустым)

        Args:
            bucket: Имя бакета

        Returns:
            Ответ от MinIO
        """
        response = await self._client.delete_bucket(Bucket=bucket)
        return response

    async def bucket_exists(self, bucket: str) -> bool:
        """
        Проверка существования бакета

        Args:
            bucket: Имя бакета

        Returns:
            True если бакет существует, False в противном случае
        """
        try:
            await self._client.head_bucket(Bucket=bucket)
            return True
        except ClientError:
            return False

    async def list_buckets(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех бакетов

        Returns:
            Список бакетов
        """
        response = await self._client.list_buckets()
        return response.get('Buckets', [])

    async def ensure_bucket_exists(self, bucket: str):
        """
        Проверка существования бакета и его создание при необходимости

        Args:
            bucket: Имя бакета
        """
        if not await self.bucket_exists(bucket):
            await self.create_bucket(bucket)

    # === Методы для работы с файлами ===

    async def upload_file(
            self,
            file_data: bytes,
            object_name: str,
            bucket: Optional[str] = None,
            content_type: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Загрузка файла в MinIO

        Args:
            file_data: Данные файла в виде bytes
            object_name: Имя объекта в MinIO
            bucket: Имя бакета (если None, используется дефолтный)
            content_type: MIME тип файла
            metadata: Дополнительные метаданные

        Returns:
            Ответ от MinIO
        """
        bucket = self._get_bucket(bucket)
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        if metadata:
            extra_args['Metadata'] = metadata

        response = await self._client.put_object(
            Bucket=bucket,
            Key=object_name,
            Body=file_data,
            **extra_args
        )
        return response

    async def upload_fileobj(
            self,
            file_obj: BinaryIO,
            object_name: str,
            bucket: Optional[str] = None,
            content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Загрузка файлового объекта в MinIO

        Args:
            file_obj: Файловый объект
            object_name: Имя объекта в MinIO
            bucket: Имя бакета (если None, используется дефолтный)
            content_type: MIME тип файла

        Returns:
            Ответ от MinIO
        """
        bucket = self._get_bucket(bucket)
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type

        response = await self._client.put_object(
            Bucket=bucket,
            Key=object_name,
            Body=file_obj,
            **extra_args
        )
        return response

    async def download_file(
            self,
            object_name: str,
            bucket: Optional[str] = None
    ) -> bytes:
        """
        Скачивание файла из MinIO

        Args:
            object_name: Имя объекта в MinIO
            bucket: Имя бакета (если None, используется дефолтный)

        Returns:
            Содержимое файла в виде bytes
        """
        bucket = self._get_bucket(bucket)
        response = await self._client.get_object(
            Bucket=bucket,
            Key=object_name
        )

        async with response['Body'] as stream:
            return await stream.read()

    async def download_fileobj(
            self,
            object_name: str,
            file_obj: BinaryIO,
            bucket: Optional[str] = None
    ):
        """
        Скачивание файла из MinIO в файловый объект

        Args:
            object_name: Имя объекта в MinIO
            file_obj: Файловый объект для записи
            bucket: Имя бакета (если None, используется дефолтный)
        """
        bucket = self._get_bucket(bucket)
        response = await self._client.get_object(
            Bucket=bucket,
            Key=object_name
        )

        async with response['Body'] as stream:
            while True:
                chunk = await stream.read(8192)
                if not chunk:
                    break
                file_obj.write(chunk)

    async def delete_file(
            self,
            object_name: str,
            bucket: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Удаление файла из MinIO

        Args:
            object_name: Имя объекта в MinIO
            bucket: Имя бакета (если None, используется дефолтный)

        Returns:
            Ответ от MinIO
        """
        bucket = self._get_bucket(bucket)
        response = await self._client.delete_object(
            Bucket=bucket,
            Key=object_name
        )
        return response

    async def delete_files(
            self,
            object_names: List[str],
            bucket: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Массовое удаление файлов из MinIO

        Args:
            object_names: Список имен объектов
            bucket: Имя бакета (если None, используется дефолтный)

        Returns:
            Ответ от MinIO
        """
        bucket = self._get_bucket(bucket)
        objects = [{'Key': name} for name in object_names]
        response = await self._client.delete_objects(
            Bucket=bucket,
            Delete={'Objects': objects}
        )
        return response

    async def file_exists(
            self,
            object_name: str,
            bucket: Optional[str] = None
    ) -> bool:
        """
        Проверка существования файла

        Args:
            object_name: Имя объекта в MinIO
            bucket: Имя бакета (если None, используется дефолтный)

        Returns:
            True если файл существует, False в противном случае
        """
        bucket = self._get_bucket(bucket)
        try:
            await self._client.head_object(
                Bucket=bucket,
                Key=object_name
            )
            return True
        except ClientError:
            return False

    async def get_file_info(
            self,
            object_name: str,
            bucket: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Получение информации о файле

        Args:
            object_name: Имя объекта в MinIO
            bucket: Имя бакета (если None, используется дефолтный)

        Returns:
            Метаданные файла
        """
        bucket = self._get_bucket(bucket)
        response = await self._client.head_object(
            Bucket=bucket,
            Key=object_name
        )
        return response

    async def list_files(
            self,
            prefix: str = "",
            bucket: Optional[str] = None,
            max_keys: int = 1000
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Получение списка файлов с использованием пагинации

        Args:
            prefix: Префикс для фильтрации объектов
            bucket: Имя бакета (если None, используется дефолтный)
            max_keys: Максимальное количество ключей на страницу

        Yields:
            Информация о каждом объекте
        """
        bucket = self._get_bucket(bucket)
        paginator = self._client.get_paginator('list_objects_v2')

        async for result in paginator.paginate(
                Bucket=bucket,
                Prefix=prefix,
                PaginationConfig={'PageSize': max_keys}
        ):
            for obj in result.get('Contents', []):
                yield obj

    async def get_presigned_url(
            self,
            object_name: str,
            bucket: Optional[str] = None,
            expiration: int = 3600,
            method: str = 'get_object'
    ) -> str:
        """
        Генерация presigned URL для доступа к файлу

        Args:
            object_name: Имя объекта в MinIO
            bucket: Имя бакета (если None, используется дефолтный)
            expiration: Время жизни URL в секундах (по умолчанию 1 час)
            method: Метод доступа ('get_object' или 'put_object')

        Returns:
            Presigned URL
        """
        bucket = self._get_bucket(bucket)
        url = await self._client.generate_presigned_url(
            method,
            Params={
                'Bucket': bucket,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
        return url

    async def copy_file(
            self,
            source_object: str,
            dest_object: str,
            source_bucket: Optional[str] = None,
            dest_bucket: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Копирование файла внутри MinIO (в том числе между бакетами)

        Args:
            source_object: Имя исходного объекта
            dest_object: Имя целевого объекта
            source_bucket: Исходный бакет (если None, используется дефолтный)
            dest_bucket: Целевой бакет (если None, используется дефолтный)

        Returns:
            Ответ от MinIO
        """
        source_bucket = self._get_bucket(source_bucket)
        dest_bucket = self._get_bucket(dest_bucket)

        copy_source = {
            'Bucket': source_bucket,
            'Key': source_object
        }

        response = await self._client.copy_object(
            CopySource=copy_source,
            Bucket=dest_bucket,
            Key=dest_object
        )
        return response

    async def move_file(
            self,
            source_object: str,
            dest_object: str,
            source_bucket: Optional[str] = None,
            dest_bucket: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Перемещение файла (копирование + удаление исходного)

        Args:
            source_object: Имя исходного объекта
            dest_object: Имя целевого объекта
            source_bucket: Исходный бакет (если None, используется дефолтный)
            dest_bucket: Целевой бакет (если None, используется дефолтный)

        Returns:
            Ответ от MinIO
        """
        # Копируем файл
        response = await self.copy_file(
            source_object, dest_object,
            source_bucket, dest_bucket
        )

        # Удаляем исходный
        await self.delete_file(source_object, source_bucket)

        return response
