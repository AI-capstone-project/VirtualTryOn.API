from add import add
from make_path import create_image_path

def test_add():
    assert add(2, 3) == 5  # Happy path
    assert add(-1, 1) == 0  # Edge case
    assert add(0, 0) == 0  # Another edge case
    
class TestCreateImagePath:
    def __init__(self) -> None:
        self.filename = "image.jpg"  
    
def test_create_image_path():
    result = create_image_path(TestCreateImagePath())  # This might return a tuple
    print(result)  # Add this to print the result and debug
    
    # Check if the second element of the tuple (the filename) ends with ".jpg"
    if isinstance(result[1], str):
        assert result[1].endswith(".jpg")  # Check the filename in result[1]
    else:
        assert False, "Expected a string as the filename in the result tuple"
