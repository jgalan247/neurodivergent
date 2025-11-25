"""
Prompt Generator for AdaptEd.

Generates comprehensive AI prompts based on student profiles and conditions.
"""
from typing import List, Optional
from students.models import StudentProfile, StudentCondition, AdaptationSettings
from assessments.models import Assessment


class PromptGenerator:
    """
    Generates AI prompts for content adaptation based on student profiles.
    """

    # Core rules that always apply
    CORE_RULES = """
=== ABSOLUTE RULES (NEVER VIOLATE) ===
1. NEVER provide answers to questions
2. NEVER add new factual information that wasn't in the original
3. NEVER change the educational objectives or learning outcomes
4. NEVER modify mathematical calculations, formulas, or equations
5. NEVER alter quoted text, citations, or source material
6. NEVER change proper nouns, names, dates, or specific data
7. Preserve ALL question marks and the interrogative nature of questions
8. Keep the same number of questions as the original
9. Maintain mark allocations exactly as specified
"""

    # Content preservation rules based on flags
    CONTENT_RULES = {
        'quotations': """
QUOTATION RULES:
- Preserve ALL quoted text exactly as written in quotation marks
- Do not paraphrase or simplify text within quotes
- You may add context around quotes, but the quoted text must remain unchanged
- Include citation information exactly as provided
""",
        'mathematical_notation': """
MATHEMATICAL NOTATION RULES:
- Preserve ALL mathematical symbols, equations, and formulas exactly
- Do not write out numbers in words if they appear as numerals
- Keep fraction formats (e.g., 3/4) as shown
- Preserve mathematical operators (+, -, ×, ÷, =, <, >, etc.)
- Do not convert units or measurements
- Preserve algebraic expressions exactly
""",
        'code': """
CODE RULES:
- Preserve ALL code exactly as written
- Do not modify syntax, spacing, or indentation in code blocks
- You may add explanatory text around code, but the code itself must remain unchanged
- Keep variable names, function names, and comments exactly as written
""",
        'diagrams': """
DIAGRAM REFERENCE RULES:
- Preserve all references to diagrams, figures, charts, and images
- Keep figure numbers and labels exactly as specified
- You may add descriptive text to help interpret diagrams
- Reference diagrams by their original names/numbers
""",
        'poetry': """
POETRY/VERSE RULES:
- Preserve ALL poetry exactly as written - every word, line break, and punctuation mark
- Do not paraphrase or modernise poetic language
- Maintain original stanza structure
- Keep rhyme schemes intact
""",
        'script': """
SCRIPT/DIALOGUE RULES:
- Preserve ALL dialogue exactly as written
- Maintain character names and stage directions
- Keep the format of script notation (character: dialogue)
"""
    }

    # Condition-specific prompts from the specification
    CONDITION_PROMPTS = {
        'dyslexia': """
--- DYSLEXIA ADAPTATIONS ---
- Use simple, common vocabulary where possible (preserve technical terms)
- Break complex sentences into shorter ones (max {max_sentence_length} words)
- Use active voice, not passive
- Avoid double negatives
- Replace complex connectives: "however" → "but", "therefore" → "so"
- One instruction per sentence
{syllable_instruction}
- Highlight key action words in instructions: **Calculate**, **Explain**, **List**
- Number all steps explicitly
- Add white space between sections
- Keep questions on single pages where possible (indicate if content continues)
""",
        'autism': """
--- AUTISM SPECTRUM ADAPTATIONS ---
- CRITICAL: Remove ALL idioms, metaphors, and figurative language
- Replace with literal, concrete alternatives
- Common idioms to replace:
  * "A piece of cake" → "easy" or "simple"
  * "Break a leg" → "good luck"
  * "Hit the nail on the head" → "correct" or "exactly right"
  * "Costs an arm and a leg" → "very expensive"
  * "Under the weather" → "feeling ill"
  * "Raining cats and dogs" → "raining very heavily"

- Remove ALL sarcasm and implied meanings
- Make every instruction completely explicit:
  BAD: "Show your working"
  GOOD: "Write down each calculation step you used. Show the numbers and operations."

- Remove ambiguous quantifiers:
  BAD: "Answer some of the questions"
  GOOD: "Answer questions 1, 2, 3, 4, and 5"

- Add explicit structure markers:
  "SECTION A: [TOPIC] (Questions X-Y)"
  "Question X of Y"
  "END OF SECTION"

- Provide explicit time guidance where appropriate:
  "Most students spend about 3 minutes on this question"

- Make answer format explicit:
  BAD: "Explain your answer"
  GOOD: "Write 2-3 sentences explaining why you chose this answer"

- Replace vague pronouns with specific nouns:
  BAD: "Calculate it"
  GOOD: "Calculate the area"

- Use consistent terminology throughout - never use synonyms for the same concept
- Remove decorative language and unnecessary adjectives
- Present one instruction per line
- Use concrete, specific language always
""",
        'adhd': """
--- ADHD ADAPTATIONS ---
- Chunk content into small, manageable sections (max {questions_per_section} questions per section)
- Add clear section breaks with headers
- Include progress markers: "Question X of Y" or "Section X of Y"
- Highlight key action words: **Calculate**, **Explain**, **List**
- Highlight key numbers and data in word problems
- Keep all information needed for a question on the same page/view
- For multi-step problems, break into explicit numbered steps:
  BAD: "Find the area and then calculate the cost"
  GOOD:
  "Step 1: Calculate the area of the rectangle
   Step 2: Multiply the area by the given price to find the total cost"

- Add time estimates where helpful: "(~2 minutes)"
- Include "checkpoint" markers: "✓ Section Complete - X questions done!"
- Remove all unnecessary decorative elements
- Use white space generously between questions
- For long word problems, bold the key information:
  "Sarah has **12 apples**. She gives **3 apples** to Tom."

- Add reference boxes for formulas or key information students might forget
- Suggest an order: "Start with Question 1" (reduce decision paralysis)
- Keep sentences short and direct
- One instruction per line
""",
        'dyscalculia': """
--- DYSCALCULIA ADAPTATIONS ---
- Add visual representations of quantities where appropriate
- Break multi-step calculations into explicit numbered steps:
  BAD: "Calculate 24 × 15"
  GOOD:
  "Calculate 24 × 15
   Step 1: Break 15 into 10 + 5
   Step 2: Calculate 24 × 10 = ___
   Step 3: Calculate 24 × 5 = ___
   Step 4: Add your answers: ___ + ___ = ___"

- Include place value support for large numbers:
  "The number 3,456 has:
   3 thousands | 4 hundreds | 5 tens | 6 ones"

- Add number lines for questions involving sequences or comparisons

- Include formula reminders in a visible box:
  "REMEMBER: Area of rectangle = length × width"

- Use concrete contexts:
  BAD: "Calculate 3 + 7"
  GOOD: "Tom has 3 sweets. He gets 7 more sweets. How many sweets does Tom have now?"

- Provide scaffolded answer spaces:
  "Working space:
   Step 1: _______________
   Step 2: _______________
   Final answer: _______________"

- For word problems, extract and list the key numbers:
  "Key information:
   • Price per item: £2.50
   • Number of items: 6
   • Money paid: £20"

- Use consistent mathematical language (don't alternate between "times", "multiply", "×")
- Add estimation prompts: "Your answer should be approximately..."
- Include "check your answer" prompts: "Does this answer make sense?"
""",
        'visual_processing': """
--- VISUAL PROCESSING ADAPTATIONS ---
- Describe all layout requirements explicitly:
  * Single column layout only
  * Generous spacing between all elements
  * Clear section borders
  * No text wrapping around images

- Simplify any diagrams described:
  * Remove decorative elements
  * Use clear, simple lines
  * Add explicit labels to all parts
  * Use distinct descriptions for different elements

- Structure text for easy visual tracking:
  * Short paragraphs (3-4 lines maximum)
  * Clear line breaks between ideas
  * Numbered points for sequences
  * Bullet points for lists

- Add explicit visual organisation:
  * Section headers clearly marked
  * Question numbers prominent
  * Answer spaces clearly described

- For any visual content references, provide text alternatives:
  * "The diagram shows a rectangle with width 4cm and height 6cm"
  * Describe what students need to see/understand

- Remove visual clutter:
  * No decorative elements
  * No complex formatting references
  * Consistent structure throughout
""",
        'auditory_processing': """
--- AUDITORY PROCESSING ADAPTATIONS ---
- Ensure all instructions are fully written out (not reliant on audio)
- Structure information visually with clear headers and sections
- For any content that might be read aloud:
  * Use clear, distinct words (avoid similar-sounding terms close together)
  * Short sentences for easier processing
  * Pause points indicated between sections

- Reinforce key information through visual means:
  * Bold important words
  * Use bullet points
  * Include summary boxes

- Ensure assessment doesn't disadvantage students who can't process audio well
""",
        'working_memory': """
--- WORKING MEMORY ADAPTATIONS ---
- Ensure all information needed to answer is visible with the question
- For multi-part questions, repeat the scenario/context for each part:
  BAD:
  "Sarah has 12 apples.
   a) How many are left if she gives 3 to Tom?
   b) She then buys 5 more. How many now?"

  GOOD:
  "Sarah has 12 apples.
   a) Sarah has 12 apples. She gives 3 to Tom. How many apples does Sarah have left?

   b) After giving apples to Tom, Sarah has [your answer from a] apples. She then buys 5 more apples. How many apples does Sarah have now?"

- Break multi-step problems into single steps with space for each:
  "Step 1: Write down the first number: ______
   Step 2: Write down the operation: ______
   Step 3: Write down the second number: ______
   Step 4: Calculate your answer: ______"

- Add reference boxes for information students will need:
  "REFERENCE:
   • 1 km = 1000 m
   • 1 hour = 60 minutes"

- Include prompts that help students track their progress:
  "You have completed: Step 1 ✓ Step 2 □ Step 3 □"

- Provide sentence starters for written answers:
  "The character felt ___ because ___"

- For long-form answers, provide planning templates:
  "Point 1: ______
   Evidence: ______
   Explanation: ______"
""",
        'processing_speed': """
--- PROCESSING SPEED ADAPTATIONS ---
- Use the most direct, clear language possible
- Remove all unnecessary words:
  BAD: "Can you please calculate what the total amount would be if you were to add these numbers together"
  GOOD: "Add these numbers. Write the total."

- Short sentences only (maximum 10-12 words)
- One question per section where possible
- Clear, uncluttered layout description
- Include reassuring notes:
  "Take your time with this question"
  "There is no rush"

- Reduce reading load where possible:
  * Use bullet points not paragraphs
  * Remove redundant context
  * Get to the question quickly

- Simplify vocabulary (while preserving technical terms)
- Consider if any questions could be combined or streamlined
""",
        'anxiety': """
--- ANXIETY REDUCTION ADAPTATIONS ---
- Use calm, encouraging language throughout:
  * "Let's try this question"
  * "Do your best"
  * "It's okay to find this challenging"

- Avoid alarming or pressuring language:
  * Remove: "You must...", "You should know...", "This is easy..."
  * Remove: "Hurry", "Quickly", "Time is running out"

- Frame questions positively:
  BAD: "Don't forget to show your working"
  GOOD: "Remember to show your working - you can earn marks for each step"

- Include reassuring statements:
  * "You can come back to this question later"
  * "Just do what you can"
  * "Your teacher knows you're trying your best"

- Make partial credit explicit:
  * "Even if you don't get the final answer, you can earn marks by showing your method"

- Structure for success:
  * Start with accessible questions
  * Build in complexity gradually

- Remove competitive or comparative language:
  * Remove: "Most students can do this"
  * Remove: "This should be quick"

- Add grounding prompts at section breaks:
  * "Well done on completing Section A. Take a breath before continuing."
""",
        'eal': """
--- EAL (English as Additional Language) ADAPTATIONS ---
- Simplify non-technical vocabulary:
  BAD: "Approximately calculate the perimeter"
  GOOD: "Find the perimeter" (keep "perimeter" as technical term)

- Remove idioms and culturally-specific references:
  * No British slang or colloquialisms
  * Replace UK-specific contexts with universal ones:
    BAD: "At a boot sale, John buys..."
    GOOD: "At a market, John buys..."

- Use clear, simple sentence structures:
  * Subject-verb-object order
  * Avoid complex subordinate clauses
  * One idea per sentence

- Provide technical vocabulary support:
  * Bold technical terms on first use
  * Include simple definition in brackets: "the perimeter (the distance around the outside)"

- Remove assumed cultural knowledge:
  * Explain any cultural references
  * Use internationally understood contexts
  * Use simple, common names
"""
    }

    def generate_system_prompt(
        self,
        student_profile: StudentProfile,
        assessment: Assessment,
        subject_terms: List[str] = None
    ) -> str:
        """
        Generate a complete system prompt for adapting assessment content.

        Args:
            student_profile: The student's profile with conditions
            assessment: The assessment being adapted
            subject_terms: List of subject-specific protected terms

        Returns:
            Complete system prompt string
        """
        prompt_parts = []

        # 1. Introduction
        prompt_parts.append("""You are an educational content adaptation specialist. Your role is to modify assessment content to make it accessible for students with specific learning needs while preserving educational integrity and academic rigour.

Your output should be the complete adapted assessment content, ready for the student to use.""")

        # 2. Core rules
        prompt_parts.append(self.CORE_RULES)

        # 3. Content-specific rules based on flags
        content_flags = assessment.content_flags or {}
        for flag_name, rule_text in self.CONTENT_RULES.items():
            if content_flags.get(flag_name):
                prompt_parts.append(rule_text)

        # 4. Protected terms
        all_terms = list(subject_terms or [])
        all_terms.extend(assessment.protected_terms or [])
        if all_terms:
            terms_str = ', '.join(f'"{t}"' for t in all_terms)
            prompt_parts.append(f"""
PROTECTED TERMS (never simplify or change these):
{terms_str}
""")

        # 5. Student profile settings
        try:
            settings = student_profile.adaptation_settings
        except AdaptationSettings.DoesNotExist:
            settings = None

        prompt_parts.append(self._generate_profile_section(student_profile, settings))

        # 6. Condition-specific adaptations
        conditions = student_profile.conditions.all()
        for condition in conditions:
            condition_prompt = self._get_condition_prompt(condition, settings)
            if condition_prompt:
                prompt_parts.append(condition_prompt)

        # 7. Output format
        prompt_parts.append(self._generate_output_format(settings))

        return '\n\n'.join(prompt_parts)

    def _generate_profile_section(
        self,
        student_profile: StudentProfile,
        settings: Optional[AdaptationSettings]
    ) -> str:
        """Generate the student profile section of the prompt."""
        if not settings:
            return """
=== STUDENT PROFILE ===
Use standard adaptation settings.
"""

        return f"""
=== STUDENT PROFILE ===
Target Reading Level: Year {settings.reading_year_level}
Maximum Sentence Length: {settings.max_sentence_length} words
Vocabulary Simplification: {settings.vocabulary_simplification}/10 (1=maximum, 10=none)
Key Word Highlighting: {"Yes" if settings.key_word_highlighting else "No"}
Progress Indicators: {"Yes" if settings.progress_indicators else "No"}
Numbered Steps: {"Yes" if settings.numbered_steps else "No"}
Questions Per Section: {settings.questions_per_section}
"""

    def _get_condition_prompt(
        self,
        condition: StudentCondition,
        settings: Optional[AdaptationSettings]
    ) -> str:
        """Get the prompt section for a specific condition."""
        condition_type = condition.condition_type
        base_prompt = self.CONDITION_PROMPTS.get(condition_type, '')

        if not base_prompt:
            return ''

        # Replace placeholders with actual settings
        if settings:
            base_prompt = base_prompt.format(
                max_sentence_length=settings.max_sentence_length,
                questions_per_section=settings.questions_per_section,
                syllable_instruction="- Add syllable breaks to words over 3 syllables: in-de-pen-dent" if settings.syllable_breaking else ""
            )
        else:
            base_prompt = base_prompt.format(
                max_sentence_length=15,
                questions_per_section=3,
                syllable_instruction=""
            )

        # Add intensive instructions for significant severity
        if condition.severity == 'significant':
            base_prompt += f"""

IMPORTANT: This student has SIGNIFICANT {condition.get_condition_type_display()} needs.
Apply these adaptations thoroughly and consistently throughout the entire document.
"""

        return base_prompt

    def _generate_output_format(self, settings: Optional[AdaptationSettings]) -> str:
        """Generate output format instructions."""
        format_instructions = """
=== OUTPUT FORMAT ===
- Return the complete adapted assessment
- Use clear markdown formatting:
  * Use headers (##, ###) for sections
  * Use **bold** for emphasis and key terms
  * Use numbered lists for steps
  * Use bullet points for lists
  * Use horizontal rules (---) between sections
- Preserve question numbering from the original
- Include all parts of multi-part questions
- Do not add any commentary or explanations about what you changed
- Output ONLY the adapted assessment content
"""

        if settings:
            if settings.progress_indicators:
                format_instructions += "\n- Include progress indicators: 'Question X of Y'"
            if settings.section_breaks:
                format_instructions += "\n- Add clear section breaks between groups of questions"
            if settings.reference_panels:
                format_instructions += "\n- Include reference boxes with key formulas/information at the start of relevant sections"
            if settings.scaffolded_answers:
                format_instructions += "\n- Include answer scaffolding with step-by-step spaces for working"
            if settings.encouragement_prompts:
                format_instructions += "\n- Add brief encouraging prompts at section breaks"

        return format_instructions


def get_combined_profile_settings(student_profile: StudentProfile) -> dict:
    """
    Generate combined settings when a student has multiple conditions.

    Uses the 'most supportive' approach where the most helpful setting wins.
    """
    conditions = list(student_profile.conditions.all())

    # Start with defaults
    combined = {
        'literal_language_mode': False,
        'syllable_breaking': False,
        'timer_display': 'show',
        'feedback_style': 'neutral',
        'max_sentence_length': 15,
        'questions_per_section': 3,
    }

    condition_types = [c.condition_type for c in conditions]

    # If autism is present, always enable literal language
    if 'autism' in condition_types:
        combined['literal_language_mode'] = True

    # If anxiety is present, use encouraging feedback and hide timer
    if 'anxiety' in condition_types:
        combined['feedback_style'] = 'encouraging'
        combined['timer_display'] = 'hide'

    # If dyslexia is present, enable syllable breaking
    if 'dyslexia' in condition_types:
        combined['syllable_breaking'] = True
        combined['max_sentence_length'] = min(combined['max_sentence_length'], 12)

    # If ADHD is present, reduce questions per section
    if 'adhd' in condition_types:
        combined['questions_per_section'] = min(combined['questions_per_section'], 2)

    # Use shortest sentence length from any condition
    if 'processing_speed' in condition_types:
        combined['max_sentence_length'] = min(combined['max_sentence_length'], 10)

    return combined
