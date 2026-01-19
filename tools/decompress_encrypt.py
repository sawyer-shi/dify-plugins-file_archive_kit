import io
import pyzipper
import py7zr
from dify_plugin import Tool
from .file_utils import get_file_type

class DecompressEncryptTool(Tool):
    def _invoke(self, tool_parameters: dict):
        archive_file = tool_parameters.get('archive_file')
        password = tool_parameters.get('password')
        extracted_count = 0
        
        memory_file = io.BytesIO(archive_file.blob)

        try:
            if pyzipper.is_zipfile(memory_file):
                memory_file.seek(0)
                try:
                    with pyzipper.AESZipFile(memory_file) as zf:
                        zf.setpassword(password.encode('utf-8'))
                        for name in zf.namelist():
                            if name.endswith('/'): continue
                            clean_name = name.split('/')[-1]
                            if not clean_name: continue
                            yield self.create_blob_message(
                                blob=zf.read(name),
                                meta={"filename": clean_name, "mime_type": get_file_type(clean_name)}
                            )
                            extracted_count += 1
                except RuntimeError as e:
                    if 'Bad password' in str(e) or 'CRC' in str(e):
                         yield self.create_text_message("Error: Incorrect ZIP password.")
                         return
                    raise e
            
            elif py7zr.is_7zfile(memory_file):
                memory_file.seek(0)
                try:
                    with py7zr.SevenZipFile(memory_file, 'r', password=password) as zf:
                        for name, bio in zf.readall().items():
                            clean_name = name.split('/')[-1]
                            if not clean_name or not bio: continue
                            bio.seek(0)
                            yield self.create_blob_message(
                                blob=bio.read(),
                                meta={"filename": clean_name, "mime_type": get_file_type(clean_name)}
                            )
                            extracted_count += 1
                except (py7zr.exceptions.PasswordRequired, py7zr.exceptions.Bad7zFile):
                    yield self.create_text_message("Error: Incorrect 7Z password.")
                    return
            
            else:
                yield self.create_text_message("Unsupported format for decryption.")
                return

            yield self.create_text_message(f"Decrypted {extracted_count} files.")
        
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
