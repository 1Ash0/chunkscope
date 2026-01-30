"""
PDF Processor Service
Robust PDF text extraction with character-level coordinates using PyMuPDF
"""
import hashlib
import time
from pathlib import Path
from typing import Generator, Optional

import fitz  # PyMuPDF

from app.core.errors import CorruptedPDFError, PasswordProtectedError, PDFExtractionError
from app.core.logging import get_logger
from app.schemas.pdf_schemas import (
    BlockType,
    BoundingBox,
    CharacterInfo,
    DocumentMetadata,
    ExtractedDocument,
    ExtractedPage,
    ExtractionOptions,
    Heading,
    TableCell,
    TableData,
    TextBlock,
    TextLine,
    TextSpan,
)

logger = get_logger(__name__)


class PDFProcessor:
    """
    PDF text extraction service with character-level coordinates.
    
    Uses PyMuPDF (fitz) for fast, memory-efficient extraction.
    Supports:
    - Character-level bounding boxes
    - Multi-column layout detection
    - Table detection
    - Heading extraction
    - Streaming for large documents
    """
    
    # Font size thresholds for heading detection
    HEADING_SIZE_MULTIPLIER = 1.2  # 20% larger than average = heading
    
    def __init__(self, default_options: Optional[ExtractionOptions] = None):
        self.default_options = default_options or ExtractionOptions()
    
    def extract_document(
        self,
        path: str | Path,
        options: Optional[ExtractionOptions] = None
    ) -> ExtractedDocument:
        """
        Extract all content from a PDF document.
        
        Args:
            path: Path to the PDF file
            options: Extraction options (uses defaults if not provided)
            
        Returns:
            ExtractedDocument with pages, metadata, and headings
            
        Raises:
            CorruptedPDFError: If PDF is corrupted or invalid
            PasswordProtectedError: If PDF requires a password
            PDFExtractionError: For other extraction failures
        """
        opts = options or self.default_options
        start_time = time.time()
        path = Path(path)
        
        try:
            doc = fitz.open(str(path))
        except fitz.FileDataError as e:
            logger.error("pdf_corrupted", path=str(path), error=str(e))
            raise CorruptedPDFError(f"Cannot open PDF: {e}")
        except FileNotFoundError as e:
            logger.error("pdf_not_found", path=str(path), error=str(e))
            raise PDFExtractionError(f"PDF file not found: {path}")
        except Exception as e:
            logger.error("pdf_open_failed", path=str(path), error=str(e))
            raise PDFExtractionError(f"Failed to open PDF: {e}")
        
        # Calculate file hash for caching (after successful open)
        file_hash = self._calculate_file_hash(path)
        
        try:
            # Check for password protection
            if doc.is_encrypted:
                doc.close()
                raise PasswordProtectedError()
            
            # Extract metadata
            metadata = self._extract_metadata(doc)
            
            # Determine page range
            start_page, end_page = self._get_page_range(doc.page_count, opts)
            
            # Extract pages
            pages: list[ExtractedPage] = []
            all_headings: list[Heading] = []
            avg_font_size = self._calculate_avg_font_size(doc, start_page, min(start_page + 5, end_page))
            
            for page_num in range(start_page, end_page):
                page = doc.load_page(page_num)
                extracted_page = self._extract_page(page, page_num, opts, avg_font_size)
                pages.append(extracted_page)
                all_headings.extend(extracted_page.headings)
            
            extraction_time_ms = int((time.time() - start_time) * 1000)
            
            # Update metadata flags based on extraction
            metadata.has_tables = any(len(p.tables) > 0 for p in pages)
            
            result = ExtractedDocument(
                page_count=doc.page_count,
                metadata=metadata,
                pages=pages,
                headings=all_headings,
                extraction_time_ms=extraction_time_ms,
                file_hash=file_hash
            )
            
            logger.info(
                "pdf_extracted",
                path=str(path),
                pages=len(pages),
                blocks=result.total_blocks,
                tables=result.total_tables,
                time_ms=extraction_time_ms
            )
            
            return result
            
        finally:
            doc.close()
    
    def stream_pages(
        self,
        path: str | Path,
        options: Optional[ExtractionOptions] = None
    ) -> Generator[ExtractedPage, None, None]:
        """
        Memory-efficient page-by-page extraction for large PDFs.
        
        Yields one page at a time, freeing memory after each page.
        Ideal for documents with 1000+ pages.
        
        Args:
            path: Path to the PDF file
            options: Extraction options
            
        Yields:
            ExtractedPage for each page
        """
        opts = options or self.default_options
        path = Path(path)
        
        try:
            doc = fitz.open(str(path))
        except fitz.FileDataError as e:
            raise CorruptedPDFError(f"Cannot open PDF: {e}")
        except Exception as e:
            raise PDFExtractionError(f"Failed to open PDF: {e}")
        
        try:
            if doc.is_encrypted:
                raise PasswordProtectedError()
            
            start_page, end_page = self._get_page_range(doc.page_count, opts)
            avg_font_size = self._calculate_avg_font_size(doc, start_page, min(start_page + 5, end_page))
            
            for page_num in range(start_page, end_page):
                page = doc.load_page(page_num)
                yield self._extract_page(page, page_num, opts, avg_font_size)
                # Page is automatically freed when we move to next iteration
                
        finally:
            doc.close()
    
    def extract_page(
        self,
        path: str | Path,
        page_number: int,
        options: Optional[ExtractionOptions] = None
    ) -> ExtractedPage:
        """
        Extract a single page from a PDF.
        
        Args:
            path: Path to the PDF file
            page_number: 0-indexed page number
            options: Extraction options
            
        Returns:
            ExtractedPage for the specified page
        """
        opts = options or self.default_options
        path = Path(path)
        
        try:
            doc = fitz.open(str(path))
        except fitz.FileDataError as e:
            raise CorruptedPDFError(f"Cannot open PDF: {e}")
        
        try:
            if doc.is_encrypted:
                raise PasswordProtectedError()
                
            if page_number < 0 or page_number >= doc.page_count:
                raise PDFExtractionError(
                    f"Page {page_number} out of range (0-{doc.page_count - 1})"
                )
            
            avg_font_size = self._calculate_avg_font_size(doc, page_number, page_number + 1)
            page = doc.load_page(page_number)
            return self._extract_page(page, page_number, opts, avg_font_size)
            
        finally:
            doc.close()
    
    def get_page_count(self, path: str | Path) -> int:
        """Get the total page count without full extraction."""
        try:
            doc = fitz.open(str(path))
            count = doc.page_count
            doc.close()
            return count
        except Exception as e:
            raise PDFExtractionError(f"Failed to get page count: {e}")
    
    def _extract_page(
        self,
        page: fitz.Page,
        page_num: int,
        opts: ExtractionOptions,
        avg_font_size: float
    ) -> ExtractedPage:
        """Extract content from a single PyMuPDF page object."""
        # Get page dimensions
        rect = page.rect
        
        # Extract text with detailed structure
        blocks = self._extract_blocks(page, page_num, opts, avg_font_size)
        
        # Detect multi-column layout
        if opts.detect_columns:
            blocks = self._detect_columns(blocks, rect.width)
        
        # Extract tables
        tables: list[TableData] = []
        if opts.extract_tables:
            tables = self._extract_tables(page)
        
        # Extract headings
        headings: list[Heading] = []
        if opts.detect_headings:
            headings = self._extract_headings(blocks, page_num, avg_font_size)
        
        return ExtractedPage(
            page_number=page_num,
            width=rect.width,
            height=rect.height,
            rotation=page.rotation,
            blocks=blocks,
            tables=tables,
            headings=headings
        )
    
    def _extract_blocks(
        self,
        page: fitz.Page,
        page_num: int,
        opts: ExtractionOptions,
        avg_font_size: float
    ) -> list[TextBlock]:
        """Extract text blocks with optional character-level details."""
        # Use "dict" output for full structure
        page_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        
        blocks: list[TextBlock] = []
        
        for block_idx, block in enumerate(page_dict.get("blocks", [])):
            # Skip image blocks for now (type 1)
            if block.get("type") == 1:
                continue
                
            bbox = BoundingBox(
                x0=block["bbox"][0],
                y0=block["bbox"][1],
                x1=block["bbox"][2],
                y1=block["bbox"][3]
            )
            
            lines: list[TextLine] = []
            block_text_parts = []
            
            for line in block.get("lines", []):
                line_bbox = BoundingBox(
                    x0=line["bbox"][0],
                    y0=line["bbox"][1],
                    x1=line["bbox"][2],
                    y1=line["bbox"][3]
                )
                
                spans: list[TextSpan] = []
                line_text_parts = []
                
                for span in line.get("spans", []):
                    span_bbox = BoundingBox(
                        x0=span["bbox"][0],
                        y0=span["bbox"][1],
                        x1=span["bbox"][2],
                        y1=span["bbox"][3]
                    )
                    
                    # Extract character-level info if requested
                    characters: list[CharacterInfo] = []
                    if opts.extract_characters:
                        characters = self._extract_characters(span)
                    
                    text_span = TextSpan(
                        text=span.get("text", ""),
                        bbox=span_bbox,
                        font=span.get("font", ""),
                        size=span.get("size", 0),
                        flags=span.get("flags", 0),
                        color=span.get("color"),
                        characters=characters
                    )
                    spans.append(text_span)
                    line_text_parts.append(span.get("text", ""))
                
                text_line = TextLine(
                    text="".join(line_text_parts),
                    bbox=line_bbox,
                    spans=spans
                )
                lines.append(text_line)
                block_text_parts.append(text_line.text)
            
            text_block = TextBlock(
                text="\n".join(block_text_parts),
                bbox=bbox,
                block_type=BlockType.TEXT,
                block_number=block_idx,
                lines=lines
            )
            blocks.append(text_block)
        
        return blocks
    
    def _extract_characters(self, span: dict) -> list[CharacterInfo]:
        """Extract character-level coordinates from a span."""
        characters = []
        text = span.get("text", "")
        
        # PyMuPDF provides origin (x, y) for the span
        # We need to estimate character positions
        if not text:
            return characters
        
        span_bbox = span["bbox"]
        span_width = span_bbox[2] - span_bbox[0]
        char_width = span_width / len(text) if text else 0
        char_height = span_bbox[3] - span_bbox[1]
        
        x = span_bbox[0]
        y = span_bbox[1]
        
        for char in text:
            characters.append(CharacterInfo(
                char=char,
                x=x,
                y=y,
                width=char_width,
                height=char_height,
                font=span.get("font", ""),
                size=span.get("size", 0),
                color=span.get("color")
            ))
            x += char_width
        
        return characters
    
    def _detect_columns(self, blocks: list[TextBlock], page_width: float) -> list[TextBlock]:
        """Detect multi-column layout and assign column indices."""
        if not blocks or len(blocks) < 2:
            return blocks
        
        # Get x-coordinates of block centers
        centers = [(b.bbox.x0 + b.bbox.x1) / 2 for b in blocks]
        
        # Simple heuristic: if centers cluster around multiple x positions
        # We use a threshold-based approach
        mid_point = page_width / 2
        threshold = page_width * 0.1  # 10% tolerance
        
        left_blocks = []
        right_blocks = []
        center_blocks = []
        
        for block, center in zip(blocks, centers):
            if center < mid_point - threshold:
                left_blocks.append(block)
            elif center > mid_point + threshold:
                right_blocks.append(block)
            else:
                center_blocks.append(block)
        
        # Only assign columns if we have a clear two-column layout
        if left_blocks and right_blocks and len(center_blocks) < len(blocks) * 0.3:
            for block in left_blocks:
                block.column_index = 0
            for block in right_blocks:
                block.column_index = 1
            # Center blocks are ambiguous
            for block in center_blocks:
                block.column_index = None
        else:
            # Single column layout
            for block in blocks:
                block.column_index = 0
        
        return blocks
    
    def _extract_tables(self, page: fitz.Page) -> list[TableData]:
        """
        Detect and extract tables from a page.
        
        Uses PyMuPDF's table detection. For more accurate table extraction,
        consider using pdfplumber as a fallback.
        """
        tables: list[TableData] = []
        
        try:
            # PyMuPDF 1.23+ has table detection
            page_tables = page.find_tables()
            
            for table in page_tables:
                bbox = BoundingBox(
                    x0=table.bbox[0],
                    y0=table.bbox[1],
                    x1=table.bbox[2],
                    y1=table.bbox[3]
                )
                
                cells: list[TableCell] = []
                table_data = table.extract()
                
                for row_idx, row in enumerate(table_data):
                    for col_idx, cell_text in enumerate(row):
                        # PyMuPDF doesn't provide per-cell bboxes easily
                        # Create approximate cell bbox
                        cells.append(TableCell(
                            text=cell_text or "",
                            row=row_idx,
                            col=col_idx,
                            bbox=bbox,  # Simplified - use table bbox
                            rowspan=1,
                            colspan=1
                        ))
                
                tables.append(TableData(
                    bbox=bbox,
                    rows=len(table_data),
                    cols=len(table_data[0]) if table_data else 0,
                    cells=cells
                ))
                
        except Exception as e:
            # Table detection may fail on some PDFs
            logger.warning("table_detection_failed", error=str(e))
        
        return tables
    
    def _extract_headings(
        self,
        blocks: list[TextBlock],
        page_num: int,
        avg_font_size: float
    ) -> list[Heading]:
        """Detect headings based on font size and formatting."""
        headings: list[Heading] = []
        
        heading_threshold = avg_font_size * self.HEADING_SIZE_MULTIPLIER
        
        for block in blocks:
            # Check if block has larger font
            max_font_size = 0
            for line in block.lines:
                for span in line.spans:
                    max_font_size = max(max_font_size, span.size)
            
            if max_font_size > heading_threshold:
                # Determine heading level based on size
                size_ratio = max_font_size / avg_font_size
                if size_ratio > 2.0:
                    level = 1
                elif size_ratio > 1.6:
                    level = 2
                elif size_ratio > 1.4:
                    level = 3
                else:
                    level = 4
                
                # Skip very long blocks (not headings)
                if len(block.text) < 200:
                    headings.append(Heading(
                        text=block.text.strip(),
                        level=level,
                        bbox=block.bbox,
                        page_number=page_num
                    ))
        
        return headings
    
    def _extract_metadata(self, doc: fitz.Document) -> DocumentMetadata:
        """Extract document metadata."""
        meta = doc.metadata or {}
        
        # Parse keywords
        keywords = []
        if meta.get("keywords"):
            keywords = [k.strip() for k in meta["keywords"].split(",")]
        
        return DocumentMetadata(
            title=meta.get("title"),
            author=meta.get("author"),
            subject=meta.get("subject"),
            creator=meta.get("creator"),
            producer=meta.get("producer"),
            creation_date=meta.get("creationDate"),
            modification_date=meta.get("modDate"),
            keywords=keywords,
            is_encrypted=doc.is_encrypted,
            is_ocr_required=self._check_ocr_required(doc),
            has_images=self._check_has_images(doc)
        )
    
    def _check_ocr_required(self, doc: fitz.Document) -> bool:
        """Check if document needs OCR (has images but no text)."""
        # Sample first few pages
        for page_num in range(min(3, doc.page_count)):
            page = doc.load_page(page_num)
            text = page.get_text().strip()
            images = page.get_images()
            
            if images and not text:
                return True
        
        return False
    
    def _check_has_images(self, doc: fitz.Document) -> bool:
        """Check if document contains images."""
        for page_num in range(min(5, doc.page_count)):
            page = doc.load_page(page_num)
            if page.get_images():
                return True
        return False
    
    def _calculate_avg_font_size(
        self,
        doc: fitz.Document,
        start_page: int,
        end_page: int
    ) -> float:
        """Calculate average font size across sample pages."""
        sizes = []
        
        for page_num in range(start_page, min(end_page, doc.page_count)):
            page = doc.load_page(page_num)
            page_dict = page.get_text("dict")
            
            for block in page_dict.get("blocks", []):
                if block.get("type") == 1:  # Skip images
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if span.get("size", 0) > 0:
                            sizes.append(span["size"])
        
        return sum(sizes) / len(sizes) if sizes else 12.0
    
    def _get_page_range(
        self,
        total_pages: int,
        opts: ExtractionOptions
    ) -> tuple[int, int]:
        """Determine start and end page based on options."""
        start = 0
        end = total_pages
        
        if opts.page_range:
            start = max(0, opts.page_range[0])
            end = min(total_pages, opts.page_range[1])
        
        if opts.max_pages:
            end = min(end, start + opts.max_pages)
        
        return start, end
    
    def _calculate_file_hash(self, path: Path) -> str:
        """Calculate SHA-256 hash of file for caching."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()


# Singleton instance for convenience
pdf_processor = PDFProcessor()
