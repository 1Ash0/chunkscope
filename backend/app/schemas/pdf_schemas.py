"""
PDF Extraction Schemas
Data models for PDF text extraction with character-level coordinates
"""
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class BlockType(str, Enum):
    """Type of content block in a PDF."""
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"


class BoundingBox(BaseModel):
    """Bounding box coordinates (PDF coordinate system)."""
    x0: float = Field(description="Left edge x-coordinate")
    y0: float = Field(description="Top edge y-coordinate")
    x1: float = Field(description="Right edge x-coordinate")
    y1: float = Field(description="Bottom edge y-coordinate")
    
    @property
    def width(self) -> float:
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        return self.y1 - self.y0
    
    @property
    def center(self) -> tuple[float, float]:
        return ((self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2)


class CharacterInfo(BaseModel):
    """Character-level information with coordinates."""
    char: str = Field(description="The character")
    x: float = Field(description="X-coordinate (left edge)")
    y: float = Field(description="Y-coordinate (top edge)")
    width: float = Field(description="Character width")
    height: float = Field(description="Character height")
    font: str = Field(default="", description="Font name")
    size: float = Field(default=0, description="Font size in points")
    color: Optional[int] = Field(default=None, description="Text color as integer")


class TextSpan(BaseModel):
    """A span of text with consistent formatting."""
    text: str
    bbox: BoundingBox
    font: str = ""
    size: float = 0
    flags: int = 0  # Bold=1, Italic=2, etc.
    color: Optional[int] = None
    characters: list[CharacterInfo] = Field(default_factory=list)


class TextLine(BaseModel):
    """A line of text within a block."""
    text: str
    bbox: BoundingBox
    spans: list[TextSpan] = Field(default_factory=list)


class TextBlock(BaseModel):
    """A block of text (paragraph, heading, etc.)."""
    text: str
    bbox: BoundingBox
    block_type: BlockType = BlockType.TEXT
    block_number: int = 0
    lines: list[TextLine] = Field(default_factory=list)
    
    # For multi-column detection
    column_index: Optional[int] = None


class TableCell(BaseModel):
    """A cell within a table."""
    text: str
    row: int
    col: int
    bbox: BoundingBox
    rowspan: int = 1
    colspan: int = 1


class TableData(BaseModel):
    """Extracted table structure."""
    bbox: BoundingBox
    rows: int
    cols: int
    cells: list[TableCell] = Field(default_factory=list)
    
    def to_list(self) -> list[list[str]]:
        """Convert to 2D list of strings."""
        result = [["" for _ in range(self.cols)] for _ in range(self.rows)]
        for cell in self.cells:
            if 0 <= cell.row < self.rows and 0 <= cell.col < self.cols:
                result[cell.row][cell.col] = cell.text
        return result


class Heading(BaseModel):
    """Detected heading/section."""
    text: str
    level: int = Field(ge=1, le=6, description="Heading level 1-6")
    bbox: BoundingBox
    page_number: int


class ExtractedPage(BaseModel):
    """Extraction results for a single page."""
    page_number: int = Field(ge=0, description="0-indexed page number")
    width: float
    height: float
    rotation: int = 0
    blocks: list[TextBlock] = Field(default_factory=list)
    tables: list[TableData] = Field(default_factory=list)
    headings: list[Heading] = Field(default_factory=list)
    
    @property
    def full_text(self) -> str:
        """Get all text from the page."""
        return "\n".join(block.text for block in self.blocks)
    
    @property
    def column_count(self) -> int:
        """Estimate number of columns on the page."""
        if not self.blocks:
            return 1
        columns = set(b.column_index for b in self.blocks if b.column_index is not None)
        return len(columns) if columns else 1


class DocumentMetadata(BaseModel):
    """PDF document metadata."""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    
    # Additional computed metadata
    is_encrypted: bool = False
    is_ocr_required: bool = False
    has_images: bool = False
    has_tables: bool = False


class ExtractedDocument(BaseModel):
    """Complete document extraction result."""
    page_count: int
    metadata: DocumentMetadata
    pages: list[ExtractedPage] = Field(default_factory=list)
    headings: list[Heading] = Field(default_factory=list)  # All headings across pages
    
    # Processing info
    extraction_time_ms: Optional[int] = None
    file_hash: Optional[str] = None
    
    @property
    def full_text(self) -> str:
        """Get all text from the document."""
        return "\n\n".join(page.full_text for page in self.pages)
    
    @property
    def total_blocks(self) -> int:
        return sum(len(page.blocks) for page in self.pages)
    
    @property
    def total_tables(self) -> int:
        return sum(len(page.tables) for page in self.pages)


class ExtractionOptions(BaseModel):
    """Options for PDF extraction."""
    extract_characters: bool = Field(
        default=False, 
        description="Extract character-level coordinates (slower)"
    )
    extract_tables: bool = Field(
        default=True, 
        description="Detect and extract tables"
    )
    detect_headings: bool = Field(
        default=True, 
        description="Detect headings based on font size"
    )
    detect_columns: bool = Field(
        default=True, 
        description="Detect multi-column layouts"
    )
    max_pages: Optional[int] = Field(
        default=None, 
        description="Maximum pages to process (None = all)"
    )
    page_range: Optional[tuple[int, int]] = Field(
        default=None, 
        description="Range of pages to process (start, end)"
    )
