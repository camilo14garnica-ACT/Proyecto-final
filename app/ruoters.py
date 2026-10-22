from django.db import DEFAULT_DB_ALIAS


class EnrutadorDobleBase:
    """
    Todas las apps (Usuarios, inventario, etc..) trabajan con la base LOCAL.
    la copia en la nube se hace con guarda_en_ambas() o using('remota).
    """
    
    def db_for_read(self, model, **hints):
        return 'default'
    
    def db_for_write(self, model, **hints):
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'usuarios' and model_name == 'usuariosyncpendiente':
            return db == DEFAULT_DB_ALIAS
        return True  #Las tablas se crean en las dos bases