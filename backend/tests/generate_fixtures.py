"""
Generate sample PDF fixtures for testing document analyzer
"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# Create fixtures directory
fixtures_dir = Path(__file__).parent / "fixtures"
fixtures_dir.mkdir(exist_ok=True)

def create_legal_contract():
    """Create a sample legal contract PDF"""
    pdf_path = fixtures_dir / "sample_contract.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30
    )
    story.append(Paragraph("PROFESSIONAL SERVICES AGREEMENT", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Sections with legal language
    sections = [
        ("1. PARTIES", "This Agreement is entered into as of January 1, 2024, by and between ChunkScope Inc., a Delaware corporation with its principal place of business at 123 Main Street, San Francisco, CA 94102 (hereinafter referred to as 'Company'), and the Client identified in the Statement of Work attached hereto as Exhibit A (hereinafter referred to as 'Client')."),
        ("2. SCOPE OF SERVICES", "The Company agrees to provide professional consulting services as described in the Statement of Work. The services shall include but not be limited to: (a) technical consultation regarding document processing systems; (b) implementation of retrieval-augmented generation pipelines; (c) performance optimization and evaluation; and (d) such other services as may be mutually agreed upon in writing by the parties."),
        ("3. TERM AND TERMINATION", "This Agreement shall commence on the Effective Date and shall continue for a period of twelve (12) months unless earlier terminated in accordance with the provisions herein. Either party may terminate this Agreement upon thirty (30) days written notice to the other party. In the event of termination, Client shall pay Company for all services rendered through the effective date of termination."),
        ("4. COMPENSATION", "In consideration for the services provided hereunder, Client agrees to pay Company the fees set forth in the Statement of Work. Payment terms are Net 30 days from the date of invoice. Late payments shall accrue interest at the rate of 1.5% per month or the maximum rate permitted by law, whichever is less."),
        ("5. CONFIDENTIALITY", "Each party acknowledges that it may have access to certain confidential information of the other party. Each party agrees to maintain the confidentiality of such information and not to disclose it to any third party without the prior written consent of the disclosing party, except as required by law."),
    ]
    
    for heading, text in sections:
        story.append(Paragraph(heading, styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(text, styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
    
    doc.build(story)
    print(f"Created: {pdf_path}")

def create_technical_docs():
    """Create a sample technical documentation PDF"""
    pdf_path = fixtures_dir / "technical_docs.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph("ChunkScope API Documentation", styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    
    # Introduction
    story.append(Paragraph("1. Introduction", styles['Heading1']))
    story.append(Paragraph(
        "ChunkScope provides a comprehensive API for document processing and retrieval-augmented generation. "
        "This documentation covers the core endpoints, authentication, and usage examples.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Code example
    story.append(Paragraph("2. Authentication", styles['Heading1']))
    story.append(Paragraph("All API requests require authentication using JWT tokens:", styles['BodyText']))
    story.append(Spacer(1, 0.1*inch))
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=9,
        leftIndent=20,
        backColor=colors.lightgrey
    )
    
    story.append(Paragraph(
        "import requests<br/>"
        "<br/>"
        "headers = {<br/>"
        "    'Authorization': 'Bearer YOUR_TOKEN_HERE',<br/>"
        "    'Content-Type': 'application/json'<br/>"
        "}<br/>"
        "<br/>"
        "response = requests.get(<br/>"
        "    'https://api.chunkscope.com/v1/documents',<br/>"
        "    headers=headers<br/>"
        ")",
        code_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Endpoints table
    story.append(Paragraph("3. Core Endpoints", styles['Heading1']))
    story.append(Spacer(1, 0.1*inch))
    
    data = [
        ['Method', 'Endpoint', 'Description'],
        ['GET', '/api/v1/documents', 'List all documents'],
        ['POST', '/api/v1/documents', 'Upload a new document'],
        ['GET', '/api/v1/chunks', 'Retrieve document chunks'],
        ['POST', '/api/v1/analyze/document', 'Analyze document structure'],
    ]
    
    table = Table(data, colWidths=[1*inch, 2.5*inch, 2.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    
    doc.build(story)
    print(f"Created: {pdf_path}")

def create_blog_post():
    """Create a sample blog post PDF"""
    pdf_path = fixtures_dir / "blog_post.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph("The Future of Document Processing with AI", styles['Title']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("By Jane Smith | January 15, 2024", styles['Italic']))
    story.append(Spacer(1, 0.3*inch))
    
    # Content
    paragraphs = [
        "In recent years, artificial intelligence has revolutionized how we interact with documents. "
        "From simple text extraction to sophisticated semantic understanding, AI-powered tools are "
        "transforming document processing workflows across industries.",
        
        "One of the most exciting developments is retrieval-augmented generation (RAG), which combines "
        "the power of large language models with efficient document retrieval. This approach allows "
        "systems to provide accurate, contextual answers by first finding relevant information and "
        "then generating responses based on that context.",
        
        "The key to successful RAG implementation lies in how documents are chunked and indexed. "
        "Traditional fixed-size chunking often splits important context across boundaries, leading "
        "to degraded performance. Semantic chunking, which uses AI to identify natural breakpoints "
        "in text, offers a more intelligent approach.",
        
        "As we look to the future, we can expect even more sophisticated document processing techniques. "
        "Multi-modal understanding, combining text with images and tables, will become standard. "
        "Real-time processing of streaming documents will enable new use cases in customer support "
        "and content moderation.",
        
        "The democratization of these technologies through accessible APIs and open-source tools means "
        "that developers of all skill levels can build powerful document processing applications. "
        "This is just the beginning of an exciting new era in information management."
    ]
    
    for para in paragraphs:
        story.append(Paragraph(para, styles['BodyText']))
        story.append(Spacer(1, 0.15*inch))
    
    doc.build(story)
    print(f"Created: {pdf_path}")

if __name__ == "__main__":
    print("Generating test fixtures...")
    create_legal_contract()
    create_technical_docs()
    create_blog_post()
    print("All fixtures created successfully!")
