from fpdf import FPDF
import os

def create_spanish_pdf():
    # Ensure the input directory exists
    if not os.path.exists('input'):
        os.makedirs('input')
        
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="INFORME DE ALTA MEDICA", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    
    # 1. Identity Section
    pdf.cell(200, 10, txt="DATOS DEL PACIENTE", ln=True)
    pdf.cell(200, 10, txt="Nombre : Sr. Carlos Ruiz", ln=True)
    pdf.cell(200, 10, txt="Numero de Hospital : ES-445566", ln=True)
    pdf.cell(200, 10, txt="Edad / Sexo : 29 anos / Masculino", ln=True)
    pdf.cell(200, 10, txt="Medico : Dr. Alberto Gomez", ln=True)
    pdf.ln(5)

    # 2. Clinical Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="DIAGNOSTICO", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="Fractura de tibia distal derecha tras caida accidental. No se observan complicaciones.")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="TRATAMIENTO RECOMENDADO", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="- Inmovilizacion con yeso durante 6 semanas.\n- Ibuprofeno 600mg cada 8 horas.\n- Mantener la pierna elevada.")
    pdf.ln(10)

    # 3. Administrative Footer (The Noise)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, txt="Sede Social : Hospital Real de Madrid, Calle Mayor 10, 28013 Madrid.", ln=True)

    # Output the PDF
    pdf.output("input/spanish_report.pdf")
    print("🚀 Spanish Medical Report generated: input/spanish_report.pdf")

if __name__ == "__main__":
    create_spanish_pdf()
    