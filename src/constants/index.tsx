import About from "../pages/About";
import Detection from "../pages/Detection";
import Generate from "../pages/Generate";
import Home from "../pages/Home";


export const NavRoutes = [
  { path: "/", element: <Home /> },
  { path: "/detection", element: <Detection /> },
  { path: "/generate", element: <Generate /> },
  { path: "/about", element: <About /> },
];

export const navItems = [
  { path: "/detection", label: "Detection" },
  { path: "/generate", label: "Generation" },
  { path: "/about", label: "About Us" },
];

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