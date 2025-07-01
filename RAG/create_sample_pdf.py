"""
Simple script to create a sample PDF for testing the RAG bot
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_sample_pdf():
    """Create a sample PDF document for testing"""
    
    # Ensure pdfs directory exists
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')
    
    # Create PDF file
    pdf_path = 'pdfs/sample_ai_healthcare_research.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Content
    story = []
    
    # Title
    title = Paragraph("Artificial Intelligence in Healthcare: A Research Study", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Abstract
    abstract_title = Paragraph("Abstract", styles['Heading2'])
    story.append(abstract_title)
    
    abstract_text = """
    This research paper explores the applications of Artificial Intelligence (AI) in healthcare settings. 
    We examine three key areas: diagnostic imaging, drug discovery, and personalized treatment plans. 
    Our findings suggest that AI implementation can improve diagnostic accuracy by 23% and reduce 
    treatment planning time by 40%.
    """
    story.append(Paragraph(abstract_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Introduction
    intro_title = Paragraph("Introduction", styles['Heading2'])
    story.append(intro_title)
    
    intro_text = """
    Healthcare systems worldwide face increasing pressure to provide accurate, efficient, and 
    cost-effective care. Artificial Intelligence presents unprecedented opportunities to address 
    these challenges through automation, pattern recognition, and predictive analytics.
    
    The global healthcare AI market is projected to reach $102 billion by 2028, growing at a 
    compound annual growth rate (CAGR) of 44.9%.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Key Findings
    findings_title = Paragraph("Key Findings", styles['Heading2'])
    story.append(findings_title)
    
    # Diagnostic Imaging
    diagnostic_title = Paragraph("1. Diagnostic Imaging", styles['Heading3'])
    story.append(diagnostic_title)
    
    diagnostic_text = """
    • AI algorithms achieved 95.2% accuracy in detecting lung cancer from CT scans<br/>
    • Reduced false positive rates by 15% compared to traditional methods<br/>
    • Processing time decreased from 30 minutes to 3 minutes per scan
    """
    story.append(Paragraph(diagnostic_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Drug Discovery
    drug_title = Paragraph("2. Drug Discovery", styles['Heading3'])
    story.append(drug_title)
    
    drug_text = """
    • Machine learning models identified potential drug candidates 60% faster<br/>
    • Cost reduction of approximately $2.6 billion per approved drug<br/>
    • Success rate improved from 12% to 18% in clinical trials
    """
    story.append(Paragraph(drug_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Personalized Treatment
    treatment_title = Paragraph("3. Personalized Treatment", styles['Heading3'])
    story.append(treatment_title)
    
    treatment_text = """
    • Patient outcome predictions improved by 35%<br/>
    • Treatment effectiveness increased through genomic analysis<br/>
    • Reduced adverse drug reactions by 28%
    """
    story.append(Paragraph(treatment_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Methodology
    method_title = Paragraph("Methodology", styles['Heading2'])
    story.append(method_title)
    
    method_text = """
    Our research involved:
    1. Analysis of 15 major hospitals across 5 countries
    2. Review of 50,000 patient records
    3. Comparison of AI-assisted vs traditional diagnostic methods
    4. 18-month longitudinal study
    """
    story.append(Paragraph(method_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Challenges
    challenges_title = Paragraph("Challenges and Limitations", styles['Heading2'])
    story.append(challenges_title)
    
    challenges_text = """
    Despite promising results, several challenges remain:
    • Data privacy and security concerns
    • Integration with existing healthcare systems
    • Need for extensive staff training
    • Regulatory compliance requirements
    """
    story.append(Paragraph(challenges_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Conclusions
    conclusion_title = Paragraph("Conclusions", styles['Heading2'])
    story.append(conclusion_title)
    
    conclusion_text = """
    AI in healthcare shows tremendous promise for improving patient outcomes and operational efficiency. 
    However, successful implementation requires careful planning, adequate training, and robust data 
    governance frameworks.
    
    Key recommendations:
    1. Invest in staff training and change management
    2. Establish clear data governance policies
    3. Start with pilot programs before full-scale deployment
    4. Ensure compliance with healthcare regulations
    """
    story.append(Paragraph(conclusion_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    return pdf_path

if __name__ == "__main__":
    try:
        pdf_path = create_sample_pdf()
        print(f"✅ Sample PDF created successfully: {pdf_path}")
        print("📄 The PDF contains research about AI in Healthcare")
        print("🤖 You can now test the RAG bot with this document!")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        print("💡 You can manually add any PDF file to the pdfs/ directory instead")
