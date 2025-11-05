"""
PDF Generation Service for MCP Fake News Detection System
Generates PDF reports for detection and generation results
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating PDF reports from detection and generation results"""
    
    def __init__(self, storage_base_path: str = "storage"):
        """
        Initialize PDF service
        
        Args:
            storage_base_path: Base path for storing PDF files
        """
        # Convert to absolute path if relative
        base_path = Path(storage_base_path)
        if not base_path.is_absolute():
            # If relative, resolve from backend directory
            import os
            backend_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
            base_path = backend_dir / storage_base_path
        
        self.storage_base_path = base_path
        self.detections_path = self.storage_base_path / "detections"
        self.generations_path = self.storage_base_path / "generations"
        
        # Create directories if they don't exist
        self.detections_path.mkdir(parents=True, exist_ok=True)
        self.generations_path.mkdir(parents=True, exist_ok=True)
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        
        # Result style
        self.styles.add(ParagraphStyle(
            name='ResultText',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=HexColor('#2c3e50'),
            backColor=HexColor('#f8f9fa'),
            borderPadding=10,
            spaceAfter=10
        ))
    
    def _format_text(self, text: str, max_length: int = 5000) -> str:
        """Format text for PDF (escape HTML and truncate if needed)"""
        if not text:
            return ""
        # Escape HTML special characters
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "... (truncated)"
        return text
    
    def _format_confidence(self, confidence: float) -> str:
        """Format confidence as percentage"""
        return f"{confidence * 100:.2f}%"
    
    def _create_info_table(self, data: Dict[str, Any]) -> Table:
        """Create an information table"""
        table_data = []
        for key, value in data.items():
            if value is not None:
                table_data.append([
                    Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['CustomBody']),
                    Paragraph(str(value), self.styles['CustomBody'])
                ])
        
        if not table_data:
            return None
        
        table = Table(table_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        return table
    
    def generate_detection_pdf(self, record_id: str, detection_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Generate PDF for detection result
        
        Args:
            record_id: MongoDB record ID
            detection_data: Detection result data
            
        Returns:
            Dict with 'pdf_path' and 'pdf_url', or None if failed
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_{record_id}_{timestamp}.pdf"
            file_path = self.detections_path / filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Title
            story.append(Paragraph("Fake News Detection Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.3*inch))
            
            # Metadata
            metadata = {
                "Detection Type": detection_data.get("type", "Unknown"),
                "Created At": detection_data.get("created_at", "N/A"),
                "Record ID": record_id
            }
            metadata_table = self._create_info_table(metadata)
            if metadata_table:
                story.append(metadata_table)
                story.append(Spacer(1, 0.2*inch))
            
            # Original Text
            text = detection_data.get("text", "")
            if text:
                story.append(Paragraph("Original Text", self.styles['CustomHeading']))
                story.append(Paragraph(self._format_text(text), self.styles['CustomBody']))
                story.append(Spacer(1, 0.2*inch))
            
            # Detection Result
            result = detection_data.get("result", {})
            if result:
                story.append(Paragraph("Detection Results", self.styles['CustomHeading']))
                
                # Final Prediction
                final_pred = result.get("final_prediction", {})
                if final_pred:
                    prediction = final_pred.get("prediction", "Unknown")
                    fake_prob = final_pred.get("fake_probability", 0)
                    confidence = final_pred.get("confidence", 0)
                    
                    result_text = f"""
                    <b>Prediction:</b> {prediction.upper()}<br/>
                    <b>Fake Probability:</b> {self._format_confidence(fake_prob)}<br/>
                    <b>Confidence:</b> {self._format_confidence(confidence)}
                    """
                    story.append(Paragraph(result_text, self.styles['ResultText']))
                    story.append(Spacer(1, 0.15*inch))
                
                # Model Results
                model_results = result.get("model_results", {})
                if model_results:
                    story.append(Paragraph("Model Analysis", self.styles['CustomHeading']))
                    for model_name, model_result in model_results.items():
                        if isinstance(model_result, dict):
                            model_text = f"<b>{model_name.replace('_', ' ').title()}:</b> "
                            if "prediction" in model_result:
                                model_text += f"{model_result['prediction']}"
                            if "confidence" in model_result:
                                model_text += f" (Confidence: {self._format_confidence(model_result['confidence'])})"
                            story.append(Paragraph(model_text, self.styles['CustomBody']))
                            story.append(Spacer(1, 0.1*inch))
                
                # Additional Details
                if "details" in result:
                    story.append(Paragraph("Additional Details", self.styles['CustomHeading']))
                    details_text = self._format_text(str(result["details"]), max_length=2000)
                    story.append(Paragraph(details_text, self.styles['CustomBody']))
            
            # Build PDF
            doc.build(story)
            
            # Return paths
            relative_path = f"detections/{filename}"
            pdf_url = f"/api/detection/history/{record_id}/pdf"
            
            logger.info(f"Generated detection PDF: {file_path}")
            return {
                "pdf_path": str(file_path),
                "pdf_url": pdf_url,
                "relative_path": relative_path
            }
            
        except Exception as e:
            logger.error(f"Error generating detection PDF: {str(e)}")
            return None
    
    def generate_generation_pdf(self, record_id: str, generation_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Generate PDF for generation result
        
        Args:
            record_id: MongoDB record ID
            generation_data: Generation result data
            
        Returns:
            Dict with 'pdf_path' and 'pdf_url', or None if failed
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generation_{record_id}_{timestamp}.pdf"
            file_path = self.generations_path / filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Title
            story.append(Paragraph("Fake News Generation Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.3*inch))
            
            # Metadata
            metadata = {
                "Topic": generation_data.get("topic", "Unknown"),
                "Strategy": generation_data.get("strategy", "Unknown"),
                "Model Type": generation_data.get("model_type", "Unknown"),
                "Created At": generation_data.get("created_at", "N/A"),
                "Record ID": record_id
            }
            metadata_table = self._create_info_table(metadata)
            if metadata_table:
                story.append(metadata_table)
                story.append(Spacer(1, 0.2*inch))
            
            # Generation Result
            result = generation_data.get("result", {})
            if result:
                # Generated Article
                article = result.get("article", "")
                if article:
                    story.append(Paragraph("Generated Article", self.styles['CustomHeading']))
                    story.append(Paragraph(self._format_text(article), self.styles['CustomBody']))
                    story.append(Spacer(1, 0.2*inch))
                
                # Generation Parameters
                if "params" in result:
                    story.append(Paragraph("Generation Parameters", self.styles['CustomHeading']))
                    params_text = self._format_text(str(result["params"]), max_length=1000)
                    story.append(Paragraph(params_text, self.styles['CustomBody']))
                    story.append(Spacer(1, 0.2*inch))
                
                # Additional Metadata
                if "metadata" in result:
                    story.append(Paragraph("Additional Information", self.styles['CustomHeading']))
                    metadata_text = self._format_text(str(result["metadata"]), max_length=1000)
                    story.append(Paragraph(metadata_text, self.styles['CustomBody']))
            
            # Build PDF
            doc.build(story)
            
            # Return paths
            relative_path = f"generations/{filename}"
            pdf_url = f"/api/generation/history/{record_id}/pdf"
            
            logger.info(f"Generated generation PDF: {file_path}")
            return {
                "pdf_path": str(file_path),
                "pdf_url": pdf_url,
                "relative_path": relative_path
            }
            
        except Exception as e:
            logger.error(f"Error generating generation PDF: {str(e)}")
            return None
    
    def get_pdf_path(self, relative_path: str) -> Optional[Path]:
        """
        Get full path to PDF file from relative path
        
        Args:
            relative_path: Relative path like "detections/filename.pdf"
            
        Returns:
            Full Path object or None if not found
        """
        file_path = self.storage_base_path / relative_path
        if file_path.exists():
            return file_path
        return None

