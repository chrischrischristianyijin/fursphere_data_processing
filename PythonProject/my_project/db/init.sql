CREATE TABLE IF NOT EXISTS survey_data (
    submission_id SERIAL PRIMARY KEY,             -- Unique ID per submission
    email TEXT NOT NULL,                          -- 用户的邮箱
    ip TEXT NOT NULL,                             -- 用户的 IP 地址

    pet_type TEXT NOT NULL,                       -- 宠物类型 (Cat/Dog)
    pet_name TEXT NOT NULL,                       -- 宠物名字
    pet_breed TEXT NOT NULL,                      -- 宠物品种
    pet_gender TEXT NOT NULL,                     -- 宠物性别 (Boy/Girl)
    pet_age INT NOT NULL,                         -- 宠物年龄

    personality_behavior JSONB NOT NULL,         -- 所有行为数据的列表
    mbti_type TEXT,                              -- MBTI类型 (例如: 'ENFP')
    mbti_scores JSONB,                           -- MBTI各维度分数

    ai_output_image TEXT,                        -- AI 生成的图片 URL
    ai_output_text TEXT,                         -- AI 生成的文字描述

    created_at TIMESTAMP DEFAULT NOW(),           -- 提交时间
    generated_at TIMESTAMP                        -- AI 生成的时间
);