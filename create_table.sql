-- Eliminar tablas existentes si existen
DROP TABLE IF EXISTS catas_a;
DROP TABLE IF EXISTS catas_b;
DROP TABLE IF EXISTS catas_c;
DROP TABLE IF EXISTS catas_d;

-- Crear tabla para Ron A
CREATE TABLE catas_a (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    pureza INTEGER NOT NULL,
    olfato_intensidad INTEGER NOT NULL,
    olfato_complejidad INTEGER NOT NULL,
    gusto_intensidad INTEGER NOT NULL,
    gusto_complejidad INTEGER NOT NULL,
    gusto_persistencia INTEGER NOT NULL,
    armonia INTEGER NOT NULL,
    total INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);

-- Crear tabla para Ron B
CREATE TABLE catas_b (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    pureza INTEGER NOT NULL,
    olfato_intensidad INTEGER NOT NULL,
    olfato_complejidad INTEGER NOT NULL,
    gusto_intensidad INTEGER NOT NULL,
    gusto_complejidad INTEGER NOT NULL,
    gusto_persistencia INTEGER NOT NULL,
    armonia INTEGER NOT NULL,
    total INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);

-- Crear tabla para Ron C
CREATE TABLE catas_c (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    pureza INTEGER NOT NULL,
    olfato_intensidad INTEGER NOT NULL,
    olfato_complejidad INTEGER NOT NULL,
    gusto_intensidad INTEGER NOT NULL,
    gusto_complejidad INTEGER NOT NULL,
    gusto_persistencia INTEGER NOT NULL,
    armonia INTEGER NOT NULL,
    total INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);

-- Crear tabla para Ron D
CREATE TABLE catas_d (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    pureza INTEGER NOT NULL,
    olfato_intensidad INTEGER NOT NULL,
    olfato_complejidad INTEGER NOT NULL,
    gusto_intensidad INTEGER NOT NULL,
    gusto_complejidad INTEGER NOT NULL,
    gusto_persistencia INTEGER NOT NULL,
    armonia INTEGER NOT NULL,
    total INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);

-- Crear índices para cada tabla
CREATE INDEX idx_catas_a_nombre ON catas_a(nombre);
CREATE INDEX idx_catas_a_timestamp ON catas_a(timestamp DESC);
CREATE INDEX idx_catas_b_nombre ON catas_b(nombre);
CREATE INDEX idx_catas_b_timestamp ON catas_b(timestamp DESC);
CREATE INDEX idx_catas_c_nombre ON catas_c(nombre);
CREATE INDEX idx_catas_c_timestamp ON catas_c(timestamp DESC);
CREATE INDEX idx_catas_d_nombre ON catas_d(nombre);
CREATE INDEX idx_catas_d_timestamp ON catas_d(timestamp DESC);

-- Habilitar RLS para cada tabla
ALTER TABLE catas_a ENABLE ROW LEVEL SECURITY;
ALTER TABLE catas_b ENABLE ROW LEVEL SECURITY;
ALTER TABLE catas_c ENABLE ROW LEVEL SECURITY;
ALTER TABLE catas_d ENABLE ROW LEVEL SECURITY;

-- Crear políticas para permitir todas las operaciones
CREATE POLICY "Permitir todas las operaciones en catas_a" ON catas_a FOR ALL USING (true);
CREATE POLICY "Permitir todas las operaciones en catas_b" ON catas_b FOR ALL USING (true);
CREATE POLICY "Permitir todas las operaciones en catas_c" ON catas_c FOR ALL USING (true);
CREATE POLICY "Permitir todas las operaciones en catas_d" ON catas_d FOR ALL USING (true); 