import os
import sys
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())
import lunch_bot

def test_ai_hype_generation():
    print("Testing AI Hype Generation...")
    
    # Configure stdout to handle emojis if possible, or just catch the error
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    # 1. Test missing API key
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
        result = lunch_bot.get_ai_hype()
        # Use repr() to safely print strings with emojis
        print(f"Test 1 (Missing Key): {repr(result)}")
        assert "missing" in result.lower()

    # 2. Test mock generation
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        with patch("google.genai.Client") as mock_client_class:
            mock_client = mock_client_class.return_value
            # Mock the nested models.generate_content call
            mock_client.models.generate_content.return_value = MagicMock(text="MOCK HYPE! 🔥")
            
            result = lunch_bot.get_ai_hype(prompt_type="manual")
            print(f"Test 2 (Mock Success): {repr(result)}")
            assert "MOCK HYPE" in result

    print("\nAI Logic Tests Passed!")

if __name__ == "__main__":
    test_ai_hype_generation()
