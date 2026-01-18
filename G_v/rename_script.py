import os

def replace_in_file(file_path, old_text, new_text):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if old_text in content:
        new_content = content.replace(old_text, new_text)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Updated: {file_path}")

def walk_and_replace(directory, old_text, new_text):
    for root, dirs, files in os.walk(directory):
        if '.git' in dirs:
            dirs.remove('.git')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        
        for file in files:
            if file.endswith(('.html', '.js', '.py', '.css', '.md')):
                file_path = os.path.join(root, file)
                replace_in_file(file_path, old_text, new_text)

if __name__ == "__main__":
    target_dir = r"e:\WorkingProjects\IHORMS\G_v"
    walk_and_replace(target_dir, "IHORMS", "IHORMS")
    print("Bulk replacement complete.")
