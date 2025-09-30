import os
import numpy as np
from django.core.management.base import BaseCommand
from souffleApp.models import SouffleApp as Curso
from openai import OpenAI
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Generate and store embeddings for all courses in the database"

    def handle(self, *args, **kwargs):
        # ✅ Load OpenAI API key
        load_dotenv('./openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        # ✅ Fetch all courses from the database
        courses = Curso.objects.all()
        self.stdout.write(f"Found {courses.count()} courses in the database")

        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        # ✅ Iterate through courses and generate embeddings
        for course in courses:
            try:
                emb = get_embedding(course.long_description)
                # ✅ Store embedding as binary in the database
                course.embedding = emb.tobytes()
                course.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Embedding stored for: {course.title}"))
            except Exception as e:
                self.stderr.write(f"❌ Failed to generate embedding for {course.title}: {e}")

        self.stdout.write(self.style.SUCCESS("🎯 Finished generating embeddings for all courses"))