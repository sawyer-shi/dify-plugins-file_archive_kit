"""Limits that keep archive extraction within the plugin's memory budget.

The plugin runs with 256 MB of memory and holds the archive and the extracted
files in memory. zipfile, tarfile and py7zr can all be made to allocate far
more than that by a small crafted archive, so this module caps entry count and
uncompressed size, and patches the few places where those libraries would read
unbounded data before any of our checks run.
"""
import bz2
import io
import lzma
import ntpath
import re
import struct
import tarfile

import py7zr
import py7zr.archiveinfo
import py7zr.py7zr
import pyzipper.zipfile
from py7zr.io import Py7zIO, WriterFactory

MAX_ENTRY_COUNT = 1000
MAX_TOTAL_UNCOMPRESSED_SIZE = 64 * 1024 * 1024
_MAX_METADATA_SIZE = 1024 * 1024
_CHUNK_SIZE = 1024 * 1024


class ArchiveLimitError(Exception):
    pass


def _entry_count_error():
    return ArchiveLimitError(f"Archive contains more than {MAX_ENTRY_COUNT} entries.")


def _size_limit_error():
    return ArchiveLimitError(
        f"Archive exceeds the {MAX_TOTAL_UNCOMPRESSED_SIZE // (1024 * 1024)} MB uncompressed size limit."
    )


# py7zr parses the whole header before we can look at the entry list, and sizes
# its decompression buffer from the host's free memory. Bound both.
py7zr.archiveinfo.MAX_NUMFILES = MAX_ENTRY_COUNT
py7zr.archiveinfo.MAX_HEADER_SIZE = _MAX_METADATA_SIZE
py7zr.py7zr.get_memory_limit = lambda: _CHUNK_SIZE


class _BoundedDecompressor:
    """bz2/LZMA decompressor for zip entries that cannot inflate past the size limit.

    zipfile passes an output limit only to the deflate decompressor; for bz2 and
    LZMA it inflates each compressed chunk completely, so a few KB can expand to
    gigabytes before the caller sees any data.
    """

    def __init__(self, compress_type):
        self._lzma = compress_type == pyzipper.zipfile.ZIP_LZMA
        self._decomp = None if self._lzma else bz2.BZ2Decompressor()
        self._unconsumed = b''
        self.eof = False

    def decompress(self, data):
        if self._decomp is None:
            # Zip LZMA entries start with a 4-byte header and the LZMA properties,
            # parsed the same way as pyzipper.zipfile.LZMADecompressor.
            self._unconsumed += data
            if len(self._unconsumed) <= 4:
                return b''
            psize = struct.unpack('<H', self._unconsumed[2:4])[0]
            if len(self._unconsumed) <= 4 + psize:
                return b''
            self._decomp = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[
                lzma._decode_filter_properties(lzma.FILTER_LZMA1, self._unconsumed[4:4 + psize])
            ])
            data = self._unconsumed[4 + psize:]
            self._unconsumed = b''

        result = self._decomp.decompress(data, max_length=MAX_TOTAL_UNCOMPRESSED_SIZE + 1)
        if len(result) > MAX_TOTAL_UNCOMPRESSED_SIZE or not (self._decomp.eof or self._decomp.needs_input):
            raise _size_limit_error()
        self.eof = self._decomp.eof
        return result


_original_get_decompressor = pyzipper.zipfile.ZipExtFile.get_decompressor


def _get_decompressor(self, compress_type):
    if compress_type in (pyzipper.zipfile.ZIP_BZIP2, pyzipper.zipfile.ZIP_LZMA):
        return _BoundedDecompressor(compress_type)
    return _original_get_decompressor(self, compress_type)


pyzipper.zipfile.ZipExtFile.get_decompressor = _get_decompressor


class _SafeTarInfo(tarfile.TarInfo):
    """Rejects tar metadata that tarfile would read into memory in one piece.

    GNU long names and pax headers are read whole, and sparse maps are built
    while iterating, all before the caller sees the member.
    """

    def _proc_member(self, tarfile_obj):
        if self.type == tarfile.GNUTYPE_SPARSE:
            raise ArchiveLimitError("Sparse tar members are not supported.")
        if self.type in (tarfile.GNUTYPE_LONGNAME, tarfile.GNUTYPE_LONGLINK,
                         tarfile.XHDTYPE, tarfile.XGLTYPE, tarfile.SOLARIS_XHDTYPE) \
                and self.size > _MAX_METADATA_SIZE:
            raise ArchiveLimitError("Tar header is too large.")
        return super()._proc_member(tarfile_obj)

    def _proc_gnusparse_00(self, *args):
        raise ArchiveLimitError("Sparse tar members are not supported.")

    _proc_gnusparse_01 = _proc_gnusparse_00
    _proc_gnusparse_10 = _proc_gnusparse_00


def open_tar(data):
    """Open a tar archive with the safe header parser, or return None if it is not a tar."""
    try:
        return tarfile.open(fileobj=io.BytesIO(data), mode='r:*', tarinfo=_SafeTarInfo)
    except tarfile.TarError:
        return None


def check_declared_sizes(sizes):
    """Reject an archive whose header-declared entry count or total size exceeds the limits."""
    sizes = list(sizes)
    if len(sizes) > MAX_ENTRY_COUNT:
        raise _entry_count_error()
    if sum(sizes) > MAX_TOTAL_UNCOMPRESSED_SIZE:
        raise _size_limit_error()


class ExtractionLimiter:
    """Tracks entry count and actual uncompressed bytes while extracting one archive."""

    def __init__(self):
        self.entries = 0
        self.remaining = MAX_TOTAL_UNCOMPRESSED_SIZE

    def count_entry(self, declared_size=0):
        self.entries += 1
        if self.entries > MAX_ENTRY_COUNT:
            raise _entry_count_error()
        if declared_size > self.remaining:
            raise _size_limit_error()

    def read(self, fileobj):
        # Read in chunks and stop one byte past the budget, so a header that
        # under-reports the size cannot make us buffer more than the limit.
        # BytesIO.getvalue() hands over its buffer without another copy.
        buf = io.BytesIO()
        while True:
            chunk = fileobj.read(min(_CHUNK_SIZE, self.remaining + 1 - buf.tell()))
            if not chunk:
                break
            buf.write(chunk)
            if buf.tell() > self.remaining:
                raise _size_limit_error()
        self.remaining -= buf.tell()
        return buf.getvalue()


def iter_zip(zf):
    """Yield (name, data) for each file in an open zip archive, within the limits."""
    infos = zf.infolist()
    check_declared_sizes(info.file_size for info in infos)
    limiter = ExtractionLimiter()
    for info in infos:
        if info.is_dir():
            continue
        with zf.open(info) as src:
            data = limiter.read(src)
        yield info.filename, data


class _BufferIO(Py7zIO):
    """In-memory 7z output whose contents can be taken without copying.

    py7zr's own BytesIOFactory silently truncates at its limit and only exposes
    a copying read(); the total size here is bounded by max_extract_size instead.
    """

    def __init__(self):
        self.buffer = io.BytesIO()

    def write(self, s):
        return self.buffer.write(s)

    def read(self, size=None):
        return self.buffer.read(size)

    def seek(self, offset, whence=0):
        return self.buffer.seek(offset, whence)

    def flush(self):
        pass

    def size(self):
        return len(self.buffer.getbuffer())


class _BufferFactory(WriterFactory):
    def __init__(self):
        self.products = {}

    def create(self, filename):
        product = self.products[filename] = _BufferIO()
        return product


def iter_7z(fileobj, password=None):
    """Yield (name, data) for each file in a 7z archive, within the limits."""
    with py7zr.SevenZipFile(fileobj, 'r', password=password, max_extract_size=MAX_TOTAL_UNCOMPRESSED_SIZE) as zf:
        check_declared_sizes(entry.uncompressed for entry in zf.list())
        factory = _BufferFactory()
        zf.extractall(factory=factory)
    # Release each buffer as soon as it is handed out.
    for name in list(factory.products):
        yield name, factory.products.pop(name).buffer.getvalue()


def iter_tar(tf):
    """Yield (name, data) for each regular file in an open tar archive, within the limits."""
    limiter = ExtractionLimiter()
    for member in tf:
        limiter.count_entry(member.size)
        if member.isfile():
            f_obj = tf.extractfile(member)
            if f_obj:
                yield member.name, limiter.read(f_obj)


def safe_entry_name(filename, index):
    """Reduce a name to a plain file name so it cannot escape the extraction directory."""
    name = re.sub(r'[\x00-\x1f]', '', filename or '')
    name = ntpath.splitdrive(name.replace('\\', '/'))[1].split('/')[-1].replace(':', '_')
    if name in ('', '.', '..'):
        name = f"file_{index}"
    return name
