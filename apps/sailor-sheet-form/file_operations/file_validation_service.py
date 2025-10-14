"""
File Validation Service
Handles file type detection, validation, and content analysis.
"""

import mimetypes


class FileValidationService:
    """Service for file validation and type detection."""
    
    def __init__(self):
        # Allowed file extensions for security
        self.allowed_extensions = {
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 
            'jpg', 'jpeg', 'png', 'gif', 'txt'
        }
        
        # Magic bytes for file type detection
        self.magic_signatures = {
            b'\x25\x50\x44\x46': 'pdf',  # PDF
            b'\x89\x50\x4E\x47': 'png',  # PNG
            b'\xFF\xD8\xFF': 'jpg',      # JPEG
            b'\x47\x49\x46\x38': 'gif',  # GIF
            b'\x50\x4B\x03\x04': 'docx', # DOCX/XLSX/PPTX (ZIP-based)
            b'\xD0\xCF\x11\xE0': 'doc',  # DOC/XLS/PPT (OLE2)
            b'\x50\x4B\x05\x06': 'zip',  # ZIP
            b'\x52\x61\x72\x21': 'rar',  # RAR
        }
        
        # MIME type to extension mapping
        self.mime_to_extension = {
            'application/pdf': '.pdf',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff',
            'image/webp': '.webp',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.ms-powerpoint': '.ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'text/plain': '.txt',
            'text/csv': '.csv',
            'application/zip': '.zip',
            'application/x-rar-compressed': '.rar',
            'application/x-7z-compressed': '.7z',
            'application/json': '.json',
            'application/xml': '.xml',
            'text/html': '.html',
            'text/css': '.css',
            'application/javascript': '.js',
            'application/octet-stream': '.bin',  # Keep as fallback but try to avoid
        }
    
    def is_allowed_file(self, filename: str) -> bool:
        """
        Check if file extension is allowed.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if file extension is allowed
        """
        if not filename or '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.allowed_extensions
    
    def detect_file_type_from_content(self, file_content: bytes) -> str:
        """
        Detect file type from file content using magic bytes.
        
        Args:
            file_content: Bytes content of the file
            
        Returns:
            str: File extension without dot, or None if not detected
        """
        if not file_content:
            return None
        
        # Check magic bytes for common file types
        for signature, ext in self.magic_signatures.items():
            if file_content.startswith(signature):
                print(f"DEBUG: Detected file type from content: {ext}")
                return ext
        
        # Check for text files
        try:
            # Try to decode as text
            text_content = file_content[:1024].decode('utf-8', errors='ignore')
            if text_content.isprintable():
                print(f"DEBUG: Detected text file")
                return 'txt'
        except:
            pass
        
        print(f"DEBUG: Could not detect file type from content")
        return None
    
    def get_extension_from_content_type(self, content_type: str) -> str:
        """
        Get file extension from MIME content type.
        
        Args:
            content_type: MIME content type
            
        Returns:
            str: File extension with dot
        """
        return self.mime_to_extension.get(content_type.lower(), '.bin')
    
    def get_mime_type_from_filename(self, filename: str) -> str:
        """
        Get MIME type from filename extension.
        
        Args:
            filename: Name of the file
            
        Returns:
            str: MIME type or 'application/octet-stream' if not found
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    def validate_file_content(self, file_content: bytes, expected_extension: str) -> bool:
        """
        Validate that file content matches expected extension.
        
        Args:
            file_content: Bytes content of the file
            expected_extension: Expected file extension
            
        Returns:
            bool: True if content matches expected type
        """
        detected_type = self.detect_file_type_from_content(file_content)
        
        if not detected_type:
            return True  # Can't detect, assume valid
        
        # Map detected types to extensions
        type_to_ext = {
            'pdf': 'pdf',
            'png': 'png', 
            'jpg': 'jpg',
            'gif': 'gif',
            'docx': 'docx',
            'doc': 'doc',
            'zip': 'zip',
            'rar': 'rar',
            'txt': 'txt'
        }
        
        expected_type = type_to_ext.get(expected_extension.lower())
        return detected_type == expected_type if expected_type else True
