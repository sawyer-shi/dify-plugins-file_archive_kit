import io
import pyzipper
import py7zr
from dify_plugin import Tool

class CompressEncryptTool(Tool):
    def _invoke(self, tool_parameters: dict):
        files = tool_parameters.get('files')
        archive_name = tool_parameters.get('archive_name')
        fmt = tool_parameters.get('format')
        password = tool_parameters.get('password')
        
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
            
            yield self.create_text_message(f"Encrypted {ext} archive created.")
        
        except Exception as e:
            yield self.create_text_message(f"Encryption failed: {str(e)}")
