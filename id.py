import rstr
class idgenerator():
    def __init__(self):
        pass
    
    def generate_id(pattern: str, existing_ids: list) -> str:
        """
        Generate a random string that matches the given regex pattern.
        Example pattern: '[A-Z]{3}[0-9]{4}'
        """
        try:
            new_id = rstr.xeger(pattern)
            while new_id in existing_ids:
                new_id = rstr.xeger(pattern)
            return new_id
        except Exception as e:
            print("Error generating string from pattern:", e)
            return None
    
# Example usage
if __name__ == "__main__":
    pattern = r'^P[A-Z0-9]{5}$'  # e.g., AB123
    id_instance = idgenerator()
    random_id = id_instance.generate_id(pattern)
    print("Generated ID:", random_id)