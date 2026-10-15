import io
import lzma
import pyzipper
import py7zr
from dify_plugin import Tool
from .archive_limits import iter_7z, iter_zip, safe_entry_name
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
                        for name, data in iter_zip(zf):
                            yield self._blob_message(name, data, extracted_count)
                            extracted_count += 1
                except RuntimeError as e:
                    if 'Bad password' in str(e) or 'CRC' in str(e):
                         yield self.create_text_message("Error: Incorrect ZIP password.")
                         return
                    raise e
            
            # Use a fresh stream: is_zipfile() moved the position, and is_7zfile() checks from there.
            elif py7zr.is_7zfile(io.BytesIO(archive_file.blob)):
                try:
                    for name, data in iter_7z(io.BytesIO(archive_file.blob), password=password):
                        yield self._blob_message(name, data, extracted_count)
                        extracted_count += 1
                # 7z has no password check value: a wrong password surfaces as one of these
                # decoding errors, which are indistinguishable from a corrupted archive.
                except (py7zr.exceptions.PasswordRequired, py7zr.exceptions.Bad7zFile,
                        py7zr.exceptions.CrcError, lzma.LZMAError, EOFError, TypeError):
                    yield self.create_text_message("Error: Incorrect 7Z password or corrupted archive.")
                    return
            
            else:
                yield self.create_text_message("Unsupported format for decryption.")
                return

            yield self.create_text_message(f"Decrypted {extracted_count} files.")
        
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

    def _blob_message(self, name, data, index):
        clean_name = safe_entry_name(name, index)
        return self.create_blob_message(
            blob=data,
            meta={"filename": clean_name, "mime_type": get_file_type(clean_name)}
        )
