DOCS_SECTIONS = {
    "library": [
        {
            "name": "API Reference",
            "description": "Generate a complete list of all publicly exported functions, classes, and constants "
            "from the library\n"
            "For each item, include:\n"
            "- Its name\n"
            "- Description of what it does\n"
            "- Function signature with types and descriptions of parameters and return values\n"
            "- Example usage\n"
            "Do not omit any significant exports — include everything that would be relevant to a developer using "
            "this library\n"
            "Group related items (e.g., utility functions, configuration, components) under subsections if helpful\n",
        },
    ],
    "web_app": [
        {
            "name": "Deployment",
            "description": "Describe how to build and deploy the application to production\n"
            "Include relevant deployment commands and target platforms (e.g., Vercel, Netlify, Docker)\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List the main frameworks, libraries, and tools (e.g., React, Vue, Vite, Tailwind)\n\n",
        },
        {
            "name": "Feature Highlights",
            "description": "Describe core user-facing features or flows "
            "(e.g., authentication, dashboards, routing)\n\n",
        },
        {
            "name": "Configuration",
            "description": "Mention any configurable options, build settings, or plugins used\n\n",
        },
    ],
    "api_service": [
        {
            "name": "API Documentation",
            "description": "List the available endpoints or routes\n"
            "For each endpoint, include:\n"
            "Method (GET, POST, etc.)\n"
            "Path and parameters\n"
            "Example request and response\n"
            "Authentication requirements (if any)\n"
            "If an OpenAPI/Swagger spec or GraphQL schema exists, link to it\n\n",
        },
        {
            "name": "Authentication",
            "description": "Describe how authentication works (e.g., API keys, OAuth, JWT)\n"
            "Include example headers or auth flow steps if needed\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List major frameworks, libraries, or tools (e.g., Express, FastAPI, Prisma)\n\n",
        },
        {
            "name": "Deployment",
            "description": "Describe how to deploy the service (e.g., Docker, CI/CD, cloud platforms)\n"
            "Include environment config or scaling considerations if relevant\n\n",
        },
    ],
    "mobile_app": [
        {
            "name": "Supported Platforms",
            "description": "Indicate whether the app runs on Android, iOS, or both\n"
            "Mention any platform-specific dependencies or limitations\n\n",
        },
        {
            "name": "Running the App",
            "description": "Show commands to run the app on a simulator/emulator or real device\n"
            "Include platform-specific commands if needed (e.g., `npx react-native run-ios`, `flutter run`)\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List the frameworks, SDKs, and libraries used (e.g., React Native, Flutter, Firebase)\n\n",
        },
        {
            "name": "Key Screens and Features",
            "description": "Highlight core screens or flows within the app (e.g., login, profile, dashboard)\n"
            "Optionally include screenshots or descriptions of user interactions\n\n",
        },
        {
            "name": "Build and Deployment",
            "description": "Provide steps for creating production builds\n"
            "Mention any tools or services used for distribution (e.g., TestFlight, Play Store, Expo)\n\n",
        },
    ],
    "tutorial": [
        {
            "name": "Tutorial Structure",
            "description": "Break down the tutorial into sections, stages, or lessons\n"
            "Briefly describe what each section teaches or builds\n"
            "Link to key files or folders associated with each part\n\n",
        },
        {
            "name": "Learning Outcomes",
            "description": "Clearly list the skills or concepts users will have mastered by the end\n\n",
        },
        {
            "name": "Code Examples and Exercises",
            "description": "Mention inline code snippets, checkpoints, or interactive examples\n"
            "If exercises are included, describe how users should complete or test them\n\n",
        },
        {
            "name": "Next Steps / Further Reading",
            "description": "Suggest where users can go after completing the tutorial\n"
            "Include links to additional docs, libraries, or related tutorials\n\n",
        },
    ],
    "template": (
        {
            "name": "Customization Guide",
            "description": "Explain which parts of the codebase are intended to be modified by users\n"
            "Offer guidance on how to rename, rebrand, or restructure parts of the template\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List the frameworks, libraries, and tools integrated into the template "
            "(e.g., ESLint, Prettier, Tailwind, Express)\n\n",
        },
        {
            "name": "Use Cases",
            "description": "Provide example scenarios where this template is useful "
            "(e.g., 'Use this for building a REST API with authentication')\n"
            "Link to live demos or projects built from this template if available\n\n",
        },
        {
            "name": "Contributing",
            "description": "If the template is open to contributions, provide basic instructions for "
            "submitting improvements\n\n",
        },
    ),
    "cli_tool": [
        {
            "name": "Usage",
            "description": "Show how to use the tool from the command line\n"
            "Include at least 2–3 example commands with explanations of the output\n"
            "Demonstrate the most common and useful flags or options\n"
            "If the tool supports subcommands, show examples of each\n\n",
        },
        {
            "name": "Command Reference",
            "description": "List all available commands, flags, and options in a table or list format\n"
            "Explain each option clearly, including defaults and accepted values\n\n",
        },
        {
            "name": "Configuration",
            "description": "Describe any optional or required configuration files (e.g., `.clirc`, `config.json`)\n"
            "Show example configurations and where to place them\n\n",
        },
        {
            "name": "Contributing",
            "description": "Outline how to contribute, test changes, or add new commands\n\n",
        },
    ],
    "framework": [
        {
            "name": "Core Concepts",
            "description": "Explain the main components or building blocks "
            "(e.g., modules, services, lifecycle, routing, etc.)\n"
            "Include diagrams or conceptual overviews if helpful\n\n",
        },
        {
            "name": "Extension Points",
            "description": "Describe how developers can extend the framework "
            "(e.g., plugins, middleware, custom components)\n"
            "Include examples of common extension use cases\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List core dependencies, supported environments, or language-level features leveraged\n\n",
        },
        {
            "name": "Best Practices",
            "description": "Offer guidance for structuring large projects, writing maintainable code, or "
            "following framework conventions\n\n",
        },
    ],
    "data_science": [
        {
            "name": "Dataset",
            "description": "Describe the dataset used (source, size, structure)\n"
            "Include schema information or link to external data sources\n\n",
        },
        {
            "name": "Model Architecture and Training",
            "description": "Briefly describe the model(s) used and why they were chosen\n"
            "Include training scripts and command-line instructions\n\n",
        },
        {
            "name": "Evaluation and Results",
            "description": "Summarize how the model was evaluated and key performance metrics\n"
            "   - Include training scripts and command-line instructions\n"
            "   - Mention metrics used for evaluation\n\n",
        },
        {
            "name": "Inference / How to Use the Model",
            "description": "Explain how to run inference or apply the model to new data\n"
            "Include input/output formats and example commands or code\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List key tools, libraries, and frameworks (e.g., scikit-learn, TensorFlow, pandas)\n\n",
        },
    ],
    "plugin": [
        {
            "name": "Usage",
            "description": "Show how to enable and configure the plugin\n"
            "Include code snippets or configuration steps\n\n",
        },
        {
            "name": "Integration Points",
            "description": "Describe hooks, lifecycle methods, or extension APIs the plugin interacts with\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List frameworks, languages, or tooling\n\n",
        },
    ],
    "chrome_extension": [
        {
            "name": "Usage",
            "description": "Explain how users interact with the extension "
            "(e.g., popup UI, context menu, background scripts)\n"
            "Include example scenarios or screenshots if applicable\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List libraries or frameworks (e.g., vanilla JS, React, Tailwind)\n\n",
        },
    ],
    "jupyter_notebook": [
        {
            "name": "Notebook Summary",
            "description": "List and briefly describe each notebook in the repo\n"
            "Mention whether they build on each other or are standalone\n\n",
        },
        {
            "name": "Dataset (if applicable)",
            "description": "Describe any datasets used and where they come from\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List libraries (e.g., pandas, matplotlib, scikit-learn)\n\n",
        },
    ],
    "infrastructure": [
        {
            "name": "Configuration Files",
            "description": "Explain the structure and purpose of major files (e.g., `main.tf`, `docker-compose.yml`, "
            "`playbooks/`)\n\n",
        },
        {
            "name": "Deployment Workflow",
            "description": "Describe how deployments are triggered and verified\n"
            "Mention any CI/CD pipelines, remote state management, or secrets handling\n\n",
        },
        {
            "name": "Environments",
            "description": "Clarify how to deploy to multiple environments (dev, staging, prod)\n\n",
        },
    ],
    "smart_contract": [
        {
            "name": "Contracts",
            "description": "Describe the main contract(s) and what each one does\n"
            "Include deployment steps and how to interact with them\n\n",
        },
        {
            "name": "Testing",
            "description": "Explain how to run tests and what framework is used\n\n",
        },
    ],
    "dapp": [
        {
            "name": "Architecture",
            "description": "Provide a high-level diagram or explanation of how the frontend "
            "interacts with smart contracts\n"
            "Mention key technologies used on both sides (e.g., React, Ethers.js, Anchor, Web3.js)\n\n",
        },
        {
            "name": "Smart Contracts",
            "description": "Describe the deployed contracts and how to interact with them\n"
            "Include deployment instructions and test commands\n\n",
        },
        {
            "name": "Frontend",
            "description": "Describe key UI components and user flows (e.g., connect wallet, mint token, submit vote)\n"
            "Mention any integrations with IPFS, oracles, or off-chain data\n\n",
        },
    ],
    "game": [
        {
            "name": "Controls and Gameplay",
            "description": "Explain player controls and core mechanics\n"
            "Optionally include screenshots, video, or demo links\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List engines, frameworks, or libraries used to build the game\n\n",
        },
    ],
    "desktop_app": [
        {
            "name": "Usage",
            "description": "Describe the app's main features and user workflows\n"
            "Include screenshots if applicable\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List major libraries, frameworks, and build tools\n\n",
        },
    ],
    "dataset": [
        {
            "name": "Dataset Details",
            "description": "Describe the structure and format (e.g., CSV, JSON, images, text)\n"
            "Include column definitions, schema, or data dictionaries\n"
            "Mention the number of records, size, and any notable characteristics\n\n",
        },
        {
            "name": "Usage Instructions",
            "description": "Provide example code snippets for loading and using the dataset (e.g., pandas, SQL, etc.)\n"
            "Mention any preprocessing steps if needed\n\n",
        },
        {
            "name": "Related Work / Source Links",
            "description": "Link to original data sources, research papers, or related projects (if applicable)\n\n",
        },
    ],
    "other": [
        {
            "name": "Features / Capabilities",
            "description": "List the core features or components of the project\n"
            "Include relevant examples, demos, or configurations if applicable\n\n",
        },
        {
            "name": "Technologies Used",
            "description": "List any major frameworks, libraries, or languages identified in the project\n\n",
        },
        {
            "name": "Usage Examples",
            "description": "Include example commands or steps showing how to use the project\n\n",
        },
    ],
}

INITIAL_SECTIONS = [
    {
        "name": "Project Overview",
        "description": "A concise description of what the codebase does\n"
        "- Its main purpose and the problems it solves\n"
        "- Key features and benefits\n\n",
    },
    {
        "name": "Getting Started, Installation, and Setup",
        "description": "Include a quick start guide with usage instructions. Leave detailed installation instructions "
        "to the Installation and Setup section.\n\n"
        "Provide all necessary instruction to install and use the project, including dependencies and "
        "platform-specific instructions (if applicable)\n"
        "Include steps for both running the app in development and building a production release (if applicable)\n\n",
    },
]

FINAL_SECTIONS = [
    {
        "name": "Project Structure",
        "description": "Briefly explain the purpose of key directories and files\n\n",
    },
    {
        "name": "Additional Notes",
        "description": "Focus on making the README useful and descriptive, "
        "even if the project type is ambiguous\n"
        "- Use best judgment to tailor the content to the actual "
        "functionality and audience of the project\n"
        "- Avoid placeholder text and strive to extract real, useful information from the codebase",
    },
    {
        "name": "Contributing",
        "description": "Include basic instructions for how others can contribute\n"
        "- Mention any specific guidelines or requirements for contributions (e.g. code style, testing, etc.)\n\n",
    },
    {
        "name": "License",
        "description": "State the type of license and include a link to the license file\n\n"
        "If no license is mentioned, state that the code is unlicensed and explain the implications.",
    },
]
