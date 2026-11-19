/*
    Documentos digitales de un movimiento de almacén.

    El archivo se guarda fuera de SQL Server. Esta tabla guarda
    el identificador, el movimiento, el nombre original, el nombre
    almacenado, la ruta relativa, la extensión, el tamaño, el estado,
    la fecha y el login. La baja es lógica (esta_activo = 0).

    La aplicación genera el UUID (uuid4) al insertar. NEWID() cubre
    un alta hecha fuera de la aplicación.

    SQL Server 2008 R2: uniqueidentifier, datetime2 y SYSDATETIME().
    Este script no borra la tabla si ya existe.
*/
USE SIAC;
GO

IF OBJECT_ID(N'dbo.S43alm_movimientos_archivos', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.S43alm_movimientos_archivos
    (
        archivo_id           uniqueidentifier NOT NULL
            CONSTRAINT DF_mov_archivos_archivo_id DEFAULT (NEWID()),
        movimiento_id        int NOT NULL,
        nombre_original      varchar(255) NOT NULL,
        nombre_archivo       varchar(255) NOT NULL,
        ruta_archivo         varchar(500) NOT NULL,
        extension            varchar(10) NULL,
        tamano_bytes         bigint NULL,
        esta_activo          bit NOT NULL
            CONSTRAINT DF_mov_archivos_esta_activo DEFAULT ((1)),
        fecha_registro       datetime2 NOT NULL
            CONSTRAINT DF_mov_archivos_fecha_registro DEFAULT (SYSDATETIME()),
        c_usuari_login       char(20) NOT NULL,

        CONSTRAINT PK_mov_archivos
            PRIMARY KEY CLUSTERED (archivo_id),

        CONSTRAINT FK_mov_archivo_movimiento
            FOREIGN KEY (movimiento_id)
            REFERENCES dbo.S43alm_movimientos (movimiento_id)
    );
END
GO
