import os


def save_html_content_to_file(file_content, filename, file_extension, file_location):
    if not os.path.exists(file_location):
        os.makedirs(file_location)
    if file_location.endswith('/'):
        file_location = file_location[:-1]
    if file_extension.startswith('.'):
        file_extension = file_extension[1:]
    with open('{}/{}.{}'.format(file_location, filename, file_extension), mode='w+', encoding='utf-8') as file:
        file.write(file_content)
