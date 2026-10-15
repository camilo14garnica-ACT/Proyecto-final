from django.core.management.base import BaseCommand, CommandError
import time

from usuarios.sync import encolar_usuarios_locales, procesar_pendientes


class Command(BaseCommand):
    help = 'Sincroniza con Neon los usuarios locales pendientes.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--todos',
            action='store_true',
            help='Encola también todos los usuarios locales existentes.',
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=100,
            help='Máximo de pendientes procesados por ejecución.',
        )
        parser.add_argument(
            '--continuo',
            action='store_true',
            help='Revisa periódicamente la cola hasta detener el proceso.',
        )
        parser.add_argument(
            '--intervalo',
            type=int,
            default=60,
            help='Segundos entre revisiones en modo continuo.',
        )

    def handle(self, *args, **options):
        limite = options['limite']
        if limite < 1:
            raise CommandError('--limite debe ser mayor que cero.')
        intervalo = options['intervalo']
        if intervalo < 1:
            raise CommandError('--intervalo debe ser mayor que cero.')

        if options['todos']:
            encolar_usuarios_locales()

        try:
            while True:
                resultado = procesar_pendientes(limite=limite)
                self.stdout.write(
                    'Sincronización: '
                    f"{resultado['sincronizados']} enviados, "
                    f"{resultado['fallidos']} con error, "
                    f"{resultado['pendientes']} pendientes."
                )
                for error in resultado['errores']:
                    self.stderr.write(error)

                if not options['continuo']:
                    break
                time.sleep(intervalo)
        except KeyboardInterrupt:
            self.stdout.write('Celador detenido.')