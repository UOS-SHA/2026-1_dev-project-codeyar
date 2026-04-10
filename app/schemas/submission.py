from pydantic import BaseModel, Field

class SubmitRequest(BaseModel):
    code: str = Field(..., description="The user's source code to be executed")
    language: str = Field("python", description="Language of the source code")
    time_limit: float = Field(2.0, description="Execution time limit in seconds")
    memory_limit: int = Field(128, description="Execution memory limit in MB")

class SubmitResponse(BaseModel):
    token: str
    status: str
