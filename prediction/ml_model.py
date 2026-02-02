"""
Disease Prediction ML Model
This is a simplified prediction system. In production, you would use a trained ML model.
"""

import json
from types import SimpleNamespace

from .models import Disease, Symptom

# Fallback info when a predicted disease is not in the database (description, prevention, diet, exercise)
# diet: { recommended: [{food_item, description}], avoid: [{food_item, description}] }
# exercises: [{ exercise_name, description, duration, intensity }]
DISEASE_FALLBACK_INFO = {
    'GERD': {
        'description': 'GERD (Gastroesophageal Reflux Disease) is a condition where stomach acid frequently flows back into the tube connecting your mouth and stomach. This backwash can irritate the lining of your esophagus and cause heartburn, chest pain, and throat irritation.',
        'precautions': [
            'Avoid large meals; eat smaller, more frequent meals',
            'Avoid lying down within 2–3 hours after eating',
            'Limit fatty foods, chocolate, caffeine, and alcohol',
            'Maintain a healthy weight',
            'Raise the head of your bed 6–8 inches if symptoms occur at night',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Oatmeal', 'description': 'High fibre, absorbs acid; eat for breakfast.'},
                {'food_item': 'Ginger', 'description': 'Natural anti-inflammatory; use in tea or cooking.'},
                {'food_item': 'Non-citrus fruits (bananas, melons)', 'description': 'Low acid; gentle on the esophagus.'},
                {'food_item': 'Lean poultry and fish', 'description': 'Baked or grilled; avoid frying.'},
                {'food_item': 'Leafy greens, broccoli, cucumber', 'description': 'Low acid vegetables; steamed or raw.'},
                {'food_item': 'Whole grains (brown rice, quinoa)', 'description': 'Fibre-rich; avoid white bread.'},
            ],
            'avoid': [
                {'food_item': 'Citrus fruits and tomatoes', 'description': 'High acid; can trigger reflux.'},
                {'food_item': 'Fried and fatty foods', 'description': 'Slow digestion; increase pressure on LES.'},
                {'food_item': 'Chocolate and peppermint', 'description': 'Relax the lower esophageal sphincter.'},
                {'food_item': 'Caffeine and alcohol', 'description': 'Stimulate acid production and relax LES.'},
                {'food_item': 'Spicy foods and garlic/onions', 'description': 'Can worsen heartburn in many people.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Walking', 'description': 'Low impact; improves digestion. Avoid right after meals.', 'duration': '20–30 min daily', 'intensity': 'light'},
            {'exercise_name': 'Cycling (moderate)', 'description': 'Avoid high intensity; stay upright.', 'duration': '15–20 min', 'intensity': 'moderate'},
        ],
        'severity_level': 'moderate',
        'specialist_required': 'Gastroenterologist',
    },
    'Diabetes': {
        'description': 'Diabetes is a chronic condition that affects how your body turns food into energy. With diabetes, your body either does not make enough insulin or cannot use the insulin it makes well, leading to high blood sugar.',
        'precautions': [
            'Eat a balanced diet and control carbohydrate intake',
            'Exercise regularly (at least 150 minutes per week)',
            'Monitor blood sugar as advised by your doctor',
            'Maintain a healthy weight',
            'Take prescribed medications consistently',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Non-starchy vegetables (spinach, broccoli)', 'description': 'Low carb; high fibre and nutrients.'},
                {'food_item': 'Whole grains (oats, quinoa, brown rice)', 'description': 'Slow-release carbs; control blood sugar.'},
                {'food_item': 'Lean protein (chicken, fish, tofu)', 'description': 'Helps satiety; minimal impact on glucose.'},
                {'food_item': 'Legumes (lentils, chickpeas)', 'description': 'Fibre and protein; moderate portions.'},
                {'food_item': 'Nuts and seeds (almonds, chia)', 'description': 'Healthy fats; small handfuls.'},
                {'food_item': 'Berries (blueberries, strawberries)', 'description': 'Lower GI fruit; in moderation.'},
            ],
            'avoid': [
                {'food_item': 'Sugary drinks and sweets', 'description': 'Spike blood sugar; avoid or limit strictly.'},
                {'food_item': 'White bread and refined flour', 'description': 'Rapid glucose rise; choose whole grain.'},
                {'food_item': 'Fried and high-fat processed foods', 'description': 'Worsen insulin resistance.'},
                {'food_item': 'Large portions of rice, pasta', 'description': 'Control portions; pair with protein/veg.'},
                {'food_item': 'Dried fruits and fruit juices', 'description': 'Concentrated sugar; prefer whole fruit.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Brisk walking', 'description': 'Improves insulin sensitivity; safe for most.', 'duration': '30 min, 5 days/week', 'intensity': 'moderate'},
            {'exercise_name': 'Cycling', 'description': 'Low impact; good for blood sugar control.', 'duration': '20–30 min', 'intensity': 'moderate'},
            {'exercise_name': 'Strength training', 'description': 'Builds muscle; helps glucose uptake.', 'duration': '2–3 sessions/week', 'intensity': 'moderate'},
        ],
        'severity_level': 'high',
        'specialist_required': 'Endocrinologist',
    },
    'Hypertension': {
        'description': 'Hypertension (high blood pressure) is when the force of blood against your artery walls is consistently too high. It often has no symptoms but can lead to heart disease, stroke, and kidney problems.',
        'precautions': [
            'Reduce sodium intake',
            'Exercise regularly and maintain a healthy weight',
            'Limit alcohol and avoid smoking',
            'Manage stress and get enough sleep',
            'Take prescribed blood pressure medication as directed',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Leafy greens (spinach, kale)', 'description': 'High potassium; supports healthy BP.'},
                {'food_item': 'Berries and bananas', 'description': 'Potassium and antioxidants.'},
                {'food_item': 'Oats and whole grains', 'description': 'Fibre; helps lower BP.'},
                {'food_item': 'Fat-free or low-fat dairy', 'description': 'Calcium; choose low-sodium options.'},
                {'food_item': 'Beets and beet juice', 'description': 'Nitrates; may help relax blood vessels.'},
                {'food_item': 'Garlic (in food)', 'description': 'May have mild BP-lowering effect.'},
            ],
            'avoid': [
                {'food_item': 'High-sodium foods (pickles, chips)', 'description': 'Raises blood pressure; limit to <2300 mg/day.'},
                {'food_item': 'Processed and canned foods', 'description': 'Often high in salt; read labels.'},
                {'food_item': 'Excess alcohol', 'description': 'Limit to 1 drink/day for women, 2 for men.'},
                {'food_item': 'Fried and fatty foods', 'description': 'Worsen heart health and weight.'},
                {'food_item': 'Caffeine in excess', 'description': 'Can temporarily raise BP; moderate use.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Walking or jogging', 'description': 'Aerobic activity lowers BP over time.', 'duration': '30 min, most days', 'intensity': 'moderate'},
            {'exercise_name': 'Swimming', 'description': 'Full-body; low impact on joints.', 'duration': '20–30 min', 'intensity': 'moderate'},
            {'exercise_name': 'Cycling', 'description': 'Good cardio; build up gradually.', 'duration': '25–30 min', 'intensity': 'moderate'},
        ],
        'severity_level': 'high',
        'specialist_required': 'Cardiologist',
    },
    'Common Cold': {
        'description': 'The common cold is a viral infection of your nose and throat. It is usually harmless and most people recover within 7–10 days. Symptoms include runny nose, cough, sore throat, sneezing, and sometimes fever.',
        'precautions': [
            'Wash hands frequently with soap and water',
            'Avoid touching your face, especially nose and eyes',
            'Get plenty of rest and stay hydrated',
            'Use a humidifier and avoid smoke',
            'Cover your mouth when coughing or sneezing',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Warm soups and broths', 'description': 'Hydration; soothes throat and congestion.'},
                {'food_item': 'Honey (in tea or warm water)', 'description': 'Soothes cough; avoid in infants <1 year.'},
                {'food_item': 'Citrus and vitamin C foods', 'description': 'Oranges, kiwi; support immunity.'},
                {'food_item': 'Ginger and turmeric tea', 'description': 'Anti-inflammatory; warming.'},
                {'food_item': 'Chicken soup', 'description': 'Fluids, electrolytes, easy to digest.'},
                {'food_item': 'Plain toast, rice, bananas', 'description': 'Bland; easy on the stomach.'},
            ],
            'avoid': [
                {'food_item': 'Dairy (if it thickens mucus)', 'description': 'Some find it worsens congestion.'},
                {'food_item': 'Sugary drinks and sweets', 'description': 'Can suppress immunity; dehydrate.'},
                {'food_item': 'Alcohol', 'description': 'Dehydrates; weakens immunity.'},
                {'food_item': 'Heavy, fatty meals', 'description': 'Hard to digest when unwell.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Light walking', 'description': 'Only if you feel up to it; rest if fever or very weak.', 'duration': '10–15 min', 'intensity': 'light'},
        ],
        'severity_level': 'low',
        'specialist_required': 'General Physician',
    },
    'Migraine': {
        'description': 'Migraine is a neurological condition that causes moderate to severe headache, often on one side, along with nausea, sensitivity to light and sound, and sometimes visual disturbances (aura).',
        'precautions': [
            'Identify and avoid triggers (stress, certain foods, lack of sleep)',
            'Maintain a regular sleep schedule',
            'Stay hydrated and eat at regular times',
            'Reduce screen time and bright lights when possible',
            'Consider preventive medication if prescribed by your doctor',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Leafy greens and non-citrus fruits', 'description': 'Less likely to trigger migraines.'},
                {'food_item': 'Whole grains and oats', 'description': 'Stable energy; avoid skipping meals.'},
                {'food_item': 'Lean protein (chicken, fish)', 'description': 'Regular meals help prevent attacks.'},
                {'food_item': 'Ginger (tea or food)', 'description': 'May reduce nausea and inflammation.'},
                {'food_item': 'Magnesium-rich foods (spinach, almonds)', 'description': 'Some evidence for migraine prevention.'},
                {'food_item': 'Water and herbal tea', 'description': 'Dehydration can trigger migraines.'},
            ],
            'avoid': [
                {'food_item': 'Aged cheese and processed meats', 'description': 'Tyramine can trigger migraines.'},
                {'food_item': 'Alcohol (especially red wine)', 'description': 'Common trigger.'},
                {'food_item': 'Caffeine (excess or withdrawal)', 'description': 'Moderate use; avoid sudden changes.'},
                {'food_item': 'Chocolate and MSG', 'description': 'Common migraine triggers.'},
                {'food_item': 'Artificial sweeteners (aspartame)', 'description': 'Can trigger in some people.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Walking', 'description': 'Gentle; avoid intense exercise during attacks.', 'duration': '20–30 min', 'intensity': 'light'},
            {'exercise_name': 'Yoga or stretching', 'description': 'Reduces stress; may lower attack frequency.', 'duration': '15–20 min', 'intensity': 'light'},
        ],
        'severity_level': 'moderate',
        'specialist_required': 'Neurologist',
    },
    'Asthma': {
        'description': 'Asthma is a condition in which your airways narrow, swell, and may produce extra mucus, making breathing difficult. It can cause coughing, wheezing, shortness of breath, and chest tightness.',
        'precautions': [
            'Avoid known allergens and irritants (dust, pollen, smoke)',
            'Use your inhaler as prescribed',
            'Keep an action plan and know when to seek emergency care',
            'Get a flu shot annually',
            'Monitor your breathing and avoid overexertion in cold or polluted air',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Fruits and vegetables (apples, carrots)', 'description': 'Antioxidants; may support lung function.'},
                {'food_item': 'Vitamin D sources (eggs, fortified milk)', 'description': 'Low vitamin D linked to worse asthma.'},
                {'food_item': 'Omega-3 foods (salmon, flaxseed)', 'description': 'Anti-inflammatory.'},
                {'food_item': 'Whole grains', 'description': 'Fibre; avoid refined flour if allergic.'},
                {'food_item': 'Magnesium-rich foods (spinach, nuts)', 'description': 'May help relax airways.'},
            ],
            'avoid': [
                {'food_item': 'Sulfites (wine, dried fruit)', 'description': 'Can trigger asthma in some.'},
                {'food_item': 'Known food allergens', 'description': 'Identify and avoid your triggers.'},
                {'food_item': 'Heavy meals before exercise', 'description': 'Can worsen exercise-induced asthma.'},
                {'food_item': 'Excess cold drinks', 'description': 'May trigger bronchospasm in some.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Walking or light jogging', 'description': 'Warm up well; use reliever before exercise if advised.', 'duration': '20–30 min', 'intensity': 'light'},
            {'exercise_name': 'Swimming', 'description': 'Warm, humid air; often well tolerated.', 'duration': '20 min', 'intensity': 'moderate'},
            {'exercise_name': 'Cycling (moderate)', 'description': 'Controlled intensity; avoid cold, dry air.', 'duration': '15–25 min', 'intensity': 'moderate'},
        ],
        'severity_level': 'moderate',
        'specialist_required': 'Pulmonologist',
    },
    'Gastroenteritis': {
        'description': 'Gastroenteritis (stomach flu) is inflammation of the stomach and intestines, usually caused by a virus or bacteria. Symptoms include diarrhea, nausea, vomiting, abdominal pain, and sometimes fever.',
        'precautions': [
            'Stay hydrated with water, oral rehydration solutions, or clear broths',
            'Avoid dairy, fatty foods, and caffeine until you recover',
            'Wash hands frequently to prevent spread',
            'Rest and eat bland foods (e.g., toast, rice, bananas) when able',
            'Seek medical care if symptoms are severe or last more than a few days',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'BRAT (bananas, rice, applesauce, toast)', 'description': 'Bland; easy to digest during recovery.'},
                {'food_item': 'Oral rehydration solution (ORS)', 'description': 'Replaces fluids and electrolytes.'},
                {'food_item': 'Clear broths and soups', 'description': 'Hydration and light nutrition.'},
                {'food_item': 'Plain crackers or toast', 'description': 'Settle stomach; small portions.'},
                {'food_item': 'Boiled potatoes (no butter)', 'description': 'Easy to digest; add when tolerating solids.'},
                {'food_item': 'Ginger tea', 'description': 'May ease nausea; sip slowly.'},
            ],
            'avoid': [
                {'food_item': 'Dairy products', 'description': 'Hard to digest; can worsen diarrhea.'},
                {'food_item': 'Fatty, fried, or spicy foods', 'description': 'Irritate the gut.'},
                {'food_item': 'Caffeine and alcohol', 'description': 'Dehydrate and irritate.'},
                {'food_item': 'Sugary drinks and sweets', 'description': 'Can worsen diarrhea.'},
                {'food_item': 'Raw vegetables and high-fibre foods', 'description': 'Until stomach settles.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Rest', 'description': 'Avoid exercise until vomiting and diarrhea stop; rehydrate first.', 'duration': 'Rest until recovered', 'intensity': 'light'},
        ],
        'severity_level': 'moderate',
        'specialist_required': 'Gastroenterologist',
    },
    'Bronchitis': {
        'description': 'Bronchitis is inflammation of the bronchial tubes that carry air to your lungs. It causes cough (often with mucus), chest discomfort, fatigue, and sometimes fever. It can be acute or chronic.',
        'precautions': [
            'Rest and drink plenty of fluids',
            'Avoid smoke and other irritants',
            'Use a humidifier to ease breathing',
            'Take over-the-counter or prescribed cough/decongestant as advised',
            'See a doctor if cough lasts more than 3 weeks or you have high fever',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Warm soups and broths', 'description': 'Hydration; soothes throat and loosens mucus.'},
                {'food_item': 'Honey (in warm water or tea)', 'description': 'Soothes cough; avoid in infants <1 year.'},
                {'food_item': 'Fruits and vegetables (vitamin C)', 'description': 'Oranges, kiwi; support immunity.'},
                {'food_item': 'Ginger and turmeric', 'description': 'Anti-inflammatory; warming.'},
                {'food_item': 'Plain rice, toast, bananas', 'description': 'Easy to digest when fatigued.'},
                {'food_item': 'Water and herbal tea', 'description': 'Stay well hydrated.'},
            ],
            'avoid': [
                {'food_item': 'Dairy (if it thickens mucus)', 'description': 'Some find it worsens cough.'},
                {'food_item': 'Fried and fatty foods', 'description': 'Hard to digest; can worsen inflammation.'},
                {'food_item': 'Alcohol and smoke', 'description': 'Irritate airways.'},
                {'food_item': 'Cold drinks and ice cream', 'description': 'Can trigger coughing in some.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Rest first', 'description': 'Rest until fever and severe cough improve.', 'duration': 'Until improved', 'intensity': 'light'},
            {'exercise_name': 'Light walking', 'description': 'When feeling better; avoid cold air.', 'duration': '10–15 min', 'intensity': 'light'},
        ],
        'severity_level': 'moderate',
        'specialist_required': 'Pulmonologist',
    },
    'Pneumonia': {
        'description': 'Pneumonia is an infection that inflames the air sacs in one or both lungs. The air sacs may fill with fluid or pus, causing cough, fever, chest pain, shortness of breath, and fatigue.',
        'precautions': [
            'Get vaccinated (flu and pneumococcal vaccines as recommended)',
            'Wash hands regularly and avoid close contact with sick people',
            'Rest, stay hydrated, and take prescribed antibiotics if given',
            'Seek prompt medical care for high fever or difficulty breathing',
            'Avoid smoking and maintain good overall health',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Soups and broths', 'description': 'Hydration; easy to eat when weak.'},
                {'food_item': 'Protein (chicken, fish, eggs)', 'description': 'Supports recovery; soft forms.'},
                {'food_item': 'Fruits and vegetables', 'description': 'Vitamins and antioxidants.'},
                {'food_item': 'Whole grains (oatmeal, rice)', 'description': 'Energy; easy to digest.'},
                {'food_item': 'Water and electrolyte drinks', 'description': 'Stay hydrated; fever increases need.'},
                {'food_item': 'Honey (for cough)', 'description': 'Soothes throat; avoid in infants <1 year.'},
            ],
            'avoid': [
                {'food_item': 'Alcohol', 'description': 'Dehydrates; weakens immunity.'},
                {'food_item': 'Heavy, fatty meals', 'description': 'Hard to digest when ill.'},
                {'food_item': 'Smoking and smoke exposure', 'description': 'Damages lungs.'},
                {'food_item': 'Excess caffeine', 'description': 'Can dehydrate.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Rest', 'description': 'No exercise until fever is gone and doctor approves.', 'duration': 'Until recovered', 'intensity': 'light'},
            {'exercise_name': 'Deep breathing (when advised)', 'description': 'Helps expand lungs; ask your doctor.', 'duration': '5–10 min, 2–3 times/day', 'intensity': 'light'},
        ],
        'severity_level': 'high',
        'specialist_required': 'Pulmonologist',
    },
    'Arthritis': {
        'description': 'Arthritis is inflammation of one or more joints, leading to pain, stiffness, swelling, and reduced range of motion. There are many types; osteoarthritis and rheumatoid arthritis are common.',
        'precautions': [
            'Stay active with low-impact exercise (swimming, walking)',
            'Maintain a healthy weight to reduce joint stress',
            'Apply heat or cold as advised for pain and stiffness',
            'Protect joints during daily activities',
            'Take prescribed medications and attend follow-ups with your doctor',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Fatty fish (salmon, mackerel)', 'description': 'Omega-3; anti-inflammatory.'},
                {'food_item': 'Leafy greens (spinach, kale)', 'description': 'Vitamin K; may protect joints.'},
                {'food_item': 'Nuts and seeds (walnuts, flaxseed)', 'description': 'Healthy fats; anti-inflammatory.'},
                {'food_item': 'Olive oil', 'description': 'Oleocanthal; anti-inflammatory.'},
                {'food_item': 'Berries and cherries', 'description': 'Antioxidants; may reduce inflammation.'},
                {'food_item': 'Whole grains and beans', 'description': 'Fibre; maintain healthy weight.'},
            ],
            'avoid': [
                {'food_item': 'Processed and fried foods', 'description': 'Can increase inflammation.'},
                {'food_item': 'Excess sugar and refined carbs', 'description': 'Linked to inflammation.'},
                {'food_item': 'Excess red meat', 'description': 'Moderate; choose lean cuts.'},
                {'food_item': 'Alcohol in excess', 'description': 'Can worsen inflammation.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Walking', 'description': 'Low impact; keeps joints mobile.', 'duration': '20–30 min daily', 'intensity': 'light'},
            {'exercise_name': 'Swimming or water aerobics', 'description': 'No joint stress; full range of motion.', 'duration': '25–30 min', 'intensity': 'moderate'},
            {'exercise_name': 'Cycling (stationary or outdoor)', 'description': 'Low impact; strengthens legs.', 'duration': '15–25 min', 'intensity': 'moderate'},
            {'exercise_name': 'Stretching and range-of-motion', 'description': 'Reduces stiffness; do daily.', 'duration': '10–15 min', 'intensity': 'light'},
        ],
        'severity_level': 'moderate',
        'specialist_required': 'Rheumatologist',
    },
    'Anxiety': {
        'description': 'Anxiety is a mental health condition characterized by excessive worry, restlessness, rapid heartbeat, sweating, difficulty concentrating, and sleep problems. It can interfere with daily life.',
        'precautions': [
            'Practice relaxation techniques (deep breathing, meditation)',
            'Maintain a regular sleep schedule and limit caffeine',
            'Stay physically active and connect with others',
            'Limit exposure to stressors when possible',
            'Seek therapy or medication as recommended by a mental health professional',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Complex carbs (oats, whole grain)', 'description': 'Steady energy; may promote calm.'},
                {'food_item': 'Magnesium-rich foods (spinach, almonds)', 'description': 'Supports relaxation.'},
                {'food_item': 'Omega-3 (fish, flaxseed)', 'description': 'May support brain health and mood.'},
                {'food_item': 'Probiotics (yogurt, fermented foods)', 'description': 'Gut-brain axis; some evidence for anxiety.'},
                {'food_item': 'Herbal teas (chamomile, lavender)', 'description': 'Calming; avoid if on sedatives.'},
                {'food_item': 'Regular meals and hydration', 'description': 'Low blood sugar can worsen anxiety.'},
            ],
            'avoid': [
                {'food_item': 'Excess caffeine', 'description': 'Can increase heart rate and anxiety.'},
                {'food_item': 'Alcohol', 'description': 'Temporary relief but worsens anxiety long term.'},
                {'food_item': 'High sugar and processed foods', 'description': 'Blood sugar swings can trigger anxiety.'},
                {'food_item': 'Skipping meals', 'description': 'Eat regularly to avoid low blood sugar.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Walking or jogging', 'description': 'Releases endorphins; reduces tension.', 'duration': '20–30 min', 'intensity': 'moderate'},
            {'exercise_name': 'Yoga', 'description': 'Combines movement and breathing; calming.', 'duration': '20–40 min', 'intensity': 'light'},
            {'exercise_name': 'Swimming or cycling', 'description': 'Aerobic; good for stress relief.', 'duration': '25–30 min', 'intensity': 'moderate'},
        ],
        'severity_level': 'moderate',
        'specialist_required': 'Psychiatrist',
    },
    'Depression': {
        'description': 'Depression is a mood disorder that causes persistent sadness, loss of interest in activities, fatigue, changes in sleep and appetite, and can affect how you feel, think, and handle daily activities.',
        'precautions': [
            'Stay connected with family and friends',
            'Maintain a routine and set small, achievable goals',
            'Exercise regularly and prioritize sleep',
            'Avoid alcohol and recreational drugs',
            'Seek professional help (therapy and/or medication) as recommended',
        ],
        'diet': {
            'recommended': [
                {'food_item': 'Omega-3 (fatty fish, walnuts)', 'description': 'Linked to better mood; support brain health.'},
                {'food_item': 'Leafy greens and folate (spinach, broccoli)', 'description': 'Folate supports mood.'},
                {'food_item': 'Whole grains and complex carbs', 'description': 'Steady energy; avoid blood sugar crashes.'},
                {'food_item': 'Lean protein (chicken, legumes)', 'description': 'Amino acids for neurotransmitters.'},
                {'food_item': 'Vitamin D sources (eggs, fortified milk)', 'description': 'Low vitamin D linked to depression.'},
                {'food_item': 'Regular meals', 'description': 'Skipping meals can worsen low mood and energy.'},
            ],
            'avoid': [
                {'food_item': 'Alcohol and recreational drugs', 'description': 'Worsen depression; avoid self-medicating.'},
                {'food_item': 'Excess sugar and refined carbs', 'description': 'Energy crashes; can worsen mood.'},
                {'food_item': 'Skipping meals', 'description': 'Eat regularly even when appetite is low.'},
                {'food_item': 'Heavy processed foods', 'description': 'Whole foods support better mood.'},
            ],
        },
        'exercises': [
            {'exercise_name': 'Walking', 'description': 'Start small; even 10–15 min helps mood.', 'duration': '20–30 min', 'intensity': 'light'},
            {'exercise_name': 'Jogging or cycling', 'description': 'Aerobic exercise; strong evidence for mild–moderate depression.', 'duration': '25–30 min', 'intensity': 'moderate'},
            {'exercise_name': 'Yoga or stretching', 'description': 'Combines movement and mindfulness.', 'duration': '20 min', 'intensity': 'light'},
        ],
        'severity_level': 'moderate',
        'specialist_required': 'Psychiatrist',
    },
}


def get_fallback_disease_info(name):
    """Return a disease-like object with fallback info if the disease is not in the DB."""
    if not name or not isinstance(name, str):
        return None
    key = name.strip()
    for map_name, info in DISEASE_FALLBACK_INFO.items():
        if map_name.lower() == key.lower():
            return SimpleNamespace(
                name=map_name,
                description=info['description'],
                severity_level=info['severity_level'],
                specialist_required=info['specialist_required'],
            )
    return None


def get_fallback_recommendations(disease_name):
    """
    Return full recommendations (precautions, diet, exercises, medicines) for a disease
    from DISEASE_FALLBACK_INFO. Used when the disease is not in the database.
    """
    if not disease_name or not isinstance(disease_name, str):
        return {
            'precautions': [],
            'diet': {'recommended': [], 'avoid': []},
            'exercises': [],
            'medicines': [],
        }
    name = disease_name.strip().lower()
    for key, info in DISEASE_FALLBACK_INFO.items():
        if key.lower() == name:
            diet = info.get('diet') or {}
            rec = diet.get('recommended') or []
            avoid = diet.get('avoid') or []
            exercises = info.get('exercises') or []
            return {
                'precautions': info.get('precautions') or [],
                'diet': {
                    'recommended': [{'food_item': str(x.get('food_item', '')), 'description': str(x.get('description', ''))} for x in rec],
                    'avoid': [{'food_item': str(x.get('food_item', '')), 'description': str(x.get('description', ''))} for x in avoid],
                },
                'exercises': [
                    {
                        'exercise_name': str(ex.get('exercise_name', '')),
                        'description': str(ex.get('description', '')),
                        'duration': str(ex.get('duration', '')),
                        'intensity': str(ex.get('intensity', '')),
                    }
                    for ex in exercises
                ],
                'medicines': [],
            }
    return {
        'precautions': [],
        'diet': {'recommended': [], 'avoid': []},
        'exercises': [],
        'medicines': [],
    }


class DiseasePredictionModel:
    """
    Disease prediction model based on weighted symptom matching.
    Uses expanded symptom lists and a scoring algorithm that rewards
    both how many of the disease's symptoms match and how many of the
    user's selected symptoms are explained.
    """
    
    # Expanded disease–symptom mapping (normalized: lowercase, spaces as underscore)
    # More symptoms per disease = more accurate matching
    DISEASE_SYMPTOM_MAP = {
        'GERD': [
            'acidity', 'heartburn', 'chest_pain', 'cough', 'throat_irritation', 'difficulty_swallowing',
            'regurgitation', 'bloating', 'burning_chest', 'sour_taste', 'hoarseness', 'chronic_cough',
            'nausea_after_meals', 'bad_breath', 'tooth_erosion', 'lump_in_throat', 'wheezing',
            'pain_after_eating', 'belching', 'hiccups', 'stomach_pain', 'dry_cough',
        ],
        'Diabetes': [
            'frequent_urination', 'excessive_thirst', 'fatigue', 'blurred_vision', 'weight_loss',
            'increased_hunger', 'slow_healing', 'numbness_tingling', 'dry_skin', 'yeast_infections',
            'irritability', 'dizziness', 'weakness', 'mood_changes', 'dark_skin_patches',
            'repeated_infections', 'excessive_sweating', 'trembling', 'confusion', 'headache',
        ],
        'Hypertension': [
            'headache', 'dizziness', 'chest_pain', 'shortness_of_breath', 'nosebleeds',
            'blurred_vision', 'fatigue', 'irregular_heartbeat', 'anxiety', 'ear_pounding',
            'facial_flushing', 'blood_urine', 'chest_pressure', 'difficulty_sleeping',
            'nervousness', 'sweating', 'nausea', 'weakness', 'confusion', 'vision_problems',
        ],
        'Common Cold': [
            'runny_nose', 'cough', 'sore_throat', 'sneezing', 'fever', 'congestion',
            'mild_headache', 'body_aches', 'fatigue', 'watery_eyes', 'stuffy_nose',
            'scratchy_throat', 'mild_chills', 'loss_of_appetite', 'slight_fever',
            'mucus', 'postnasal_drip', 'hoarseness', 'ear_fullness', 'sinus_pressure',
        ],
        'Migraine': [
            'severe_headache', 'nausea', 'light_sensitivity', 'visual_disturbances', 'sound_sensitivity',
            'throbbing_pain', 'one_sided_headache', 'vomiting', 'aura', 'blurred_vision',
            'dizziness', 'fatigue', 'neck_pain', 'mood_changes', 'food_cravings',
            'stiff_neck', 'confusion', 'tingling', 'weakness', 'difficulty_speaking',
        ],
        'Asthma': [
            'shortness_of_breath', 'wheezing', 'chest_tightness', 'cough', 'difficulty_breathing',
            'rapid_breathing', 'anxiety', 'fatigue', 'trouble_sleeping', 'chronic_cough',
            'chest_pain', 'rapid_pulse', 'pale_skin', 'sweating', 'panic',
            'exercise_induced_symptoms', 'nighttime_cough', 'phlegm', 'tight_chest',
        ],
        'Gastroenteritis': [
            'diarrhea', 'nausea', 'vomiting', 'abdominal_pain', 'fever', 'cramping',
            'bloating', 'loss_of_appetite', 'dehydration', 'weakness', 'headache',
            'muscle_aches', 'watery_stools', 'stomach_upset', 'chills', 'fatigue',
            'blood_in_stool', 'mucus_in_stool', 'urgent_bowel_movement',
        ],
        'Bronchitis': [
            'cough', 'mucus_production', 'fatigue', 'chest_discomfort', 'fever', 'shortness_of_breath',
            'sore_throat', 'runny_nose', 'body_aches', 'wheezing', 'phlegm', 'chills',
            'chest_tightness', 'headache', 'blocked_nose', 'sneezing', 'hoarseness',
            'green_yellow_mucus', 'breathing_difficulty', 'weakness',
        ],
        'Pneumonia': [
            'cough', 'fever', 'chest_pain', 'shortness_of_breath', 'fatigue', 'chills',
            'sweating', 'phlegm', 'blood_in_phlegm', 'loss_of_appetite', 'nausea',
            'vomiting', 'rapid_breathing', 'sharp_chest_pain', 'confusion', 'bluish_lips',
            'muscle_aches', 'weakness', 'headache', 'diarrhea', 'ear_pain',
        ],
        'Arthritis': [
            'joint_pain', 'stiffness', 'swelling', 'reduced_range_of_motion', 'tenderness',
            'warm_joints', 'morning_stiffness', 'fatigue', 'fever', 'weight_loss',
            'joint_deformity', 'grinding_sensation', 'bone_spurs', 'muscle_weakness',
            'numbness_tingling', 'difficulty_walking', 'redness_around_joints',
            'cracking_joints', 'pain_after_rest', 'inflammation',
        ],
        'Anxiety': [
            'restlessness', 'rapid_heartbeat', 'sweating', 'difficulty_concentrating', 'insomnia',
            'irritability', 'muscle_tension', 'worry', 'fatigue', 'panic', 'trembling',
            'chest_tightness', 'shortness_of_breath', 'dizziness', 'nausea', 'headache',
            'stomach_upset', 'avoiding_situations', 'feeling_on_edge', 'sleep_problems',
        ],
        'Depression': [
            'persistent_sadness', 'loss_of_interest', 'fatigue', 'sleep_changes', 'appetite_changes',
            'weight_changes', 'hopelessness', 'irritability', 'difficulty_concentrating',
            'suicidal_thoughts', 'aches_pains', 'digestive_issues', 'slowed_movement',
            'guilt', 'worthlessness', 'low_energy', 'insomnia', 'oversleeping',
            'withdrawal', 'loss_of_pleasure', 'indecisiveness',
        ],
    }
    
    def predict(self, symptoms_list):
        """
        Predict disease using weighted scoring:
        - Rewards diseases that explain more of the user's selected symptoms.
        - Requires at least 2 matching symptoms to reduce false positives.
        - Confidence reflects both match count and specificity.
        """
        if not symptoms_list:
            return None
        
        symptoms_set = set(s.lower().strip().replace(' ', '_') for s in symptoms_list)
        if not symptoms_set:
            return None
        
        best_disease = None
        best_score = -1.0
        best_matches = 0
        
        for disease_name, disease_symptoms in self.DISEASE_SYMPTOM_MAP.items():
            disease_set = set(disease_symptoms)
            intersection = symptoms_set.intersection(disease_set)
            match_count = len(intersection)
            
            # Allow single-symptom matches but treat them as low-confidence.
            # Previously we required at least 2 matches; now we accept 1 match
            # but apply a penalty so single-symptom predictions are clearly lower confidence.
            if match_count == 0:
                continue
            
            # Weighted score: how much of the disease profile matches (specificity)
            # + how much of user's selection we explain (coverage)
            n_disease = len(disease_set)
            n_user = len(symptoms_set)
            specificity = match_count / n_disease if n_disease else 0   # match vs disease symptoms
            coverage = match_count / n_user if n_user else 0             # match vs user selection
            # Combined: 55% specificity, 45% coverage, scaled to 0–100
            score = (0.55 * specificity + 0.45 * coverage) * 100
            # Slight boost for more matches (more evidence)
            if match_count >= 4:
                score = min(99, score + 8)
            elif match_count >= 3:
                score = min(99, score + 4)

            # Penalize single-symptom matches so they appear as low-confidence.
            if match_count == 1:
                # Scale down strongly but keep a small minimum confidence (5%)
                score = max(5.0, score * 0.35)
            
            if score > best_score:
                best_score = score
                best_disease = disease_name
                best_matches = match_count
        
        if best_disease is None:
            return None
        
        confidence_score = round(min(99, best_score), 2)
        
        try:
            disease = Disease.objects.get(name=best_disease)
            return {
                'disease': disease,
                'confidence': confidence_score,
                'severity': disease.severity_level,
                'specialist': disease.specialist_required
            }
        except Disease.DoesNotExist:
            fallback = DISEASE_FALLBACK_INFO.get(best_disease, {})
            return {
                'disease_name': best_disease,
                'confidence': confidence_score,
                'severity': fallback.get('severity_level', 'moderate'),
                'specialist': fallback.get('specialist_required', 'General Physician')
            }
    
    def get_available_symptoms(self):
        """Get all available symptoms from database"""
        return Symptom.objects.all()


def predict_disease(symptoms):
    """
    Main function to predict disease from symptoms
    Args:
        symptoms: list of symptom names
    Returns:
        prediction dict or None
    """
    model = DiseasePredictionModel()
    return model.predict(symptoms)


def get_disease_recommendations(disease):
    """
    Get all recommendations for a disease
    Returns: {
        'precautions': [...],
        'diet': {'recommended': [...], 'avoid': [...]},
        'exercises': [...],
        'medicines': [...]
    }
    """
    try:
        disease_obj = Disease.objects.get(name=disease) if isinstance(disease, str) else disease
        
        if not disease_obj:
            return None
        
        # Get precautions
        precautions = list(disease_obj.precautions.all().values_list('precaution', flat=True))
        
        # Get diet recommendations - ensure all fields are strings
        diet_recommended = [
            {
                'food_item': str(item.get('food_item', '')),
                'description': str(item.get('description', ''))
            }
            for item in disease_obj.diet_recommendations.filter(is_recommended=True).values('food_item', 'description')
        ]
        diet_avoid = [
            {
                'food_item': str(item.get('food_item', '')),
                'description': str(item.get('description', ''))
            }
            for item in disease_obj.diet_recommendations.filter(is_recommended=False).values('food_item', 'description')
        ]
        
        # Get exercises - ensure all fields are strings
        exercises = [
            {
                'exercise_name': str(ex.get('exercise_name', '')),
                'description': str(ex.get('description', '')),
                'duration': str(ex.get('duration', '')),
                'intensity': str(ex.get('intensity', ''))
            }
            for ex in disease_obj.exercises.all().values('exercise_name', 'description', 'duration', 'intensity')
        ]
        
        # Get top 5 medicines - ensure all fields are strings
        medicines = [
            {
                'medicine_name': str(m.get('medicine_name', '')),
                'generic_name': str(m.get('generic_name', '')),
                'dosage': str(m.get('dosage', '')),
                'description': str(m.get('description', '')),
                'side_effects': str(m.get('side_effects', ''))
            }
            for m in disease_obj.medicines.all()[:5].values('medicine_name', 'generic_name', 'dosage', 'description', 'side_effects')
        ]
        
        return {
            'precautions': [str(p) for p in precautions] if precautions else [],
            'diet': {
                'recommended': diet_recommended if diet_recommended else [],
                'avoid': diet_avoid if diet_avoid else []
            },
            'exercises': exercises if exercises else [],
            'medicines': medicines if medicines else []
        }
    except (Disease.DoesNotExist, AttributeError, Exception) as e:
        # Return empty recommendations structure instead of None
        return {
            'precautions': [],
            'diet': {
                'recommended': [],
                'avoid': []
            },
            'exercises': [],
            'medicines': []
        }