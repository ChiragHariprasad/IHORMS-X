# IHORMS Project Report - LaTeX Compilation Guide

## Overview
This document provides instructions for compiling the IHORMS project report LaTeX file.

## Prerequisites

### Required Software
1. **LaTeX Distribution:**
   - **Windows:** MiKTeX (https://miktex.org/) or TeX Live
   - **macOS:** MacTeX (https://www.tug.org/mactex/)
   - **Linux:** TeX Live (`sudo apt-get install texlive-full`)

2. **PDF Viewer:** Adobe Acrobat Reader, SumatraPDF, or built-in PDF viewer

3. **Optional:** LaTeX Editor
   - TeXstudio (Recommended)
   - Overleaf (Online, no installation needed)
   - VS Code with LaTeX Workshop extension

## Required LaTeX Packages

The report uses the following packages (automatically installed by most distributions):
- `geometry` - Page layout and margins
- `fancyhdr` - Headers and footers
- `graphicx` - Image inclusion
- `times` - Times New Roman font
- `titlesec` - Section title formatting
- `caption` - Figure captions
- `hyperref` - Hyperlinks and references
- `enumitem` - List formatting
- `tikz`, `pgf-umlcd` - Diagram creation
- `array`, `longtable`, `multirow`, `booktabs` - Tables
- `listings`, `xcolor` - Code listings
- `eso-pic` - Page borders

## Compilation Steps

### Method 1: Using TeXstudio (Recommended for Beginners)

1. Install TeXstudio: https://www.texstudio.org/
2. Open `IHORMS_Report.tex` in TeXstudio
3. Press **F5** or click the green compile button
4. The PDF will be generated automatically

### Method 2: Using Command Line

```bash
# Navigate to the project directory
cd e:\WorkingProjects\IHORMS-X\G_v

# Compile the LaTeX document (run twice for proper references)
pdflatex IHORMS_Report.tex
pdflatex IHORMS_Report.tex

# The output PDF will be: IHORMS_Report.pdf
```

### Method 3: Using Overleaf (Online)

1. Go to https://www.overleaf.com/
2. Create a new blank project
3. Upload `IHORMS_Report.tex`
4. Click "Recompile" 
5. Download the generated PDF

## Adding Diagrams and Screenshots

### ER Diagram
Replace the placeholder on **page ~10** with your actual ER diagram.
The report expects `er.png`.
```latex
\includegraphics[width=0.95\textwidth]{er.png}
```

### DFD Diagrams
The report expects the following images:
- `dfd0.png` - Context diagram (page ~12)
- `dfd1.png` - Level 1 DFD (page ~13)
- `dfd2.png` - Level 2 DFD (page ~15)

### Relational Schema
- `relationaldig.png` - Relational Schema Diagram (page ~17)

### Appendix Screenshots
Add screenshot images (pages ~24-30):
- `screenshot_superadmin.png` - Super admin dashboard
- `screenshot_billing_analytics.png` - Billing charts
- `screenshot_doctor.png` - Doctor portal
- `screenshot_nurse_vitals.png` - Nurse telemetry
- `screenshot_receptionist.png` - Patient registration
- `screenshot_billing_create.png` - Bill creation
- `screenshot_patient_bills.png` - Patient bills
- `screenshot_pharmacy.png` - Pharmacy inventory
- `screenshot_schema.png` - Database schema from pgAdmin

### Adding Images to LaTeX

1. Save all images in the same folder as `IHORMS_Report.tex`
2. Replace the placeholder `\fbox{\parbox{...}}` sections with:
```latex
\includegraphics[width=0.8\textwidth]{your_image_filename.png}
```

## Customization

### Update Student Information
Edit the title page (lines ~90-110):
```latex
{\large [Your Name]\par}
{\large [Your USN]\par}
```

### Update Guide Information
```latex
{\large [Guide Name]\par}
{\large Assistant Professor\par}
```

### Add RVCE Logo
Place `rvce_logo.png` in the same directory, or remove line ~118 if logo is not available

## File Structure

```
e:\WorkingProjects\IHORMS-X\G_v\
├── IHORMS_Report.tex          # Main LaTeX source file
├── IHORMS_Report.pdf          # Generated PDF (after compilation)
├── rvce_logo.png              # College logo (optional)
├── er_diagram.png             # ER diagram image
├── dfd_level0.png             # DFD Level 0
├── dfd_level1.png             # DFD Level 1
├── dfd_level2.png             # DFD Level 2
├── screenshot_*.png           # UI screenshots
└── README_LATEX.md            # This file
```

## Common Issues and Solutions

### Issue 1: "File not found" error for images
**Solution:** Ensure all image files are in the same directory as the .tex file, or provide full paths

### Issue 2: Page borders not showing
**Solution:** Install the `eso-pic` package: `tlmgr install eso-pic`

### Issue 3: Times New Roman font not working
**Solution:** The `times` package uses a Times-like font. For exact Times New Roman, use XeLaTeX:
```bash
xelatex IHORMS_Report.tex
```

### Issue 4: References not compiling
**Solution:** Run pdflatex twice to resolve cross-references

### Issue 5: Table of Contents not updating
**Solution:** Delete auxiliary files (.aux, .toc) and recompile

## Report Specifications Met

✅ Times New Roman text - 12 pt (base font)
✅ Title headings - Bold, 16 pt
✅ Subtitles - Bold, 14 pt  
✅ Approximately 20 pages (with images)
✅ All chapters include preambles (italicized introductions)
✅ Figures have captions and are referenced in text
✅ Every page has border (using eso-pic package)
✅ Header (from Introduction): Project title (left), 2024-25 (right), Font 11
✅ Footer: Department of AIML, RVCE (left), Page number (right)
✅ References in IEEE format

## Generating Final PDF

After adding all images and customizations:

```bash
# Clean previous builds
rm *.aux *.log *.toc *.out

# Compile twice for proper references
pdflatex IHORMS_Report.tex
pdflatex IHORMS_Report.tex

# Open the PDF
start IHORMS_Report.pdf  # Windows
open IHORMS_Report.pdf   # macOS
xdg-open IHORMS_Report.pdf  # Linux
```

## Printing for Softbound

1. Open `IHORMS_Report.pdf`
2. Print settings:
   - Paper: A4
   - Print on both sides (if available)
   - Margins: Default (already set in LaTeX)
3. Take to binding center for softbound binding

## Support

For LaTeX help:
- Official LaTeX Documentation: https://www.latex-project.org/help/documentation/
- Stack Exchange TeX: https://tex.stackexchange.com/
- Overleaf Tutorials: https://www.overleaf.com/learn

## License

This report template is created for academic purposes for RVCE AIML Department.
