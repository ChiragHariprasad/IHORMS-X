import xml.etree.ElementTree as ET
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

def generate_reports():
    xml_file = 'test_results.xml'
    if not os.path.exists(xml_file):
        print(f"Error: {xml_file} not found.")
        return

    tree = ET.parse(xml_file)
    root = tree.getroot()

    test_data = []
    
    # Extract test summary
    summary = {
        'total': int(root.attrib.get('tests', 0)),
        'failures': int(root.attrib.get('failures', 0)),
        'errors': int(root.attrib.get('errors', 0)),
        'skipped': int(root.attrib.get('skipped', 0)),
        'time': float(root.attrib.get('time', 0.0))
    }
    summary['passed'] = summary['total'] - summary['failures'] - summary['errors'] - summary['skipped']
    
    # Extract individual test cases
    for testcase in root.iter('testcase'):
        name = testcase.attrib.get('name')
        classname = testcase.attrib.get('classname')
        time_taken = float(testcase.attrib.get('time', 0.0))
        
        status = 'PASSED'
        message = ''
        
        failure = testcase.find('failure')
        if failure is not None:
            status = 'FAILED'
            message = failure.attrib.get('message', '')
            
        error = testcase.find('error')
        if error is not None:
            status = 'ERROR'
            message = error.attrib.get('message', '')

        skipped = testcase.find('skipped')
        if skipped is not None:
            status = 'SKIPPED'
            message = skipped.attrib.get('message', '')
            
        test_data.append({
            'Test Class': classname,
            'Test Name': name,
            'Status': status,
            'Time (s)': time_taken,
            'Message': message
        })

    # Save to CSV
    df = pd.DataFrame(test_data)
    csv_filename = f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(csv_filename, index=False)
    print(f"CSV report saved to {csv_filename}")

    # Generate PDF Report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="IHORMS Test Execution Report", ln=True, align='C')
    pdf.ln(10)
    
    # Summary Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Execution Summary", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, txt=f"Total Tests: {summary['total']}", ln=True)
    pdf.cell(200, 10, txt=f"Passed: {summary['passed']}", ln=True)
    pdf.cell(200, 10, txt=f"Failed: {summary['failures']}", ln=True)
    pdf.cell(200, 10, txt=f"Errors: {summary['errors']}", ln=True)
    pdf.cell(200, 10, txt=f"Skipped: {summary['skipped']}", ln=True)
    pdf.cell(200, 10, txt=f"Total Time: {summary['time']}s", ln=True)
    pdf.ln(10)
    
    # Detailed Failures Section (if any)
    if summary['failures'] > 0 or summary['errors'] > 0:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Failed/Error Test Cases", ln=True)
        pdf.set_font("Arial", size=10)
        
        for item in test_data:
            if item['Status'] in ['FAILED', 'ERROR']:
                pdf.set_text_color(255, 0, 0)
                pdf.cell(200, 8, txt=f"[{item['Status']}] {item['Test Class']}::{item['Test Name']}", ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 5, txt=f"Message: {item['Message'][:300]}...") # Truncate long messages
                pdf.ln(2)

    pdf_filename = f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    pdf.output(pdf_filename)
    print(f"PDF report saved to {pdf_filename}")

if __name__ == "__main__":
    generate_reports()
