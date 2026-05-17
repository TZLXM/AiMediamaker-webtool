"""
模型配置 Pydantic Schema
"""
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ParameterOption(BaseModel):
    name: str
    value: Any
    label: str
    description: Optional[str] = None


class ParameterSchema(BaseModel):
    key: str
    label: str
    type: str  # select, number, boolean, text
    required: bool = False
    default: Optional[Any] = None
    options: Optional[List[ParameterOption]] = None
    min: Optional[Any] = None
    max: Optional[Any] = None
    description: Optional[str] = None


class ApiConfigResponse(BaseModel):
    id: int
    name: str
    platform: str
    api_key: str
    base_url: str
    total_concurrency: int
    is_active: bool
    extra_config: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class ApiConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    platform: str = "volcengine_ark"
    api_key: str = Field(..., min_length=1)
    base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    total_concurrency: int = Field(default=5, ge=1, le=100)
    is_active: bool = True
    extra_config: Optional[dict] = None
    
    @field_validator("api_key")
    @classmethod
    def validate_api_key_ascii(cls, v: str) -> str:
        try:
            v.encode("ascii")
        except UnicodeEncodeError:
            raise ValueError("API Key 只能包含 ASCII 字符，不能包含中文或其他特殊字符")
        return v


class ApiConfigUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=64)
    platform: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    total_concurrency: Optional[int] = Field(default=None, ge=1, le=100)
    is_active: Optional[bool] = None
    extra_config: Optional[dict] = None
    
    @field_validator("api_key")
    @classmethod
    def validate_api_key_ascii(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            v.encode("ascii")
        except UnicodeEncodeError:
            raise ValueError("API Key 只能包含 ASCII 字符，不能包含中文或其他特殊字符")
        return v


class ModelConfigResponse(BaseModel):
    id: int
    name: str
    model_id: str
    mode: str  # image or video
    description: Optional[str]
    concurrency_limit: int
    parameters_schema: List[ParameterSchema]
    supported_input_types: List[str]
    is_active: bool
    sort_order: int
    api_config_id: int
    
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)


class ModelConfigCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: str = Field(..., min_length=1, max_length=64)
    model_id: str = Field(..., min_length=1, max_length=64)
    api_config_id: int = Field(..., ge=1)
    mode: str = Field(..., pattern="^(image|video)$")
    description: Optional[str] = None
    concurrency_limit: int = Field(default=2, ge=1, le=50)
    parameters_schema: List[ParameterSchema] = Field(default_factory=list)
    supported_input_types: List[str] = Field(default_factory=list)
    is_active: bool = True
    sort_order: int = 0


class ModelConfigUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: Optional[str] = Field(default=None, min_length=1, max_length=64)
    model_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    api_config_id: Optional[int] = None
    mode: Optional[str] = Field(default=None, pattern="^(image|video)$")
    description: Optional[str] = None
    concurrency_limit: Optional[int] = Field(default=None, ge=1, le=50)
    parameters_schema: Optional[List[ParameterSchema]] = None
    supported_input_types: Optional[List[str]] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class ModelSelectorInfo(BaseModel):
    """前端模型选择器所需信息"""
    model_config = ConfigDict(protected_namespaces=())
    model_id: str
    name: str
    mode: str
    description: Optional[str]
    parameters: List[ParameterSchema]
    supported_input_types: List[str]


# ============== System Config ==============

class SystemConfigResponse(BaseModel):
    config_key: str
    config_value: Optional[dict] = None
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class SystemConfigUpdate(BaseModel):
    config_value: dict
    description: Optional[str] = None


class TosConfigValue(BaseModel):
    endpoint: str = "tos-cn-beijing.volces.com"
    region: str = "cn-beijing"
    bucket: str = ""
    access_key: str = ""
    secret_key: str = ""
