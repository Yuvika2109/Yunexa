import re

def extract_yt_term(command):
    # Try matching "play X on youtube" pattern
    pattern1 = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern1, command, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Try matching "X on youtube" pattern
    pattern2 = r'(.*?)\s+on\s+youtube'
    match = re.search(pattern2, command, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # If no patterns match, just remove "on youtube" and return the rest
    if "on youtube" in command.lower():
        cleaned = command.lower().replace("on youtube", "").strip()
        if cleaned:
            return cleaned
    
    # If all else fails, return the original query without "on youtube"
    return command.replace("on youtube", "").strip()

def remove_words(input_string, words_to_remove):
    words = input_string.split()
    filtered_words = [word for word in words if word.lower() not in words_to_remove]
    result_string = ' '.join(filtered_words)
    return result_string