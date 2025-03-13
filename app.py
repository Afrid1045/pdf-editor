from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import io

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/remove_links', methods=['POST'])
def remove_links():
    if 'pdf' not in request.files:
        return {"error": "No file uploaded"}, 400
    
    pdf_file = request.files['pdf']

    if pdf_file.filename == '':
        return {"error": "No selected file"}, 400

    # Read the PDF
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Remove all hyperlinks and mailto links
    for page in doc:
        # Remove all link annotations
        annot = page.first_annot
        while annot:
            subtype = annot.type[0]  # Get annotation type
            if subtype == 2:  # 2 = Link Annotation in PyMuPDF
                page.delete_annot(annot)
            annot = annot.next  # Move to the next annotation

        # Remove all interactive elements (including hidden links)
        links = page.get_links()
        for link in links:
            if "mailto:" in link.get("uri", "") or link.get("uri"):  
                page.delete_link(link)

    # Save cleaned PDF to memory
    output_pdf = io.BytesIO()
    doc.save(output_pdf)
    output_pdf.seek(0)

    return send_file(output_pdf, mimetype="application/pdf", as_attachment=True, download_name="cleaned.pdf")

if __name__ == '__main__':
    app.run(debug=True)
