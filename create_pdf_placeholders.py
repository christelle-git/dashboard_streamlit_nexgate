#!/usr/bin/env python3
"""
Script pour créer des fichiers PDF de remplacement
pour les documents non accessibles via Wayback Machine
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os

def create_pdf_placeholder(filename, title, content, author="Christelle Lusso"):
    """Crée un fichier PDF de remplacement"""
    
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#00E673')
    )
    
    # Style pour le contenu
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_JUSTIFY
    )
    
    # Style pour l'auteur
    author_style = ParagraphStyle(
        'Author',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.gray
    )
    
    # Contenu du document
    story = []
    
    # Titre
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Auteur
    story.append(Paragraph(f"<b>Auteur :</b> {author}", author_style))
    story.append(Spacer(1, 30))
    
    # Contenu
    for paragraph in content:
        story.append(Paragraph(paragraph, content_style))
        story.append(Spacer(1, 12))
    
    # Note de remplacement
    note_style = ParagraphStyle(
        'Note',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.red
    )
    
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "<b>Note :</b> Ce document est un fichier de remplacement. "
        "Le document original sera restauré une fois que nexgate.ch sera de nouveau accessible.",
        note_style
    ))
    
    # Générer le PDF
    doc.build(story)
    print(f"✅ Fichier créé : {filename}")

def main():
    """Crée tous les fichiers PDF de remplacement"""
    
    # Créer le dossier pdf s'il n'existe pas
    if not os.path.exists('pdf'):
        os.makedirs('pdf')
    
    # Abstract Lusso
    abstract_content = [
        "Ce document présente un résumé de la présentation sur la simulation bidimensionnelle "
        "des écoulements viscoplastiques Drucker-Prager par régularisation, avec application "
        "à l'effondrement granulaire.",
        "La méthode proposée utilise une approche de régularisation pour traiter les "
        "singularités inhérentes aux modèles viscoplastiques, permettant une simulation "
        "numérique stable et précise des phénomènes d'écoulement granulaire.",
        "Les résultats obtenus montrent une bonne concordance avec les expériences "
        "de laboratoire et ouvrent la voie à de nouvelles applications dans le domaine "
        "de la mécanique des milieux granulaires."
    ]
    
    create_pdf_placeholder(
        'pdf/abstract_lusso.pdf',
        'Abstract - Simulation d\'écoulements viscoplastiques',
        abstract_content
    )
    
    # Présentation LJLL
    presentation_content = [
        "Cette présentation détaille les aspects méthodologiques et numériques "
        "de la simulation d'écoulements viscoplastiques.",
        "Les points clés abordés incluent :",
        "• La formulation du modèle Drucker-Prager régularisé",
        "• Les schémas numériques utilisés pour la discrétisation",
        "• La validation sur des cas tests académiques",
        "• L'application à l'effondrement granulaire",
        "• La comparaison avec les résultats expérimentaux",
        "Cette approche permet de surmonter les difficultés numériques "
        "traditionnellement rencontrées dans la simulation de milieux granulaires."
    ]
    
    create_pdf_placeholder(
        'pdf/presentation_ljll.pdf',
        'Présentation LJLL - Écoulements viscoplastiques',
        presentation_content
    )
    
    # Thèse de doctorat
    thesis_content = [
        "Cette thèse de doctorat présente une contribution originale à la modélisation "
        "numérique des écoulements gravitationnels viscoplastiques avec transition "
        "fluide/solide.",
        "Le travail s'articule autour de plusieurs axes :",
        "• Développement de modèles mathématiques pour les écoulements granulaires",
        "• Mise en œuvre de schémas numériques adaptés aux singularités viscoplastiques",
        "• Validation expérimentale sur des cas d'étude représentatifs",
        "• Application à des problèmes géophysiques et industriels",
        "Les résultats obtenus contribuent à une meilleure compréhension "
        "des phénomènes d'écoulement dans les milieux granulaires et ouvrent "
        "de nouvelles perspectives pour la modélisation de phénomènes naturels "
        "tels que les avalanches et les coulées de débris."
    ]
    
    create_pdf_placeholder(
        'pdf/thesis.pdf',
        'Thèse de Doctorat - Modélisation numérique des écoulements gravitationnels viscoplastiques',
        thesis_content
    )
    
    print("\n🎉 Tous les fichiers PDF de remplacement ont été créés !")
    print("📁 Dossier : pdf/")
    print("📄 Fichiers créés :")
    print("   - abstract_lusso.pdf")
    print("   - presentation_ljll.pdf") 
    print("   - thesis.pdf")

if __name__ == "__main__":
    main() 