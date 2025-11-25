"""
Management command to seed initial data for AdaptEd.
"""
from django.core.management.base import BaseCommand
from adaptations.models import ContentRule, SubjectTerms, IdiomDictionary
from students.models import AdaptationTemplate


class Command(BaseCommand):
    help = 'Seed initial data for AdaptEd platform'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...')

        # Content Rules
        rules = [
            ('never_answer', 'NEVER provide answers to questions. Your role is to adapt the FORMAT and LANGUAGE, not to solve problems.'),
            ('never_add_info', 'NEVER add new factual information that wasn\'t in the original. You may add structural elements (headers, prompts) but not new content.'),
            ('preserve_quotations', 'Preserve ALL quoted text exactly as written. Do not paraphrase or simplify text within quotation marks.'),
            ('preserve_maths', 'Preserve ALL mathematical symbols, equations, and formulas exactly. Do not convert or simplify mathematical notation.'),
            ('preserve_code', 'Preserve ALL code exactly as written. Do not modify syntax, spacing, or indentation in code blocks.'),
            ('preserve_diagrams', 'Preserve all references to diagrams, figures, charts, and images. Keep figure numbers and labels exactly as specified.'),
        ]

        for rule_type, prompt_text in rules:
            ContentRule.objects.get_or_create(
                rule_type=rule_type,
                defaults={'prompt_text': prompt_text, 'is_active': True}
            )
        self.stdout.write(f'  Created {len(rules)} content rules')

        # Subject Terms
        subjects = {
            'mathematics': [
                'perimeter', 'area', 'volume', 'radius', 'diameter', 'circumference',
                'fraction', 'numerator', 'denominator', 'integer', 'decimal', 'equation',
                'formula', 'variable', 'coefficient', 'constant', 'parallel', 'perpendicular',
                'adjacent', 'hypotenuse', 'mean', 'median', 'mode', 'range', 'probability',
                'ratio', 'proportion', 'percentage', 'algebra', 'geometry', 'trigonometry',
                'quadratic', 'linear', 'polynomial', 'factor', 'multiple', 'prime', 'composite'
            ],
            'science': [
                'atom', 'molecule', 'electron', 'proton', 'neutron', 'photosynthesis',
                'respiration', 'osmosis', 'diffusion', 'velocity', 'acceleration', 'force',
                'momentum', 'energy', 'compound', 'element', 'mixture', 'solution', 'cell',
                'nucleus', 'chromosome', 'gene', 'DNA', 'evolution', 'species', 'ecosystem',
                'habitat', 'organism', 'tissue', 'organ'
            ],
            'english': [
                'metaphor', 'simile', 'personification', 'alliteration', 'onomatopoeia',
                'protagonist', 'antagonist', 'narrator', 'character', 'stanza', 'verse',
                'rhyme', 'rhythm', 'imagery', 'noun', 'verb', 'adjective', 'adverb',
                'pronoun', 'conjunction', 'preposition', 'clause', 'phrase', 'paragraph',
                'thesis', 'analysis', 'context', 'inference'
            ],
            'history': [
                'century', 'decade', 'era', 'period', 'dynasty', 'revolution',
                'reformation', 'renaissance', 'monarchy', 'democracy', 'republic',
                'empire', 'treaty', 'parliament', 'constitution'
            ],
            'geography': [
                'latitude', 'longitude', 'equator', 'hemisphere', 'erosion',
                'weathering', 'deposition', 'sediment', 'population', 'migration',
                'urbanisation', 'climate', 'biome', 'ecosystem', 'sustainability'
            ],
        }

        for subject, terms in subjects.items():
            SubjectTerms.objects.get_or_create(
                subject=subject,
                defaults={'terms': terms}
            )
        self.stdout.write(f'  Created subject terms for {len(subjects)} subjects')

        # Idiom Dictionary
        idioms = [
            ('a piece of cake', 'easy or simple', 'food'),
            ('break a leg', 'good luck', 'body'),
            ('hit the nail on the head', 'correct or exactly right', 'tools'),
            ('costs an arm and a leg', 'very expensive', 'body'),
            ('under the weather', 'feeling ill', 'weather'),
            ('raining cats and dogs', 'raining very heavily', 'weather'),
            ('let the cat out of the bag', 'reveal a secret', 'animals'),
            ('the ball is in your court', 'it is your turn to act or make a decision', 'sports'),
            ('bite the bullet', 'accept something difficult or unpleasant', 'general'),
            ('once in a blue moon', 'very rarely', 'nature'),
            ('break the ice', 'start a conversation or make people feel comfortable', 'nature'),
            ('beat around the bush', 'avoid talking about something directly', 'nature'),
            ('get out of hand', 'become out of control', 'body'),
            ('hang in there', 'keep trying, don\'t give up', 'general'),
            ('it takes two to tango', 'both people are responsible', 'general'),
            ('kill two birds with one stone', 'solve two problems with one action', 'animals'),
            ('miss the boat', 'miss an opportunity', 'transport'),
            ('on the ball', 'quick to understand or react', 'sports'),
            ('piece of mind', 'feeling calm and not worried', 'body'),
            ('pull someone\'s leg', 'joke with someone', 'body'),
            ('spill the beans', 'reveal a secret', 'food'),
            ('take it with a grain of salt', 'don\'t believe it completely', 'food'),
            ('the best of both worlds', 'all the advantages', 'general'),
            ('time flies', 'time passes quickly', 'time'),
            ('twist someone\'s arm', 'persuade someone', 'body'),
            ('when pigs fly', 'never', 'animals'),
        ]

        for idiom, meaning, category in idioms:
            IdiomDictionary.objects.get_or_create(
                idiom=idiom,
                defaults={'literal_meaning': meaning, 'category': category}
            )
        self.stdout.write(f'  Created {len(idioms)} idiom entries')

        # Adaptation Templates
        templates = [
            {
                'name': 'Dyslexia Standard',
                'description': 'Standard adaptations for students with dyslexia including larger text, dyslexia-friendly fonts, and syllable breaking.',
                'conditions': ['dyslexia'],
                'settings': {
                    'font': 'opendyslexic',
                    'font_size': 16,
                    'line_spacing': 1.75,
                    'letter_spacing': 10,
                    'background_colour': 'cream',
                    'syllable_breaking': True,
                    'key_word_highlighting': True,
                    'reading_year_level': 7,
                    'max_sentence_length': 12,
                    'tts_enabled': True
                },
                'is_global': True
            },
            {
                'name': 'Autism - Full Literal Mode',
                'description': 'Comprehensive adaptations for autistic students with full literal language mode and explicit instructions.',
                'conditions': ['autism'],
                'settings': {
                    'literal_language_mode': True,
                    'literal_language_intensity': 10,
                    'explicit_instructions': True,
                    'progress_indicators': True,
                    'section_breaks': True,
                    'timer_display': 'hide',
                    'visual_density': 3,
                    'feedback_style': 'neutral',
                    'questions_per_section': 3
                },
                'is_global': True
            },
            {
                'name': 'ADHD Support',
                'description': 'Adaptations for students with ADHD focusing on chunking, visual cues, and progress tracking.',
                'conditions': ['adhd'],
                'settings': {
                    'questions_per_section': 2,
                    'progress_indicators': True,
                    'key_word_highlighting': True,
                    'reference_panels': True,
                    'visual_density': 3,
                    'section_breaks': True,
                    'encouragement_prompts': True,
                    'numbered_steps': True
                },
                'is_global': True
            },
            {
                'name': 'Anxiety Reduction',
                'description': 'Calming adaptations for students with test anxiety, including encouraging language and hidden timers.',
                'conditions': ['anxiety'],
                'settings': {
                    'timer_display': 'hide',
                    'feedback_style': 'encouraging',
                    'encouragement_prompts': True,
                    'anxiety_reduction': True,
                    'progress_indicators': True,
                    'visual_density': 4
                },
                'is_global': True
            },
            {
                'name': 'Dyscalculia Support',
                'description': 'Adaptations for students with dyscalculia including scaffolded answers and visual number representations.',
                'conditions': ['dyscalculia'],
                'settings': {
                    'scaffolded_answers': True,
                    'reference_panels': True,
                    'numbered_steps': True,
                    'visual_density': 3,
                    'questions_per_section': 2
                },
                'is_global': True
            },
            {
                'name': 'Low Reading Age (Year 5)',
                'description': 'Simplified language targeting Year 5 reading level with short sentences and common vocabulary.',
                'conditions': [],
                'settings': {
                    'reading_year_level': 5,
                    'max_sentence_length': 10,
                    'vocabulary_simplification': 3,
                    'key_word_highlighting': True,
                    'numbered_steps': True
                },
                'is_global': True
            },
        ]

        for template_data in templates:
            AdaptationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
        self.stdout.write(f'  Created {len(templates)} adaptation templates')

        self.stdout.write(self.style.SUCCESS('Successfully seeded initial data'))
