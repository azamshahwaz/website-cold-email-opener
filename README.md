# 🌐 Website to AI Cold Email Opener

> Generate personalized, website-grounded **3-line cold email openers** for founder outreach using AI.

A simple AI-powered tool that analyzes a company's website and generates a personalized cold email opener based on the actual content of the website.

The application uses **Google Gemini** to generate exactly three lines:

1. 🏢 What the company does
2. 🔍 A specific observation based on its website
3. 💬 A natural conversation starter for the founder

It generates **only the opener**, not a complete cold email, and avoids inventing information when a website cannot be successfully analyzed.

---

## ✨ Features

- 🌐 **Website URL Input** — Enter a company website with or without `https://`
- 🔍 **Website Content Extraction** — Extracts meaningful information from company websites
- 🤖 **AI-Powered Generation** — Uses Google Gemini to generate personalized openers
- 📝 **Exactly 3 Lines** — Strictly validates the generated output
- 🎯 **Website-Grounded Personalization** — Generates openers based on actual website content
- 🔄 **Generate Again** — Generate a fresh variation for the same company
- 📋 **Copy Opener** — Copy the generated opener with one click
- 🧹 **Clear** — Reset the application and start again
- 📊 **Token Usage Tracking** — Displays input and output tokens
- 💰 **Cost Tracking** — Estimates API cost per generation
- ⏱️ **Response Time Tracking** — Displays generation latency
- 📄 **Company Information** — Displays extracted company description and website summary
- 🛡️ **SSRF Protection** — Validates URLs and prevents requests to private/internal addresses
- 🔒 **Prompt Injection Protection** — Treats website content as untrusted data
- ⚡ **Caching** — Avoids unnecessary repeated website extraction
- 🔁 **Retry Mechanism** — Handles transient API and network failures
- 🧪 **Automated Tests** — Tests application logic using mocked HTTP and AI responses
- 🎭 **Demo Mode** — Allows the application to run without an API key using clearly labelled fictional examples

---

## 🖥️ Application Workflow

```text
Enter Company Website URL
          │
          ▼
     URL Validation
          │
          ▼
   Website Fetching
          │
          ▼
  Content Extraction
          │
          ▼
   AI Opener Generation
          │
          ▼
   Output Validation
          │
          ▼
   Display 3-Line Opener
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web application UI |
| Google Gemini API | AI-powered opener generation |
| Google Gen AI SDK | Gemini API integration |
| Requests | Website fetching |
| BeautifulSoup4 | HTML parsing |
| Trafilatura | Main content extraction |
| python-dotenv | Environment variable management |
| Pytest | Automated testing |

---

## 📁 Project Structure

```text
website-cold-email-opener/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   └── custom.css
│
├── modules/
│   ├── website_extractor.py
│   ├── ai_generator.py
│   ├── validator.py
│   ├── security.py
│   ├── pipeline.py
│   ├── demo.py
│   ├── errors.py
│   └── utils.py
│
└── tests/
    └── ...
```

### 📦 Module Responsibilities

| Module | Responsibility |
|---|---|
| `app.py` | Streamlit UI and application flow |
| `config.py` | Configuration and environment variables |
| `website_extractor.py` | Website fetching and content extraction |
| `ai_generator.py` | Gemini prompt and AI generation |
| `validator.py` | Output cleaning and 3-line validation |
| `security.py` | URL validation and SSRF protection |
| `pipeline.py` | End-to-end processing pipeline |
| `demo.py` | Demo mode with fictional sample companies |
| `errors.py` | User-friendly application errors |
| `utils.py` | Caching, token tracking, cost calculations, and utilities |

---

## 🚀 Getting Started

### 📋 Prerequisites

- Python **3.11 or newer**
- Google Gemini API key
- Git

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/website-cold-email-opener.git
```

Navigate to the project directory:

```bash
cd website-cold-email-opener
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
```

### 3️⃣ Activate the Virtual Environment

#### Windows

```powershell
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 API Key Configuration

### 1. Get a Gemini API Key

Create an API key from Google AI Studio:

🔗 https://aistudio.google.com/apikey

### 2. Create a `.env` File

Copy `.env.example` to `.env`.

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.1-flash-lite

MAX_CONTENT_CHARS=6000
REQUEST_TIMEOUT_SECONDS=10
CACHE_TTL_SECONDS=3600
MAX_RETRIES=2

PRICE_INPUT_PER_1M_USD=0.25
PRICE_OUTPUT_PER_1M_USD=1.50
```

The application reads configuration from environment variables.

> 🔐 Never commit your `.env` file or API key to GitHub.

The `.env` file is included in `.gitignore`.

---

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will usually be available at:

```text
http://localhost:8501
```

---

## 📖 How to Use

### Step 1: Enter a Website

Enter a company website URL.

Examples:

```text
https://stripe.com
https://linear.app
https://hubspot.com
```

The application also supports URLs without a protocol:

```text
stripe.com
```

### Step 2: Generate the Opener

Click **Generate Opener**.

The application performs the following operations:

1. Validates the URL.
2. Fetches the website.
3. Extracts meaningful website content.
4. Sends the extracted content to Google Gemini.
5. Validates the generated output.
6. Displays the personalized opener.

### Step 3: Review the Result

The application displays:

- 🏢 Company description
- 📄 Extracted website content summary
- ✉️ Generated three-line opener
- 📊 Input tokens
- 📊 Output tokens
- 💰 Estimated API cost
- ⏱️ Response time

### Step 4: Use the Available Actions

| Action | Description |
|---|---|
| 📋 Copy Opener | Copies the generated three-line opener |
| 🔄 Generate Again | Generates another variation |
| 🧹 Clear | Resets the application |

Always review the generated opener before using it for outreach.

---

## 🧪 Live Testing

The application was tested using real company websites and live Gemini API generation.

### 🌐 Successful Website Tests

| Website | Result |
|---|---|
| Stripe | ✅ Successfully generated opener |
| Linear | ✅ Successfully generated opener |
| HubSpot | ✅ Successfully generated opener |

### 🔍 Error Handling Tests

| Test Scenario | Result |
|---|---|
| Valid website URL | ✅ Passed |
| URL without protocol | ✅ Supported |
| Invalid URL | ✅ Validation error displayed |
| Non-existent website | ✅ Graceful error handling |
| Website content extraction | ✅ Successful |
| Live Gemini generation | ✅ Successful |
| Exactly three lines | ✅ Validated |
| Company-specific personalization | ✅ Verified |
| Generate Again | ✅ Verified |
| Copy Opener | ✅ Verified |
| Clear | ✅ Verified |
| Token tracking | ✅ Verified |
| Cost tracking | ✅ Verified |
| Response time tracking | ✅ Verified |

### ⚠️ JavaScript-Rendered Website Test

**Website tested:** Amazon India

```text
https://www.amazon.in/
```

**Result:** The application correctly identified that the website renders its content using JavaScript and that insufficient readable text was available in the fetched HTML.

Instead of generating an opener using incomplete or guessed information, the application displayed a clear error message:

> This website renders its content with JavaScript, so no readable text was found in the HTML. Try a more static page (for example `/about`).

This demonstrates the application's ability to handle websites that cannot be successfully analyzed without generating unsupported or hallucinated content.

---

## 📊 Example Output

### Example: HubSpot

**Company Description:**

HubSpot provides a CRM platform integrating marketing, sales, service, and data tools to help businesses manage customer growth.

**Generated Opener:**

> HubSpot provides a unified CRM platform that integrates marketing, sales, service, and data tools to help businesses manage customer growth.
>
> You are positioning your platform as an agentic system where AI agents work alongside human teams to handle tasks like customer inquiries and sales prospecting.
>
> When you transition core business functions to automated agents, how do you maintain the balance between operational efficiency and the human touch your brand requires?

The generated content is based on information extracted from the submitted website.

---

## 🧠 How Website Extraction Works

The application follows a secure website extraction pipeline:

1. The URL is normalized and validated.
2. The hostname is resolved.
3. Private, internal, loopback, and reserved IP addresses are rejected.
4. The website is fetched using a timeout and size limit.
5. Redirects are followed manually and validated at every step.
6. HTML content is parsed.
7. Main website content is extracted using Trafilatura.
8. BeautifulSoup provides fallback extraction.
9. Scripts, styles, navigation, footers, cookie banners, forms, and duplicate content are removed.
10. Extracted content is truncated to a configurable maximum length.

If insufficient content is available, the application displays an appropriate error instead of generating an opener from guessed information.

---

## 🤖 How AI Generation Works

The extracted website content is passed to Google Gemini with a structured prompt.

The prompt instructs the model to generate exactly three lines:

### Line 1 — Company Overview

Explain what the company does using website-grounded information.

### Line 2 — Specific Observation

Identify something specific about the company's product, positioning, technology, business model, or website.

### Line 3 — Conversation Starter

Generate a natural, relevant question that could initiate a conversation with the founder.

### Output Validation

The generated response is validated to ensure:

- Exactly three non-empty lines
- No greeting
- No email subject
- No signature
- No unnecessary numbering
- No generic clichés
- No unsupported claims
- No complete email

If the output is invalid, the application attempts one controlled regeneration.

---

## 🔐 Security Considerations

### SSRF Protection

The application includes protections against Server-Side Request Forgery:

- Rejects localhost URLs
- Rejects private IP addresses
- Rejects loopback addresses
- Rejects link-local addresses
- Rejects reserved IP addresses
- Rejects internal domain names
- Rejects URLs containing credentials
- Allows only HTTP and HTTPS
- Restricts ports to 80 and 443
- Validates redirects
- Limits response size

### Prompt Injection Protection

Website content is treated as untrusted data.

The application:

- Separates website content from system instructions
- Uses delimiters around website content
- Sanitizes control characters
- Removes delimiter-like content
- Explicitly instructs the model not to follow instructions contained within website content

### API Key Security

- API keys are stored in environment variables or Streamlit secrets.
- API keys are never hardcoded.
- API keys are never included in prompts.
- API keys are not intentionally logged.
- `.env` is excluded from Git using `.gitignore`.

### HTML Safety

All text displayed in the application is HTML-escaped.

---

## ⚠️ Limitations

- JavaScript-rendered websites may not expose sufficient content in their initial HTML.
- Some websites block automated requests.
- Only the submitted webpage is analyzed.
- Using a specific page such as `/about` may provide better results.
- Website extraction depends on the content available to the application.
- Cache data is stored in memory and resets when the application restarts.
- Output quality depends on the quality and relevance of the extracted website content.
- Generated openers should always be reviewed before sending.

---

## 🧪 Automated Testing

Run the test suite:

```bash
python -m pytest -q
```

The tests use mocked HTTP requests and mocked AI responses, so they do not require a Gemini API key or internet access.

The test suite covers:

- URL validation
- URL normalization
- SSRF protection
- Private and internal IP rejection
- Website extraction
- Redirect handling
- Timeout handling
- HTTP errors
- Invalid HTML
- Empty website content
- Content size limits
- Output validation
- Three-line formatting
- Gemini API error handling
- Retry logic
- Prompt injection protection
- Pipeline execution
- Caching
- Streamlit UI behaviour

---

## 💰 Cost Considerations

The application tracks:

- Input tokens
- Output tokens
- Estimated API cost
- Response time

Actual API costs depend on:

- Website content length
- Prompt size
- Gemini model
- Output length
- Regeneration requests
- Current API pricing

### 📊 Observed Testing Metrics

| Website | Input Tokens | Output Tokens | Estimated Cost |
|---|---:|---:|---:|
| Stripe | 2,018 | 70 | $0.000061 |
| Linear | 940 | 78 | $0.00035 |
| HubSpot | 1,639 | 81 | $0.00053 |

These values are observed application metrics during testing and may vary depending on the website content and model pricing configuration.

### Cost Estimation Formula

```text
Cost =
(Input Tokens × Input Price)
+
(Output Tokens × Output Price)
```

The application includes a configurable cost estimator.

For production usage, verify the latest Gemini API pricing:

🔗 https://ai.google.dev/gemini-api/docs/pricing

---

## ☁️ Deployment — Streamlit Community Cloud

### 1. Push the Repository to GitHub

Ensure your repository is public or accessible to Streamlit Community Cloud.

### 2. Open Streamlit Community Cloud

🔗 https://share.streamlit.io

### 3. Create a New App

Select:

- GitHub repository
- Branch: `main`
- Main file: `app.py`

### 4. Configure Secrets

Under **Advanced Settings → Secrets**, configure:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
GEMINI_MODEL = "gemini-3.1-flash-lite"
```

### 5. Deploy

Click **Deploy**.

The application can also run in Demo Mode if an API key is not configured.

---

## 🎭 Demo Mode

The application supports Demo Mode.

When no API key is configured, it can provide clearly labelled fictional examples without making AI API calls.

Demo output is explicitly labelled:

```text
DEMO OUTPUT — Not generated by a live AI model.
```

This allows users to explore the application without configuring an API key.

---

## 🔮 Future Improvements

### 🌐 Advanced Website Analysis

- **JavaScript-Rendered Website Support** — Use Playwright or a headless browser as a fallback when standard HTML extraction cannot retrieve meaningful content.
- **Multi-Page Website Analysis** — Analyze multiple relevant pages instead of only the submitted URL.
- **Automatic Page Discovery** — Automatically discover and analyze relevant pages such as `/about`, `/products`, `/services`, and `/features`.
- **Smart Page Selection** — Prioritize pages containing company information, product details, technology, business model, and positioning.
- **Fallback Extraction Pipeline** — Attempt standard HTML extraction first, followed by browser-based rendering when insufficient content is detected.

### 🎯 Personalization

- Custom outreach tone selection
- Industry-specific opener generation
- Founder-specific personalization
- Additional context input for the sender
- Custom conversation starter styles

### 📧 Outreach Features

- Full cold email generation as an optional feature
- Multiple opener variations
- Email subject line generation
- Outreach campaign management

### 💾 Application Features

- Database-backed generation history
- User authentication
- Analytics dashboard
- Usage tracking
- Export generated openers

### 🚀 Infrastructure

- Production deployment with rate limiting
- Improved caching strategy
- Background processing for website analysis
- Additional AI model support

---

## 👨‍💻 Author

Built as part of an AI-focused engineering assessment.

---

## 📄 License

This project is intended for educational and assessment purposes.
