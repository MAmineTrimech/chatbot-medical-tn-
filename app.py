from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# Charger les datasets Excel
df_villes = pd.read_excel('dataset.xlsx', sheet_name='Villes')
df_symptomes = pd.read_excel('dataset.xlsx', sheet_name='Symptomes')
df_cadres = pd.read_excel('dataset.xlsx', sheet_name='Cadres')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadres_list')
def cadres_list():
    try:
        # Vérifier si la colonne "Cadre Medical" existe
        if 'Cadre Medical' in df_cadres.columns:
            cadres_list = df_cadres['Cadre Medical'].dropna().tolist()
            return jsonify({"cadres_list": cadres_list})
        else:
            return jsonify({"error": "Colonne 'Cadre Medical' non trouvée."})
    except Exception as e:
        print(f"Erreur lors de la génération de la liste des cadres: {e}")
        return jsonify({"error": "Erreur lors de la génération de la liste des cadres."})

@app.route('/generate_contact', methods=['POST'])
def generate_contact():
    data = request.get_json()
    code_postal = data.get('code_postal')
    symptome = data.get('symptome')
    cadre_medical = data.get('cadre_medical')

    try:
        ville_info = df_villes[df_villes['Code Postal'] == int(code_postal)]
        if ville_info.empty:
            return jsonify({"error": "Code postal non trouvé."})

        ville = ville_info.iloc[0]['Ville']
        gouvernorat = ville_info.iloc[0]['Gouvernorat']

        if symptome:
            symptome_info = df_symptomes[df_symptomes['Symptomes'].str.contains(symptome, case=False, na=False)]
            if symptome_info.empty:
                return jsonify({"warning": "Symptôme non trouvé, mais le traitement peut continuer."})

        contact_url = f"http://contactmedic.com/{cadre_medical.replace(' ', '_')}"

        return jsonify({
            "cadre_medical": cadre_medical,
            "ville": ville,
            "gouvernorat": gouvernorat,
            "contact_url": contact_url
        })

    except Exception as e:
        print(f"Erreur lors de la génération du contact: {e}")
        return jsonify({"error": "Erreur lors de la génération du contact."})

if __name__ == '__main__':
    app.run(debug=True)
