from pydantic import BaseModel, Field


class TestCaseCreate(BaseModel):
    """
    Schema for creating a new test case.
    problem_id comes from the URL path, not the request body.
    """
    input_data: str = Field(min_length=1, max_length=50_000, description="The input given to the program")
    expected_output: str = Field(min_length=1, max_length=50_000, description="The expected output of the program")
    is_hidden: bool = Field(default=False, description="Hidden test cases are not shown to users")


class TestCaseResponse(BaseModel):
    """
    Schema returned to the client after creating or fetching a test case.
    We expose all fields except internal database metadata.
    """
    test_case_id: int
    problem_id: int
    input_data: str
    expected_output: str
    is_hidden: bool
