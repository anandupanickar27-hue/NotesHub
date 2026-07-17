from django.core.management.base import BaseCommand

from notes.models import Note
from notes.vector_store import save_to_chroma, collection


class Command(BaseCommand):
    help = "Rebuilds the ChromaDB index from all notes."

    def handle(self, *args, **kwargs):

        self.stdout.write("Clearing existing Chroma collection...")

        try:
            all_docs = collection.get()

            if all_docs["ids"]:
                collection.delete(ids=all_docs["ids"])

        except Exception as e:
            self.stderr.write(f"Could not clear collection: {e}")

        notes = Note.objects.all()

        count = 0

        for note in notes:
            try:
                save_to_chroma(note)
                count += 1
                self.stdout.write(f"Indexed: {note.title}")
            except Exception as e:
                self.stderr.write(f"Failed: {note.title} - {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully indexed {count} notes."
            )
        )