"""
模型配置 Pydantic Schema
"""
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


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
    base_url: str
    total_concurrency: int
    is_active: bool


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
    
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)


class ModelSelectorInfo(BaseModel):
    """前端模型选择器所需信息"""
    model_config = ConfigDict(protected_namespaces=())
    model_id: str
    name: str
    mode: str
    description: Optional[str]
    parameters: List[ParameterSchema]
    supported_input_types: List[str]
