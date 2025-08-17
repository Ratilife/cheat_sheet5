# Word Markdown VSTO Add-in

This repository contains the source code scaffold for a Microsoft Word VSTO add-in that provides a Markdown editor/preview pane, Ribbon commands, and basic import/export of `.md` files.

The add-in implements:
- Task Pane with WebView2-based split view (editor + live preview)
- Markdown → HTML rendering via Markdig (C#)
- Prism.js syntax highlighting, MathJax, Mermaid, DOMPurify (client-side)
- Ribbon (XML) with buttons for common Markdown actions (bold, italic, lists, code block, link, image, etc.)
- Open/Save `.md` with UTF-8
- Storage of Markdown source in the Word document `CustomXMLPart` (namespace `urn:markdown/source`)

Note: Building and running a VSTO add-in requires Windows and Visual Studio with Office Developer Tools.

## Prerequisites (on Windows)
- Microsoft Word 2016/2019/2021/365 (x64 recommended)
- Windows 10/11
- Visual Studio 2022 (Community/Pro/Enterprise)
  - Workload: Office/SharePoint development
- .NET Framework 4.8 Developer Pack
- WebView2 Runtime ( Evergreen )
- Optional: Pandoc (for DOCX→MD conversion beyond the built-in scope)

## How to use this code in Visual Studio (recommended path)
1. Open Visual Studio on Windows.
2. Create a new project: "Word VSTO Add-in" (.NET Framework). Name it `WordMarkdownAddIn`.
3. Close the newly created files `ThisAddIn.cs` and the default Ribbon if any.
4. In Solution Explorer:
   - Add existing items from this repo into your project:
     - `WordMarkdownAddIn/ThisAddIn.cs`
     - `WordMarkdownAddIn/ThisAddIn.Designer.cs`
     - `WordMarkdownAddIn/Ribbon.cs`
     - `WordMarkdownAddIn/Controls/TaskPaneControl.cs`
     - `WordMarkdownAddIn/Services/MarkdownRenderService.cs`
     - `WordMarkdownAddIn/Services/DocumentSyncService.cs`
     - `WordMarkdownAddIn/Properties/AssemblyInfo.cs` (optional override)
   - Ensure the namespaces match your project root namespace (default is `WordMarkdownAddIn`).
5. Add NuGet packages to the VSTO project:
   - `Markdig` (latest stable)
   - `Microsoft.Web.WebView2` (latest stable)
   - `NLog` (optional; not required for the scaffold)
   - `Microsoft.Office.Interop.Word` (if not already referenced by the VSTO template)
6. Build the solution. Visual Studio will generate the necessary VSTO artifacts.
7. Start debugging (F5). Word will launch with the add-in loaded. A new tab `Markdown` should appear on the Ribbon.

## Features implemented in the scaffold
- Task Pane titled `Markdown` shown by default on startup
- Editor (textarea) on the left, live preview on the right (WebView2)
- Markdown rendered via Markdig pipeline in .NET
- Prism.js highlighting, Mermaid diagrams, MathJax equations, sanitized with DOMPurify
- Ribbon buttons for:
  - Toggle Pane, Open `.md`, Save `.md`
  - Bold, Italic, Strikethrough, Inline Code
  - Headings (H1), Bullet list, Numbered list, Checkbox, Table, Link, Image, Horizontal rule
  - Code block (with language), Mermaid block, Math block
- Markdown is stored in the active Word document inside a `CustomXMLPart` with namespace `urn:markdown/source`

## Notes
- The scaffold uses a simple textarea editor for reliability. You can replace it with Monaco editor later if desired.
- Mermaid rendering converts code blocks with language `mermaid` into `<div class="mermaid">` before initializing Mermaid.
- MathJax renders inline `$...$` and display `$$...$$` math. Markdig math extension is enabled.
- HTML blocks in Markdown are sanitized in the preview for safety (DOMPurify). You can adjust the whitelist inside `preview` script.

## Known limitations
- The project file (`.csproj`) for VSTO is not included; create the project via Visual Studio template and add these sources.
- Some advanced round-trip conversions Word↔Markdown require Pandoc and are out of scope of this scaffold.

## Uninstall / Clean
- Close all Word instances before rebuilding.
- Visual Studio manages registration/unregistration of the add-in during Debug runs.

## Troubleshooting
- If the Task Pane is blank, ensure WebView2 Runtime is installed.
- If the Ribbon is missing, confirm the add-in is loaded under File → Options → Add-ins → COM Add-ins.
- If build fails due to references, reinstall the Office Developer Tools workload and verify PiA references.