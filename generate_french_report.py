from fpdf import FPDF
import os

def create_french_pdf():
    # Ensure the input directory exists
    if not os.path.exists('input'):
        os.makedirs('input')
        
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="RESUME DE SORTIE MEDICALE", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="DETAILS DU PATIENT", ln=True)
    pdf.cell(200, 10, txt="Nom : Mme. Sophie Lefebvre", ln=True)
    pdf.cell(200, 10, txt="Identifiant Patient : FR-992834", ln=True)
    pdf.cell(200, 10, txt="Age / Sexe : 45 ans / Femme", ln=True)
    pdf.cell(200, 10, txt="Medecin : Dr. Jean Dupont", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="DIAGNOSTIC", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="Pneumonie communautaire aigue de la base droite.")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="TRAITEMENT CONSEILLE", ln=True)
    pdf.set_font("Arial", size=12)
    # CHANGED: Replaced Unicode bullet points with '-'
    pdf.multi_cell(0, 10, txt="- Amoxicilline 1g, trois fois par jour.\n- Paracetamol 1g en cas de fievre.\n- Repos complet.")
    pdf.ln(10)

    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, txt="Siege social : Hopital Universitaire de Paris.", ln=True)

    pdf.output("input/french_report.pdf")
    print("🚀 French Medical Report generated successfully!")

if __name__ == "__main__":
    create_french_pdf()