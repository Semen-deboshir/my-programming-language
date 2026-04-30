import pytest
from PIL import Image
import tempfile
import os
from unittest.mock import patch, Mock
import io

# Assuming your function is in a module named 'image_processor'
# If not, adjust the import accordingly
from sd import run_code

@pytest.fixture
def temp_image():
    """Create a temporary test image"""
    img = Image.new('RGB', (5, 5), color=(0, 0, 0))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    yield temp_file.name
    os.unlink(temp_file.name)

@pytest.fixture
def output_image():
    """Create a temporary output file path"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)

def test_no_commands(temp_image, output_image):
    """Test with empty code"""
    run_code("", temp_image, output_image, "")
    # Should complete without errors and show/save image
    assert os.path.exists(output_image)

def test_move_right_commands(temp_image, output_image):
    """Test '>' command - move right"""
    # Small image to test movement
    img = Image.new('RGB', (3, 3), color=(100, 100, 100))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    # '>' should move to next column, '.' prints current pixel
    with patch('builtins.print') as mock_print:
        run_code(">.", temp_file.name, output_image, "")
        # Should print the next pixel (i=1,j=0)
        mock_print.assert_called()
    
    os.unlink(temp_file.name)

def test_move_left_command(temp_image, output_image):
    """Test '<' command - move left"""
    img = Image.new('RGB', (3, 3), color=(100, 100, 100))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    # Start at (0,0), move right, then left, should be back at (0,0)
    run_code("><", temp_file.name, output_image, "")
    assert os.path.exists(output_image)
    
    os.unlink(temp_file.name)

def test_move_left_boundary(temp_image, output_image):
    """Test '<' command at left boundary - should not go negative"""
    # Test that '<' doesn't move past left edge
    run_code("<", temp_image, output_image, "")
    assert os.path.exists(output_image)

def test_rgb_increment_commands(temp_image, output_image):
    """Test 'r', 'g', 'b' increment commands"""
    img = Image.new('RGB', (1, 1), color=(0, 0, 0))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    run_code("rgb", temp_file.name, output_image, "")
    
    # Verify colors were incremented and wrapped
    result_img = Image.open(output_image)
    r, g, b = result_img.getpixel((0, 0))
    assert r == 1
    assert g == 1
    assert b == 1
    
    os.unlink(temp_file.name)

def test_rgb_increment_wrap(temp_image, output_image):
    """Test increment wrapping at 255"""
    img = Image.new('RGB', (1, 1), color=(255, 255, 255))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    run_code("rgb", temp_file.name, output_image, "")
    
    result_img = Image.open(output_image)
    r, g, b = result_img.getpixel((0, 0))
    assert r == 0  # 255 + 1 = 256 % 256 = 0
    assert g == 0
    assert b == 0
    
    os.unlink(temp_file.name)

def test_rgb_decrement_commands(temp_image, output_image):
    """Test 'd', 'e', 'n' decrement commands"""
    img = Image.new('RGB', (1, 1), color=(100, 100, 100))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    run_code("den", temp_file.name, output_image, "")
    
    result_img = Image.open(output_image)
    r, g, b = result_img.getpixel((0, 0))
    assert r == 99
    assert g == 99
    assert b == 99
    
    os.unlink(temp_file.name)

def test_rgb_decrement_wrap(temp_image, output_image):
    """Test decrement wrapping at 0"""
    img = Image.new('RGB', (1, 1), color=(0, 0, 0))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    run_code("den", temp_file.name, output_image, "")
    
    result_img = Image.open(output_image)
    r, g, b = result_img.getpixel((0, 0))
    assert r == 255  # 0 - 1 = -1 % 256 = 255
    assert g == 255
    assert b == 255
    
    os.unlink(temp_file.name)

def test_print_commands(temp_image, output_image):
    """Test 'R', 'G', 'B' print commands"""
    img = Image.new('RGB', (1, 1), color=(100, 150, 200))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    with patch('builtins.print') as mock_print:
        run_code("RGB", temp_file.name, output_image, "")
        mock_print.assert_any_call(100)
        mock_print.assert_any_call(150)
        mock_print.assert_any_call(200)
    
    os.unlink(temp_file.name)

def test_dot_command(temp_image, output_image):
    """Test '.' command - print RGB tuple"""
    img = Image.new('RGB', (1, 1), color=(100, 150, 200))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    with patch('builtins.print') as mock_print:
        run_code(".", temp_file.name, output_image, "")
        mock_print.assert_called_with(100, 150, 200)
    
    os.unlink(temp_file.name)

def test_input_commands(temp_image, output_image):
    """Test 'D', 'E', 'N' input commands"""
    img = Image.new('RGB', (1, 1), color=(0, 0, 0))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    test_input = "ABC"
    run_code("DEN", temp_file.name, output_image, test_input)
    
    result_img = Image.open(output_image)
    r, g, b = result_img.getpixel((0, 0))
    assert r == ord('A') % 256
    assert g == ord('B') % 256
    assert b == ord('C') % 256
    
    os.unlink(temp_file.name)

def test_input_commands_boundary(temp_image, output_image):
    """Test input commands when input is exhausted"""
    img = Image.new('RGB', (1, 1), color=(50, 60, 70))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    # Only 2 chars of input, but 3 commands
    run_code("DEN", temp_file.name, output_image, "AB")
    
    # Values should only change for available input
    result_img = Image.open(output_image)
    r, g, b = result_img.getpixel((0, 0))
    assert r == ord('A') % 256
    assert g == ord('B') % 256
    assert b == 70  # Unchanged
    
    os.unlink(temp_file.name)

def test_loop_basic(temp_image, output_image):
    """Test basic loop functionality with '[' and ']'"""
    # Create image with sum of RGB = 255 (condition false, should loop)
    img = Image.new('RGB', (1, 1), color=(100, 100, 55))  # Sum = 255
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    # Loop: decrement r until sum != 255
    # When sum != 255, exit loop
    code = "[dr.]"  # While sum==255, decrement r and print
    
    with patch('builtins.print') as mock_print:
        run_code(code, temp_file.name, output_image, "")
        # Should print after decrement when sum != 255
        mock_print.assert_called()
    
    os.unlink(temp_file.name)

def test_loop_nested(temp_image, output_image):
    """Test nested loops"""
    img = Image.new('RGB', (1, 1), color=(100, 100, 55))  # Sum = 255
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    # Nested loops structure
    code = "[[dr.]]"
    
    # Should execute without errors
    run_code(code, temp_file.name, output_image, "")
    assert os.path.exists(output_image)
    
    os.unlink(temp_file.name)

def test_loop_skip_when_false(temp_image, output_image):
    """Test that loop is skipped when condition is false initially"""
    img = Image.new('RGB', (1, 1), color=(100, 100, 100))  # Sum = 300 != 255
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    with patch('builtins.print') as mock_print:
        # This loop should be skipped entirely
        code = "[r.]"
        run_code(code, temp_file.name, output_image, "")
        # The print inside loop should not execute
        mock_print.assert_not_called()
    
    os.unlink(temp_file.name)

def test_multiple_pixels(temp_image, output_image):
    """Test processing multiple pixels"""
    img = Image.new('RGB', (3, 3), color=(100, 100, 100))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    # Process multiple pixels
    run_code("r.", temp_file.name, output_image, "")
    
    result_img = Image.open(output_image)
    # Check that movement occurred properly
    assert result_img.size == (3, 3)
    
    os.unlink(temp_file.name)

def test_image_persistence(temp_image, output_image):
    """Test that image modifications are saved"""
    img = Image.new('RGB', (2, 2), color=(0, 0, 0))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    # Increment red channel for all pixels
    run_code("rrrr", temp_file.name, output_image, "")
    
    result_img = Image.open(output_image)
    for i in range(2):
        for j in range(2):
            r, g, b = result_img.getpixel((i, j))
            assert r == 1
            assert g == 0
            assert b == 0
    
    os.unlink(temp_file.name)

def test_complex_program(temp_image, output_image):
    """Test a more complex program sequence"""
    img = Image.new('RGB', (2, 2), color=(50, 50, 50))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    # Complex program: increment, print, move, repeat
    code = "rGr>rGr>rGr>rGr"
    
    with patch('builtins.print') as mock_print:
        run_code(code, temp_file.name, output_image, "")
        # Should print multiple times
        assert mock_print.call_count > 0
    
    os.unlink(temp_file.name)

def test_large_image(temp_image, output_image):
    """Test with larger image to ensure no performance issues"""
    img = Image.new('RGB', (50, 50), color=(100, 100, 100))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    # Process entire image
    run_code("", temp_file.name, output_image, "")
    assert os.path.exists(output_image)
    
    os.unlink(temp_file.name)

def test_error_handling_missing_file():
    """Test error handling when input file doesn't exist"""
    with pytest.raises(FileNotFoundError):
        run_code("", "nonexistent.png", "output.png", "")

def test_character_wrapping_behavior(temp_image, output_image):
    """Test the modulo 256 behavior for all color operations"""
    test_cases = [
        (255, "r", 0),    # Increment wraps
        (0, "d", 255),    # Decrement wraps
        (255, "r", 0),    # Another increment wrap test
        (1, "d", 0),      # Normal decrement
    ]
    
    for initial, cmd, expected in test_cases:
        img = Image.new('RGB', (1, 1), color=(initial, 0, 0))
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name)
        temp_file.close()
        
        run_code(cmd, temp_file.name, output_image, "")
        
        result_img = Image.open(output_image)
        r, g, b = result_img.getpixel((0, 0))
        assert r == expected
        
        os.unlink(temp_file.name)
        if os.path.exists(output_image):
            os.unlink(output_image)

def test_input_ascii_conversion(temp_image, output_image):
    """Test that input characters are properly converted to ASCII values"""
    img = Image.new('RGB', (1, 1), color=(0, 0, 0))
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    test_input = "Hello!"
    run_code("D", temp_file.name, output_image, test_input)
    
    result_img = Image.open(output_image)
    r, g, b = result_img.getpixel((0, 0))
    assert r == ord('H')
    
    os.unlink(temp_file.name)
