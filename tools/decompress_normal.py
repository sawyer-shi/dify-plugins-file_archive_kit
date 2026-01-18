import io
import tarfile
import pyzipper
import py7zr
from dify_plugin import Tool

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
                    for name in zf.namelist():
                        if name.endswith('/'): continue
                        clean_name = name.split('/')[-1]
                        if not clean_name: continue
                        yield self.create_blob_message(
                            blob=zf.read(name),
                            meta={"filename": clean_name}
                        )
                        extracted_count += 1

            elif py7zr.is_7zfile(memory_file):
                memory_file.seek(0)
                with py7zr.SevenZipFile(memory_file, 'r') as zf:
                    for name, bio in zf.readall().items():
                        clean_name = name.split('/')[-1]
                        if not clean_name or not bio: continue
                        bio.seek(0)
                        yield self.create_blob_message(
                            blob=bio.read(),
                            meta={"filename": clean_name}
                        )
                        extracted_count += 1

            elif tarfile.is_tarfile(memory_file):
                memory_file.seek(0)
                with tarfile.open(fileobj=memory_file, mode='r:*') as tf:
                    for member in tf.getmembers():
                        if member.isfile():
                            f_obj = tf.extractfile(member)
                            if f_obj:
                                clean_name = member.name.split('/')[-1]
                                if not clean_name: continue
                                yield self.create_blob_message(
                                    blob=f_obj.read(),
                                    meta={"filename": clean_name}
                                )
                                extracted_count += 1
            else:
                yield self.create_text_message("Unknown file format.")
                return

            yield self.create_text_message(f"Extracted {extracted_count} files.")
        
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
