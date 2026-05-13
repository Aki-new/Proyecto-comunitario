BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "colores" (
	"id"	INTEGER,
	"valor"	TEXT NOT NULL,
	"estado"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "pacientes" (
	"id"	INTEGER,
	"nombre1"	TEXT NOT NULL,
	"nombre2"	TEXT,
	"apellido1"	TEXT NOT NULL,
	"apellido2"	TEXT,
	"cedula"	TEXT UNIQUE,
	"lugar_nacimiento"	TEXT NOT NULL,
	"fecha_nacimiento"	TEXT NOT NULL,
	"estado_vital"	INTEGER NOT NULL,
	"estado"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "tarjetas" (
	"id"	INTEGER,
	"num_historia"	TEXT NOT NULL UNIQUE,
	"id_paciente"	INTEGER NOT NULL,
	"id_color"	INTEGER NOT NULL,
	"estado"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("id_color") REFERENCES "colores"("id"),
	FOREIGN KEY("id_paciente") REFERENCES "pacientes"("id")
);
CREATE TABLE IF NOT EXISTS "usuarios" (
	"id"	INTEGER,
	"nombre"	TEXT NOT NULL,
	"apellido"	TEXT NOT NULL,
	"cedula"	INTEGER NOT NULL UNIQUE,
	"usuario"	TEXT NOT NULL UNIQUE,
	"clave"	TEXT NOT NULL,
	"estado"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE VIEW vista_paciente_tarjeta AS
SELECT 
    pacientes.nombre1, 
    pacientes.nombre2, 
    pacientes.apellido1, 
    pacientes.apellido2, 
    pacientes.cedula, 
    pacientes.fecha_nacimiento, 
    pacientes.lugar_nacimiento, 
    pacientes.estado_vital,
    tarjetas.num_historia,
    colores.valor AS color
FROM pacientes
JOIN tarjetas ON pacientes.id = tarjetas.id_paciente
JOIN colores ON colores.id = tarjetas.id_color
WHERE pacientes.estado = 1;
CREATE INDEX IF NOT EXISTS "idx_historias_id_paciente" ON "tarjetas" (
	"id_paciente"
);
CREATE INDEX IF NOT EXISTS "idx_pacientes_numero_cedula" ON "pacientes" (
	"cedula"
);
CREATE INDEX IF NOT EXISTS "idx_pacientes_primer_apellido" ON "pacientes" (
	"apellido1"
);
CREATE INDEX IF NOT EXISTS "idx_pacientes_primer_nombre" ON "pacientes" (
	"nombre1"
);
CREATE INDEX IF NOT EXISTS "idx_usuarios_primer_apellido" ON "usuarios" (
	"apellido"
);
CREATE INDEX IF NOT EXISTS "idx_usuarios_primer_nombre" ON "usuarios" (
	"nombre"
);
COMMIT;
