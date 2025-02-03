# Prompt Definition Language (PDL): A Dynamic Prompting Tool

The Prompt Definition Language (PDL) is a simple, yet powerful, text-based language designed to enable the creation of *dynamic* and reusable prompts. PDL provides a set of directives that allow you to:

*   **Include external content:** Incorporate text from files or URLs.
*   **Utilize AI-generated content:** Integrate AI models to generate text, expanding your prompts on the fly.
*   **Define reusable macros:** Create named text snippets for efficient repetition and modification.
*   **Introduce randomness:** Inject variability into prompts using randomized choices.

PDL is designed to be user-friendly, with a straightforward syntax and intuitive keywords. Let's dive into the details.

## Key Features of PDL

### 1. Directives: The Building Blocks

Directives are special instructions that begin with the `#` symbol at the start of a line. They provide the logic for manipulating text and creating dynamic prompts. Directives consist of:

   *   A **keyword** which specifies the action (`#include`, `#open`, `#ask`, `#define`, `#random`)
   *   An optional **name** for the created macro, if the result of a directive is intended to be stored in the macro, and
   *   A **content** enclosed in curly braces `{}`

   For example:

   ```pdl
   #define GREETING {Hello,}

### 2. Dynamic Content Inclusion
PDL can include dynamic text from external sources using directives:

#include {file_path}: Includes the content of a local file specified by the file_path.

#open {url}: Fetches and includes the content from the specified URL.

#ask {prompt}: Sends a text-based prompt to a configured AI model (like Google's Gemini) and includes the AI-generated response.

These directives allow you to combine static text with content sourced from files, websites, or generative AI, creating much more complex and context-rich prompts on the fly.

### 3. Macros: Reusability and Customization
Macros are named text variables defined using #define:

#define PERSON_NAME {Bob}
#define FULL_GREETING {#GREETING my name is #PERSON_NAME}

Macros are used within the text by placing # before their name: #GREETING, #PERSON_NAME, and are recursively expanded. This feature enables you to:

Avoid repetitive text.

Easily modify common text blocks throughout the prompt.

Compose complex prompts from simple building blocks.

### 4. Random Choices
The #random directive allows injecting variation by selecting a random item from a list:

#random COLOR {red, green, blue}

Each time this directive is processed, the macro COLOR is assigned one of the three choices.

5. Comment Support
PDL supports two types of comments:

Multiline Comments: Enclosed between /* and */, can span multiple lines.

End-of-Line Comments: Begin with // and continue until the end of the line. URLs are excluded from being treated as comments (e.g. http://example.com // and some comments).

6. The Preprocessing Loop
PDL processes the text in a multi-step process, repeating it until the final result stabilizes:

Comment Removal: Removes multiline and end-of-line comments, except parts of URLs.

Line Handling: Splits by line breaks, trims lines, and combines incomplete directives.

Paragraph Grouping: Groups consecutive non-empty lines into single-line paragraphs.

Directive Execution: Executes all directives, saving macros and/or modifying the text.

Macro Expansion: Recursively expands macros within text.

Using PDL for Dynamic Prompts
PDL lets you craft dynamic prompts that adapt to various scenarios, creating complex and variable prompts by combining text:

Generate tailored content: Use the #ask directive to dynamically generate elements like names, story details, or summaries.

Create personalized experiences: Randomly select from options using #random to introduce customized experiences.

Combine AI and existing text: Create complex prompts that include human-written text and AI-generated sections.

Improve test coverage: By using random elements you can get more variety of test prompts.

Conclusion
PDL provides a flexible approach to prompt engineering by allowing you to define dynamic prompts. Through its directives, you can integrate diverse content sources, use AI for generation, maintain consistency with macros, and add variations with randomness. PDL simplifies the process of crafting sophisticated and powerful prompts for various applications.

