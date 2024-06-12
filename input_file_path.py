# input_file_path.py

def get_file_path():
    file_path = input("実行したいPythonファイルのパスを入力してください: ")
    return file_path

file_path = get_file_path()

# 入力されたファイルパスを保存
with open('file_path.txt', 'w') as file:
    file.write(file_path)

print(f"入力されたファイルパスは '{file_path}' です。")

