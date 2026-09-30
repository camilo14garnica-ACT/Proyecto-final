class EnrutadorDobleBase:
    """
    Todas las apps (Usuarios, inventario, etc..) trabajan con la base LOCAL.
    la copia en la nube se hace con guarda_en_ambas() o using('remota).
    """
    
    def db_of_read(self, model, **hints):
        return 'default'
    
    def db_of_write(self, model, **hints):
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_local, model_name, **hints):
        return True  #Las tablas se crean en las dos bases