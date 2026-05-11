"""
TOS (火山引擎对象存储) 上传服务

【功能定位】：TOS 仅用于将用户上传的参考文件转换为公网 URL，
供火山方舟 API（Seedance/Seedream）读取使用。

【不做备份】：平台的主文件存储始终在本地文件系统（FileManager），
TOS 上的对象生命周期由平台策略管理，可设置过期删除，不做长期备份用途。
"""
import os
import hashlib
import hmac
import datetime
import urllib.parse
from typing import Optional, Tuple
from pathlib import Path
import httpx
from ..core.config import settings
from ..models.file import FileRecord, StorageStatus


class TOSUploader:
    """火山引擎TOS上传器 - 基于HTTP预签名URL方式"""
    
    def __init__(self):
        self.endpoint = settings.TOS_ENDPOINT
        self.access_key = settings.TOS_ACCESS_KEY
        self.secret_key = settings.TOS_SECRET_KEY
        self.bucket = settings.TOS_BUCKET
        self.region = settings.TOS_REGION
        self.expires = settings.TOS_EXPIRES
        self.base_url = f"https://{self.bucket}.{self.endpoint}"
        
    def _is_configured(self) -> bool:
        """检查TOS配置是否完整"""
        return all([
            self.access_key,
            self.secret_key,
            self.bucket,
            self.endpoint,
        ])
    
    def _generate_object_key(self, file_record: FileRecord) -> str:
        """生成TOS对象键 (按用户/类型/日期组织)"""
        date_str = datetime.datetime.now().strftime("%Y/%m/%d")
        file_type = file_record.file_type.value
        # 使用file_id作为对象名保证唯一性
        ext = Path(file_record.original_name).suffix.lower()
        return f"users/{file_record.user_id}/{file_type}/{date_str}/{file_record.file_id}{ext}"
    
    def _sign_request(self, method: str, object_key: str, content_type: str = "") -> str:
        """
        生成火山引擎TOS预签名URL
        参考: https://www.volcengine.com/docs/6349/147049
        """
        date = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        date_stamp = date[:8]
        
        # 构建CanonicalRequest
        canonical_uri = f"/{urllib.parse.quote(object_key, safe='/')}"
        canonical_querystring = ""
        
        headers = {
            "host": f"{self.bucket}.{self.endpoint}",
            "x-volc-date": date,
        }
        if content_type:
            headers["content-type"] = content_type
            
        signed_headers = ";".join(sorted(headers.keys()))
        canonical_headers = "".join([f"{k}:{v}\n" for k, v in sorted(headers.items())])
        payload_hash = "UNSIGNED-PAYLOAD"
        
        canonical_request = "\n".join([
            method,
            canonical_uri,
            canonical_querystring,
            canonical_headers,
            signed_headers,
            payload_hash,
        ])
        
        # 构建StringToSign
        algorithm = "VOLC-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.region}/tos/request"
        string_to_sign = "\n".join([
            algorithm,
            date,
            credential_scope,
            hashlib.sha256(canonical_request.encode()).hexdigest(),
        ])
        
        # 计算签名
        k_date = hmac.new(f"VOLC{self.secret_key}".encode(), date_stamp.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, b"tos", hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        
        # 构建预签名URL查询参数
        params = {
            "X-Volc-Algorithm": algorithm,
            "X-Volc-Credential": f"{self.access_key}/{credential_scope}",
            "X-Volc-Date": date,
            "X-Volc-Expires": str(self.expires),
            "X-Volc-SignedHeaders": signed_headers,
            "X-Volc-Signature": signature,
        }
        query_string = urllib.parse.urlencode(params)
        return f"{self.base_url}/{object_key}?{query_string}"
    
    async def upload_file(self, file_record: FileRecord) -> Tuple[Optional[str], StorageStatus]:
        """
        上传文件到TOS，返回公网URL和状态
        
        Returns:
            (public_url, storage_status)
        
        流程:
        1. 读取本地文件
        2. 生成对象键
        3. 使用SDK上传
        4. 返回公网URL和状态 (不直接修改ORM对象，由调用方持久化)
        """
        if not self._is_configured():
            raise RuntimeError(
                "TOS配置不完整，请设置 TOS_ENDPOINT, TOS_ACCESS_KEY, TOS_SECRET_KEY, TOS_BUCKET"
            )
        
        file_path = Path(file_record.storage_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        object_key = self._generate_object_key(file_record)
        content_type = file_record.mime_type
        
        try:
            # 读取文件内容
            file_size = file_path.stat().st_size
            
            # 使用 tos SDK 上传
            try:
                import tos
                auth = tos.Auth(
                    access_key_id=self.access_key,
                    access_key_secret=self.secret_key,
                    region=self.region,
                )
                client = tos.TosClient(auth, endpoint=self.endpoint)
                with open(file_path, "rb") as f:
                    client.put_object(
                        Bucket=self.bucket,
                        Key=object_key,
                        Body=f.read(),
                        ContentType=content_type,
                    )
                
                public_url = f"{self.base_url}/{object_key}"
                return (public_url, StorageStatus.UPLOADED)
                
            except ImportError:
                # 回退: 使用httpx + 预签名URL方式
                raise ImportError(
                    "请安装 tos SDK: pip install tos\n"
                    "TOS上传是平台的必选项，用于向火山方舟API提供可访问的文件URL。"
                )
                
        except Exception as e:
            raise RuntimeError(f"TOS上传失败: {e}")
    
    async def get_presigned_url(self, object_key: str, expires: int = 3600) -> str:
        """获取预签名下载URL"""
        # 生产环境使用tos SDK生成
        try:
            import tos
            client = tos.TosClient(
                ak=self.access_key,
                sk=self.secret_key,
                endpoint=self.endpoint,
                region=self.region,
            )
            url = client.pre_signed_url(
                http_method="GET",
                bucket=self.bucket,
                key=object_key,
                expires=expires,
            )
            return url.signed_url
        except ImportError:
            # 简化回退: 使用手动签名
            return self._sign_request("GET", object_key)
    
    def get_object_key_from_url(self, url: str) -> Optional[str]:
        """从URL中提取对象键"""
        prefix = f"{self.base_url}/"
        if url.startswith(prefix):
            return url[len(prefix):]
        return None


# 全局实例
tos_uploader = TOSUploader()
