import io
import secrets
import string
import json
import pyzipper
import py7zr
from dify_plugin import Tool

def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

class CompressEncryptAutoTool(Tool):
    def _invoke(self, tool_parameters: dict):
        files = tool_parameters.get('files')
        archive_name = tool_parameters.get('archive_name')
        fmt = tool_parameters.get('format')
        
        password = generate_password()
        
        memory_file = io.BytesIO()
        mime_type = 'application/zip'
        ext = 'zip'

        try:
            if fmt == 'zip':
                with pyzipper.AESZipFile(memory_file, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
                    zf.setpassword(password.encode('utf-8'))
                    for f in files:
                        zf.writestr(f.filename, f.blob)
                mime_type = 'application/zip'
                ext = 'zip'
            
            elif fmt == '7z':
                with py7zr.SevenZipFile(memory_file, 'w', password=password) as zf:
                    for f in files:
                        zf.writestr(f.blob, f.filename)
                mime_type = 'application/x-7z-compressed'
                ext = '7z'

            memory_file.seek(0)
            
            yield self.create_blob_message(
                blob=memory_file.getvalue(),
                meta={
                    "filename": f"{archive_name}.{ext}",
                    "mime_type": mime_type
                }
            )
            
            password_warning = "\n" + "="*50 + "\n"
            password_warning += "⚠️  IMPORTANT: SAVE THIS PASSWORD ⚠️\n"
            password_warning += "="*50 + "\n"
            password_warning += f"Archive: {archive_name}.{ext}\n"
            password_warning += f"Password: {password}\n"
            password_warning += "="*50 + "\n"
            password_warning += "Please save this password in a secure location.\n"
            password_warning += "You will need it to decrypt the archive.\n"
            password_warning += "="*50 + "\n"
            
            yield self.create_text_message(password_warning)
            
            result_json = {
                "status": "success",
                "archive_name": f"{archive_name}.{ext}",
                "format": ext,
                "file_count": len(files),
                "password": password,
                "password_warning": "IMPORTANT: SAVE THIS PASSWORD - You will need it to decrypt the archive!"
            }
            yield self.create_json_message(result_json)
        
        except Exception as e:
            yield self.create_text_message(f"Encryption failed: {str(e)}")
