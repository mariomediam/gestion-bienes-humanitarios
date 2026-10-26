/*
    Cambia archivo_id de BIGINT IDENTITY a uniqueidentifier.

    Borra la tabla y la vuelve a crear. Las filas de prueba se pierden.
    El resto de columnas queda igual que en la tabla actual.
    La aplicacion genera el UUID (uuid4) al insertar. NEWID() cubre
    un alta hecha fuera de la aplicacion.

    SQL Server 2008 R2: uniqueidentifier, datetime2 y SYSDATETIME().
*/
USE SIAC;
GO

IF OBJECT_ID(N'dbo.S43edan_formulario_2a_archivos', N'U') IS NOT NULL
    DROP TABLE dbo.S43edan_formulario_2a_archivos;
GO

SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO

CREATE TABLE dbo.S43edan_formulario_2a_archivos
(
    archivo_id           uniqueidentifier NOT NULL
        CONSTRAINT DF_f2a_archivos_archivo_id DEFAULT (NEWID()),
    formulario_2a_id     int NOT NULL,
    nombre_original      varchar(255) NOT NULL,
    nombre_archivo       varchar(255) NOT NULL,
    ruta_archivo         varchar(500) NOT NULL,
    extension            varchar(10) NULL,
    tamano_bytes         bigint NULL,
    esta_activo          bit NOT NULL
        CONSTRAINT DF_f2a_archivos_esta_activo DEFAULT ((1)),
    fecha_registro       datetime2 NOT NULL
        CONSTRAINT DF_f2a_archivos_fecha_registro DEFAULT (SYSDATETIME()),
    c_usuari_login       char(20) NOT NULL,

    CONSTRAINT PK_f2a_archivos
        PRIMARY KEY CLUSTERED (archivo_id),

    CONSTRAINT FK_f2a_archivo_formulario
        FOREIGN KEY (formulario_2a_id)
        REFERENCES dbo.S43edan_formulario_2a (formulario_2a_id)
);
GO
