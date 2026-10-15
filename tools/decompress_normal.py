import io
import pyzipper
import py7zr
from dify_plugin import Tool
from .archive_limits import iter_7z, iter_tar, iter_zip, open_tar, safe_entry_name
from .file_utils import get_file_type

class DecompressNormalTool(Tool):
    def _invoke(self, tool_parameters: dict):
        archive_file = tool_parameters.get('archive_file')
        content = archive_file.blob
        memory_file = io.BytesIO(content)
        extracted_count = 0

        try:
            if pyzipper.is_zipfile(memory_file):
                memory_file.seek(0)
                with pyzipper.ZipFile(memory_file) as zf:
                    for name, data in iter_zip(zf):
                        yield self._blob_message(name, data, extracted_count)
                        extracted_count += 1

            # Use a fresh stream: is_zipfile() moved the position, and is_7zfile() checks from there.
            elif py7zr.is_7zfile(io.BytesIO(content)):
                try:
                    for name, data in iter_7z(io.BytesIO(content)):
                        yield self._blob_message(name, data, extracted_count)
                        extracted_count += 1
                except py7zr.exceptions.PasswordRequired:
                    yield self.create_text_message("Error: This archive is password-protected. Use Encrypted Decompress instead.")
                    return

            elif (tf := open_tar(content)) is not None:
                with tf:
                    for name, data in iter_tar(tf):
                        yield self._blob_message(name, data, extracted_count)
                        extracted_count += 1
            else:
                yield self.create_text_message("Unknown file format.")
                return

            yield self.create_text_message(f"Extracted {extracted_count} files.")
        
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

    def _blob_message(self, name, data, index):
        clean_name = safe_entry_name(name, index)
        return self.create_blob_message(
            blob=data,
            meta={"filename": clean_name, "mime_type": get_file_type(clean_name)}
        )
