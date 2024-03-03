import uuid, time , os


def set_uploaded_filename(filename):
    filename, ext = os.path.splitext(os.path.basename(filename))
    new_filename = uuid.uuid5(uuid.NAMESPACE_URL, f'{filename}-{time.time()}')
    output_filename = f'{new_filename}{ext}'
    return output_filename
