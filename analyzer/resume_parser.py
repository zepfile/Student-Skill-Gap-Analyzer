import os
import re
from pathlib import Path


class ResumeParser:
    def __init__(self):
        pass

    def parse_file(self, file_path: str) -> dict:
        """
        Extracts text and structured sections from PDF, DOCX, or TXT file.
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        raw_text = ""
        if ext == ".pdf":
            raw_text = self._read_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            raw_text = self._read_docx(file_path)
        else:
            raw_text = self._read_txt(file_path)

        sections = self._extract_sections(raw_text)

        return {
            "filename": path.name,
            "raw_text": raw_text,
            "char_count": len(raw_text),
            "word_count": len(raw_text.split()),
            "sections": sections
        }

    def extract_text_from_file(self, file_path: str) -> str:
        """Extracts plain text string from PDF, DOCX, or TXT file."""
        parsed = self.parse_file(file_path)
        return parsed.get("raw_text", "")

    def extract_sections(self, text: str) -> dict:
        """Public alias for _extract_sections."""
        return self._extract_sections(text)

    def _read_pdf(self, file_path: str) -> str:
        """Reads text from PDF using pypdf with robust error recovery."""
        text_content = []
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        except Exception as e:
            # Fallback simple binary string scrape if pypdf has any issue
            try:
                with open(file_path, "rb") as f:
                    content = f.read().decode("latin-1", errors="ignore")
                    text_content.append(content)
            except Exception:
                pass
        return "\n".join(text_content)

    def _read_docx(self, file_path: str) -> str:
        """Reads text from docx file."""
        text_content = []
        try:
            import docx
            doc = docx.Document(file_path)
            for p in doc.paragraphs:
                if p.text.strip():
                    text_content.append(p.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        text_content.append(" | ".join(row_text))
        except Exception:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text_content.append(f.read())
            except Exception:
                pass
        return "\n".join(text_content)

    def _read_txt(self, file_path: str) -> str:
        """Reads plain text / markdown file."""
        for enc in ["utf-8", "latin-1", "utf-16"]:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read()
            except Exception:
                continue
        return ""

    def _extract_sections(self, text: str) -> dict:
        """
        Segments the resume text into standard sections:
        Education, Experience, Projects, Skills, Summary/Objective.
        """
        sections = {
            "summary": "",
            "education": "",
            "experience": "",
            "projects": "",
            "skills": "",
            "certifications": ""
        }

        # Heading patterns
        headings = [
            ("summary", r"(?:summary|objective|about\s+me|profile)"),
            ("skills", r"(?:technical\s+skills|skills|technologies|proficiencies|core\s+competencies)"),
            ("experience", r"(?:experience|work\s+history|employment|internships|work\s+experience)"),
            ("projects", r"(?:projects|academic\s+projects|personal\s+projects)"),
            ("education", r"(?:education|academic\s+background|qualifications|academics)"),
            ("certifications", r"(?:certifications|licenses|achievements|awards)")
        ]

        lines = text.split("\n")
        current_section = "summary"
        section_buffers = {k: [] for k in sections}

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            matched = False
            # Check if this line looks like a header
            if len(line_str) < 40:
                for key, pattern in headings:
                    if re.match(rf"^(?:[\#\*\-_\s]*){pattern}[:\s]*$", line_str, re.IGNORECASE):
                        current_section = key
                        matched = True
                        break

            if not matched:
                section_buffers[current_section].append(line_str)

        for k in sections:
            sections[k] = "\n".join(section_buffers[k])

        return sections

