from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(filename, text, size=(400, 300), color=(100, 150, 200)):
    """Crée une image de remplacement avec du texte"""
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    
    # Ajoute du texte
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Centre le texte
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Ajoute une bordure
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(255, 255, 255), width=3)
    
    img.save(filename)
    print(f"Créé: {filename}")

# Crée les dossiers
os.makedirs('drawing', exist_ok=True)
os.makedirs('pdf', exist_ok=True)

# Image de profil
create_placeholder_image('labo.jpg', 'Photo de Profil\nChristelle Lusso', (385, 250), (0, 230, 115))

# Images de dessins
drawings = [
    ('paperPhys_cp.jpg', 'Paper Physics'),
    ('books_stack_cp.jpg', 'Books Stack'),
    ('school_cp.jpg', 'School'),
    ('navier_stokes_green_tv_cp.jpg', 'Navier Stokes'),
    ('finger_noze_2.jpg', 'Finger Noze'),
    ('wake_up.jpg', 'Wake Up'),
    ('run_run.JPG', 'Run Run'),
    ('sport_training.jpg', 'Sport Training'),
    ('dense_cp.jpg', 'Dense'),
    ('massue_tot_cp.jpg', 'Massue'),
    ('joke_maths_cp.jpg', 'Joke Maths'),
    ('BD_criterium.jpg', 'BD Criterium'),
    ('sparkling.jpg', 'Sparkling'),
    ('crazy_love_cp_clean.jpg', 'Crazy Love'),
    ('lenny_cp.jpg', 'Lenny')
]

for filename, text in drawings:
    create_placeholder_image(f'drawing/{filename}', text, (270, 200), (200, 100, 150))

# Fichiers PDF de remplacement
def create_pdf_placeholder(filename, text):
    """Crée un fichier texte qui simule un PDF"""
    with open(filename, 'w') as f:
        f.write(f"PLACEHOLDER PDF: {text}\n")
        f.write("=" * 50 + "\n")
        f.write("Ce fichier remplace temporairement le PDF original\n")
        f.write("qui n'est pas accessible via Wayback Machine.\n")
        f.write("Le contenu original sera restauré une fois que\n")
        f.write("nexgate.ch sera de nouveau accessible.\n")
    print(f"Créé: {filename}")

create_pdf_placeholder('pdf/abstract_lusso.pdf', 'Abstract Lusso')
create_pdf_placeholder('pdf/presentation_ljll.pdf', 'Presentation LJLL')
create_pdf_placeholder('thesis.pdf', 'PhD Thesis')

print("\n✅ Toutes les images et PDF de remplacement ont été créés !")
print("Le site devrait maintenant afficher correctement.") 