USE [SIAC]
GO
/****** Object:  Table [dbo].[S43alm_almacenes]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43alm_almacenes](
	[almacen_id] [int] IDENTITY(1,1) NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](150) NOT NULL,
	[ubicacion] [nvarchar](300) NULL,
	[esta_activo] [bit] NOT NULL,
	[fecha_creacion] [datetime] NOT NULL,
 CONSTRAINT [PK_alm_almacenes] PRIMARY KEY CLUSTERED 
(
	[almacen_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_alm_almacenes_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43alm_movimiento_detalle]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43alm_movimiento_detalle](
	[movimiento_detalle_id] [int] IDENTITY(1,1) NOT NULL,
	[movimiento_id] [int] NOT NULL,
	[bien_id] [int] NOT NULL,
	[cantidad] [decimal](18, 6) NOT NULL,
	[cantidad_texto] [varchar](30) NULL,
	[es_devolvible] [bit] NOT NULL,
	[observacion] [nvarchar](500) NULL,
	[fecha_creacion] [datetime] NOT NULL,
 CONSTRAINT [PK_alm_movimiento_detalle] PRIMARY KEY CLUSTERED 
(
	[movimiento_detalle_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_alm_mov_det_bien_modalidad] UNIQUE NONCLUSTERED 
(
	[movimiento_id] ASC,
	[bien_id] ASC,
	[es_devolvible] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43alm_movimientos]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43alm_movimientos](
	[movimiento_id] [int] IDENTITY(1,1) NOT NULL,
	[almacen_id] [int] NOT NULL,
	[tipo_movimiento_id] [smallint] NOT NULL,
	[estado_movimiento_id] [smallint] NOT NULL,
	[movimiento_origen_id] [int] NULL,
	[fecha_movimiento] [datetime] NOT NULL,
	[documento_referencia] [nvarchar](100) NULL,
	[fecha_documento] [date] NULL,
	[destinatario] [nvarchar](250) NULL,
	[observacion] [nvarchar](1000) NULL,
	[fecha_confirmacion] [datetime] NULL,
	[encargado_almacen_id] [smallint] NOT NULL,
	[c_usuari_login] [char](20) NOT NULL,
	[fecha_creacion] [datetime] NOT NULL,
	[fecha_modificacion] [datetime] NULL,
 CONSTRAINT [PK_alm_movimientos] PRIMARY KEY CLUSTERED 
(
	[movimiento_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43bah_personal]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43bah_personal](
	[personal_id] [smallint] IDENTITY(1,1) NOT NULL,
	[apellido_paterno] [nvarchar](50) NOT NULL,
	[apellido_materno] [nvarchar](50) NOT NULL,
	[nombres] [nvarchar](150) NOT NULL,
	[es_evaluador_edan] [bit] NOT NULL,
	[es_encargado_almacen] [bit] NOT NULL,
	[esta_activo] [bit] NOT NULL,
	[fecha_creacion] [datetime] NOT NULL,
	[fecha_modificacion] [datetime] NULL,
 CONSTRAINT [PK_bah_personal] PRIMARY KEY CLUSTERED 
(
	[personal_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43bah_planilla_entrega]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43bah_planilla_entrega](
	[planilla_entrega_id] [int] IDENTITY(1,1) NOT NULL,
	[numero_planilla] [int] NOT NULL,
	[anio_planilla] [int] NOT NULL,
	[integrante_receptor_id] [int] NOT NULL,
	[fecha_entrega] [date] NOT NULL,
	[estado_planilla_id] [smallint] NOT NULL,
	[observacion] [nvarchar](1000) NULL,
	[fecha_emision] [datetime] NULL,
	[fecha_anulacion] [datetime] NULL,
	[motivo_anulacion] [nvarchar](500) NULL,
	[c_usuari_login] [char](20) NOT NULL,
	[fecha_creacion] [datetime] NOT NULL,
	[fecha_modificacion] [datetime] NULL,
	[movimiento_almacen_id] [int] NULL,
 CONSTRAINT [PK_bah_planilla_entrega] PRIMARY KEY CLUSTERED 
(
	[planilla_entrega_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_alm_estados_movimiento]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_alm_estados_movimiento](
	[estado_movimiento_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_alm_estados_movimiento] PRIMARY KEY CLUSTERED 
(
	[estado_movimiento_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_alm_estados_movimiento_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_alm_tipos_movimiento]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_alm_tipos_movimiento](
	[tipo_movimiento_id] [smallint] NOT NULL,
	[codigo] [varchar](50) NOT NULL,
	[nombre] [nvarchar](150) NOT NULL,
	[naturaleza] [char](1) NOT NULL,
	[requiere_movimiento_origen] [bit] NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_alm_tipos_movimiento] PRIMARY KEY CLUSTERED 
(
	[tipo_movimiento_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_alm_tipos_movimiento_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_bah_bienes]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_bah_bienes](
	[bien_id] [int] IDENTITY(1,1) NOT NULL,
	[categoria_bien_id] [smallint] NOT NULL,
	[unidad_medida_id] [smallint] NOT NULL,
	[codigo] [varchar](50) NOT NULL,
	[nombre] [nvarchar](250) NOT NULL,
	[descripcion] [nvarchar](500) NULL,
	[orden_impresion] [smallint] NULL,
	[esta_activo] [bit] NOT NULL,
	[visible_planilla] [bit] NOT NULL,
 CONSTRAINT [PK_cat_bah_bienes] PRIMARY KEY CLUSTERED 
(
	[bien_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_bah_bienes_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_bah_categorias_bienes]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_bah_categorias_bienes](
	[categoria_bien_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[orden] [smallint] NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_bah_categorias_bienes] PRIMARY KEY CLUSTERED 
(
	[categoria_bien_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_bah_categorias_bienes_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_bah_estados_planilla]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_bah_estados_planilla](
	[estado_planilla_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_bah_estados_planilla] PRIMARY KEY CLUSTERED 
(
	[estado_planilla_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_bah_estados_planilla_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_bah_reglas_entrega]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_bah_reglas_entrega](
	[regla_entrega_id] [int] IDENTITY(1,1) NOT NULL,
	[bien_id] [int] NOT NULL,
	[tipo_calculo_id] [smallint] NOT NULL,
	[cantidad_base] [decimal](18, 6) NOT NULL,
	[cantidad_base_texto] [varchar](30) NULL,
	[aplica_damnificado] [bit] NOT NULL,
	[aplica_afectado] [bit] NOT NULL,
	[cantidad_maxima] [decimal](18, 6) NULL,
	[cantidad_maxima_texto] [varchar](30) NULL,
	[observacion] [nvarchar](500) NULL,
	[esta_activo] [bit] NOT NULL,
	[fecha_creacion] [datetime] NOT NULL,
	[fecha_modificacion] [datetime] NULL,
 CONSTRAINT [PK_cat_bah_reglas_entrega] PRIMARY KEY CLUSTERED 
(
	[regla_entrega_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_bah_tipos_calculo]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_bah_tipos_calculo](
	[tipo_calculo_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](150) NOT NULL,
	[descripcion] [nvarchar](500) NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_bah_tipos_calculo] PRIMARY KEY CLUSTERED 
(
	[tipo_calculo_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_bah_tipos_calculo_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_bah_unidades_medida]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_bah_unidades_medida](
	[unidad_medida_id] [smallint] NOT NULL,
	[codigo] [varchar](20) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[abreviatura] [nvarchar](20) NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_bah_unidades_medida] PRIMARY KEY CLUSTERED 
(
	[unidad_medida_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_bah_unidades_medida_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_categorias_medios_vida]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_categorias_medios_vida](
	[categoria_medio_vida_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_categorias_medios_vida] PRIMARY KEY CLUSTERED 
(
	[categoria_medio_vida_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_categorias_medios_vida_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_condiciones_persona]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_condiciones_persona](
	[condicion_persona_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_condiciones_persona] PRIMARY KEY CLUSTERED 
(
	[condicion_persona_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_condiciones_persona_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_condiciones_vivienda]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_condiciones_vivienda](
	[condicion_vivienda_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_condiciones_vivienda] PRIMARY KEY CLUSTERED 
(
	[condicion_vivienda_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_condiciones_vivienda_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_enfermedades_cronicas]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_enfermedades_cronicas](
	[enfermedad_cronica_id] [smallint] NOT NULL,
	[codigo_formulario] [smallint] NOT NULL,
	[nombre] [nvarchar](200) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_enfermedades_cronicas] PRIMARY KEY CLUSTERED 
(
	[enfermedad_cronica_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_enfermedades_cronicas_codigo] UNIQUE NONCLUSTERED 
(
	[codigo_formulario] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_estados_registro]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_estados_registro](
	[estado_registro_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_estados_registro] PRIMARY KEY CLUSTERED 
(
	[estado_registro_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_estados_registro_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_grados_lesion]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_grados_lesion](
	[grado_lesion_id] [smallint] NOT NULL,
	[codigo] [varchar](10) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_grados_lesion] PRIMARY KEY CLUSTERED 
(
	[grado_lesion_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_grados_lesion_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_materiales_pared]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_materiales_pared](
	[material_pared_id] [smallint] NOT NULL,
	[codigo_formulario] [smallint] NOT NULL,
	[nombre] [nvarchar](200) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_materiales_pared] PRIMARY KEY CLUSTERED 
(
	[material_pared_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_materiales_pared_codigo] UNIQUE NONCLUSTERED 
(
	[codigo_formulario] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_materiales_piso]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_materiales_piso](
	[material_piso_id] [smallint] NOT NULL,
	[codigo_formulario] [smallint] NOT NULL,
	[nombre] [nvarchar](200) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_materiales_piso] PRIMARY KEY CLUSTERED 
(
	[material_piso_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_materiales_piso_codigo] UNIQUE NONCLUSTERED 
(
	[codigo_formulario] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_materiales_techo]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_materiales_techo](
	[material_techo_id] [smallint] NOT NULL,
	[codigo_formulario] [smallint] NOT NULL,
	[nombre] [nvarchar](200) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_materiales_techo] PRIMARY KEY CLUSTERED 
(
	[material_techo_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_materiales_techo_codigo] UNIQUE NONCLUSTERED 
(
	[codigo_formulario] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_roles_familiares]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_roles_familiares](
	[rol_familiar_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_roles_familiares] PRIMARY KEY CLUSTERED 
(
	[rol_familiar_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_roles_familiares_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_tipos_danio_personal]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_tipos_danio_personal](
	[tipo_danio_personal_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_tipos_danio_personal] PRIMARY KEY CLUSTERED 
(
	[tipo_danio_personal_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_tipos_danio_personal_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_tipos_discapacidad]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_tipos_discapacidad](
	[tipo_discapacidad_id] [smallint] NOT NULL,
	[codigo_formulario] [smallint] NOT NULL,
	[nombre] [nvarchar](150) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_tipos_discapacidad] PRIMARY KEY CLUSTERED 
(
	[tipo_discapacidad_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_tipos_discapacidad_codigo] UNIQUE NONCLUSTERED 
(
	[codigo_formulario] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_tipos_documento]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_tipos_documento](
	[tipo_documento_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_tipos_documento] PRIMARY KEY CLUSTERED 
(
	[tipo_documento_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_tipos_documento_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_tipos_medios_vida]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_tipos_medios_vida](
	[tipo_medio_vida_id] [smallint] NOT NULL,
	[categoria_medio_vida_id] [smallint] NOT NULL,
	[codigo_formulario] [smallint] NOT NULL,
	[nombre] [nvarchar](200) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_tipos_medios_vida] PRIMARY KEY CLUSTERED 
(
	[tipo_medio_vida_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_tipos_medios_vida_codigo] UNIQUE NONCLUSTERED 
(
	[categoria_medio_vida_id] ASC,
	[codigo_formulario] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_tipos_peligro]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_tipos_peligro](
	[tipo_peligro_id] [int] NOT NULL,
	[codigo] [varchar](10) NOT NULL,
	[nombre] [nvarchar](200) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_tipos_peligro] PRIMARY KEY CLUSTERED 
(
	[tipo_peligro_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_tipos_peligro_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43cat_tipos_uso_instalacion]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43cat_tipos_uso_instalacion](
	[tipo_uso_instalacion_id] [smallint] NOT NULL,
	[codigo] [varchar](30) NOT NULL,
	[nombre] [nvarchar](100) NOT NULL,
	[esta_activo] [bit] NOT NULL,
 CONSTRAINT [PK_cat_tipos_uso_instalacion] PRIMARY KEY CLUSTERED 
(
	[tipo_uso_instalacion_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_cat_tipos_uso_instalacion_codigo] UNIQUE NONCLUSTERED 
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43edan_emergencias]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43edan_emergencias](
	[emergencia_id] [int] IDENTITY(1,1) NOT NULL,
	[numero_evaluacion] [varchar](50) NOT NULL,
	[codigo_sinpad] [varchar](30) NULL,
	[tipo_peligro_id] [int] NOT NULL,
	[fecha_emergencia] [date] NOT NULL,
	[hora_ocurrencia_estimada] [time](0) NULL,
	[esta_activo] [bit] NOT NULL,
	[c_usuari_login] [char](20) NOT NULL,
	[fecha_creacion] [datetime] NOT NULL,
	[fecha_modificacion] [datetime] NULL,
 CONSTRAINT [PK_edan_emergencias] PRIMARY KEY CLUSTERED 
(
	[emergencia_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43edan_formulario_2a]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43edan_formulario_2a](
	[formulario_2a_id] [int] IDENTITY(1,1) NOT NULL,
	[emergencia_id] [int] NOT NULL,
	[departamento_id] [char](2) NOT NULL,
	[provincia_id] [char](2) NOT NULL,
	[distrito_id] [char](2) NOT NULL,
	[fecha_empadronamiento] [date] NOT NULL,
	[hora_empadronamiento] [time](0) NULL,
	[localidad] [nvarchar](200) NULL,
	[barrio_sector_urbanizacion] [nvarchar](250) NULL,
	[centro_poblado] [nvarchar](200) NULL,
	[caserio] [nvarchar](200) NULL,
	[anexo] [nvarchar](200) NULL,
	[calle_manzana] [nvarchar](250) NULL,
	[edificio_piso_dpto] [nvarchar](250) NULL,
	[otros_ubicacion] [nvarchar](250) NULL,
	[numero_hoja] [smallint] NOT NULL,
	[total_hojas] [smallint] NULL,
	[institucion] [nvarchar](250) NULL,
	[evaluador_id] [smallint] NOT NULL,
	[estado_registro_id] [smallint] NOT NULL,
	[c_usuari_login] [char](20) NOT NULL,
	[fecha_creacion] [datetime] NOT NULL,
	[fecha_modificacion] [datetime] NULL,
 CONSTRAINT [PK_edan_formulario_2a] PRIMARY KEY CLUSTERED 
(
	[formulario_2a_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43edan_formulario_2a_familias]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43edan_formulario_2a_familias](
	[familia_id] [int] IDENTITY(1,1) NOT NULL,
	[vivienda_id] [int] NOT NULL,
	[numero_orden] [smallint] NOT NULL,
	[fecha_creacion] [datetime] NOT NULL,
 CONSTRAINT [PK_f2a_familias] PRIMARY KEY CLUSTERED 
(
	[familia_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_f2a_familia_orden] UNIQUE NONCLUSTERED 
(
	[vivienda_id] ASC,
	[numero_orden] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43edan_formulario_2a_integrantes]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43edan_formulario_2a_integrantes](
	[integrante_id] [int] IDENTITY(1,1) NOT NULL,
	[familia_id] [int] NOT NULL,
	[persona_id] [int] NOT NULL,
	[rol_familiar_id] [smallint] NOT NULL,
	[numero_orden] [smallint] NOT NULL,
	[edad] [smallint] NOT NULL,
	[condicion_persona_id] [smallint] NOT NULL,
	[tipo_danio_personal_id] [smallint] NULL,
	[grado_lesion_id] [smallint] NULL,
	[gestante_semanas] [smallint] NULL,
	[tipo_discapacidad_id] [smallint] NULL,
	[enfermedad_cronica_id] [smallint] NULL,
	[fecha_creacion] [datetime] NOT NULL,
 CONSTRAINT [PK_f2a_integrantes] PRIMARY KEY CLUSTERED 
(
	[integrante_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_f2a_integrante_orden] UNIQUE NONCLUSTERED 
(
	[familia_id] ASC,
	[numero_orden] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_f2a_integrante_persona] UNIQUE NONCLUSTERED 
(
	[familia_id] ASC,
	[persona_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43edan_formulario_2a_medios_vida]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43edan_formulario_2a_medios_vida](
	[medio_vida_id] [int] IDENTITY(1,1) NOT NULL,
	[familia_id] [int] NOT NULL,
	[tipo_medio_vida_id] [smallint] NOT NULL,
	[cantidad] [int] NOT NULL,
	[observacion] [nvarchar](500) NULL,
	[fecha_creacion] [datetime] NOT NULL,
 CONSTRAINT [PK_f2a_medios_vida] PRIMARY KEY CLUSTERED 
(
	[medio_vida_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_f2a_medio_vida_familia_tipo] UNIQUE NONCLUSTERED 
(
	[familia_id] ASC,
	[tipo_medio_vida_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43edan_formulario_2a_viviendas]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43edan_formulario_2a_viviendas](
	[vivienda_id] [int] IDENTITY(1,1) NOT NULL,
	[formulario_2a_id] [int] NOT NULL,
	[numero_orden] [smallint] NOT NULL,
	[numero_lote] [nvarchar](50) NULL,
	[tenencia_propia] [bit] NULL,
	[tipo_uso_instalacion_id] [smallint] NOT NULL,
	[condicion_vivienda_id] [smallint] NULL,
	[material_techo_id] [smallint] NULL,
	[material_pared_id] [smallint] NULL,
	[material_piso_id] [smallint] NULL,
	[fecha_creacion] [datetime] NOT NULL,
 CONSTRAINT [PK_f2a_vivienda] PRIMARY KEY CLUSTERED 
(
	[vivienda_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_f2a_instalacion_orden] UNIQUE NONCLUSTERED 
(
	[formulario_2a_id] ASC,
	[numero_orden] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[S43personas]    Script Date: 3/10/2026 12:35:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[S43personas](
	[persona_id] [int] IDENTITY(1,1) NOT NULL,
	[tipo_documento_id] [smallint] NULL,
	[numero_documento] [varchar](20) NULL,
	[apellido_paterno] [nvarchar](50) NOT NULL,
	[apellido_materno] [nvarchar](50) NOT NULL,
	[nombres] [nvarchar](150) NOT NULL,
	[fecha_nacimiento] [date] NOT NULL,
	[sexo] [char](1) NOT NULL,
	[telefono] [nvarchar](50) NOT NULL,
	[correo] [nvarchar](50) NOT NULL,
	[esta_activo] [bit] NOT NULL,
	[fecha_creacion] [datetime] NOT NULL,
	[c_usuari_login] [char](20) NOT NULL,
	[fecha_modificacion] [datetime] NULL,
 CONSTRAINT [PK_personas] PRIMARY KEY CLUSTERED 
(
	[persona_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[S43alm_almacenes] ADD  CONSTRAINT [DF_alm_almacenes_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43alm_almacenes] ADD  CONSTRAINT [DF_alm_almacenes_fecha]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle] ADD  CONSTRAINT [DF_alm_mov_det_devolvible]  DEFAULT ((0)) FOR [es_devolvible]
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle] ADD  CONSTRAINT [DF_alm_mov_det_fecha]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43alm_movimientos] ADD  CONSTRAINT [DF_alm_movimiento_estado]  DEFAULT ((1)) FOR [estado_movimiento_id]
GO
ALTER TABLE [dbo].[S43alm_movimientos] ADD  CONSTRAINT [DF_alm_movimiento_fecha]  DEFAULT (getdate()) FOR [fecha_movimiento]
GO
ALTER TABLE [dbo].[S43alm_movimientos] ADD  CONSTRAINT [DF_alm_movimiento_fecha_creacion]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43bah_personal] ADD  CONSTRAINT [DF_bah_personal_evaluador]  DEFAULT ((0)) FOR [es_evaluador_edan]
GO
ALTER TABLE [dbo].[S43bah_personal] ADD  CONSTRAINT [DF_bah_personal_almacen]  DEFAULT ((0)) FOR [es_encargado_almacen]
GO
ALTER TABLE [dbo].[S43bah_personal] ADD  CONSTRAINT [DF_bah_personal_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43bah_personal] ADD  CONSTRAINT [DF_bah_personal_fecha_creacion]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43bah_planilla_entrega] ADD  CONSTRAINT [DF_bah_planilla_estado]  DEFAULT ((1)) FOR [estado_planilla_id]
GO
ALTER TABLE [dbo].[S43bah_planilla_entrega] ADD  CONSTRAINT [DF_bah_planilla_fecha_creacion]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43cat_alm_estados_movimiento] ADD  CONSTRAINT [DF_cat_alm_estado_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_alm_tipos_movimiento] ADD  CONSTRAINT [DF_cat_alm_tipo_requiere_origen]  DEFAULT ((0)) FOR [requiere_movimiento_origen]
GO
ALTER TABLE [dbo].[S43cat_alm_tipos_movimiento] ADD  CONSTRAINT [DF_cat_alm_tipo_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_bah_bienes] ADD  CONSTRAINT [DF_cat_bah_bien_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_bah_bienes] ADD  CONSTRAINT [DF_S43cat_bah_bienes_visible_planilla]  DEFAULT ((1)) FOR [visible_planilla]
GO
ALTER TABLE [dbo].[S43cat_bah_categorias_bienes] ADD  CONSTRAINT [DF_cat_bah_categoria_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_bah_estados_planilla] ADD  CONSTRAINT [DF_cat_bah_estado_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] ADD  CONSTRAINT [DF_cat_bah_regla_damnificado]  DEFAULT ((0)) FOR [aplica_damnificado]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] ADD  CONSTRAINT [DF_cat_bah_regla_afectado]  DEFAULT ((0)) FOR [aplica_afectado]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] ADD  CONSTRAINT [DF_cat_bah_regla_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] ADD  CONSTRAINT [DF_cat_bah_regla_fecha_creacion]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43cat_bah_tipos_calculo] ADD  CONSTRAINT [DF_cat_bah_tipos_calculo_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_bah_unidades_medida] ADD  CONSTRAINT [DF_cat_bah_unidad_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_categorias_medios_vida] ADD  CONSTRAINT [DF_cat_categorias_medios_vida_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_condiciones_persona] ADD  CONSTRAINT [DF_cat_condiciones_persona_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_condiciones_vivienda] ADD  CONSTRAINT [DF_cat_condiciones_vivienda_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_enfermedades_cronicas] ADD  CONSTRAINT [DF_cat_enfermedades_cronicas_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_estados_registro] ADD  CONSTRAINT [DF_cat_estados_registro_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_grados_lesion] ADD  CONSTRAINT [DF_cat_grados_lesion_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_materiales_pared] ADD  CONSTRAINT [DF_cat_materiales_pared_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_materiales_piso] ADD  CONSTRAINT [DF_cat_materiales_piso_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_materiales_techo] ADD  CONSTRAINT [DF_cat_materiales_techo_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_roles_familiares] ADD  CONSTRAINT [DF_cat_roles_familiares_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_tipos_danio_personal] ADD  CONSTRAINT [DF_cat_tipos_danio_personal_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_tipos_discapacidad] ADD  CONSTRAINT [DF_cat_tipos_discapacidad_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_tipos_documento] ADD  CONSTRAINT [DF_cat_tipos_documento_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_tipos_medios_vida] ADD  CONSTRAINT [DF_cat_tipos_medios_vida_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_tipos_peligro] ADD  CONSTRAINT [DF_cat_tipos_peligro_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43cat_tipos_uso_instalacion] ADD  CONSTRAINT [DF_cat_tipos_uso_instalacion_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43edan_emergencias] ADD  CONSTRAINT [DF_edan_emergencias_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43edan_emergencias] ADD  CONSTRAINT [DF_edan_emergencias_fecha_creacion]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a] ADD  CONSTRAINT [DF_f2a_numero_hoja]  DEFAULT ((1)) FOR [numero_hoja]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a] ADD  CONSTRAINT [DF_f2a_estado]  DEFAULT ((1)) FOR [estado_registro_id]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a] ADD  CONSTRAINT [DF_f2a_fecha_creacion]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_familias] ADD  CONSTRAINT [DF_f2a_familia_fecha]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] ADD  CONSTRAINT [DF_f2a_integrante_fecha]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_medios_vida] ADD  CONSTRAINT [DF_f2a_medio_vida_fecha]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas] ADD  CONSTRAINT [DF_f2a_vivienda_fecha]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43personas] ADD  CONSTRAINT [DF_personas_activo]  DEFAULT ((1)) FOR [esta_activo]
GO
ALTER TABLE [dbo].[S43personas] ADD  CONSTRAINT [DF_personas_fecha_creacion]  DEFAULT (getdate()) FOR [fecha_creacion]
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle]  WITH CHECK ADD  CONSTRAINT [FK_alm_mov_det_bien] FOREIGN KEY([bien_id])
REFERENCES [dbo].[S43cat_bah_bienes] ([bien_id])
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle] CHECK CONSTRAINT [FK_alm_mov_det_bien]
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle]  WITH CHECK ADD  CONSTRAINT [FK_alm_mov_det_movimiento] FOREIGN KEY([movimiento_id])
REFERENCES [dbo].[S43alm_movimientos] ([movimiento_id])
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle] CHECK CONSTRAINT [FK_alm_mov_det_movimiento]
GO
ALTER TABLE [dbo].[S43alm_movimientos]  WITH CHECK ADD  CONSTRAINT [FK_alm_movimiento_almacen] FOREIGN KEY([almacen_id])
REFERENCES [dbo].[S43alm_almacenes] ([almacen_id])
GO
ALTER TABLE [dbo].[S43alm_movimientos] CHECK CONSTRAINT [FK_alm_movimiento_almacen]
GO
ALTER TABLE [dbo].[S43alm_movimientos]  WITH CHECK ADD  CONSTRAINT [FK_alm_movimiento_estado] FOREIGN KEY([estado_movimiento_id])
REFERENCES [dbo].[S43cat_alm_estados_movimiento] ([estado_movimiento_id])
GO
ALTER TABLE [dbo].[S43alm_movimientos] CHECK CONSTRAINT [FK_alm_movimiento_estado]
GO
ALTER TABLE [dbo].[S43alm_movimientos]  WITH CHECK ADD  CONSTRAINT [FK_alm_movimiento_origen] FOREIGN KEY([movimiento_origen_id])
REFERENCES [dbo].[S43alm_movimientos] ([movimiento_id])
GO
ALTER TABLE [dbo].[S43alm_movimientos] CHECK CONSTRAINT [FK_alm_movimiento_origen]
GO
ALTER TABLE [dbo].[S43alm_movimientos]  WITH CHECK ADD  CONSTRAINT [FK_alm_movimiento_tipo] FOREIGN KEY([tipo_movimiento_id])
REFERENCES [dbo].[S43cat_alm_tipos_movimiento] ([tipo_movimiento_id])
GO
ALTER TABLE [dbo].[S43alm_movimientos] CHECK CONSTRAINT [FK_alm_movimiento_tipo]
GO
ALTER TABLE [dbo].[S43alm_movimientos]  WITH CHECK ADD  CONSTRAINT [FK_S43alm_movimientos_S43bah_personal] FOREIGN KEY([encargado_almacen_id])
REFERENCES [dbo].[S43bah_personal] ([personal_id])
GO
ALTER TABLE [dbo].[S43alm_movimientos] CHECK CONSTRAINT [FK_S43alm_movimientos_S43bah_personal]
GO
ALTER TABLE [dbo].[S43bah_planilla_entrega]  WITH CHECK ADD  CONSTRAINT [FK_bah_planilla_estado] FOREIGN KEY([estado_planilla_id])
REFERENCES [dbo].[S43cat_bah_estados_planilla] ([estado_planilla_id])
GO
ALTER TABLE [dbo].[S43bah_planilla_entrega] CHECK CONSTRAINT [FK_bah_planilla_estado]
GO
ALTER TABLE [dbo].[S43bah_planilla_entrega]  WITH CHECK ADD  CONSTRAINT [FK_bah_planilla_integrante_receptor] FOREIGN KEY([integrante_receptor_id])
REFERENCES [dbo].[S43edan_formulario_2a_integrantes] ([integrante_id])
GO
ALTER TABLE [dbo].[S43bah_planilla_entrega] CHECK CONSTRAINT [FK_bah_planilla_integrante_receptor]
GO
ALTER TABLE [dbo].[S43bah_planilla_entrega]  WITH CHECK ADD  CONSTRAINT [FK_bah_planilla_movimiento_almacen] FOREIGN KEY([movimiento_almacen_id])
REFERENCES [dbo].[S43alm_movimientos] ([movimiento_id])
GO
ALTER TABLE [dbo].[S43bah_planilla_entrega] CHECK CONSTRAINT [FK_bah_planilla_movimiento_almacen]
GO
ALTER TABLE [dbo].[S43cat_bah_bienes]  WITH CHECK ADD  CONSTRAINT [FK_cat_bah_bien_categoria] FOREIGN KEY([categoria_bien_id])
REFERENCES [dbo].[S43cat_bah_categorias_bienes] ([categoria_bien_id])
GO
ALTER TABLE [dbo].[S43cat_bah_bienes] CHECK CONSTRAINT [FK_cat_bah_bien_categoria]
GO
ALTER TABLE [dbo].[S43cat_bah_bienes]  WITH CHECK ADD  CONSTRAINT [FK_cat_bah_bien_unidad] FOREIGN KEY([unidad_medida_id])
REFERENCES [dbo].[S43cat_bah_unidades_medida] ([unidad_medida_id])
GO
ALTER TABLE [dbo].[S43cat_bah_bienes] CHECK CONSTRAINT [FK_cat_bah_bien_unidad]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega]  WITH CHECK ADD  CONSTRAINT [FK_cat_bah_regla_bien] FOREIGN KEY([bien_id])
REFERENCES [dbo].[S43cat_bah_bienes] ([bien_id])
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] CHECK CONSTRAINT [FK_cat_bah_regla_bien]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega]  WITH CHECK ADD  CONSTRAINT [FK_cat_bah_regla_tipo_calculo] FOREIGN KEY([tipo_calculo_id])
REFERENCES [dbo].[S43cat_bah_tipos_calculo] ([tipo_calculo_id])
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] CHECK CONSTRAINT [FK_cat_bah_regla_tipo_calculo]
GO
ALTER TABLE [dbo].[S43cat_tipos_medios_vida]  WITH CHECK ADD  CONSTRAINT [FK_cat_tipos_medios_vida_categoria] FOREIGN KEY([categoria_medio_vida_id])
REFERENCES [dbo].[S43cat_categorias_medios_vida] ([categoria_medio_vida_id])
GO
ALTER TABLE [dbo].[S43cat_tipos_medios_vida] CHECK CONSTRAINT [FK_cat_tipos_medios_vida_categoria]
GO
ALTER TABLE [dbo].[S43edan_emergencias]  WITH CHECK ADD  CONSTRAINT [FK_edan_emergencias_tipo_peligro] FOREIGN KEY([tipo_peligro_id])
REFERENCES [dbo].[S43cat_tipos_peligro] ([tipo_peligro_id])
GO
ALTER TABLE [dbo].[S43edan_emergencias] CHECK CONSTRAINT [FK_edan_emergencias_tipo_peligro]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a]  WITH CHECK ADD  CONSTRAINT [FK_f2a_emergencia] FOREIGN KEY([emergencia_id])
REFERENCES [dbo].[S43edan_emergencias] ([emergencia_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a] CHECK CONSTRAINT [FK_f2a_emergencia]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a]  WITH CHECK ADD  CONSTRAINT [FK_f2a_estado] FOREIGN KEY([estado_registro_id])
REFERENCES [dbo].[S43cat_estados_registro] ([estado_registro_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a] CHECK CONSTRAINT [FK_f2a_estado]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a]  WITH CHECK ADD  CONSTRAINT [FK_S43edan_formulario_2a_S43bah_personal] FOREIGN KEY([evaluador_id])
REFERENCES [dbo].[S43bah_personal] ([personal_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a] CHECK CONSTRAINT [FK_S43edan_formulario_2a_S43bah_personal]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_familias]  WITH CHECK ADD  CONSTRAINT [FK_f2a_familia_vivienda] FOREIGN KEY([vivienda_id])
REFERENCES [dbo].[S43edan_formulario_2a_viviendas] ([vivienda_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_familias] CHECK CONSTRAINT [FK_f2a_familia_vivienda]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [FK_f2a_integrante_condicion] FOREIGN KEY([condicion_persona_id])
REFERENCES [dbo].[S43cat_condiciones_persona] ([condicion_persona_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [FK_f2a_integrante_condicion]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [FK_f2a_integrante_danio] FOREIGN KEY([tipo_danio_personal_id])
REFERENCES [dbo].[S43cat_tipos_danio_personal] ([tipo_danio_personal_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [FK_f2a_integrante_danio]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [FK_f2a_integrante_familia] FOREIGN KEY([familia_id])
REFERENCES [dbo].[S43edan_formulario_2a_familias] ([familia_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [FK_f2a_integrante_familia]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [FK_f2a_integrante_grado_lesion] FOREIGN KEY([grado_lesion_id])
REFERENCES [dbo].[S43cat_grados_lesion] ([grado_lesion_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [FK_f2a_integrante_grado_lesion]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [FK_f2a_integrante_persona] FOREIGN KEY([persona_id])
REFERENCES [dbo].[S43personas] ([persona_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [FK_f2a_integrante_persona]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [FK_f2a_integrante_rol] FOREIGN KEY([rol_familiar_id])
REFERENCES [dbo].[S43cat_roles_familiares] ([rol_familiar_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [FK_f2a_integrante_rol]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [FK_f2a_salud_discapacidad] FOREIGN KEY([tipo_discapacidad_id])
REFERENCES [dbo].[S43cat_tipos_discapacidad] ([tipo_discapacidad_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [FK_f2a_salud_discapacidad]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [FK_f2a_salud_enfermedad] FOREIGN KEY([enfermedad_cronica_id])
REFERENCES [dbo].[S43cat_enfermedades_cronicas] ([enfermedad_cronica_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [FK_f2a_salud_enfermedad]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_medios_vida]  WITH CHECK ADD  CONSTRAINT [FK_f2a_medio_vida_familia] FOREIGN KEY([familia_id])
REFERENCES [dbo].[S43edan_formulario_2a_familias] ([familia_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_medios_vida] CHECK CONSTRAINT [FK_f2a_medio_vida_familia]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_medios_vida]  WITH CHECK ADD  CONSTRAINT [FK_f2a_medio_vida_tipo] FOREIGN KEY([tipo_medio_vida_id])
REFERENCES [dbo].[S43cat_tipos_medios_vida] ([tipo_medio_vida_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_medios_vida] CHECK CONSTRAINT [FK_f2a_medio_vida_tipo]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas]  WITH CHECK ADD  CONSTRAINT [FK_f2a_instalacion_formulario] FOREIGN KEY([formulario_2a_id])
REFERENCES [dbo].[S43edan_formulario_2a] ([formulario_2a_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas] CHECK CONSTRAINT [FK_f2a_instalacion_formulario]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas]  WITH CHECK ADD  CONSTRAINT [FK_f2a_instalacion_pared] FOREIGN KEY([material_pared_id])
REFERENCES [dbo].[S43cat_materiales_pared] ([material_pared_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas] CHECK CONSTRAINT [FK_f2a_instalacion_pared]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas]  WITH CHECK ADD  CONSTRAINT [FK_f2a_instalacion_piso] FOREIGN KEY([material_piso_id])
REFERENCES [dbo].[S43cat_materiales_piso] ([material_piso_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas] CHECK CONSTRAINT [FK_f2a_instalacion_piso]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas]  WITH CHECK ADD  CONSTRAINT [FK_f2a_instalacion_techo] FOREIGN KEY([material_techo_id])
REFERENCES [dbo].[S43cat_materiales_techo] ([material_techo_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas] CHECK CONSTRAINT [FK_f2a_instalacion_techo]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas]  WITH CHECK ADD  CONSTRAINT [FK_f2a_instalacion_tipo_uso] FOREIGN KEY([tipo_uso_instalacion_id])
REFERENCES [dbo].[S43cat_tipos_uso_instalacion] ([tipo_uso_instalacion_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas] CHECK CONSTRAINT [FK_f2a_instalacion_tipo_uso]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas]  WITH CHECK ADD  CONSTRAINT [FK_f2a_vivienda_condicion] FOREIGN KEY([condicion_vivienda_id])
REFERENCES [dbo].[S43cat_condiciones_vivienda] ([condicion_vivienda_id])
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas] CHECK CONSTRAINT [FK_f2a_vivienda_condicion]
GO
ALTER TABLE [dbo].[S43personas]  WITH CHECK ADD  CONSTRAINT [FK_personas_tipo_documento] FOREIGN KEY([tipo_documento_id])
REFERENCES [dbo].[S43cat_tipos_documento] ([tipo_documento_id])
GO
ALTER TABLE [dbo].[S43personas] CHECK CONSTRAINT [FK_personas_tipo_documento]
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle]  WITH CHECK ADD  CONSTRAINT [CK_alm_mov_det_cantidad] CHECK  (([cantidad]<>(0)))
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle] CHECK CONSTRAINT [CK_alm_mov_det_cantidad]
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle]  WITH CHECK ADD  CONSTRAINT [CK_alm_mov_det_cantidad_texto] CHECK  (([cantidad_texto] IS NULL OR ltrim(rtrim([cantidad_texto]))<>''))
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle] CHECK CONSTRAINT [CK_alm_mov_det_cantidad_texto]
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle]  WITH CHECK ADD  CONSTRAINT [CK_alm_mov_det_devolvible] CHECK  (([cantidad]<(0) OR [es_devolvible]=(0)))
GO
ALTER TABLE [dbo].[S43alm_movimiento_detalle] CHECK CONSTRAINT [CK_alm_mov_det_devolvible]
GO
ALTER TABLE [dbo].[S43alm_movimientos]  WITH CHECK ADD  CONSTRAINT [CK_alm_movimiento_origen_distinto] CHECK  (([movimiento_origen_id] IS NULL OR [movimiento_origen_id]<>[movimiento_id]))
GO
ALTER TABLE [dbo].[S43alm_movimientos] CHECK CONSTRAINT [CK_alm_movimiento_origen_distinto]
GO
ALTER TABLE [dbo].[S43bah_personal]  WITH CHECK ADD  CONSTRAINT [CK_bah_personal_tipo] CHECK  (([es_evaluador_edan]=(1) OR [es_encargado_almacen]=(1)))
GO
ALTER TABLE [dbo].[S43bah_personal] CHECK CONSTRAINT [CK_bah_personal_tipo]
GO
ALTER TABLE [dbo].[S43cat_alm_tipos_movimiento]  WITH CHECK ADD  CONSTRAINT [CK_cat_alm_tipos_movimiento_naturaleza] CHECK  (([naturaleza]='M' OR [naturaleza]='S' OR [naturaleza]='E'))
GO
ALTER TABLE [dbo].[S43cat_alm_tipos_movimiento] CHECK CONSTRAINT [CK_cat_alm_tipos_movimiento_naturaleza]
GO
ALTER TABLE [dbo].[S43cat_bah_bienes]  WITH CHECK ADD  CONSTRAINT [CK_cat_bah_bien_orden] CHECK  (([orden_impresion] IS NULL OR [orden_impresion]>(0)))
GO
ALTER TABLE [dbo].[S43cat_bah_bienes] CHECK CONSTRAINT [CK_cat_bah_bien_orden]
GO
ALTER TABLE [dbo].[S43cat_bah_categorias_bienes]  WITH CHECK ADD  CONSTRAINT [CK_cat_bah_categorias_orden] CHECK  (([orden]>(0)))
GO
ALTER TABLE [dbo].[S43cat_bah_categorias_bienes] CHECK CONSTRAINT [CK_cat_bah_categorias_orden]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega]  WITH CHECK ADD  CONSTRAINT [CK_cat_bah_regla_aplicacion] CHECK  (([aplica_damnificado]=(1) OR [aplica_afectado]=(1)))
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] CHECK CONSTRAINT [CK_cat_bah_regla_aplicacion]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega]  WITH CHECK ADD  CONSTRAINT [CK_cat_bah_regla_base_texto] CHECK  (([cantidad_base_texto] IS NULL OR ltrim(rtrim([cantidad_base_texto]))<>''))
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] CHECK CONSTRAINT [CK_cat_bah_regla_base_texto]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega]  WITH CHECK ADD  CONSTRAINT [CK_cat_bah_regla_cantidad_base] CHECK  (([cantidad_base]>(0)))
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] CHECK CONSTRAINT [CK_cat_bah_regla_cantidad_base]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega]  WITH CHECK ADD  CONSTRAINT [CK_cat_bah_regla_cantidad_maxima] CHECK  (([cantidad_maxima] IS NULL OR [cantidad_maxima]>(0)))
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] CHECK CONSTRAINT [CK_cat_bah_regla_cantidad_maxima]
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega]  WITH CHECK ADD  CONSTRAINT [CK_cat_bah_regla_maximo_texto] CHECK  (([cantidad_maxima_texto] IS NULL OR ltrim(rtrim([cantidad_maxima_texto]))<>''))
GO
ALTER TABLE [dbo].[S43cat_bah_reglas_entrega] CHECK CONSTRAINT [CK_cat_bah_regla_maximo_texto]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a]  WITH CHECK ADD  CONSTRAINT [CK_f2a_numero_hoja] CHECK  (([numero_hoja]>(0)))
GO
ALTER TABLE [dbo].[S43edan_formulario_2a] CHECK CONSTRAINT [CK_f2a_numero_hoja]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a]  WITH CHECK ADD  CONSTRAINT [CK_f2a_total_hojas] CHECK  (([total_hojas] IS NULL OR [total_hojas]>=[numero_hoja]))
GO
ALTER TABLE [dbo].[S43edan_formulario_2a] CHECK CONSTRAINT [CK_f2a_total_hojas]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_familias]  WITH CHECK ADD  CONSTRAINT [CK_f2a_familia_orden] CHECK  (([numero_orden]>(0)))
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_familias] CHECK CONSTRAINT [CK_f2a_familia_orden]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [CK_f2a_integrante_edad] CHECK  (([edad]>=(0) AND [edad]<=(130)))
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [CK_f2a_integrante_edad]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [CK_f2a_integrante_grado] CHECK  (([grado_lesion_id] IS NULL OR [tipo_danio_personal_id]=(1)))
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [CK_f2a_integrante_grado]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes]  WITH CHECK ADD  CONSTRAINT [CK_f2a_salud_gestante] CHECK  (([gestante_semanas] IS NULL OR [gestante_semanas]>=(1) AND [gestante_semanas]<=(45)))
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_integrantes] CHECK CONSTRAINT [CK_f2a_salud_gestante]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_medios_vida]  WITH CHECK ADD  CONSTRAINT [CK_f2a_medio_vida_cantidad] CHECK  (([cantidad]>(0)))
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_medios_vida] CHECK CONSTRAINT [CK_f2a_medio_vida_cantidad]
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas]  WITH CHECK ADD  CONSTRAINT [CK_f2a_instalacion_orden] CHECK  (([numero_orden]>(0)))
GO
ALTER TABLE [dbo].[S43edan_formulario_2a_viviendas] CHECK CONSTRAINT [CK_f2a_instalacion_orden]
GO
ALTER TABLE [dbo].[S43personas]  WITH CHECK ADD  CONSTRAINT [CK_personas_documento] CHECK  (([numero_documento] IS NULL AND [tipo_documento_id] IS NULL OR [numero_documento] IS NOT NULL AND [tipo_documento_id] IS NOT NULL))
GO
ALTER TABLE [dbo].[S43personas] CHECK CONSTRAINT [CK_personas_documento]
GO

/****** Object:  View [dbo].[DISTRITO]    Script Date: 3/10/2026 23:14:06 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


ALTER VIEW [dbo].[DISTRITO]
AS

SELECT left(c_lugar_id,2) as departamento_id,
substring(c_lugar_id,3,2) as provincia_id,
substring(c_lugar_id,5,2) as distrito_id, 
n_lugar_nombre as distrito_nombre, 
f_activo
FROM PVL.dbo.LUGAR
WHERE c_tiplug_id=3

GO
