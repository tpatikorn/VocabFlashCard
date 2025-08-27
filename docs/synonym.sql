CREATE TABLE synonyms(
    id serial,
    category varchar,
    meaning varchar,
    words _text
);

INSERT INTO synonyms (category, meaning, words) VALUES
('Adjectives for Description and Evaluation','Complex/difficult','{Intricate, convoluted, sophisticated, elaborate, arduous, challenging, demanding, labyrinthine, perplexing, formidable, strenuous, troublesome, daunting, puzzling, baffling, abstruse}'),
('Adjectives for Description and Evaluation','Few/scarce','{Paltry, meagre, insufficient, deficient, nominal, rare, sparse, scant, inadequate, lacking, limited, few and far between, negligible, minimal, insubstantial}'),
('Adjectives for Description and Evaluation','Hidden/unclear','{Ambiguous, obscure, covert, clandestine, elusive, intangible, inexplicable, enigmatic, vague, cryptic, concealed, veiled, nebulous, arcane, recondite, inscrutable, mysterious}'),
('Adjectives for Description and Evaluation','Important/significant','{Crucial, vital, paramount, essential, fundamental, indispensable, integral, pivotal, key, momentous, notable, consequential, significant, considerable, salient, prominent, preeminent, weighty, far-reaching}'),
('Adjectives for Description and Evaluation','Many/numerous','{Myriad, countless, a plethora of, a multitude of, abundant, copious, considerable, profuse, innumerable, teeming, bountiful, scores of, a host of, a swarm of, in abundance}'),
('Adjectives for Description and Evaluation','Modern/current','{Contemporary, cutting-edge, state-of-the-art, prevailing, novel, recent, up-to-date, current, futuristic, groundbreaking, avant-garde, ultramodern, innovative, leading-edge}'),
('Adjectives for Description and Evaluation','Negative/harmful','{Detrimental, adverse, deleterious, pernicious, malevolent, disadvantageous, undesirable, destructive, ruinous, catastrophic, noxious, toxic, corrosive, inimical, malignant, crippling, debilitating, disastrous}'),
('Adjectives for Description and Evaluation','Obvious/clear','{Manifest, evident, apparent, palpable, unequivocal, unambiguous, conspicuous, transparent, lucid, explicit, distinct, overt, plain, straightforward, self-evident, discernible, undeniable}'),
('Adjectives for Description and Evaluation','Positive/beneficial','{Advantageous, constructive, favourable, propitious, salutary, wholesome, lucrative, auspicious, prosperous, profitable, benign, beneficial, productive, felicitous, fruitful, enriching, rewarding, uplifting}'),
('Adjectives for Description and Evaluation','Traditional/old','{Conventional, archaic, obsolete, antiquated, outmoded, time-honoured, customary, orthodox, ancient, historical, vintage, classic, traditional, conventional}'),
('Adverbs and Linking Phrases','For adding points','{Furthermore, moreover, in addition, besides, what''s more, additionally, plus, concurrently, likewise, simultaneously, as well as, equally important, coupled with, not to mention}'),
('Adverbs and Linking Phrases','For contrasting ideas','{However, nevertheless, nonetheless, conversely, on the contrary, by contrast, in opposition, yet, still, despite this, on the other hand, in spite of this}'),
('Adverbs and Linking Phrases','For emphasis','{Indeed, notably, specifically, particularly, significantly, remarkably, especially, above all, crucially, in fact, without a doubt, unequivocally, beyond question}'),
('Adverbs and Linking Phrases','For expressing opinion','{From my perspective, in my view, as I see it, personally, it seems to me that, I believe, I am of the opinion that, to my mind, in my humble opinion, one could argue that}'),
('Adverbs and Linking Phrases','For giving examples','{For instance, for example, to illustrate, namely, such as, a case in point, specifically, in particular, a good example is, by way of illustration}'),
('Adverbs and Linking Phrases','For showing a result','{Consequently, as a result, hence, thus, therefore, accordingly, subsequently, as a consequence, for this reason, thereby, due to this, in the aftermath of, with the result that}'),
('Adverbs and Linking Phrases','For summarizing','{In conclusion, to conclude, to summarize, in short, in sum, on the whole, all in all, to put it briefly, in essence, ultimately, in a nutshell, to recap, in summary}'),
('Nouns for Abstract Concepts and Issues','Change/transformation','{Evolution, transition, paradigm shift, metamorphosis, fluctuation, volatility, revolution, alteration, mutation, conversion, shift, development, upheaval, flux, progression}'),
('Nouns for Abstract Concepts and Issues','Development/progress','{Advancement, proliferation, expansion, momentum, stride, evolution, growth, progression, improvement, leap, surge, headway, flourishing, maturation, ascendancy}'),
('Nouns for Abstract Concepts and Issues','Freedom/autonomy','{Liberty, independence, self-determination, sovereignty, emancipation, liberation, autonomy, license, unconstraint, deliverance, leeway, latitude}'),
('Nouns for Abstract Concepts and Issues','Impact/effect','{Repercussion, ramification, consequence, outcome, fallout, aftermath, result, influence, footprint, impression, significance, weight, ripple effect}'),
('Nouns for Abstract Concepts and Issues','Inequality/injustice','{Disparity, discrepancy, injustice, bias, prejudice, discrimination, inequity, unfairness, favoritism, segregation, imbalance, partiality, bigotry, marginalization}'),
('Nouns for Abstract Concepts and Issues','Knowledge/understanding','{Comprehension, insight, expertise, proficiency, cognition, awareness, perception, wisdom, erudition, acumen, grasp, intellect, mastery, cognizance}'),
('Nouns for Abstract Concepts and Issues','Poverty/lack','{Deprivation, destitution, indigence, dearth, scarcity, paucity, insolvency, privation, need, famine, want, insufficiency, penury, impecuniousness, hardship}'),
('Nouns for Abstract Concepts and Issues','Problem/challenge','{Dilemma, predicament, hurdle, obstacle, impediment, quandary, complication, issue, trouble, difficulty, plight, conundrum, setback, barrier, adversity}'),
('Nouns for Abstract Concepts and Issues','Solution/resolution','{Remedy, panacea, resolution, antidote, breakthrough, strategy, approach, fix, cure, answer, key, tactic, method, formula, measure}'),
('Nouns for Abstract Concepts and Issues','Wealth/prosperity','{Affluence, opulence, prosperity, abundance, boom, riches, fortune, luxury, plenty, flourishing, success, bounty, well-being, cornucopia}'),
('Verbs for Analysis and Argument','To achieve/accomplish','{Attain, acquire, procure, secure, fulfil, realize, garner, execute, complete, succeed, reach, obtain, procure, master, effectuate, culminate in}'),
('Verbs for Analysis and Argument','To affect/influence','{Impact, shape, mould, determine, govern, influence, modify, alter, transform, revolutionize, contribute to, bring about, dictate, control, regulate, sway, bias}'),
('Verbs for Analysis and Argument','To agree/concur','{Concede, assent, subscribe to, validate, corroborate, acquiesce, concur, endorse, sanction, approve, uphold, confirm, ratify, coincide, harmonize, reconcile}'),
('Verbs for Analysis and Argument','To cause/bring about','{Generate, produce, initiate, trigger, precipitate, foster, instigate, induce, spawn, cultivate, lead to, result in, give rise to, incite, provoke, propel, spark, engineer}'),
('Verbs for Analysis and Argument','To disagree/oppose','{Contradict, refute, challenge, rebut, dispute, undermine, dissent, object, oppose, counter, negate, repudiate, invalidate, contest, renounce, reject, condemn}'),
('Verbs for Analysis and Argument','To examine/analyze','{Scrutinize, investigate, probe, dissect, evaluate, assess, appraise, inspect, review, critique, study, explore, delve into}'),
('Verbs for Analysis and Argument','To increase/grow','{Accelerate, proliferate, escalate, expand, surge, burgeon, augment, multiply, enhance, amplify, swell, climb, soar, skyrocket, accumulate, mushroom, snowball, intensify}'),
('Verbs for Analysis and Argument','To reduce/decrease','{Diminish, lessen, mitigate, curb, curtail, alleviate, erode, decline, shrink, dwindle, subside, abate, fall, plummet, compress, contract, downsize, curtail, slacken}'),
('Verbs for Analysis and Argument','To show/illustrate','{Demonstrate, indicate, highlight, reveal, exemplify, manifest, underscore, convey, depict, illustrate, portray, elucidate, substantiate, prove, exhibit, display, present, denote, signify}'),
('Verbs for Analysis and Argument','To state/declare','{Assert, contend, maintain, propose, posit, claim, argue, affirm, profess, articulate, enunciate, pronounce, avow, aver, allege, submit, hold, opine}');


CREATE TABLE synonym_games (
    id serial PRIMARY KEY UNIQUE,
    user_id int REFERENCING(users.id)NOT NULL,
    played_at timestamptz NOT NULL DEFAULT NOW()
);

CREATE TABLE synonym_scores (
    id serial PRIMARY KEY UNIQUE,
    game_id int REFERENCING(synonym_games.id),
    subgame_order int NOT NULL,
    meaning varchar NOT NULL,
    score float
);
