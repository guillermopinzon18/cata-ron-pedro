-- Create the catas table
CREATE TABLE IF NOT EXISTS catas (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ron VARCHAR(1) NOT NULL,
    pureza INTEGER DEFAULT 0,
    olfato_intensidad INTEGER DEFAULT 0,
    olfato_complejidad INTEGER DEFAULT 0,
    gusto_intensidad INTEGER DEFAULT 0,
    gusto_complejidad INTEGER DEFAULT 0,
    gusto_persistencia INTEGER DEFAULT 0,
    armonia INTEGER DEFAULT 0,
    total INTEGER DEFAULT 0,
    notas TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(nombre, ron)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_catas_nombre ON catas(nombre);
CREATE INDEX IF NOT EXISTS idx_catas_ron ON catas(ron);
CREATE INDEX IF NOT EXISTS idx_catas_timestamp ON catas(timestamp);

-- Enable Row Level Security (RLS)
ALTER TABLE catas ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (since this is a public app)
CREATE POLICY "Allow all operations" ON catas
    FOR ALL
    USING (true)
    WITH CHECK (true); 