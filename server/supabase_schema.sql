-- ============================================
-- Supabase Schema pour Marketplace de Voix
-- ============================================

-- Table 1: marketplace_voices
-- Catalogue des voix premium disponibles à l'achat
CREATE TABLE IF NOT EXISTS marketplace_voices (
    id SERIAL PRIMARY KEY,
    voice_id INTEGER NOT NULL UNIQUE,  -- Speaker ID (5-107)
    name VARCHAR(255) NOT NULL,
    description TEXT,
    gender VARCHAR(20),
    age_range VARCHAR(50),
    language VARCHAR(100),
    price DECIMAL(10, 2) DEFAULT 9.99,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table 2: user_voices
-- Les voix possédées par chaque utilisateur
CREATE TABLE IF NOT EXISTS user_voices (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    voice_id INTEGER NOT NULL,
    is_classic BOOLEAN DEFAULT FALSE,  -- TRUE pour les voix 1-4
    acquired_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, voice_id)
);

-- Table 3: voice_purchases (optionnel - pour historique)
CREATE TABLE IF NOT EXISTS voice_purchases (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    voice_id INTEGER NOT NULL,
    price DECIMAL(10, 2),
    purchased_at TIMESTAMP DEFAULT NOW()
);

-- Indexes pour performance
CREATE INDEX IF NOT EXISTS idx_user_voices_user_id ON user_voices(user_id);
CREATE INDEX IF NOT EXISTS idx_user_voices_voice_id ON user_voices(voice_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_available ON marketplace_voices(is_available);

-- ============================================
-- Données initiales
-- ============================================

-- Insérer les 4 voix classiques dans user_voices pour tous les users
-- (À faire côté application lors de la création d'un nouveau user)

-- Exemples de voix premium dans le marketplace
INSERT INTO marketplace_voices (voice_id, name, description, gender, age_range, language, price) VALUES
(5, 'Alex - Young Asian Male', 'Energetic young voice, perfect for dynamic content', 'male', '18-25', 'Mandarin', 9.99),
(6, 'Maria - Hispanic Professional', 'Warm professional voice for corporate content', 'female', '36-45', 'American English', 12.99),
(8, 'James - British Authority', 'Deep authoritative British voice', 'male', '56-65', 'British English', 14.99),
(10, 'Tyrone - African American Narrator', 'Rich narrative voice', 'male', '36-45', 'American English', 11.99),
(11, 'Emma - Young Professional', 'Clear young professional voice', 'female', '18-25', 'American English', 9.99),
(15, 'Catherine - Mature Narrator', 'Experienced mature narrator', 'female', '46-55', 'American English', 13.99),
(20, 'Marcus - Deep Bass', 'Very deep bass voice', 'male', '26-35', 'American English', 15.99),
(25, 'Sarah - Gentle Voice', 'Soft gentle voice for relaxation', 'female', '46-55', 'American English', 10.99),
(32, 'Diana - Senior Wisdom', 'Wise mature voice', 'female', '56-65', 'American English', 12.99),
(33, 'Patricia - Calm Professional', 'Calm professional female voice', 'female', '56-65', 'American English', 11.99),
(38, 'Carlos - Hispanic Male', 'Latino male voice', 'male', '26-35', 'American English', 9.99),
(42, 'Miguel - Spanish Voice', 'Native Spanish speaker', 'male', '18-25', 'Spanish', 14.99),
(46, 'Ryan - Professional Male', 'Professional corporate male', 'male', '26-35', 'American English', 10.99),
(50, 'Grace - Petite Senior', 'Gentle senior female voice', 'female', '56-65', 'American English', 11.99),
(54, 'Robert - Mature Authority', 'Authoritative mature male', 'male', '46-55', 'American English', 13.99),
(67, 'Layla - Asian Female', 'Unique Asian female voice', 'female', '18-25', 'Dari', 16.99),
(71, 'Darnell - Young African American', 'Young energetic voice', 'male', '18-25', 'American English', 9.99),
(84, 'Elizabeth - Elderly Narrator', 'Warm elderly narrator', 'female', '66-75', 'American English', 14.99),
(97, 'William - Senior Male', 'Distinguished senior male', 'male', '56-65', 'American English', 13.99),
(101, 'Kevin - Tall Professional', 'Professional tall male voice', 'male', '46-55', 'American English', 12.99)
ON CONFLICT (voice_id) DO NOTHING;

-- ============================================
-- Fonctions utiles (optionnel)
-- ============================================

-- Fonction pour donner les 4 voix classiques à un nouveau user
CREATE OR REPLACE FUNCTION grant_classic_voices(p_user_id VARCHAR)
RETURNS VOID AS $$
BEGIN
    INSERT INTO user_voices (user_id, voice_id, is_classic)
    VALUES
        (p_user_id, 1, TRUE),
        (p_user_id, 2, TRUE),
        (p_user_id, 3, TRUE),
        (p_user_id, 4, TRUE)
    ON CONFLICT (user_id, voice_id) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour acheter une voix
CREATE OR REPLACE FUNCTION purchase_voice(p_user_id VARCHAR, p_voice_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    v_price DECIMAL(10, 2);
BEGIN
    -- Vérifier que la voix existe et est disponible
    SELECT price INTO v_price
    FROM marketplace_voices
    WHERE voice_id = p_voice_id AND is_available = TRUE;

    IF v_price IS NULL THEN
        RETURN FALSE;
    END IF;

    -- Ajouter la voix à l'utilisateur
    INSERT INTO user_voices (user_id, voice_id, is_classic)
    VALUES (p_user_id, p_voice_id, FALSE)
    ON CONFLICT (user_id, voice_id) DO NOTHING;

    -- Enregistrer l'achat
    INSERT INTO voice_purchases (user_id, voice_id, price)
    VALUES (p_user_id, p_voice_id, v_price);

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
