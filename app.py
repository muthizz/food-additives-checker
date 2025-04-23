# Food Additives Checker (Pendeteksi Bahan Tambahan Makanan)

from flask import Flask, request, render_template_string

app = Flask(__name__)

# Simulasi database bahan tambahan makanan (E-number dan deskripsi)
additives_db = {
    "E100": {"nama": "Curcumin", "fungsi": "Pewarna alami", "kategori": "Aman"},
    "E102": {"nama": "Tartrazine", "fungsi": "Pewarna sintetis", "kategori": "Perhatian untuk anak-anak"},
    "E200": {"nama": "Asam Sorbat", "fungsi": "Pengawet", "kategori": "Aman dalam batas tertentu"},
    "E951": {"nama": "Aspartame", "fungsi": "Pemanis buatan", "kategori": "Perhatian untuk penderita PKU"},
}

html_template = '''
<!doctype html>
<html>
<head>
    <title>Food Additives Checker</title>
</head>
<body>
    <h1>Cek Bahan Tambahan Makanan (E-number)</h1>
    <form method="post">
        Masukkan E-number (contoh: E100): <input type="text" name="ecode">
        <input type="submit" value="Cek">
    </form>
    {% if hasil %}
        <h2>Hasil:</h2>
        {% if hasil_found %}
            <p><strong>Nama:</strong> {{ hasil['nama'] }}</p>
            <p><strong>Fungsi:</strong> {{ hasil['fungsi'] }}</p>
            <p><strong>Kategori Keamanan:</strong> {{ hasil['kategori'] }}</p>
        {% else %}
            <p style="color: red;">E-number tidak ditemukan dalam database.</p>
        {% endif %}
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = None
    hasil_found = False
    if request.method == 'POST':
        ecode = request.form['ecode'].upper()
        if ecode in additives_db:
            hasil = additives_db[ecode]
            hasil_found = True
        else:
            hasil = {}
    return render_template_string(html_template, hasil=hasil, hasil_found=hasil_found)

if __name__ == '__main__':
    app.run(debug=True)
