def get_file_type(filename: str):
    ext = filename.split('.')[-1]
    ext_html_content_type_map = {
        'txt': 'text/plain',
        'html': 'text/html',
        'htm': 'text/html',
        'jpg': 'image/jpg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'icon': 'image/x-icon',
        'gif': 'image/gif',
        'css': 'text/css',
        'wav': 'audio/wav',
        'mp3': 'audio/mp3',
        'mp4': 'video/mp4',
        'js': 'application/javascript',
        'json': 'application/json',
        'pdf': 'application/pdf'
    }
    return ext_html_content_type_map.get(ext, 'text/plain')
