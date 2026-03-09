def get_file_type(filename: str):
    ext = filename.split('.')[-1]
    ext_html_content_type_map = {
        'html': 'text/html',
        'htm': 'text/html',
        'jpg': 'image/jpg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'css': 'text/css',
        'au': 'audio/basic',
        'avi': 'audio/x-msvideo',
        'wav': 'audio/wav',
        'mpeg': 'video/mepg',
        'mp3': 'audio/mpeg',
        'txt': 'text/plain'
    }
    return ext_html_content_type_map.get(ext, 'text/plain')