import io
import tarfile
import pyzipper
import py7zr
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .archive_limits import safe_entry_name

class CompressNormalTool(Tool):
    def _invoke(self, tool_parameters: dict):
        files = tool_parameters.get('files')
        archive_name = tool_parameters.get('archive_name', 'archive')
        fmt = tool_parameters.get('format', 'zip')
        
        memory_file = io.BytesIO()
        mime_type = 'application/zip'
        extension = 'zip'

        try:
            if fmt == 'zip':
                with pyzipper.ZipFile(memory_file, 'w', compression=pyzipper.ZIP_LZMA) as zf:
                    for i, f in enumerate(files):
                        zf.writestr(safe_entry_name(f.filename, i), f.blob)
                mime_type = 'application/zip'
                extension = 'zip'

            elif fmt == '7z':
                with py7zr.SevenZipFile(memory_file, 'w') as zf:
                    for i, f in enumerate(files):
                        zf.writestr(f.blob, safe_entry_name(f.filename, i))
                mime_type = 'application/x-7z-compressed'
                extension = '7z'

            elif fmt == 'tar.gz':
                with tarfile.open(fileobj=memory_file, mode='w:gz') as tf:
                    for i, f in enumerate(files):
                        data = f.blob
                        info = tarfile.TarInfo(name=safe_entry_name(f.filename, i))
                        info.size = len(data)
                        tf.addfile(info, io.BytesIO(data))
                mime_type = 'application/gzip'
                extension = 'tar.gz'

            memory_file.seek(0)
            
            yield self.create_blob_message(
                blob=memory_file.getvalue(),
                meta={
                    "filename": f"{archive_name}.{extension}",
                    "mime_type": mime_type
                }
            )
            
            yield self.create_text_message(f"Successfully compressed to {extension}.")
        
        except Exception as e:
            yield self.create_text_message(f"Compression failed: {str(e)}")
