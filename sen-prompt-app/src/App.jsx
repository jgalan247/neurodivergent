import { useState, useEffect, useRef } from "react";
import jsPDF from "jspdf";
import pptxgen from "pptxgenjs";
import katex from "katex";
import "katex/dist/katex.min.css";

const ADAPTATIONS = [
  { id: "use_icons", label: "Use icons to support key ideas" },
  { id: "add_visuals", label: "Add diagrams or visuals to explain concepts" },
  { id: "use_timelines", label: "Use timelines or sequences to show order of events" },
  { id: "chunk_text", label: "Chunk text into short paragraphs or bullet points" },
  { id: "extra_spacing", label: "Use extra spacing and clear headings" },
  { id: "dyslexia_friendly_font", label: "Use a dyslexia-friendly font and high contrast" },
  { id: "use_colour_coding", label: "Use colour coding for key words/sections" },
  { id: "short_steps", label: "Break tasks into short, numbered steps" },
  { id: "timers", label: "Suggest realistic time estimates for each task" },
  { id: "high_interest_hooks", label: "Use high-interest examples and hooks" },
  { id: "minimal_text_per_page", label: "Keep minimal text per slide/page" },
  { id: "checklist_style", label: "Present tasks as a checklist" },
  { id: "movement_breaks", label: "Build in short movement/brain breaks" },
  { id: "clear_structure", label: "Use a clear, predictable lesson structure" },
  { id: "literal_language", label: "Use literal, concrete language (avoid idioms)" },
  { id: "predictable_layout", label: "Keep layout consistent across pages/slides" },
  { id: "reduced_sensory_load", label: "Avoid cluttered backgrounds and unnecessary decoration" },
  { id: "explicit_transitions", label: "Signpost and explain transitions between activities" },
  { id: "concrete_examples", label: "Use concrete, real-world maths examples" },
  { id: "visual_maths", label: "Include visual representations of numbers/operations" },
  { id: "step_by_step_maths", label: "Break calculations into explicit small steps" },
  { id: "number_lines", label: "Use number lines and manipulatives" }
];

const CONDITION_DEFAULTS = {
  Autism: [
    "clear_structure",
    "literal_language",
    "predictable_layout",
    "reduced_sensory_load",
    "add_visuals",
    "use_timelines",
    "explicit_transitions"
  ],
  Dyslexia: [
    "chunk_text",
    "extra_spacing",
    "dyslexia_friendly_font",
    "use_colour_coding",
    "use_icons",
    "add_visuals"
  ],
  ADHD: [
    "short_steps",
    "timers",
    "high_interest_hooks",
    "minimal_text_per_page",
    "checklist_style",
    "movement_breaks"
  ],
  Dyscalculia: [
    "concrete_examples",
    "visual_maths",
    "step_by_step_maths",
    "number_lines",
    "use_colour_coding",
    "chunk_text",
    "extra_spacing"
  ]
};

const KEY_STAGES = [
  { value: "KS3", label: "KS3 (11-14 years)" },
  { value: "KS4", label: "KS4 / GCSE (14-16 years)" }
];

const READING_LEVELS = [
  { value: "", label: "No adjustment" },
  { value: "below", label: "Below expected (simplified)" },
  { value: "at", label: "At expected level" },
  { value: "above", label: "Above expected (extended)" }
];

const ATTAINMENT_LEVELS = [
  { value: "low", label: "Low Attainment" },
  { value: "high", label: "High Attainment" }
];

const EXAM_BOARDS = [
  { value: "OCR", label: "OCR" },
  { value: "AQA", label: "AQA" },
  { value: "Pearson", label: "Pearson" },
  { value: "Edexcel", label: "Edexcel" }
];

const EAL_BANDS = [
  {
    value: "A",
    label: "Band A - New to English",
    guidance: "New to English: Use extensive visual supports, simplified language, bilingual resources where possible, key vocabulary with images, allow responses in first language, focus on survival/social English"
  },
  {
    value: "B",
    label: "Band B - Early Acquisition",
    guidance: "Early Acquisition: Pre-teach key vocabulary, use sentence starters and frames, provide graphic organisers, use repetition and modelling, allow extended processing time"
  },
  {
    value: "C",
    label: "Band C - Developing Competence",
    guidance: "Developing Competence: Scaffold academic language explicitly, model text structures, provide word banks for subject-specific vocabulary, use collaborative learning activities"
  },
  {
    value: "D",
    label: "Band D - Competent",
    guidance: "Competent: Focus on academic register and formal language, develop subject-specific terminology, support with complex text structures and inferential comprehension"
  },
  {
    value: "E",
    label: "Band E - Fluent",
    guidance: "Fluent: Support with nuanced academic language, idiomatic expressions, and cultural references that may still present challenges"
  }
];

const MOTHER_TONGUES = [
  { value: "Arabic", label: "Arabic / العربية", scriptType: "non-Latin", languageFamily: "Semitic" },
  { value: "Bengali", label: "Bengali / বাংলা", scriptType: "non-Latin", languageFamily: "Indo-Aryan" },
  { value: "Bulgarian", label: "Bulgarian / Български", scriptType: "Cyrillic", languageFamily: "Slavic" },
  { value: "Cantonese", label: "Cantonese / 廣東話", scriptType: "non-Latin", languageFamily: "Sino-Tibetan" },
  { value: "French", label: "French / Français", scriptType: "Latin", languageFamily: "Romance" },
  { value: "German", label: "German / Deutsch", scriptType: "Latin", languageFamily: "Germanic" },
  { value: "Gujarati", label: "Gujarati / ગુજરાતી", scriptType: "non-Latin", languageFamily: "Indo-Aryan" },
  { value: "Hindi", label: "Hindi / हिन्दी", scriptType: "non-Latin", languageFamily: "Indo-Aryan" },
  { value: "Italian", label: "Italian / Italiano", scriptType: "Latin", languageFamily: "Romance" },
  { value: "Japanese", label: "Japanese / 日本語", scriptType: "non-Latin", languageFamily: "Japonic" },
  { value: "Korean", label: "Korean / 한국어", scriptType: "non-Latin", languageFamily: "Koreanic" },
  { value: "Lithuanian", label: "Lithuanian / Lietuvių", scriptType: "Latin", languageFamily: "Baltic" },
  { value: "Mandarin", label: "Mandarin / 普通话", scriptType: "non-Latin", languageFamily: "Sino-Tibetan" },
  { value: "Pashto", label: "Pashto / پښتو", scriptType: "non-Latin", languageFamily: "Iranian" },
  { value: "Polish", label: "Polish / Polski", scriptType: "Latin", languageFamily: "Slavic" },
  { value: "Portuguese", label: "Portuguese / Português", scriptType: "Latin", languageFamily: "Romance" },
  { value: "Punjabi", label: "Punjabi / ਪੰਜਾਬੀ", scriptType: "non-Latin", languageFamily: "Indo-Aryan" },
  { value: "Romanian", label: "Romanian / Română", scriptType: "Latin", languageFamily: "Romance" },
  { value: "Russian", label: "Russian / Русский", scriptType: "Cyrillic", languageFamily: "Slavic" },
  { value: "Somali", label: "Somali / Soomaali", scriptType: "Latin", languageFamily: "Cushitic" },
  { value: "Spanish", label: "Spanish / Español", scriptType: "Latin", languageFamily: "Romance" },
  { value: "Swahili", label: "Swahili / Kiswahili", scriptType: "Latin", languageFamily: "Bantu" },
  { value: "Tamil", label: "Tamil / தமிழ்", scriptType: "non-Latin", languageFamily: "Dravidian" },
  { value: "Turkish", label: "Turkish / Türkçe", scriptType: "Latin", languageFamily: "Turkic" },
  { value: "Ukrainian", label: "Ukrainian / Українська", scriptType: "Cyrillic", languageFamily: "Slavic" },
  { value: "Urdu", label: "Urdu / اردو", scriptType: "non-Latin", languageFamily: "Indo-Aryan" },
  { value: "Vietnamese", label: "Vietnamese / Tiếng Việt", scriptType: "Latin", languageFamily: "Austroasiatic" },
  { value: "Other", label: "Other", scriptType: "unknown", languageFamily: "unknown" }
];

const LANGUAGES = [
  { value: "", label: "English (default)" },
  { value: "French", label: "French / Français" },
  { value: "Spanish", label: "Spanish / Español" },
  { value: "Portuguese", label: "Portuguese / Português" },
  { value: "Romanian", label: "Romanian / Română" },
  { value: "Bulgarian", label: "Bulgarian / Български" },
  { value: "Polish", label: "Polish / Polski" },
  { value: "Italian", label: "Italian / Italiano" },
  { value: "Afrikaans", label: "Afrikaans" }
];

const QUESTION_TYPES = [
  { id: "multiple_choice", label: "Multiple choice" },
  { id: "short_answer", label: "Short answer" },
  { id: "fill_blanks", label: "Fill in the blanks" },
  { id: "matching", label: "Matching pairs" },
  { id: "true_false", label: "True/False" },
  { id: "extended_response", label: "Extended response" },
  { id: "scaffolded", label: "Scaffolded questions (with prompts)" }
];

const PROMPT_TEMPLATES = [
  {
    id: "adapt_exam",
    name: "Adapt an Exam Paper",
    description: "Modify an existing exam for accessibility",
    values: {
      format: "worksheet",
      lessonObjectives: "Students will demonstrate their understanding through accessible assessment questions."
    }
  },
  {
    id: "revision_summary",
    name: "Create Revision Summary",
    description: "Condensed, accessible revision notes",
    values: {
      format: "summary",
      lessonObjectives: "Students will be able to review and consolidate key concepts from the topic."
    }
  },
  {
    id: "simplify_textbook",
    name: "Simplify Textbook Chapter",
    description: "Make dense text more accessible",
    values: {
      format: "summary",
      lessonObjectives: "Students will understand the main concepts presented in the original text."
    }
  },
  {
    id: "interactive_worksheet",
    name: "Interactive Worksheet",
    description: "Engaging practice activities",
    values: {
      format: "worksheet",
      lessonObjectives: "Students will practice and apply their learning through structured activities."
    }
  },
  {
    id: "flashcard_set",
    name: "Flashcard Set",
    description: "Key terms and concepts for revision",
    values: {
      format: "flashcards",
      lessonObjectives: "Students will memorise and recall key vocabulary and concepts."
    }
  }
];

const FORMAT_RULES = {
  worksheet: [
    "Clear numbering for each question/task",
    "Adequate space for written answers",
    "Instructions at the start of each section"
  ],
  "revision questions": [
    "Mix of question types (short answer, multiple choice)",
    "Mark scheme hints where appropriate",
    "Self-check answers at the end"
  ],
  summary: [
    "Key points in bullet format",
    "Important terms highlighted",
    "Maximum 1 page per sub-topic"
  ],
  "simplified PowerPoint text": [
    "One main idea per slide",
    "Maximum 6 words per bullet point",
    "Speaker notes for additional context"
  ],
  PowerPoint: [
    "One main idea per slide",
    "Large, clear fonts (minimum 24pt)",
    "High contrast colours"
  ],
  PDF: [
    "Accessible formatting with headings",
    "Alt text for images",
    "Readable font size (minimum 12pt)"
  ],
  flashcards: [
    "One concept per card",
    "Question on front, answer on back",
    "Visual cues where helpful"
  ]
};

const ADAPTATION_MAP = ADAPTATIONS.reduce((acc, item) => {
  acc[item.id] = item;
  return acc;
}, {});

const STORAGE_KEY = "sen-prompt-history";
const MAX_HISTORY = 10;

const AI_PROVIDERS = [
  { id: "gemini", name: "Gemini 2.5 Flash", model: "gemini-2.5-flash" },
  { id: "claude", name: "Claude Haiku", model: "claude-3-5-haiku-20241022" },
  { id: "openai", name: "GPT-4o Mini", model: "gpt-4o-mini" }
];

// API keys from environment variables
const CLAUDE_API_KEY = import.meta.env.VITE_CLAUDE_API_KEY;
const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const OPENAI_API_KEY = import.meta.env.VITE_OPENAI_API_KEY;

async function callClaudeAPI(prompt) {
  if (!CLAUDE_API_KEY) {
    throw new Error("Claude API key not configured. Please set VITE_CLAUDE_API_KEY environment variable.");
  }

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": CLAUDE_API_KEY,
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true"
    },
    body: JSON.stringify({
      model: "claude-3-5-haiku-20241022",
      max_tokens: 4096,
      messages: [{ role: "user", content: prompt }]
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || "Claude API error");
  }

  const data = await response.json();
  return data.content[0].text;
}

async function callGeminiAPI(prompt) {
  if (!GEMINI_API_KEY) {
    throw new Error("Gemini API key not configured. Please set VITE_GEMINI_API_KEY environment variable.");
  }

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }]
      })
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || "Gemini API error");
  }

  const data = await response.json();
  return data.candidates[0].content.parts[0].text;
}

async function callOpenAIAPI(prompt) {
  if (!OPENAI_API_KEY) {
    throw new Error("OpenAI API key not configured. Please set VITE_OPENAI_API_KEY environment variable.");
  }

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      max_tokens: 4096,
      messages: [{ role: "user", content: prompt }]
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || "OpenAI API error");
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

export default function App() {
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [format, setFormat] = useState("");
  const [conditions, setConditions] = useState([]);
  const [resource, setResource] = useState(null);
  const [lessonTitle, setLessonTitle] = useState("");
  const [lessonObjectives, setLessonObjectives] = useState("");
  const [keyStage, setKeyStage] = useState("");
  const [readingLevel, setReadingLevel] = useState("");
  const [attainmentLevel, setAttainmentLevel] = useState("");
  const [examBoard, setExamBoard] = useState("");
  const [ealBand, setEalBand] = useState("");
  const [motherTongue, setMotherTongue] = useState("");
  const [language, setLanguage] = useState("");
  const [selectedQuestionTypes, setSelectedQuestionTypes] = useState([]);
  const [selectedAdaptations, setSelectedAdaptations] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState("");
  const [darkMode, setDarkMode] = useState(false);

  // AI Provider state
  const [selectedProvider, setSelectedProvider] = useState("gemini");
  const [aiResponse, setAiResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [aiError, setAiError] = useState("");
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [isGeneratingPptx, setIsGeneratingPptx] = useState(false);
  const aiResponseRef = useRef(null);

  // Load history and dark mode preference from localStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem(STORAGE_KEY);
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error("Failed to parse history:", e);
      }
    }

    const savedDarkMode = localStorage.getItem("sen-prompt-dark-mode");
    if (savedDarkMode) {
      setDarkMode(JSON.parse(savedDarkMode));
    }
  }, []);

  // Save dark mode preference
  useEffect(() => {
    localStorage.setItem("sen-prompt-dark-mode", JSON.stringify(darkMode));
  }, [darkMode]);

  // Run prompt with selected AI provider
  const runPrompt = async (promptText) => {
    const textToRun = promptText || prompt;
    if (!textToRun) {
      setAiError("Please generate a prompt first.");
      return;
    }

    setIsLoading(true);
    setAiError("");
    setAiResponse("");

    try {
      let response;
      if (selectedProvider === "claude") {
        response = await callClaudeAPI(textToRun);
      } else if (selectedProvider === "openai") {
        response = await callOpenAIAPI(textToRun);
      } else {
        response = await callGeminiAPI(textToRun);
      }
      setAiResponse(response);
    } catch (error) {
      setAiError(error.message || "Failed to get response from AI");
    } finally {
      setIsLoading(false);
    }
  };

  // Generate prompt and run with Gemini directly
  const generateAndRunWithGemini = async () => {
    // Build the prompt (same logic as generatePrompt)
    let adaptedPrompt = `You are a ${subject || "[subject]"} teacher creating an accessible learning resource.\n`;

    if (keyStage) {
      adaptedPrompt += `Target level: ${keyStage}.\n`;
    }

    if (examBoard) {
      adaptedPrompt += `Examination board: ${examBoard} - align content with ${examBoard} specification, command words, and assessment objectives.\n`;
    }

    if (readingLevel) {
      const levelDescriptions = {
        below: "Adjust reading level BELOW expected for this key stage (simplified vocabulary, shorter sentences)",
        at: "Maintain reading level AT expected for this key stage",
        above: "Adjust reading level ABOVE expected for this key stage (extended vocabulary, more complex structures)"
      };
      adaptedPrompt += `Reading level: ${levelDescriptions[readingLevel]}.\n`;
    }

    if (language) {
      adaptedPrompt += `Output language: Translate/write the resource in ${language}.\n`;
    }

    if (resource) {
      adaptedPrompt += `Adapt the attached resource file (${resource.name}) for a neuro-divergent student.\n`;
    } else {
      adaptedPrompt += `Topic focus: ${topic || "[topic]"}.\n`;
      adaptedPrompt += `Create the output in ${format || "[output format]"} format.\n`;
    }

    if (attainmentLevel) {
      const attainmentDescriptions = {
        low: "Low Attainment - provide additional scaffolding, simpler language, more visual supports, and break down concepts into smaller steps",
        high: "High Attainment - include extension activities, deeper analysis questions, and opportunities for independent exploration"
      };
      adaptedPrompt += `Student attainment: ${attainmentDescriptions[attainmentLevel]}.\n`;
    }

    if (conditions.length > 0) {
      const conditionText = conditions.join(" + ");
      adaptedPrompt += `Student condition(s): ${conditionText}.\n`;
    }

    if (ealBand && motherTongue) {
      const bandInfo = EAL_BANDS.find(b => b.value === ealBand);
      const tongueInfo = MOTHER_TONGUES.find(t => t.value === motherTongue);

      if (bandInfo) {
        adaptedPrompt += `\nEAL Learner (Bell Foundation ${bandInfo.label}):\n`;
        adaptedPrompt += `${bandInfo.guidance}\n`;

        if (tongueInfo) {
          adaptedPrompt += `Mother tongue: ${tongueInfo.value}`;
          if (tongueInfo.scriptType !== "unknown") {
            adaptedPrompt += ` (${tongueInfo.scriptType} script, ${tongueInfo.languageFamily} language family)`;
          }
          adaptedPrompt += `.\n`;

          if (tongueInfo.scriptType === "non-Latin") {
            adaptedPrompt += `Note: Student uses non-Latin script - provide additional support for letter formation and reading direction.\n`;
          }
          if (tongueInfo.languageFamily === "Romance") {
            adaptedPrompt += `Note: Romance language speaker - leverage cognates with English where possible.\n`;
          }
          if (tongueInfo.languageFamily === "Sino-Tibetan") {
            adaptedPrompt += `Note: Tonal language speaker - explicit support for English intonation and stress patterns may help.\n`;
          }
        }
      }
    }

    if (selectedAdaptations.length > 0) {
      adaptedPrompt += `\nAdaptations to include:\n`;
      selectedAdaptations.forEach((id) => {
        const item = ADAPTATION_MAP[id];
        if (item) {
          adaptedPrompt += `- ${item.label}\n`;
        }
      });
    }

    if (selectedQuestionTypes.length > 0) {
      adaptedPrompt += `\nQuestion types to include:\n`;
      selectedQuestionTypes.forEach((id) => {
        const qt = QUESTION_TYPES.find((q) => q.id === id);
        if (qt) {
          adaptedPrompt += `- ${qt.label}\n`;
        }
      });
    }

    adaptedPrompt += `\nRewrite following these constraints now.\n\n`;
    adaptedPrompt += `Lesson Title: ${lessonTitle || "[Insert lesson title here]"}\n`;
    adaptedPrompt += `Lesson Objectives: ${lessonObjectives || "[Insert lesson objectives here]"}\n\n`;

    adaptedPrompt += `Rules:\n`;
    adaptedPrompt += `- Language: literal, clear, concise\n`;
    adaptedPrompt += `- Readability: chunked, well-spaced\n`;
    adaptedPrompt += `- Keep factual accuracy\n`;
    adaptedPrompt += `- Use supportive tone\n`;
    adaptedPrompt += `- Avoid oversimplification of key concepts\n`;
    adaptedPrompt += `- Maintain assessment objectives if present\n`;
    adaptedPrompt += `- For ALL mathematical expressions, use LaTeX notation: inline math with single dollar signs ($x^2$) and display math with double dollar signs ($$\\frac{a}{b}$$)\n`;

    if (format && FORMAT_RULES[format]) {
      adaptedPrompt += `\nFormat-specific guidelines (${format}):\n`;
      FORMAT_RULES[format].forEach((rule) => {
        adaptedPrompt += `- ${rule}\n`;
      });
    }

    // Set the prompt in state
    setPrompt(adaptedPrompt);

    // Run with Claude Haiku
    setIsLoading(true);
    setAiError("");
    setAiResponse("");

    try {
      const response = await callClaudeAPI(adaptedPrompt);
      setAiResponse(response);
    } catch (error) {
      setAiError(error.message || "Failed to get response from Claude");
    } finally {
      setIsLoading(false);
    }
  };

  const handleConditionToggle = (conditionName) => {
    setConditions((prev) => {
      const newConditions = prev.includes(conditionName)
        ? prev.filter((c) => c !== conditionName)
        : [...prev, conditionName];

      // Merge adaptations from all selected conditions
      const mergedAdaptations = new Set();
      newConditions.forEach((cond) => {
        if (CONDITION_DEFAULTS[cond]) {
          CONDITION_DEFAULTS[cond].forEach((a) => mergedAdaptations.add(a));
        }
      });
      setSelectedAdaptations([...mergedAdaptations]);

      return newConditions;
    });
  };

  const toggleAdaptation = (id) => {
    setSelectedAdaptations((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    );
  };

  const toggleQuestionType = (id) => {
    setSelectedQuestionTypes((prev) =>
      prev.includes(id) ? prev.filter((q) => q !== id) : [...prev, id]
    );
  };

  const applyTemplate = (template) => {
    if (template.values.format) setFormat(template.values.format);
    if (template.values.lessonObjectives) setLessonObjectives(template.values.lessonObjectives);
  };

  const showCopyFeedback = (message) => {
    setCopyFeedback(message);
    setTimeout(() => setCopyFeedback(""), 2000);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    showCopyFeedback("Copied!");
  };

  const generatePrompt = () => {
    let adaptedPrompt = `You are a ${subject || "[subject]"} teacher creating an accessible learning resource.\n`;

    if (keyStage) {
      adaptedPrompt += `Target level: ${keyStage}.\n`;
    }

    // Exam board
    if (examBoard) {
      adaptedPrompt += `Examination board: ${examBoard} - align content with ${examBoard} specification, command words, and assessment objectives.\n`;
    }

    // Reading level adjustment
    if (readingLevel) {
      const levelDescriptions = {
        below: "Adjust reading level BELOW expected for this key stage (simplified vocabulary, shorter sentences)",
        at: "Maintain reading level AT expected for this key stage",
        above: "Adjust reading level ABOVE expected for this key stage (extended vocabulary, more complex structures)"
      };
      adaptedPrompt += `Reading level: ${levelDescriptions[readingLevel]}.\n`;
    }

    // Language/translation
    if (language) {
      adaptedPrompt += `Output language: Translate/write the resource in ${language}.\n`;
    }

    if (resource) {
      adaptedPrompt += `Adapt the attached resource file (${resource.name}) for a neuro-divergent student.\n`;
    } else {
      adaptedPrompt += `Topic focus: ${topic || "[topic]"}.\n`;
      adaptedPrompt += `Create the output in ${format || "[output format]"} format.\n`;
    }

    // Attainment level
    if (attainmentLevel) {
      const attainmentDescriptions = {
        low: "Low Attainment - provide additional scaffolding, simpler language, more visual supports, and break down concepts into smaller steps",
        high: "High Attainment - include extension activities, deeper analysis questions, and opportunities for independent exploration"
      };
      adaptedPrompt += `Student attainment: ${attainmentDescriptions[attainmentLevel]}.\n`;
    }

    // Conditions (optional if attainment is selected)
    if (conditions.length > 0) {
      const conditionText = conditions.join(" + ");
      adaptedPrompt += `Student condition(s): ${conditionText}.\n`;
    }

    // EAL / Bell Foundation
    if (ealBand && motherTongue) {
      const bandInfo = EAL_BANDS.find(b => b.value === ealBand);
      const tongueInfo = MOTHER_TONGUES.find(t => t.value === motherTongue);

      if (bandInfo) {
        adaptedPrompt += `\nEAL Learner (Bell Foundation ${bandInfo.label}):\n`;
        adaptedPrompt += `${bandInfo.guidance}\n`;

        if (tongueInfo) {
          adaptedPrompt += `Mother tongue: ${tongueInfo.value}`;
          if (tongueInfo.scriptType !== "unknown") {
            adaptedPrompt += ` (${tongueInfo.scriptType} script, ${tongueInfo.languageFamily} language family)`;
          }
          adaptedPrompt += `.\n`;

          // Add specific guidance based on language characteristics
          if (tongueInfo.scriptType === "non-Latin") {
            adaptedPrompt += `Note: Student uses non-Latin script - provide additional support for letter formation and reading direction.\n`;
          }
          if (tongueInfo.languageFamily === "Romance") {
            adaptedPrompt += `Note: Romance language speaker - leverage cognates with English where possible.\n`;
          }
          if (tongueInfo.languageFamily === "Sino-Tibetan") {
            adaptedPrompt += `Note: Tonal language speaker - explicit support for English intonation and stress patterns may help.\n`;
          }
        }
      }
    }

    if (selectedAdaptations.length > 0) {
      adaptedPrompt += `\nAdaptations to include:\n`;
      selectedAdaptations.forEach((id) => {
        const item = ADAPTATION_MAP[id];
        if (item) {
          adaptedPrompt += `- ${item.label}\n`;
        }
      });
    }

    // Question types
    if (selectedQuestionTypes.length > 0) {
      adaptedPrompt += `\nQuestion types to include:\n`;
      selectedQuestionTypes.forEach((id) => {
        const qt = QUESTION_TYPES.find((q) => q.id === id);
        if (qt) {
          adaptedPrompt += `- ${qt.label}\n`;
        }
      });
    }

    adaptedPrompt += `\nRewrite following these constraints now.\n\n`;
    adaptedPrompt += `Lesson Title: ${lessonTitle || "[Insert lesson title here]"}\n`;
    adaptedPrompt += `Lesson Objectives: ${lessonObjectives || "[Insert lesson objectives here]"}\n\n`;

    adaptedPrompt += `Rules:\n`;
    adaptedPrompt += `- Language: literal, clear, concise\n`;
    adaptedPrompt += `- Readability: chunked, well-spaced\n`;
    adaptedPrompt += `- Keep factual accuracy\n`;
    adaptedPrompt += `- Use supportive tone\n`;
    adaptedPrompt += `- Avoid oversimplification of key concepts\n`;
    adaptedPrompt += `- Maintain assessment objectives if present\n`;
    adaptedPrompt += `- For ALL mathematical expressions, use LaTeX notation: inline math with single dollar signs ($x^2$) and display math with double dollar signs ($$\\frac{a}{b}$$)\n`;

    // Add format-specific rules
    if (format && FORMAT_RULES[format]) {
      adaptedPrompt += `\nFormat-specific guidelines (${format}):\n`;
      FORMAT_RULES[format].forEach((rule) => {
        adaptedPrompt += `- ${rule}\n`;
      });
    }

    setPrompt(adaptedPrompt);

    // Save to history
    const historyEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      subject,
      topic,
      conditions: [...conditions],
      format,
      keyStage,
      lessonTitle,
      prompt: adaptedPrompt
    };

    const newHistory = [historyEntry, ...history].slice(0, MAX_HISTORY);
    setHistory(newHistory);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newHistory));
  };

  const loadFromHistory = (entry) => {
    setSubject(entry.subject || "");
    setTopic(entry.topic || "");
    setConditions(entry.conditions || []);
    setFormat(entry.format || "");
    setKeyStage(entry.keyStage || "");
    setLessonTitle(entry.lessonTitle || "");
    setPrompt(entry.prompt || "");
    setShowHistory(false);
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  const downloadPrompt = (asJson = false) => {
    if (!prompt) return;

    if (asJson) {
      const jsonData = {
        subject,
        topic,
        conditions,
        format,
        keyStage,
        lessonTitle,
        lessonObjectives,
        selectedAdaptations,
        generatedPrompt: prompt,
        timestamp: new Date().toISOString()
      };
      const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: "application/json" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "sen_prompt.json";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      const blob = new Blob([prompt], { type: "text/plain" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "adapted_prompt.txt";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const downloadAsPdf = async () => {
    if (!aiResponse) return;

    setIsGeneratingPdf(true);

    try {
      const pdf = new jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: "a4"
      });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 15;
      const maxWidth = pageWidth - margin * 2;
      let yPosition = margin;

      // Add title
      pdf.setFontSize(18);
      pdf.setFont("helvetica", "bold");
      const title = `${subject || "Resource"} - ${topic || lessonTitle || "Output"}`;
      pdf.text(title, margin, yPosition);
      yPosition += 10;

      // Add metadata line
      pdf.setFontSize(10);
      pdf.setFont("helvetica", "normal");
      pdf.setTextColor(100);
      const metadata = [
        conditions.length > 0 ? `Adapted for: ${conditions.join(", ")}` : "",
        attainmentLevel ? `${attainmentLevel === "low" ? "Low" : "High"} Attainment` : "",
        keyStage || ""
      ].filter(Boolean).join(" | ");
      if (metadata) {
        pdf.text(metadata, margin, yPosition);
        yPosition += 8;
      }

      // Reset text color and add separator line
      pdf.setTextColor(0);
      pdf.setDrawColor(200);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 8;

      // Add content
      pdf.setFontSize(11);
      pdf.setFont("helvetica", "normal");

      // Split content into lines that fit the page width
      const lines = pdf.splitTextToSize(aiResponse, maxWidth);

      for (const line of lines) {
        // Check if we need a new page
        if (yPosition > pageHeight - margin) {
          pdf.addPage();
          yPosition = margin;
        }

        // Check for headers (lines that start with # or ** or are all caps)
        const trimmedLine = line.trim();
        const isHeader = trimmedLine.startsWith("#") ||
                         (trimmedLine.startsWith("**") && trimmedLine.endsWith("**")) ||
                         /^[A-Z][A-Z\s]+:/.test(trimmedLine);

        if (isHeader) {
          yPosition += 3; // Extra space before header
          pdf.setFont("helvetica", "bold");
          pdf.setFontSize(12);
          // Clean up markdown
          const cleanHeader = trimmedLine
            .replace(/^#+\s*/, "")
            .replace(/^\*\*/, "")
            .replace(/\*\*$/, "");
          pdf.text(cleanHeader, margin, yPosition);
          pdf.setFont("helvetica", "normal");
          pdf.setFontSize(11);
        } else {
          pdf.text(line, margin, yPosition);
        }

        yPosition += 6;
      }

      const filename = `${subject || "resource"}_${topic || "output"}_${new Date().toISOString().split("T")[0]}.pdf`;
      pdf.save(filename.replace(/\s+/g, "_"));
    } catch (error) {
      console.error("PDF generation error:", error);
      setAiError("Failed to generate PDF. Please try again.");
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const downloadAsPptx = async () => {
    if (!aiResponse) return;

    setIsGeneratingPptx(true);

    try {
      const pptx = new pptxgen();
      pptx.author = "SEN Resource Generator";
      pptx.title = `${subject || "Resource"} - ${topic || lessonTitle || "Output"}`;
      pptx.subject = "Educational Resource";

      // Parse AI response into sections
      const lines = aiResponse.split("\n");
      const sections = [];
      let currentSection = { title: "", content: [] };

      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine) continue;

        // Detect section headers (lines starting with #, **, or all caps with colon)
        const isHeader =
          trimmedLine.startsWith("#") ||
          (trimmedLine.startsWith("**") && trimmedLine.endsWith("**")) ||
          /^[A-Z][A-Z\s]+:/.test(trimmedLine) ||
          /^#{1,3}\s/.test(trimmedLine);

        if (isHeader) {
          // Save previous section if it has content
          if (currentSection.title || currentSection.content.length > 0) {
            sections.push({ ...currentSection });
          }
          // Start new section - clean up markdown formatting
          currentSection = {
            title: trimmedLine
              .replace(/^#+\s*/, "")
              .replace(/^\*\*/, "")
              .replace(/\*\*$/, "")
              .replace(/:$/, ""),
            content: []
          };
        } else {
          // Add content to current section
          currentSection.content.push(trimmedLine);
        }
      }

      // Don't forget the last section
      if (currentSection.title || currentSection.content.length > 0) {
        sections.push(currentSection);
      }

      // If no sections were detected, create one with all content
      if (sections.length === 0) {
        sections.push({
          title: topic || lessonTitle || "Content",
          content: lines.filter(l => l.trim())
        });
      }

      // Create title slide
      const titleSlide = pptx.addSlide();
      titleSlide.addText(subject || "Educational Resource", {
        x: 0.5,
        y: 1.5,
        w: 9,
        h: 1.5,
        fontSize: 36,
        bold: true,
        color: "1e293b",
        align: "center"
      });
      titleSlide.addText(topic || lessonTitle || "Adapted Resource", {
        x: 0.5,
        y: 3,
        w: 9,
        h: 1,
        fontSize: 24,
        color: "475569",
        align: "center"
      });
      if (conditions.length > 0 || attainmentLevel) {
        const subtitle = [
          conditions.length > 0 ? `Adapted for: ${conditions.join(", ")}` : "",
          attainmentLevel ? `${attainmentLevel === "low" ? "Low" : "High"} Attainment` : ""
        ].filter(Boolean).join(" | ");
        titleSlide.addText(subtitle, {
          x: 0.5,
          y: 4.2,
          w: 9,
          h: 0.5,
          fontSize: 14,
          color: "64748b",
          align: "center"
        });
      }

      // Create content slides from sections
      for (const section of sections) {
        const slide = pptx.addSlide();

        // Add section title
        slide.addText(section.title || "Content", {
          x: 0.5,
          y: 0.3,
          w: 9,
          h: 0.8,
          fontSize: 28,
          bold: true,
          color: "1e293b"
        });

        // Process content into bullet points
        const bulletPoints = [];
        for (const item of section.content) {
          // Clean up markdown formatting
          let cleanItem = item
            .replace(/^\s*[-*•]\s*/, "")  // Remove bullet markers
            .replace(/\*\*/g, "")          // Remove bold markers
            .replace(/\*/g, "")            // Remove italic markers
            .replace(/`/g, "")             // Remove code markers
            .trim();

          if (cleanItem) {
            bulletPoints.push({ text: cleanItem, options: { bullet: true } });
          }
        }

        // Add bullet points (limit per slide for readability)
        const maxBulletsPerSlide = 6;
        if (bulletPoints.length > 0) {
          const bulletsForSlide = bulletPoints.slice(0, maxBulletsPerSlide);
          slide.addText(bulletsForSlide, {
            x: 0.5,
            y: 1.3,
            w: 9,
            h: 4.5,
            fontSize: 18,
            color: "334155",
            valign: "top",
            lineSpacing: 28
          });

          // If more bullets, create additional slides
          let remainingBullets = bulletPoints.slice(maxBulletsPerSlide);
          while (remainingBullets.length > 0) {
            const extraSlide = pptx.addSlide();
            extraSlide.addText(`${section.title} (continued)`, {
              x: 0.5,
              y: 0.3,
              w: 9,
              h: 0.8,
              fontSize: 28,
              bold: true,
              color: "1e293b"
            });
            extraSlide.addText(remainingBullets.slice(0, maxBulletsPerSlide), {
              x: 0.5,
              y: 1.3,
              w: 9,
              h: 4.5,
              fontSize: 18,
              color: "334155",
              valign: "top",
              lineSpacing: 28
            });
            remainingBullets = remainingBullets.slice(maxBulletsPerSlide);
          }
        }
      }

      // Save the file
      const filename = `${subject || "resource"}_${topic || "output"}_${new Date().toISOString().split("T")[0]}`;
      await pptx.writeFile({ fileName: filename.replace(/\s+/g, "_") + ".pptx" });
    } catch (error) {
      console.error("PowerPoint generation error:", error);
      setAiError("Failed to generate PowerPoint. Please try again.");
    } finally {
      setIsGeneratingPptx(false);
    }
  };

  // Render text with KaTeX math expressions
  // Supports both inline ($...$) and display ($$...$$) math
  const renderWithMath = (text) => {
    if (!text) return null;

    // Split by display math first ($$...$$), then inline math ($...$)
    const parts = [];
    let remaining = text;
    let key = 0;

    // Process display math ($$...$$)
    while (remaining.includes("$$")) {
      const startIdx = remaining.indexOf("$$");
      const endIdx = remaining.indexOf("$$", startIdx + 2);

      if (endIdx === -1) break;

      // Add text before math
      if (startIdx > 0) {
        parts.push({ type: "text", content: remaining.slice(0, startIdx), key: key++ });
      }

      // Add display math
      const mathContent = remaining.slice(startIdx + 2, endIdx);
      parts.push({ type: "display-math", content: mathContent, key: key++ });

      remaining = remaining.slice(endIdx + 2);
    }

    // Process inline math ($...$) in remaining text
    if (remaining) {
      const inlineParts = remaining.split(/(\$[^$]+\$)/g);
      for (const part of inlineParts) {
        if (part.startsWith("$") && part.endsWith("$") && part.length > 2) {
          parts.push({ type: "inline-math", content: part.slice(1, -1), key: key++ });
        } else if (part) {
          parts.push({ type: "text", content: part, key: key++ });
        }
      }
    }

    // If no math found, return plain text
    if (parts.length === 0) {
      return <span>{text}</span>;
    }

    return parts.map((part) => {
      if (part.type === "display-math") {
        try {
          return (
            <div
              key={part.key}
              className="my-3 text-center overflow-x-auto"
              dangerouslySetInnerHTML={{
                __html: katex.renderToString(part.content, {
                  displayMode: true,
                  throwOnError: false,
                  trust: true
                })
              }}
            />
          );
        } catch (e) {
          return <div key={part.key} className="text-red-500">{`$$${part.content}$$`}</div>;
        }
      } else if (part.type === "inline-math") {
        try {
          return (
            <span
              key={part.key}
              dangerouslySetInnerHTML={{
                __html: katex.renderToString(part.content, {
                  displayMode: false,
                  throwOnError: false,
                  trust: true
                })
              }}
            />
          );
        } catch (e) {
          return <span key={part.key} className="text-red-500">{`$${part.content}$`}</span>;
        }
      } else {
        return <span key={part.key}>{part.content}</span>;
      }
    });
  };

  // Render full AI response with math support, preserving line breaks
  const renderAiResponse = (response) => {
    if (!response) return null;

    const lines = response.split("\n");
    return lines.map((line, idx) => (
      <div key={idx} className={line.trim() === "" ? "h-4" : ""}>
        {renderWithMath(line)}
      </div>
    ));
  };

  const resetForm = () => {
    setSubject("");
    setTopic("");
    setFormat("");
    setConditions([]);
    setResource(null);
    setLessonTitle("");
    setLessonObjectives("");
    setKeyStage("");
    setReadingLevel("");
    setAttainmentLevel("");
    setExamBoard("");
    setEalBand("");
    setMotherTongue("");
    setLanguage("");
    setSelectedQuestionTypes([]);
    setSelectedAdaptations([]);
    setPrompt("");
    // Reset file input
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) fileInput.value = "";
  };

  const isGenerateDisabled = () => {
    // Must have subject and either conditions OR attainment level
    if (!subject) return true;
    if (conditions.length === 0 && !attainmentLevel) return true;
    if (!resource && (!topic || !format)) return true;
    return false;
  };

  const bgClass = darkMode ? "bg-slate-900" : "bg-slate-100";
  const cardClass = darkMode ? "bg-slate-800" : "bg-white";
  const textClass = darkMode ? "text-slate-100" : "text-slate-900";
  const textMutedClass = darkMode ? "text-slate-400" : "text-slate-600";
  const textMutedSmClass = darkMode ? "text-slate-500" : "text-slate-500";
  const borderClass = darkMode ? "border-slate-600" : "border-slate-200";
  const inputBgClass = darkMode ? "bg-slate-700 border-slate-600 text-slate-100" : "bg-white border-slate-200";
  const inputBgMutedClass = darkMode ? "bg-slate-700 border-slate-600" : "bg-slate-50";

  return (
    <div className={`min-h-screen ${bgClass} p-4 transition-colors duration-200`}>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Copy feedback toast */}
        {copyFeedback && (
          <div className="fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-pulse">
            {copyFeedback}
          </div>
        )}

        <header className="space-y-1 flex justify-between items-start">
          <div>
            <h1 className={`text-3xl font-bold ${textClass}`}>
              SEN Resource Prompt Generator v2
            </h1>
            <p className={`text-sm ${textMutedClass} max-w-2xl`}>
              Build a tailored AI prompt for neuro-divergent learners. Fill in the details,
              choose adaptations, then copy or download the prompt and paste it into your preferred AI tool
              along with your resource.
            </p>
          </div>
          <div className="flex gap-2 items-center">
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${borderClass} ${textClass} hover:bg-slate-200 dark:hover:bg-slate-700`}
              title="Toggle dark mode"
            >
              {darkMode ? "☀️ Light" : "🌙 Dark"}
            </button>
          </div>
        </header>

        {/* History panel */}
        {showHistory && (
          <div className={`${cardClass} rounded-2xl shadow-md p-4 space-y-3`}>
            <div className="flex justify-between items-center">
              <h2 className={`text-lg font-semibold ${textClass}`}>Prompt History</h2>
              {history.length > 0 && (
                <button
                  onClick={clearHistory}
                  className="text-xs text-red-600 hover:text-red-700"
                >
                  Clear all
                </button>
              )}
            </div>
            {history.length === 0 ? (
              <p className={`text-sm ${textMutedClass}`}>No saved prompts yet.</p>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {history.map((entry) => (
                  <div
                    key={entry.id}
                    className={`p-3 border ${borderClass} rounded-xl cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700`}
                    onClick={() => loadFromHistory(entry)}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className={`text-sm font-medium ${textClass}`}>
                          {entry.subject} - {entry.topic || entry.lessonTitle || "Untitled"}
                        </p>
                        <p className={`text-xs ${textMutedSmClass}`}>
                          {entry.conditions?.join(", ")} | {entry.format}
                        </p>
                      </div>
                      <span className={`text-xs ${textMutedSmClass}`}>
                        {new Date(entry.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Templates */}
        <div className={`${cardClass} rounded-2xl shadow-md p-4`}>
          <h2 className={`text-md font-semibold mb-3 ${textClass}`}>Quick Templates</h2>
          <div className="flex flex-wrap gap-2">
            {PROMPT_TEMPLATES.map((template) => (
              <button
                key={template.id}
                onClick={() => applyTemplate(template)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border ${borderClass} ${textClass} hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors`}
                title={template.description}
              >
                {template.name}
              </button>
            ))}
          </div>
        </div>

        <main className="grid lg:grid-cols-3 gap-6 items-start">
          {/* Left: Form */}
          <section className={`lg:col-span-2 space-y-4 ${cardClass} rounded-2xl shadow-md p-4`}>
            <div className="flex justify-between items-center">
              <h2 className={`text-lg font-semibold ${textClass}`}>Lesson & learner details</h2>
              <button
                onClick={resetForm}
                className={`text-xs ${textMutedClass} hover:text-red-600`}
              >
                Reset form
              </button>
            </div>

            <div className="space-y-3">
              <div className="grid md:grid-cols-2 gap-3">
                <div>
                  <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Subject</label>
                  <input
                    className={`w-full p-2 border rounded-xl text-sm ${inputBgClass}`}
                    type="text"
                    placeholder="e.g. Maths, English, History"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                  />
                </div>

                <div>
                  <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Key Stage</label>
                  <div className={`flex gap-4 p-2 border rounded-xl ${inputBgMutedClass}`}>
                    {KEY_STAGES.map((ks) => (
                      <label key={ks.value} className="flex items-center gap-1.5 text-sm cursor-pointer">
                        <input
                          type="radio"
                          name="keyStage"
                          value={ks.value}
                          checked={keyStage === ks.value}
                          onChange={(e) => setKeyStage(e.target.value)}
                        />
                        <span className={textClass}>{ks.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-3">
                <div>
                  <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Lesson Title</label>
                  <input
                    className={`w-full p-2 border rounded-xl text-sm ${inputBgClass}`}
                    type="text"
                    placeholder="e.g. Fractions with Like Denominators"
                    value={lessonTitle}
                    onChange={(e) => setLessonTitle(e.target.value)}
                  />
                </div>

                <div>
                  <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Student Condition(s)</label>
                  <div className={`flex flex-wrap gap-2 p-2 border rounded-xl ${inputBgMutedClass}`}>
                    {Object.keys(CONDITION_DEFAULTS).map((cond) => (
                      <label key={cond} className="flex items-center gap-1.5 text-xs cursor-pointer">
                        <input
                          type="checkbox"
                          checked={conditions.includes(cond)}
                          onChange={() => handleConditionToggle(cond)}
                          className="rounded"
                        />
                        <span className={textClass}>{cond}</span>
                      </label>
                    ))}
                  </div>
                  <p className={`mt-1 text-xs ${textMutedSmClass}`}>
                    Select multiple conditions to merge their adaptations.
                  </p>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-3">
                <div>
                  <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Attainment Level</label>
                  <div className={`flex gap-4 p-2 border rounded-xl ${inputBgMutedClass}`}>
                    {ATTAINMENT_LEVELS.map((level) => (
                      <label key={level.value} className="flex items-center gap-1.5 text-sm cursor-pointer">
                        <input
                          type="radio"
                          name="attainmentLevel"
                          value={level.value}
                          checked={attainmentLevel === level.value}
                          onChange={(e) => setAttainmentLevel(e.target.value)}
                        />
                        <span className={textClass}>{level.label}</span>
                      </label>
                    ))}
                    {attainmentLevel && (
                      <button
                        onClick={() => setAttainmentLevel("")}
                        className={`text-xs ${textMutedClass} hover:text-red-600 ml-auto`}
                      >
                        Clear
                      </button>
                    )}
                  </div>
                  <p className={`mt-1 text-xs ${textMutedSmClass}`}>
                    Select attainment level to tailor content difficulty.
                  </p>
                </div>

                <div>
                  <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Examination Board</label>
                  <div className={`flex flex-wrap gap-3 p-2 border rounded-xl ${inputBgMutedClass}`}>
                    {EXAM_BOARDS.map((board) => (
                      <label key={board.value} className="flex items-center gap-1.5 text-sm cursor-pointer">
                        <input
                          type="radio"
                          name="examBoard"
                          value={board.value}
                          checked={examBoard === board.value}
                          onChange={(e) => setExamBoard(e.target.value)}
                        />
                        <span className={textClass}>{board.label}</span>
                      </label>
                    ))}
                    {examBoard && (
                      <button
                        onClick={() => setExamBoard("")}
                        className={`text-xs ${textMutedClass} hover:text-red-600 ml-auto`}
                      >
                        Clear
                      </button>
                    )}
                  </div>
                  <p className={`mt-1 text-xs ${textMutedSmClass}`}>
                    Align content with exam board specifications.
                  </p>
                </div>
              </div>

              {/* EAL / Bell Foundation Section */}
              <div className={`p-3 border rounded-xl ${inputBgMutedClass}`}>
                <div className="grid md:grid-cols-2 gap-3">
                  <div>
                    <label className={`block text-sm font-semibold mb-1 ${textClass}`}>
                      EAL Proficiency (Bell Foundation)
                    </label>
                    <select
                      className={`w-full p-2 border rounded-xl text-sm ${inputBgClass}`}
                      value={ealBand}
                      onChange={(e) => {
                        setEalBand(e.target.value);
                        if (!e.target.value) setMotherTongue("");
                      }}
                    >
                      <option value="">Not applicable</option>
                      {EAL_BANDS.map((band) => (
                        <option key={band.value} value={band.value}>{band.label}</option>
                      ))}
                    </select>
                    <p className={`mt-1 text-xs ${textMutedSmClass}`}>
                      For multilingual learners - select EAL proficiency band.
                    </p>
                  </div>

                  <div>
                    <label className={`block text-sm font-semibold mb-1 ${textClass}`}>
                      Mother Tongue {ealBand && <span className="text-red-500">*</span>}
                    </label>
                    <select
                      className={`w-full p-2 border rounded-xl text-sm ${inputBgClass} ${!ealBand ? 'opacity-50' : ''}`}
                      value={motherTongue}
                      onChange={(e) => setMotherTongue(e.target.value)}
                      disabled={!ealBand}
                    >
                      <option value="">Select mother tongue...</option>
                      {MOTHER_TONGUES.map((tongue) => (
                        <option key={tongue.value} value={tongue.value}>{tongue.label}</option>
                      ))}
                    </select>
                    <p className={`mt-1 text-xs ${textMutedSmClass}`}>
                      {ealBand ? "Required when EAL band is selected." : "Select EAL band first."}
                    </p>
                  </div>
                </div>
                {ealBand && !motherTongue && (
                  <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
                    Please select a mother tongue to include EAL support in the prompt.
                  </p>
                )}
              </div>

              <div>
                <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Lesson Objectives</label>
                <textarea
                  className={`w-full p-2 border rounded-xl text-sm min-h-[70px] ${inputBgClass}`}
                  placeholder="e.g. Students will be able to explain..., label..., solve..., using key vocabulary."
                  value={lessonObjectives}
                  onChange={(e) => setLessonObjectives(e.target.value)}
                />
              </div>

              {/* Reading Level & Language */}
              <div className="grid md:grid-cols-2 gap-3">
                <div>
                  <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Reading Level</label>
                  <select
                    className={`w-full p-2 border rounded-xl text-sm ${inputBgClass}`}
                    value={readingLevel}
                    onChange={(e) => setReadingLevel(e.target.value)}
                  >
                    {READING_LEVELS.map((level) => (
                      <option key={level.value} value={level.value}>{level.label}</option>
                    ))}
                  </select>
                  <p className={`mt-1 text-xs ${textMutedSmClass}`}>
                    Adjust vocabulary and sentence complexity.
                  </p>
                </div>

                <div>
                  <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Language / Translation</label>
                  <select
                    className={`w-full p-2 border rounded-xl text-sm ${inputBgClass}`}
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                  >
                    {LANGUAGES.map((lang) => (
                      <option key={lang.value} value={lang.value}>{lang.label}</option>
                    ))}
                  </select>
                  <p className={`mt-1 text-xs ${textMutedSmClass}`}>
                    Translate output to another language or use simplified English for EAL students.
                  </p>
                </div>
              </div>

              {/* Question Types */}
              <div>
                <h3 className={`text-sm font-semibold mb-1 ${textClass}`}>Question Types</h3>
                <p className={`text-xs ${textMutedSmClass} mb-2`}>
                  Select which question formats to include in worksheets or assessments.
                </p>
                <div className={`flex flex-wrap gap-2 p-2 border rounded-xl ${inputBgMutedClass}`}>
                  {QUESTION_TYPES.map((qt) => (
                    <label key={qt.id} className="flex items-center gap-1.5 text-xs cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedQuestionTypes.includes(qt.id)}
                        onChange={() => toggleQuestionType(qt.id)}
                        className="rounded"
                      />
                      <span className={textClass}>{qt.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {!resource && (
                <div className="grid md:grid-cols-2 gap-3">
                  <div>
                    <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Topic</label>
                    <input
                      className={`w-full p-2 border rounded-xl text-sm ${inputBgClass}`}
                      type="text"
                      placeholder="e.g. The Black Plague, The Great Gatsby, Fractions"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                    />
                  </div>

                  <div>
                    <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Output Format</label>
                    <select
                      className={`w-full p-2 border rounded-xl text-sm ${inputBgClass}`}
                      value={format}
                      onChange={(e) => setFormat(e.target.value)}
                    >
                      <option value="">Select format...</option>
                      <option value="worksheet">Worksheet</option>
                      <option value="revision questions">Revision Questions</option>
                      <option value="summary">Summary</option>
                      <option value="simplified PowerPoint text">Simplified PowerPoint text</option>
                      <option value="PowerPoint">PowerPoint</option>
                      <option value="PDF">PDF</option>
                      <option value="flashcards">Flashcards</option>
                    </select>
                  </div>
                </div>
              )}

              <div>
                <label className={`block text-sm font-semibold mb-1 ${textClass}`}>Upload Resource (optional)</label>
                <input
                  className={`w-full p-2 border rounded-xl text-sm ${inputBgMutedClass}`}
                  type="file"
                  onChange={(e) => setResource(e.target.files?.[0] || null)}
                />
                {resource && (
                  <div className={`mt-2 flex items-center gap-2 text-xs ${textMutedClass}`}>
                    <span className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-2 py-1 rounded">
                      📎 {resource.name}
                    </span>
                    <button
                      onClick={() => {
                        setResource(null);
                        const fileInput = document.querySelector('input[type="file"]');
                        if (fileInput) fileInput.value = "";
                      }}
                      className="text-red-500 hover:text-red-700"
                    >
                      Remove
                    </button>
                  </div>
                )}
                <p className={`mt-1 text-xs ${textMutedSmClass}`}>
                  Upload a test, worksheet, PowerPoint or PDF if you want the AI to adapt that specific file.
                  If you leave this blank, it will generate content based on the topic and format instead.
                </p>
              </div>

              <div>
                <h3 className={`text-sm font-semibold mb-1 ${textClass}`}>Adaptations</h3>
                <p className={`text-xs ${textMutedSmClass} mb-2`}>
                  These are the scaffolds you want the AI to build into the resource. Condition profiles
                  set sensible defaults, but you can customise.
                </p>
                <div className={`grid md:grid-cols-2 gap-2 max-h-60 overflow-y-auto border rounded-xl p-2 ${inputBgMutedClass}`}>
                  {ADAPTATIONS.map((item) => (
                    <label key={item.id} className={`flex items-start gap-2 text-xs cursor-pointer ${textClass}`}>
                      <input
                        type="checkbox"
                        className="mt-1"
                        checked={selectedAdaptations.includes(item.id)}
                        onChange={() => toggleAdaptation(item.id)}
                      />
                      <span>{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex flex-wrap gap-3 pt-2">
                <button
                  onClick={generatePrompt}
                  disabled={isGenerateDisabled()}
                  className={
                    "px-4 py-2 rounded-xl text-sm font-semibold text-white " +
                    (isGenerateDisabled()
                      ? "bg-slate-400 cursor-not-allowed"
                      : "bg-slate-900 hover:bg-slate-950 dark:bg-slate-600 dark:hover:bg-slate-500")
                  }
                >
                  Generate Prompt
                </button>

                <button
                  onClick={generateAndRunWithGemini}
                  disabled={isGenerateDisabled() || isLoading}
                  className={
                    "px-4 py-2 rounded-xl text-sm font-semibold text-white " +
                    (isGenerateDisabled() || isLoading
                      ? "bg-emerald-400 cursor-not-allowed"
                      : "bg-emerald-600 hover:bg-emerald-700")
                  }
                >
                  {isLoading ? "Generating..." : "Generate with Claude AI"}
                </button>

                {prompt && (
                  <>
                    <button
                      onClick={() => downloadPrompt(false)}
                      className={`px-4 py-2 rounded-xl text-sm font-semibold border ${borderClass} ${textClass} hover:bg-slate-100 dark:hover:bg-slate-700`}
                    >
                      Download (.txt)
                    </button>
                    <button
                      onClick={() => downloadPrompt(true)}
                      className={`px-4 py-2 rounded-xl text-sm font-semibold border ${borderClass} ${textClass} hover:bg-slate-100 dark:hover:bg-slate-700`}
                    >
                      Download (.json)
                    </button>
                    <button
                      onClick={() => copyToClipboard(prompt)}
                      className={`px-4 py-2 rounded-xl text-sm font-semibold border ${borderClass} ${textClass} hover:bg-slate-100 dark:hover:bg-slate-700`}
                    >
                      Copy to clipboard
                    </button>
                  </>
                )}
              </div>
            </div>
          </section>

          {/* Right: Rules + prompt preview */}
          <section className="space-y-4">
            <div className={`${cardClass} rounded-2xl shadow-md p-4`}>
              <h2 className={`text-md font-semibold mb-2 ${textClass}`}>
                Rules / constraints
                {format && <span className={`text-xs font-normal ${textMutedClass}`}> ({format})</span>}
              </h2>
              <ul className={`list-disc list-inside text-xs ${textMutedClass} space-y-1`}>
                <li>Language: literal, clear, concise</li>
                <li>Readability: chunked, well-spaced</li>
                <li>Keep factual accuracy</li>
                <li>Use supportive tone</li>
                <li>Avoid oversimplification of key concepts</li>
                <li>Maintain assessment objectives if present</li>
              </ul>
              {format && FORMAT_RULES[format] && (
                <>
                  <h3 className={`text-sm font-semibold mt-3 mb-1 ${textClass}`}>Format-specific:</h3>
                  <ul className={`list-disc list-inside text-xs ${textMutedClass} space-y-1`}>
                    {FORMAT_RULES[format].map((rule, idx) => (
                      <li key={idx}>{rule}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>

            <div className={`${cardClass} rounded-2xl shadow-md p-4 space-y-2`}>
              <div className="flex justify-between items-center">
                <h2 className={`text-md font-semibold ${textClass}`}>Generated prompt</h2>
                {prompt && (
                  <button
                    onClick={() => copyToClipboard(prompt)}
                    className={`px-3 py-1 rounded-lg text-[11px] font-semibold border ${borderClass} ${textClass} hover:bg-slate-100 dark:hover:bg-slate-700`}
                  >
                    Copy
                  </button>
                )}
              </div>
              <textarea
                className={`w-full min-h-[220px] p-2 border rounded-xl text-[11px] font-mono ${inputBgMutedClass} ${textClass}`}
                placeholder="Your prompt will appear here after you click 'Generate Prompt'."
                value={prompt}
                readOnly
              />
            </div>
          </section>
        </main>

        {/* AI Response Section */}
        {(aiResponse || aiError || isLoading) && (
          <div className={`${cardClass} rounded-2xl shadow-md p-4 space-y-3`}>
            <div className="flex justify-between items-center">
              <h2 className={`text-lg font-semibold ${textClass}`}>
                AI Response
                <span className={`text-xs font-normal ${textMutedClass} ml-2`}>
                  (Claude Haiku)
                </span>
              </h2>
              {aiResponse && (
                <div className="flex gap-2">
                  <button
                    onClick={downloadAsPdf}
                    disabled={isGeneratingPdf}
                    className={`px-3 py-1 rounded-lg text-[11px] font-semibold text-white ${isGeneratingPdf ? "bg-emerald-400" : "bg-emerald-600 hover:bg-emerald-700"}`}
                  >
                    {isGeneratingPdf ? "Generating PDF..." : "Download PDF"}
                  </button>
                  <button
                    onClick={downloadAsPptx}
                    disabled={isGeneratingPptx}
                    className={`px-3 py-1 rounded-lg text-[11px] font-semibold text-white ${isGeneratingPptx ? "bg-orange-400" : "bg-orange-600 hover:bg-orange-700"}`}
                  >
                    {isGeneratingPptx ? "Generating PPTX..." : "Download PowerPoint"}
                  </button>
                  <button
                    onClick={() => copyToClipboard(aiResponse)}
                    className={`px-3 py-1 rounded-lg text-[11px] font-semibold border ${borderClass} ${textClass} hover:bg-slate-100 dark:hover:bg-slate-700`}
                  >
                    Copy
                  </button>
                  <button
                    onClick={() => {
                      setAiResponse("");
                      setAiError("");
                    }}
                    className={`px-3 py-1 rounded-lg text-[11px] font-semibold text-red-600 border ${borderClass} hover:bg-red-50 dark:hover:bg-red-900/20`}
                  >
                    Clear
                  </button>
                </div>
              )}
            </div>

            {aiError && (
              <div className="p-3 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-xl">
                <p className="text-sm text-red-700 dark:text-red-300">{aiError}</p>
              </div>
            )}

            {isLoading && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className={`ml-3 ${textMutedClass}`}>Generating response...</span>
              </div>
            )}

            {aiResponse && (
              <div ref={aiResponseRef} className={`p-4 border rounded-xl ${inputBgMutedClass} overflow-auto max-h-[500px]`}>
                <div className={`text-sm font-sans ${textClass}`}>{renderAiResponse(aiResponse)}</div>
              </div>
            )}
          </div>
        )}

        <footer className={`text-center text-xs ${textMutedSmClass} pb-4`}>
          <p>Built for educators supporting neuro-divergent learners</p>
        </footer>
      </div>
    </div>
  );
}
