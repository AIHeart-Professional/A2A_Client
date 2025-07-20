import yaml

class PromptLoader:
    def __init__(self, file_path):
        with open(file_path, 'r') as f:
            self.prompts = yaml.safe_load(f)

    def get(self, key):
        return self.prompts.get(key, None)
