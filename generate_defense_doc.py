from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

def h1(text):
    p = doc.add_heading(text, level=1)
    p.runs[0].font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    return p

def h2(text):
    p = doc.add_heading(text, level=2)
    p.runs[0].font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
    return p

def h3(text):
    return doc.add_heading(text, level=3)

def body(text):
    return doc.add_paragraph(text)

def code_block(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.4)
    run = p.add_run(text)
    run.font.name = 'Courier New'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x20, 0x20, 0x20)
    return p

def file_ref(filename, line_start, line_end=None):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.3)
    r = p.add_run('  File: ' + filename)
    r.font.color.rgb = RGBColor(0x70, 0x70, 0x70)
    r.font.size = Pt(9)
    line_str = '  Line(s): ' + str(line_start) + (('–' + str(line_end)) if line_end else '')
    r2 = p.add_run(line_str)
    r2.font.color.rgb = RGBColor(0x19, 0x69, 0x19)
    r2.font.size = Pt(9)
    r2.bold = True
    return p

def add_table(headers, rows):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.style = 'Light List Accent 1'
    hdr = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        hdr[i].paragraphs[0].runs[0].bold = True
    for row in rows:
        r = tbl.add_row().cells
        for i, val in enumerate(row):
            r[i].text = val
    doc.add_paragraph()
    return tbl

# ── TITLE ────────────────────────────────────────────────────────────────────
title = doc.add_heading('AES System — Technical Defense Guide', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub = doc.add_paragraph('Automated Essay Scoring System — Multi-Trait Analytic Scoring')
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph()

# ── SECTION 1 — DATASETS ─────────────────────────────────────────────────────
h1('1. DATASETS')

h2('1.1  Feedback Prize 2022 (Kaggle)')
body('Real student essays graded by trained human raters on a 1.0–5.0 scale across 6 linguistic traits. This is the primary dataset.')
file_ref('backend/data/train.csv', '—')
body('Size: 3,911 unique essays  |  Score scale: 1.0–5.0 (in 0.5 increments)')
doc.add_paragraph()

add_table(
    ['Dataset Column', 'Maps To Our Trait', 'Code File', 'Line'],
    [
        ('vocabulary', 'Content & Ideas', 'train_model.py', '371'),
        ('cohesion', 'Organization', 'train_model.py', '372'),
        ('(syntax + phraseology) / 2', 'Voice & Style', 'train_model.py', '556–560'),
        ('(grammar + conventions) / 2', 'Conventions', 'train_model.py', '561–563'),
    ]
)

h3('Formula — Voice and Conventions derivation:')
code_block('Voice       = (syntax + phraseology) / 2')
code_block('Conventions = (grammar + conventions) / 2')
file_ref('backend/scripts/train_model.py', 556, 563)

h3('Formula — Normalization to 0–100:')
code_block('score_normalized = (score - min) / (max - min) * 100')
file_ref('backend/scripts/train_model.py', 345, 355)

doc.add_paragraph()
h2('1.2  PERSUADE 2.0')
body('Contains 173,266 discourse-level rows. Each essay is repeated once per paragraph annotation. After deduplication: 15,593 unique essays with holistic scores (1–6) and paragraph-level effectiveness ratings.')
file_ref('backend/data/persuade_corpus_2.0_train.csv', '—')
file_ref('backend/scripts/train_model.py', 419, 475)

body('Paragraph effectiveness values:  Effective = 1.0  |  Adequate = 0.6  |  Ineffective = 0.2')
doc.add_paragraph()

add_table(
    ['Our Trait', 'Derived From', 'Formula', 'Line'],
    [
        ('Content', 'Claim + Evidence paragraphs', 'mean(effectiveness) x 100', '436–441'),
        ('Organization', 'Lead + Concluding Statement', 'mean(effectiveness) x 100', '443–448'),
        ('Voice', 'Holistic score', '(holistic - 1) / 5 x 100', '455'),
        ('Conventions', 'Holistic score', '(holistic - 1) / 5 x 100', '456'),
    ]
)

h3('Combined Training Dataset:')
code_block('3,911 (Feedback Prize 2022)  +  15,593 (PERSUADE 2.0)  =  19,504 total essays')
file_ref('backend/scripts/train_model.py', 565, 580)

# ── SECTION 2 — ML MODEL ─────────────────────────────────────────────────────
doc.add_page_break()
h1('2. HOW THE ML MODEL WORKS')

h2('2.1  Architecture — 4 Independent XGBRegressor Models')
body('One XGBoost regression model is trained per trait. Each model receives a different feature vector tailored to its trait, then outputs a score from 0–100.')
file_ref('backend/scripts/train_model.py', 56, 92)

code_block('TF-IDF (500 features)  +  Base features (11)  +  Trait-specific (5-10 features)')
code_block('  └─────────────────────────────────────────────────────────────────────────┘')
code_block('                       XGBRegressor  -->  score 0-100')

h3('XGBoost Hyperparameters  (train_model.py lines 72–88):')
add_table(
    ['Parameter', 'Value', 'Purpose'],
    [
        ('n_estimators', '300', 'Number of trees — more trees = better fit'),
        ('max_depth', '6', 'Tree depth — prevents overfitting'),
        ('learning_rate', '0.05', 'Step size — slower learning = more stable model'),
        ('subsample', '0.8', '80% row sampling per tree — reduces overfitting'),
        ('colsample_bytree', '0.8', '80% feature sampling per tree'),
        ('gamma', '1', 'Min split gain — aggressive pruning'),
        ('min_child_weight', '3', 'Min samples per leaf node'),
    ]
)

doc.add_paragraph()
h2('2.2  Feature Engineering — 3 Layers')

h3('Layer 1 — TF-IDF (500 features) — train_model.py Line 65')
body('Converts essay text to word frequency vectors. Captures vocabulary richness and word choice.')
add_table(
    ['Setting', 'Value'],
    [
        ('max_features', '500 — top 500 most informative words/phrases'),
        ('ngram_range', '(1, 2) — unigrams and bigrams'),
        ('min_df', '2 — word must appear in at least 2 essays'),
        ('max_df', '0.85 — ignore words in more than 85% of essays'),
        ('stop_words', 'english — removes common words like "the", "is"'),
    ]
)

h3('Layer 2 — Base Features (11 features, shared by all traits) — Line 95')
add_table(
    ['Feature', 'Formula', 'Line'],
    [
        ('Word count', 'word_count / 1000', '116'),
        ('Sentence count', 'sentence_count / 50', '117'),
        ('Avg word length', 'mean([len(w) for w in words])', '118'),
        ('Avg sentence length', 'word_count / sentence_count', '119'),
        ('Vocabulary diversity', 'unique_words / total_words', '120'),
        ('Complex punctuation', 'count(; : --) / sentence_count', '121'),
        ('Comma rate', 'count(,) / sentence_count', '122'),
        ('Readability (Flesch-Kincaid)', 'FK_grade / 20', '123–126'),
        ('Contraction rate', 'contractions / (word_count/100)', '127'),
        ('Quote rate', 'quotes / (word_count/100)', '128'),
        ('Text length', 'len(text) / 10000', '129'),
    ]
)

h3('Layer 3a — Content Features (5 features) — Line 130')
add_table(
    ['Feature', 'Formula'],
    [
        ('Content word density', 'count(words where len > 6) / word_count'),
        ('Long word ratio', 'count(words where len >= 8) / word_count'),
        ('Paragraph count', 'min(paragraphs, 10) / 10'),
        ('Avg sentence length', 'word_count / sentence_count / 40'),
        ('Vocabulary diversity', 'unique_words / total_words'),
    ]
)

h3('Layer 3b — Organization Features (10 features) — Line 148')
add_table(
    ['Feature', 'What It Detects'],
    [
        ('Contrast transitions / sentence', 'however, nevertheless, on the other hand, although, despite, yet'),
        ('Addition transitions / sentence', 'furthermore, moreover, additionally, also, besides'),
        ('Conclusion transitions / sentence', 'therefore, thus, consequently, in conclusion, in summary'),
        ('Sequence transitions / sentence', 'first, second, third, finally, next, then, lastly'),
        ('Example transitions / sentence', 'for example, for instance, such as, specifically'),
        ('Total transitions / sentence', 'Overall transition word density'),
        ('has_intro (0 or 1)', 'Detects intro keywords in first 300 characters of essay'),
        ('has_conclusion (0 or 1)', 'Detects conclusion keywords in last 300 characters'),
        ('Paragraph count (normalized)', 'min(paragraphs, 10) / 10'),
        ('Sentence count (normalized)', 'min(sentences, 50) / 50'),
    ]
)

h3('Layer 3c — Voice Features (7 features) — Line 177')
add_table(
    ['Feature', 'Formula'],
    [
        ('Sentence length std', 'std(sentence_lengths) / 30'),
        ('Rhetorical question rate', 'count(?) / sentence_count'),
        ('Exclamation rate', 'count(!) / sentence_count'),
        ('Passive voice ratio', 'regex(is/are/was/were + *ed) / sentence_count'),
        ('First person frequency', 'count(I / me / my / we / our) / word_count'),
        ('Rare word ratio', 'count(words where len >= 8) / word_count'),
        ('Simile rate', 'regex(like/as + word) / sentence_count'),
    ]
)

h3('Layer 3d — Conventions Features (7 features) — Line 201')
add_table(
    ['Feature', 'Formula'],
    [
        ('Punctuation density', 'count(all punctuation marks) / word_count'),
        ('Double punctuation', 'min(count(..,,,???), 10) / 10'),
        ('Capitalization error rate', 'uncapitalized_sentences / sentence_count'),
        ('Repeated characters', 'regex([a-z])\\1{2,} — e.g. "aaaaaa"'),
        ('Contraction rate', 'count(apostrophe words) / word_count'),
        ('Length normalization', 'min(word_count, 1000) / 1000'),
        ('Comma rate', 'min(commas / sentence_count, 5) / 5'),
    ]
)

doc.add_paragraph()
h2('2.3  Model Performance (R-squared and RMSE)')
body('R-squared measures how much of the variance in human scores the model explains. RMSE is average error in points (0–100 scale).')
add_table(
    ['Trait', 'R2', 'RMSE', 'Interpretation'],
    [
        ('Voice & Style', '0.69', '12.38', 'Explains 69% of score variation — within human inter-rater range'),
        ('Conventions', '0.68', '12.53', 'Explains 68% of score variation'),
        ('Content & Ideas', '0.39', '11.63', 'Explains 39% of score variation'),
        ('Organization', '0.33', '13.96', 'Explains 33% of score variation'),
    ]
)
body('Note: Inter-rater agreement between two human graders on essay scoring is typically R2 = 0.60–0.75. Our Voice and Conventions models are within this range.')

# ── SECTION 3 — RUBRIC SYSTEM ─────────────────────────────────────────────────
doc.add_page_break()
h1('3. HOW THE RUBRIC SYSTEM WORKS')

h2('3.1  Rubric Criterion to ML Trait Mapping  (scoring_service.py Lines 186–208)')
body('Each rubric criterion name is matched to one of the 4 ML trait scores using keyword lookup. If no keyword matches, position in the rubric is used as fallback.')
add_table(
    ['Criterion Keywords', 'Mapped Trait', 'Example Criteria'],
    [
        ('thesis, argument, evidence, analysis, research, clarity, storytelling, characters, engagement, vocabulary', 'Content', 'Thesis, Evidence, Analysis, Research, Clarity'),
        ('organization, structure, flow, coherence, citations, sequence, paragraph', 'Organization', 'Structure, Citations, Organization'),
        ('voice, style, language, tone, expression, academic, rigor, syntax', 'Voice', 'Voice, Language, Rigor'),
        ('grammar, conventions, spelling, punctuation, mechanics', 'Conventions', 'Grammar, Conventions'),
    ]
)

h2('3.2  Rubric Trait Weights  (scoring_service.py Lines 140–149)')
body('Each rubric type assigns different importance weights to each trait. This makes the same essay score differently depending on the rubric selected.')
add_table(
    ['Rubric Type', 'Content', 'Organization', 'Voice', 'Conventions'],
    [
        ('Argumentative Essay (id=1)', '40%', '25%', '15%', '20%'),
        ('Expository Essay (id=2)', '35%', '30%', '15%', '20%'),
        ('Narrative Essay (id=3)', '25%', '20%', '40%', '15%'),
        ('Research Paper (id=4)', '40%', '30%', '10%', '20%'),
        ('Custom / Default', '30%', '25%', '25%', '20%'),
    ]
)

h2('3.3  Criterion Score Formula  (scoring_service.py Lines 248–252)')
h3('Formula:')
code_block('criterion_score = round( (trait_score / 100) x max_points x combined_factor )')
doc.add_paragraph()
body('Example — Thesis criterion (max 25 pts), Content ML score = 63, no penalties (combined_factor = 1.0):')
code_block('Thesis = round( (63 / 100) x 25 x 1.0 ) = round( 15.75 ) = 16 / 25')

h2('3.4  Built-in Rubric Criteria  (backend/app.py Lines 143–187)')
add_table(
    ['Rubric', 'Criterion', 'Max Points', 'Trait Used'],
    [
        ('Argumentative', 'Thesis', '25', 'Content'),
        ('Argumentative', 'Evidence', '25', 'Content'),
        ('Argumentative', 'Structure', '30', 'Organization'),
        ('Argumentative', 'Grammar', '20', 'Conventions'),
        ('Expository', 'Clarity', '30', 'Content'),
        ('Expository', 'Organization', '25', 'Organization'),
        ('Expository', 'Research', '25', 'Content'),
        ('Expository', 'Grammar', '20', 'Conventions'),
        ('Narrative', 'Storytelling', '30', 'Content'),
        ('Narrative', 'Characters', '25', 'Content'),
        ('Narrative', 'Engagement', '25', 'Voice'),
        ('Narrative', 'Language', '20', 'Voice'),
        ('Research Paper', 'Research', '30', 'Content'),
        ('Research Paper', 'Citations', '25', 'Organization'),
        ('Research Paper', 'Analysis', '25', 'Content'),
        ('Research Paper', 'Rigor', '20', 'Voice'),
    ]
)

# ── SECTION 4 — FINAL SCORE ───────────────────────────────────────────────────
doc.add_page_break()
h1('4. HOW THE FINAL SCORE IS COMPUTED')

h2('Step 1 — ML Prediction  (scoring_service.py Lines 46–48)')
code_block('prediction = scorer.predict(essay_text)')
code_block('  returns: score_content, score_organization, score_voice, score_conventions  (each 0-100)')

h2('Step 2 — Quality Penalty Factor  (scoring_service.py Lines 51–52)')
body('Penalizes essays with obvious quality problems. Converts penalty points to a multiplicative factor.')
add_table(
    ['Condition', 'Penalty Points', 'Line'],
    [
        ('Less than 20 words', '85 pts', '501'),
        ('Less than 50 words', '30 pts', '504'),
        ('Less than 100 words', '10 pts', '507'),
        ('Less than 3 sentences', '20 pts', '513'),
        ('More than 30% uncapitalized lines', '15 pts', '521'),
        ('Repeated characters (e.g. "aaaaaa")', 'up to 15 pts', '534'),
        ('Word diversity below 40%', '15 pts', '543'),
    ]
)
code_block('quality_factor = max(0.0,  1.0  -  penalty / 100)')
body('Example: penalty = 70  -->  quality_factor = 1.0 - 0.70 = 0.30')

h2('Step 3 — Topic Relevance Factor  (scoring_service.py Lines 73–79)')
body('Uses MiniLM-L6-v2 sentence transformer to compute semantic similarity between essay and prompt (score 0–100).')
code_block('if   topic_relevance < 30:   relevance_factor = 0.70   (off-topic: 30% deduction)')
code_block('elif topic_relevance < 60:   relevance_factor = 0.85   (partial: 15% deduction)')
code_block('else:                        relevance_factor = 1.0    (on-topic: no deduction)')

h2('Step 4 — Combined Factor  (scoring_service.py Line 81)')
code_block('combined_factor = quality_factor  x  relevance_factor')
body('Example: quality_factor=1.0, essay is on-topic  -->  combined_factor = 1.0 x 1.0 = 1.0')
body('Example: short essay (quality=0.30), off-topic (relevance=0.70)  -->  combined_factor = 0.21')

h2('Step 5 — Breakdown and Final Score  (scoring_service.py Lines 84–87)')
code_block('For each criterion:')
code_block('   criterion_score = round( (trait_score / 100) x max_points x combined_factor )')
code_block('')
code_block('Total Score = sum of all criterion_scores')
body('The total score is ALWAYS derived from the sum of criterion scores — they can never be inconsistent.')

h3('Complete Worked Example (Argumentative Essay, no penalties, on-topic):')
add_table(
    ['Criterion', 'Trait Used', 'ML Score (/100)', 'Max Pts', 'Calculated Score'],
    [
        ('Thesis', 'Content', '63', '25', 'round(63/100 x 25 x 1.0) = 16'),
        ('Evidence', 'Content', '63', '25', 'round(63/100 x 25 x 1.0) = 16'),
        ('Structure', 'Organization', '50', '30', 'round(50/100 x 30 x 1.0) = 15'),
        ('Grammar', 'Conventions', '47', '20', 'round(47/100 x 20 x 1.0) = 9'),
        ('TOTAL', '', '', '100', '56 / 100'),
    ]
)

# ── SECTION 5 — Q&A ───────────────────────────────────────────────────────────
doc.add_page_break()
h1('5. COMMON DEFENSE QUESTIONS AND ANSWERS')

qa_pairs = [
    (
        'Why XGBoost and not a neural network?',
        'XGBoost handles non-linear relationships between linguistic features and essay quality extremely well, is robust to noisy human-scored training data, and is interpretable. Neural networks require far more data (100k+ essays) to outperform XGBoost on structured feature sets. For our dataset size (19,504 essays), XGBoost is the appropriate choice.'
    ),
    (
        'Why 4 models instead of 1?',
        'Different writing traits are measured by fundamentally different features. A single model would average them out and lose granularity. For example, Organization is best predicted by transition word counts, while Conventions is best predicted by punctuation density — these are completely unrelated signals that benefit from separate models.'
    ),
    (
        'Why use PERSUADE 2.0 if it only has holistic scores?',
        'PERSUADE 2.0 has paragraph-level discourse effectiveness annotations (Claim, Evidence, Lead, Conclusion) which we convert to trait-level scores. This increased training data from 3,911 to 19,504 essays — a 5x increase. It significantly improved R2 for Voice (0.33 to 0.69) and Conventions (0.32 to 0.68).'
    ),
    (
        'What does R2 = 0.69 mean? Is it good?',
        'R2 = 0.69 means the model explains 69% of the variance in human essay scores. Published inter-rater agreement between two trained human graders on essay scoring tasks is typically R2 = 0.60-0.75. Our Voice and Conventions models are within that human performance range.'
    ),
    (
        'How does rubric selection affect the score?',
        'Changing the rubric changes the trait weights in the criterion score formula. For Argumentative (Content = 40%), weak content is penalized heavily. For Narrative (Voice = 40%), expressive writing is rewarded more. The same essay can score differently on different rubrics because the definition of "good writing" changes.'
    ),
    (
        'Can teachers create custom rubrics?',
        'Yes. Teachers can create custom rubrics through the Rubrics page, which saves them to Supabase. When scoring, the system fetches the custom rubric criteria from Supabase and maps each criterion name to the appropriate ML trait using keyword matching (scoring_service.py line 186).'
    ),
    (
        'How is the score consistent with the breakdown?',
        'Total Score = sum(criterion_scores). The total is always derived directly from the breakdown, so they can never be inconsistent. This was explicitly designed into scoring_service.py line 87.'
    ),
    (
        'What happens if the essay is off-topic?',
        'The sentence-transformer model (MiniLM-L6-v2) computes cosine similarity between essay and prompt embeddings. Below 30% similarity, all scores are multiplied by 0.70 (30% deduction). Between 30-60%, multiplied by 0.85 (15% deduction). Above 60%, no deduction.'
    ),
    (
        'What is TF-IDF and why use it?',
        'TF-IDF (Term Frequency-Inverse Document Frequency) converts essay words into numerical vectors based on how often a word appears in the essay versus all essays. It is effective at capturing vocabulary richness and topic relevance, and is computationally fast for real-time scoring.'
    ),
    (
        'How does the system handle custom rubrics from teachers?',
        'Custom rubrics are stored in Supabase with criteria names and point values. During scoring, the system queries Supabase for the rubric, maps each criterion to a trait using keyword matching, and applies the same criterion score formula. If a rubric title contains "argumentative", it uses Argumentative weights automatically.'
    ),
]

for q, a in qa_pairs:
    p = doc.add_paragraph()
    r = p.add_run('Q: ' + q)
    r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    body('A: ' + a)
    doc.add_paragraph()

# ── SECTION 6 — FILE INDEX ────────────────────────────────────────────────────
doc.add_page_break()
h1('6. KEY FILE AND LINE NUMBER REFERENCE')
add_table(
    ['What', 'File', 'Line(s)'],
    [
        ('TF-IDF vectorizer setup', 'backend/scripts/train_model.py', '65–75'),
        ('XGBRegressor 4-model setup', 'backend/scripts/train_model.py', '76–88'),
        ('Base features — 11 features shared by all traits', 'backend/scripts/train_model.py', '95–129'),
        ('Content features — 5 features', 'backend/scripts/train_model.py', '130–147'),
        ('Organization features — 10 features', 'backend/scripts/train_model.py', '148–176'),
        ('Voice features — 7 features', 'backend/scripts/train_model.py', '177–200'),
        ('Conventions features — 7 features', 'backend/scripts/train_model.py', '201–224'),
        ('Feature extraction combining all layers', 'backend/scripts/train_model.py', '226–244'),
        ('Model training loop (one model per trait)', 'backend/scripts/train_model.py', '245–265'),
        ('Score normalization to 0–100', 'backend/scripts/train_model.py', '345–355'),
        ('Feedback Prize 2022 format detection', 'backend/scripts/train_model.py', '367–389'),
        ('PERSUADE 2.0 loader and trait derivation', 'backend/scripts/train_model.py', '419–475'),
        ('Dataset combining (both datasets merged)', 'backend/scripts/train_model.py', '556–580'),
        ('Rubric trait weights dictionary', 'backend/scoring_service.py', '140–149'),
        ('_get_rubric_weights() — supports UUID rubrics', 'backend/scoring_service.py', '158–183'),
        ('Criterion to trait keyword mapping', 'backend/scoring_service.py', '186–208'),
        ('_build_breakdown_from_traits()', 'backend/scoring_service.py', '218–340'),
        ('Criterion score formula', 'backend/scoring_service.py', '248–252'),
        ('Quality penalty calculation', 'backend/scoring_service.py', '479–555'),
        ('quality_factor computation', 'backend/scoring_service.py', '51–52'),
        ('Topic relevance factor (relevance_factor)', 'backend/scoring_service.py', '73–79'),
        ('combined_factor = quality x relevance', 'backend/scoring_service.py', '81'),
        ('Final score = sum(breakdown)', 'backend/scoring_service.py', '87'),
        ('Built-in rubric definitions (API endpoint)', 'backend/app.py', '143–187'),
    ]
)

out = r'C:\3rd_year_files\ML\Machine-Learning-Essay-Scoring\AES_System_Defense_Guide.docx'
doc.save(out)
print('Saved:', out)
