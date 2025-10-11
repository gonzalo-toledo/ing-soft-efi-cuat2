import json
from django.core.management.base import BaseCommand
from aviones.models import Avion, Asiento

class Command(BaseCommand):
    help = "Carga aviones y genera sus asientos automáticamente desde un archivo JSON"

    def handle(self, *args, **options):
        with open("aviones/management/jsons/aviones.json", encoding="utf-8") as f:
            data = json.load(f)

        for avion_data in data:
            avion, created = Avion.objects.get_or_create(
                modelo=avion_data["modelo"],
                capacidad=avion_data["capacidad"],
                filas=avion_data["filas"],
                columnas=avion_data["columnas"]
            )

            # Si es nuevo, generamos los asientos automáticamente
            if created:
                self.stdout.write(f"✈ Creando asientos para {avion.modelo}...")
                for fila in range(1, avion.filas + 1):
                    for col in range(1, avion.columnas + 1):
                        Asiento.objects.get_or_create(
                            numero=f"{fila}{chr(64+col)}",  # ejemplo: 1A, 1B, ...
                            fila=fila,
                            columna=col,
                            tipo="Económica" if fila > 3 else "Business",
                            avion=avion
                        )

            self.stdout.write(self.style.SUCCESS(f"✔ Avión {avion.modelo} cargado correctamente."))

        self.stdout.write(self.style.SUCCESS("🚀 Carga de aviones y asientos completada."))
