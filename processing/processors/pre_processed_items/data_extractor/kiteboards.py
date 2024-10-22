import re

from processing.data.cleanup import replace_string_ignore_case

def extract_and_cleanup_kiteboard_size(name):
    # Define the regular expression patterns for various size formats
    twintip_pattern = r'(\d+(?:[.,]\d+)?)\s*(?:x|-)?\s*(\d+(?:[.,]\d+)?)?\s*(?:cm)?'
    surfboard_pattern = r"(\d+)'(\d+(?:\.\d+)?)?"  # Matches formats like 6'3 or 5'7.5

    # Try to match twintip board size
    twintip_match = re.search(twintip_pattern, name, re.IGNORECASE)
    if twintip_match:
        size1 = float(twintip_match.group(1).replace(',', '.'))
        size2 = float(twintip_match.group(2).replace(',', '.')) if twintip_match.group(2) else 0
        
        board_size = max(size1, size2)
        board_size = round(board_size)

        cleaned_name = re.sub(twintip_pattern, '', name, flags=re.IGNORECASE).strip()
        
        return cleaned_name, board_size

    # Try to match surfboard size
    surfboard_match = re.search(surfboard_pattern, name)
    if surfboard_match:
        feet = int(surfboard_match.group(1))
        inches = float(surfboard_match.group(2)) if surfboard_match.group(2) else 0
        
        board_size = f"{feet}'{inches:.1f}" if inches else f"{feet}'"

        cleaned_name = re.sub(surfboard_pattern, '', name).strip()
        
        return cleaned_name, board_size

    # If no match found
    return name, None