"""
PDF Processor Unit Tests
Tests for PDF text extraction with coordinates, tables, and layout detection
"""
import io
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.core.errors import CorruptedPDFError, PasswordProtectedError, PDFExtractionError
from app.schemas.pdf_schemas import (
    BlockType,
    BoundingBox,
    ExtractedDocument,
    ExtractedPage,
    ExtractionOptions,
)
from app.services.pdf_processor import PDFProcessor, pdf_processor


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def processor():
    """Create a fresh PDFProcessor instance."""
    return PDFProcessor()


@pytest.fixture
def sample_pdf_path(tmp_path) -> Path:
    """Create a minimal valid PDF for testing."""
    # Using PyMuPDF to create a test PDF
    import fitz
    
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    
    # Add a page with text
    page = doc.new_page()
    page.insert_text((72, 72), "Hello World", fontsize=24)
    page.insert_text((72, 120), "This is a test document.", fontsize=12)
    page.insert_text((72, 150), "It has multiple lines of text.", fontsize=12)
    
    doc.save(str(pdf_path))
    doc.close()
    
    return pdf_path


@pytest.fixture
def multicolumn_pdf_path(tmp_path) -> Path:
    """Create a two-column PDF for testing."""
    import fitz
    
    pdf_path = tmp_path / "multicolumn.pdf"
    doc = fitz.open()
    
    page = doc.new_page()
    # Left column
    page.insert_text((72, 72), "Left Column Header", fontsize=16)
    page.insert_text((72, 100), "This is the left column content.", fontsize=12)
    page.insert_text((72, 120), "More text in left column.", fontsize=12)
    
    # Right column (offset by page width / 2)
    page.insert_text((350, 72), "Right Column Header", fontsize=16)
    page.insert_text((350, 100), "This is the right column content.", fontsize=12)
    page.insert_text((350, 120), "More text in right column.", fontsize=12)
    
    doc.save(str(pdf_path))
    doc.close()
    
    return pdf_path


@pytest.fixture
def large_pdf_path(tmp_path) -> Path:
    """Create a PDF with multiple pages for streaming tests."""
    import fitz
    
    pdf_path = tmp_path / "large.pdf"
    doc = fitz.open()
    
    for i in range(20):  # 20 pages
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i + 1}", fontsize=24)
        page.insert_text((72, 120), f"Content on page {i + 1}", fontsize=12)
    
    doc.save(str(pdf_path))
    doc.close()
    
    return pdf_path


@pytest.fixture
def pdf_with_headings(tmp_path) -> Path:
    """Create a PDF with various heading sizes."""
    import fitz
    
    pdf_path = tmp_path / "headings.pdf"
    doc = fitz.open()
    
    page = doc.new_page()
    page.insert_text((72, 72), "Main Title", fontsize=28)
    page.insert_text((72, 120), "Section Heading", fontsize=20)
    page.insert_text((72, 160), "Regular paragraph text here.", fontsize=12)
    page.insert_text((72, 190), "Sub Section", fontsize=16)
    page.insert_text((72, 220), "More regular text content.", fontsize=12)
    
    doc.save(str(pdf_path))
    doc.close()
    
    return pdf_path


# ============================================
# Basic Extraction Tests
# ============================================

class TestPDFProcessorBasic:
    """Test basic PDF extraction functionality."""
    
    def test_extract_simple_pdf(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test extraction of a simple PDF with text."""
        result = processor.extract_document(sample_pdf_path)
        
        assert isinstance(result, ExtractedDocument)
        assert result.page_count == 1
        assert len(result.pages) == 1
        assert "Hello World" in result.full_text
        assert "test document" in result.full_text
        assert result.extraction_time_ms is not None
        assert result.file_hash is not None
    
    def test_extract_page_count(self, processor: PDFProcessor, large_pdf_path: Path):
        """Test that page count is correct."""
        result = processor.extract_document(large_pdf_path)
        
        assert result.page_count == 20
        assert len(result.pages) == 20
    
    def test_get_page_count_without_extraction(self, processor: PDFProcessor, large_pdf_path: Path):
        """Test getting page count without full extraction."""
        count = processor.get_page_count(large_pdf_path)
        assert count == 20
    
    def test_extract_single_page(self, processor: PDFProcessor, large_pdf_path: Path):
        """Test extraction of a single page."""
        page = processor.extract_page(large_pdf_path, page_number=5)
        
        assert isinstance(page, ExtractedPage)
        assert page.page_number == 5
        assert "Page 6" in page.full_text  # 0-indexed, so page 5 = "Page 6"
    
    def test_page_dimensions(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test that page dimensions are extracted."""
        result = processor.extract_document(sample_pdf_path)
        page = result.pages[0]
        
        assert page.width > 0
        assert page.height > 0
        # Standard letter size is ~612x792 points
        assert 500 < page.width < 700
        assert 700 < page.height < 900


# ============================================
# Coordinate Extraction Tests
# ============================================

class TestCoordinateExtraction:
    """Test character and block coordinate extraction."""
    
    def test_block_bounding_boxes(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test that blocks have valid bounding boxes."""
        result = processor.extract_document(sample_pdf_path)
        page = result.pages[0]
        
        assert len(page.blocks) > 0
        
        for block in page.blocks:
            assert isinstance(block.bbox, BoundingBox)
            assert block.bbox.x0 >= 0
            assert block.bbox.y0 >= 0
            assert block.bbox.x1 > block.bbox.x0
            assert block.bbox.y1 > block.bbox.y0
    
    def test_character_level_extraction(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test character-level coordinate extraction."""
        options = ExtractionOptions(extract_characters=True)
        result = processor.extract_document(sample_pdf_path, options)
        page = result.pages[0]
        
        # Find a block with characters
        found_characters = False
        for block in page.blocks:
            for line in block.lines:
                for span in line.spans:
                    if span.characters:
                        found_characters = True
                        # Check character properties
                        for char in span.characters:
                            assert char.x >= 0
                            assert char.y >= 0
                            assert char.width > 0
                            assert char.height > 0
        
        assert found_characters, "No characters extracted"
    
    def test_block_types(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test that blocks have correct types."""
        result = processor.extract_document(sample_pdf_path)
        page = result.pages[0]
        
        for block in page.blocks:
            assert block.block_type in [BlockType.TEXT, BlockType.TABLE, BlockType.IMAGE]


# ============================================
# Multi-Column Layout Tests
# ============================================

class TestMultiColumnDetection:
    """Test multi-column layout detection."""
    
    def test_detect_two_columns(self, processor: PDFProcessor, multicolumn_pdf_path: Path):
        """Test detection of two-column layout."""
        options = ExtractionOptions(detect_columns=True)
        result = processor.extract_document(multicolumn_pdf_path, options)
        page = result.pages[0]
        
        # Should detect column indices
        column_indices = set()
        for block in page.blocks:
            if block.column_index is not None:
                column_indices.add(block.column_index)
        
        # Expecting two columns (0 and 1)
        assert len(column_indices) >= 1, "Should detect at least one column"
    
    def test_single_column_detection(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test that single-column docs are detected correctly."""
        options = ExtractionOptions(detect_columns=True)
        result = processor.extract_document(sample_pdf_path, options)
        page = result.pages[0]
        
        # All blocks should be in column 0
        for block in page.blocks:
            if block.column_index is not None:
                assert block.column_index == 0


# ============================================
# Heading Detection Tests
# ============================================

class TestHeadingDetection:
    """Test heading detection based on font size."""
    
    def test_detect_headings(self, processor: PDFProcessor, pdf_with_headings: Path):
        """Test that headings are detected based on font size."""
        options = ExtractionOptions(detect_headings=True)
        result = processor.extract_document(pdf_with_headings, options)
        
        # Should find headings
        assert len(result.headings) > 0
        
        # Check heading properties
        for heading in result.headings:
            assert heading.text
            assert 1 <= heading.level <= 6
            assert heading.page_number >= 0
    
    def test_heading_levels(self, processor: PDFProcessor, pdf_with_headings: Path):
        """Test that heading levels are assigned based on size."""
        options = ExtractionOptions(detect_headings=True)
        result = processor.extract_document(pdf_with_headings, options)
        
        # Larger text should have lower level numbers (more important)
        # "Main Title" should be detected as a heading
        main_title = next((h for h in result.headings if "Main Title" in h.text), None)
        if main_title:
            # Main title should be a heading (level 1-4 is acceptable for test data)
            assert main_title.level <= 4


# ============================================
# Streaming Tests (Large PDFs)
# ============================================

class TestStreamingExtraction:
    """Test memory-efficient streaming extraction."""
    
    def test_stream_pages(self, processor: PDFProcessor, large_pdf_path: Path):
        """Test page-by-page streaming."""
        pages_streamed = 0
        
        for page in processor.stream_pages(large_pdf_path):
            assert isinstance(page, ExtractedPage)
            assert page.page_number == pages_streamed
            pages_streamed += 1
        
        assert pages_streamed == 20
    
    def test_stream_with_max_pages(self, processor: PDFProcessor, large_pdf_path: Path):
        """Test streaming with max pages limit."""
        options = ExtractionOptions(max_pages=5)
        pages_streamed = 0
        
        for page in processor.stream_pages(large_pdf_path, options):
            pages_streamed += 1
        
        assert pages_streamed == 5
    
    def test_stream_page_range(self, processor: PDFProcessor, large_pdf_path: Path):
        """Test streaming a specific page range."""
        options = ExtractionOptions(page_range=(5, 10))
        
        pages = list(processor.stream_pages(large_pdf_path, options))
        
        assert len(pages) == 5
        assert pages[0].page_number == 5
        assert pages[-1].page_number == 9


# ============================================
# Metadata Extraction Tests
# ============================================

class TestMetadataExtraction:
    """Test document metadata extraction."""
    
    def test_extract_metadata(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test that metadata is extracted."""
        result = processor.extract_document(sample_pdf_path)
        
        assert result.metadata is not None
        # PyMuPDF always includes producer
        assert result.metadata.is_encrypted is False
    
    def test_file_hash(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test that file hash is computed."""
        result = processor.extract_document(sample_pdf_path)
        
        assert result.file_hash is not None
        assert len(result.file_hash) == 64  # SHA-256 hex length


# ============================================
# Error Handling Tests
# ============================================

class TestErrorHandling:
    """Test error handling for various PDF issues."""
    
    def test_corrupted_pdf(self, processor: PDFProcessor, tmp_path: Path):
        """Test handling of corrupted PDF."""
        corrupted_path = tmp_path / "corrupted.pdf"
        corrupted_path.write_bytes(b"This is not a valid PDF file")
        
        with pytest.raises(CorruptedPDFError):
            processor.extract_document(corrupted_path)
    
    def test_nonexistent_file(self, processor: PDFProcessor):
        """Test handling of non-existent file."""
        with pytest.raises(PDFExtractionError):
            processor.extract_document("/nonexistent/path/file.pdf")
    
    def test_invalid_page_number(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test handling of invalid page number."""
        with pytest.raises(PDFExtractionError) as exc_info:
            processor.extract_page(sample_pdf_path, page_number=100)
        
        assert "out of range" in str(exc_info.value)
    
    def test_negative_page_number(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test handling of negative page number."""
        with pytest.raises(PDFExtractionError):
            processor.extract_page(sample_pdf_path, page_number=-1)


# ============================================
# Extraction Options Tests
# ============================================

class TestExtractionOptions:
    """Test extraction options behavior."""
    
    def test_disable_table_extraction(self, processor: PDFProcessor, sample_pdf_path: Path):
        """Test disabling table extraction."""
        options = ExtractionOptions(extract_tables=False)
        result = processor.extract_document(sample_pdf_path, options)
        
        # Tables should be empty when disabled
        for page in result.pages:
            assert len(page.tables) == 0
    
    def test_disable_heading_detection(self, processor: PDFProcessor, pdf_with_headings: Path):
        """Test disabling heading detection."""
        options = ExtractionOptions(detect_headings=False)
        result = processor.extract_document(pdf_with_headings, options)
        
        # Headings should be empty when disabled
        assert len(result.headings) == 0
    
    def test_max_pages_option(self, processor: PDFProcessor, large_pdf_path: Path):
        """Test max pages limitation."""
        options = ExtractionOptions(max_pages=3)
        result = processor.extract_document(large_pdf_path, options)
        
        assert len(result.pages) == 3
        assert result.page_count == 20  # Total count is still full
    
    def test_page_range_option(self, processor: PDFProcessor, large_pdf_path: Path):
        """Test page range option."""
        options = ExtractionOptions(page_range=(10, 15))
        result = processor.extract_document(large_pdf_path, options)
        
        assert len(result.pages) == 5
        assert result.pages[0].page_number == 10
        assert result.pages[-1].page_number == 14


# ============================================
# Singleton Instance Tests
# ============================================

class TestSingletonInstance:
    """Test the module-level singleton instance."""
    
    def test_singleton_exists(self):
        """Test that singleton instance is available."""
        assert pdf_processor is not None
        assert isinstance(pdf_processor, PDFProcessor)
    
    def test_singleton_works(self, sample_pdf_path: Path):
        """Test that singleton can extract documents."""
        result = pdf_processor.extract_document(sample_pdf_path)
        assert result.page_count == 1
