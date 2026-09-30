import uuid

from django.db import migrations, models


def populate_sync_uuids(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    database = schema_editor.connection.alias
    users = Usuario.objects.using(database).filter(sync_uuid__isnull=True)

    for user in users.iterator():
        Usuario.objects.using(database).filter(
            pk=user.pk,
            sync_uuid__isnull=True,
        ).update(sync_uuid=uuid.uuid4())


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_usuario_rol'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='sync_uuid',
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.RunPython(populate_sync_uuids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='usuario',
            name='sync_uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.CreateModel(
            name='UsuarioSyncPendiente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sync_uuid', models.UUIDField(unique=True)),
                ('operacion', models.CharField(choices=[('guardar', 'Guardar'), ('eliminar', 'Eliminar')], default='guardar', max_length=10)),
                ('intentos', models.PositiveIntegerField(default=0)),
                ('reintentar_despues', models.DateTimeField(blank=True, null=True)),
                ('ultimo_error', models.TextField(blank=True)),
                ('revision', models.PositiveBigIntegerField(default=1)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('creado',),
            },
        ),
    ]