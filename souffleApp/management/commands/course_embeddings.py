import os
import numpy as np
from django.core.management.base import BaseCommand
from souffleApp.models import SouffleApp as Curso
import google.generativeai as genai
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Generate and store embeddings for all courses in the database"

    def handle(self, *args, **kwargs):
        # ✅ Load Gemini API key
        load_dotenv('./gemini.env')
        api_key = os.environ.get('gemini_apikey')
        if not api_key:
            self.stderr.write("❌ Gemini API key not found in gemini.env file")
            return
            
        genai.configure(api_key=api_key)

        # ✅ Fetch all courses from the database
        courses = Curso.objects.all()
        self.stdout.write(f"Found {courses.count()} courses in the database")

        def get_embedding(text):
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return np.array(result['embedding'], dtype=np.float32)

        def create_comprehensive_text(course):
            """Crear texto completo combinando toda la información del curso"""
            parts = []
            
            # Información básica
            if course.title:
                parts.append(f"Título: {course.title}")
            if course.description:
                parts.append(f"Descripción: {course.description}")
            if course.long_description:
                parts.append(f"Detalles: {course.long_description}")
            
            # Información técnica
            if course.duration:
                parts.append(f"Duración: {course.duration}")
            if course.learning_outcomes:
                parts.append(f"Objetivos de aprendizaje: {course.learning_outcomes}")
            if course.materials:
                parts.append(f"Materiales necesarios: {course.materials}")
            if course.ingredients:
                parts.append(f"Ingredientes utilizados: {course.ingredients}")
            if course.price:
                parts.append(f"Precio: {course.price}")
            
            return "\n".join(parts)

        # ✅ Iterate through courses and generate embeddings
        for course in courses:
            try:
                # Crear texto completo con toda la información del curso
                comprehensive_text = create_comprehensive_text(course)
                self.stdout.write(f"📝 Generando embedding para: {course.title}")
                self.stdout.write(f"   Información analizada: {len(comprehensive_text)} caracteres")
                
                emb = get_embedding(comprehensive_text)
                # ✅ Store embedding as binary in the database
                course.embedding = emb.tobytes()
                course.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Embedding mejorado almacenado para: {course.title}"))
            except Exception as e:
                self.stderr.write(f"❌ Failed to generate embedding for {course.title}: {e}")

        self.stdout.write(self.style.SUCCESS("🎯 Finished generating enhanced embeddings for all courses"))