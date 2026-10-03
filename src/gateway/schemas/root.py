from pydantic import BaseModel, Field


class ServicesUrls(BaseModel):
    services_auth: str
    services_task: str

class ApiGatewayInfo(BaseModel):
    message: str = Field(default="API Gateway")
    version: str = "1.0.0"
    services: ServicesUrls






