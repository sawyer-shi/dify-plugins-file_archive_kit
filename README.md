# File Archive Kit

A powerful Dify plugin providing comprehensive **local** file compression and decompression capabilities. All compression and decompression operations are performed entirely on your local machine without requiring any external services, API keys, or internet connection, ensuring maximum data security and privacy. Supports .zip, .7z, and tar.gz formats with optional AES-256 password encryption for secure file archiving.

## Version Information

- **Current Version**: v0.0.1
- **Release Date**: 2026-01-18
- **Compatibility**: Dify Plugin Framework
- **Python Version**: 3.12

### Version History
- **v0.0.1** (2026-01-18): Initial release with compression and decompression capabilities

## Quick Start

1. Download file_archive_kit plugin from Dify marketplace
2. Install plugin in your Dify environment
3. Start compressing and decompressing your files immediately

## Key Features

- **100% Local Processing**: All compression and decompression operations are performed entirely on your local machine
- **No External Services Required**: No need to connect to any external services or third-party APIs
- **No API Key Needed**: Completely free to use without any API key configuration
- **Maximum Data Security**: Your files never leave your local environment, ensuring complete privacy and security
- **Zero Network Dependencies**: Works offline without requiring internet connection
- **File Type Recognition**: Automatically recognizes and preserves MIME types for 100+ file formats
- **Strong Encryption**: AES-256 encryption for password-protected archives
- **Auto Password Generation**: Generate strong random passwords automatically for encryption
<img width="738" height="950" alt="Chinese" src="https://github.com/user-attachments/assets/09efbe55-6102-424d-abbb-bc6bb0f32173" />
<img width="747" height="1050" alt="English" src="https://github.com/user-attachments/assets/2d4c9de1-9311-4a49-aa17-137943e7c71f" />


## Core Features

### Normal Compression

#### Compress Files (compress_normal)
Compress multiple files into a single archive without password protection.
- **Supported Formats**: .zip, .7z, tar.gz
- **Features**:
  - LZMA compression for .zip files
  - Standard compression for .7z and tar.gz
  - Batch file compression
  - Custom archive naming
  - Automatic MIME type preservation

#### Decompress Files (decompress_normal)
Extract files from archives without password protection.
- **Supported Formats**: .zip, .7z, tar.gz
- **Features**:
  - Automatic file type recognition (100+ formats)
  - Batch file extraction
  - Preserves original file structure
  - MIME type preservation for extracted files
  - Handles nested directories

### Encrypted Compression

#### Compress with Password (compress_encrypt)
Compress multiple files into a password-protected archive using AES-256 encryption.
- **Supported Formats**: .zip (AES-256), .7z (AES-256)
- **Features**:
  - AES-256 encryption for .zip files
  - AES-256 encryption for .7z files
  - Custom password input
  - LZMA compression for .zip files
  - Secure password handling
  - Batch file compression

#### Decompress with Password (decompress_encrypt)
Extract files from password-protected archives using AES-256 decryption.
- **Supported Formats**: .zip (AES-256), .7z (AES-256)
- **Features**:
  - AES-256 decryption for .zip files
  - AES-256 decryption for .7z files
  - Password verification
  - Automatic file type recognition (100+ formats)
  - Batch file extraction
  - Error handling for incorrect passwords

### Auto Password Encryption

#### Compress with Auto Password (compress_encrypt_auto)
Compress multiple files into a password-protected archive with auto-generated strong password.
- **Supported Formats**: .zip (AES-256), .7z (AES-256)
- **Features**:
  - AES-256 encryption for .zip files
  - AES-256 encryption for .7z files
  - Automatic strong password generation (16 characters)
  - Password includes letters, numbers, and special characters
  - Prominent password display in output
  - Password included in JSON response
  - LZMA compression for .zip files
  - Batch file compression

## Technical Advantages

- **Local Processing**: All compression and decompression is performed locally without external dependencies
- **High Compression Ratio**: LZMA compression for optimal file size reduction
- **Strong Encryption**: AES-256 encryption for maximum security
- **File Type Recognition**: Automatic MIME type detection for 100+ file formats
- **Flexible Options**: Various configuration options for different use cases
- **Error Handling**: Robust error handling with informative messages
- **Secure Processing**: Files are processed securely without data retention
- **Auto Password Generation**: Cryptographically secure random password generation
- **Multiple Formats**: Support for .zip, .7z, and tar.gz formats
- **Batch Operations**: Compress and decompress multiple files at once

## Requirements

- Python 3.12
- Dify Platform access
- Required Python packages (installed via requirements.txt):
  - dify_plugin>=0.2.0
  - pyzipper==0.3.6
  - py7zr==0.20.8

## Installation & Configuration

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install the plugin in your Dify environment following the standard plugin installation process

## Usage

The plugin provides the following tools for file compression and decompression:

### Normal Compression Tools

#### 1. Compress Files (compress_normal)
Compress multiple files into a single archive without password protection.
- **Parameters**:
  - `files`: The files to be compressed (required)
  - `archive_name`: The name of the archive file (required, default: archive)
  - `format`: The compression format (required, default: zip)
    - `zip`: ZIP format with LZMA compression
    - `7z`: 7z format
    - `tar.gz`: Tarball with gzip compression
- **Features**:
  - Batch file compression
  - Custom archive naming
  - Multiple format support
  - High compression ratio

#### 2. Decompress Files (decompress_normal)
Extract files from archives without password protection.
- **Parameters**:
  - `archive_file`: The archive file to extract (required)
- **Features**:
  - Automatic file type recognition
  - Batch file extraction
  - Preserves file structure
  - MIME type preservation
  - Supports multiple formats

### Encrypted Compression Tools

#### 3. Compress with Password (compress_encrypt)
Compress multiple files into a password-protected archive using AES-256 encryption.
- **Parameters**:
  - `files`: The files to be compressed (required)
  - `archive_name`: The name of the archive file (required, default: secure)
  - `format`: The compression format (required, default: zip)
    - `zip`: ZIP format with AES-256 encryption
    - `7z`: 7z format with AES-256 encryption
  - `password`: The password for encryption (required)
- **Features**:
  - AES-256 encryption
  - Custom password input
  - Secure password handling
  - Batch file compression
  - Multiple format support

#### 4. Decompress with Password (decompress_encrypt)
Extract files from password-protected archives using AES-256 decryption.
- **Parameters**:
  - `archive_file`: The encrypted archive file to extract (required)
  - `password`: The password for decryption (required)
- **Features**:
  - AES-256 decryption
  - Password verification
  - Automatic file type recognition
  - Batch file extraction
  - Error handling for incorrect passwords

### Auto Password Encryption Tools

#### 5. Compress with Auto Password (compress_encrypt_auto)
Compress multiple files into a password-protected archive with auto-generated strong password.
- **Parameters**:
  - `files`: The files to be compressed (required)
  - `archive_name`: The name of the archive file (required, default: secure)
  - `format`: The compression format (required, default: zip)
    - `zip`: ZIP format with AES-256 encryption
    - `7z`: 7z format with AES-256 encryption
- **Features**:
  - Auto-generated 16-character strong password
  - Password includes letters, numbers, and special characters
  - Prominent password display in text output
  - Password included in JSON response
  - AES-256 encryption
  - Cryptographically secure password generation
  - Batch file compression

## File Type Recognition

The plugin automatically recognizes and preserves MIME types for 100+ file formats, including:

- **Documents**: .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .odt, .ods, .odp, .rtf, .txt, .csv
- **Images**: .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg, .tiff, .ico, .psd, .ai
- **Audio**: .mp3, .wav, .ogg, .flac, .m4a, .wma
- **Video**: .mp4, .avi, .mkv, .mov, .wmv, .webm, .flv
- **Archives**: .zip, .7z, .rar, .tar, .gz
- **Code**: .py, .js, .html, .css, .java, .c, .cpp, .go, .rs, .php, .rb, .sh, .bat
- **And many more...**

## Notes

- All compression and decompression is performed locally without uploading files to external services
- The plugin uses LZMA compression for .zip files for optimal compression ratio
- AES-256 encryption is used for password-protected archives
- Auto-generated passwords are 16 characters long and include letters, numbers, and special characters
- For auto password encryption, the password is prominently displayed in both text and JSON output
- File types are automatically recognized and preserved during decompression
- Large files may take longer to process depending on their size and complexity
- The compression ratio depends on the type and content of the input files
- Passwords are only used during compression/decompression and are not stored

## Developer Information

- **Author**: `https://github.com/sawyer-shi`
- **Email**: sawyer36@foxmail.com
- **License**: Apache License 2.0
- **Source Code**: `https://github.com/sawyer-shi/dify-plugins-file_archive_kit`
- **Support**: Through Dify platform and GitHub Issues

## License Notice

This project is licensed under Apache License 2.0. See [LICENSE](LICENSE) file for full license text.

---

**Ready to compress and decompress your files securely?**
