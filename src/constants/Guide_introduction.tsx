export const Generation_Items: { id: string; title: string; content: React.ReactNode }[] = [
   {
      id: "source",
      title: "Intelligent Source Discovery",
      content: (
        <p className="text-sm leading-relaxed text-muted-foreground">
          Provide a topic, a URL, or an image — the system automatically retrieves authentic materials: searching real news via the News API, scraping headlines and key paragraphs from links, or summarizing images through a vision model to establish a grounded topic.
        </p>
      ),
    },
    {
      id: "style",
      title: "Style- and Domain-Aware Writing",
      content: (
        <p className="text-sm leading-relaxed text-muted-foreground">
          Users can define tone (Formal, Sensational, Fun, or Normal) and domain (Politics, Business, Sports, Technology, or General). The generator adapts vocabulary, cadence, and structure accordingly while preserving the integrity of journalistic composition—headline, lead, body, and quotations.
        </p>
      ),
    },
    {
      id: "logic",
      title: "Logic-First Fabrication",
      content: (
        <p className="text-sm leading-relaxed text-muted-foreground">
          Generated content is intentionally altered relative to authentic sources yet remains logically coherent. A built-in validation checklist maintains narrative consistency, causal flow, and alignment of quoted material.
        </p>
      ),
    },
    {
      id: "trace",
      title: "Traceable by Design",
      content: (
        <p className="text-sm leading-relaxed text-muted-foreground">
          Each article concludes with “Original report: &lt;URL&gt;.” The referenced link is presented in a dedicated verification box, ensuring transparency and facilitating rapid source auditing.
        </p>
      ),
    },
    {
      id: "models",
      title: "Models Under the Hood",
      content: (
        <ul className="list-disc pl-5 space-y-1 text-sm leading-relaxed text-muted-foreground">
          <li>
            <b>Core Text Model (GPT‑4o):</b> Oversees reasoning, stylistic modulation, and narrative structure through layered prompt design and balanced generation parameters.
          </li>
          <li>
            <b>Vision Captioning (Optional):</b> Uploaded images are summarized into concise, news-style captions that serve as contextual seeds for topic generation.
          </li>
          <li>
            <b>Real‑Source Grounding:</b> Integrates genuine headlines and introductory paragraphs fetched via News API, then generates intentionally modified yet credible narratives for controlled research purposes.
          </li>
        </ul>
    ),
    },
    {
      id: "real",
      title: "Why It Feels “Real”",
      content: (
        <p className="text-sm leading-relaxed text-muted-foreground">
          Built upon journalistic scaffolding—headline → lead → body → quotes → transitions—the generator employs domain‑specific vocabulary, consistent sentence rhythm, and natural quote pacing to achieve authentic readability.
        </p>
      ),
    },
    {
      id: "responsible",
      title: "Responsible Use",
      content: (
        <p className="text-sm leading-relaxed text-muted-foreground">
          Designed exclusively for research, evaluation, and robustness testing. Every output includes the corresponding original source link to enable verification and uphold ethical transparency. The system must not be used for real-world misinformation or publication.
        </p>
      ),
    },
  ];

export const Detection_Items = [
  {
    id: "architecture",
    title: "Multi-Layered Detection Architecture",
    content:
      "The detection framework employs a multi-layered architecture that integrates advanced machine learning models with real-time fact-verification capabilities. Each analytical layer examines a distinct dimension of the input text—including stylistic integrity, logical soundness, and factual validity—to deliver a comprehensive and evidence-based authenticity assessment.",
  },
  {
    id: "model-suite",
    title: "Integrated Model Suite for Text Analysis",
    content:
      "The analytical engine combines multiple complementary detectors: a RoBERTa-based classifier for contextual semantics and stylistic profiling; GPT-4 linguistic analysis (DetectGPT) for identifying model-like phrasing and coherence deviations; zero-shot classification for cross-domain adaptability; and GLTR statistical modeling for improbable token detection. This combination ensures coverage across writing patterns, linguistic anomalies, and reasoning inconsistencies.",
  },
  {
    id: "ensemble",
    title: "Ensemble Fusion and Confidence Calibration",
    content:
      "Outputs from all underlying detectors are aggregated using a Random Forest ensemble. The ensemble fusion process harmonizes heterogeneous signals, generating a unified verdict accompanied by calibrated confidence metrics that enhance robustness and interpretability.",
  },
  {
    id: "fact-verification",
    title: "Real-Time Fact Verification Layer",
    content:
      "To ensure factual grounding, the system leverages the Tavily API to validate extracted entities and key claims against authoritative online sources. Named entities and statements are programmatically cross-referenced with credible repositories, enabling continuous real-time verification within the detection workflow.",
  },
  {
    id: "explanation",
    title: "Transparent and Interpretable Explanations",
    content:
      "Each system verdict is accompanied by structured interpretability outputs—highlighted suspicious segments, assessments of source credibility, indicators of linguistic manipulation, and evaluations of logical coherence. This transparency enables users to understand not only the outcome of the classification but the reasoning behind it.",
  },
  {
    id: "entity-extraction",
    title: "Entity Extraction and Query Optimization",
    content:
      "The pipeline extracts named entities and critical keywords using spaCy NER and NLTK, constructing optimized queries that balance recall and precision. Query generation employs adaptive weighting and balanced Boolean logic to ensure efficient retrieval without over-restriction.",
  },
  {
    id: "news-ranking",
    title: "News Retrieval and Relevance Ranking",
    content:
      "Verified queries are submitted to Google News via SerpAPI. Candidate articles are evaluated through a hybrid ranking algorithm combining exact-term matching using regular expressions with semantic similarity scoring based on TF-IDF cosine distance. This dual-metric approach favors content that aligns both textually and semantically with the analyzed material.",
  },
  {
    id: "thresholds",
    title: "Relevance Thresholds and Output Policy",
    content:
      "Only results achieving a composite relevance score of eight or higher are returned. This policy ensures that users receive authentic, contextually pertinent information directly corresponding to the analyzed text, minimizing exposure to generic or irrelevant content.",
  },
];
