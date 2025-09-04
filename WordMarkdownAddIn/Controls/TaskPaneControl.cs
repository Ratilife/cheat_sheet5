using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

namespace WordMarkdownAddIn.Controls
{
	public class TaskPaneControl : UserControl
	{
		private readonly WebView2 _webView;
		private readonly Services.MarkdownRenderService _renderer;
		private string _latestMarkdown = string.Empty;
		private bool _coreReady = false;

		public TaskPaneControl()
		{
			_renderer = new Services.MarkdownRenderService();
			_webView = new WebView2
			{
				Dock = DockStyle.Fill
			};
			Controls.Add(_webView);
			Load += OnLoadAsync;
		}

		private async void OnLoadAsync(object sender, EventArgs e)
		{
			try
			{
				await _webView.EnsureCoreWebView2Async();
				_coreReady = true;
				_webView.CoreWebView2.WebMessageReceived += CoreWebView2_WebMessageReceived;
				_webView.CoreWebView2.Settings.AreDevToolsEnabled = true;
				_webView.CoreWebView2.Settings.IsStatusBarEnabled = false;
				_webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = true;

				_webView.NavigateToString(BuildHtmlShell());
			}
			catch (Exception ex)
			{
				MessageBox.Show($"WebView2 initialization failed: {ex.Message}");
			}
		}

		private void CoreWebView2_WebMessageReceived(object sender, CoreWebView2WebMessageReceivedEventArgs e)
		{
			try
			{
				var json = e.TryGetWebMessageAsString();
				if (string.IsNullOrEmpty(json)) return;
				// very simple protocol: type|payloadBase64
				var parts = json.Split(new[] { '|' }, 2);
				if (parts.Length != 2) return;
				var type = parts[0];
				var payload = Encoding.UTF8.GetString(Convert.FromBase64String(parts[1]));

				if (type == "mdChanged")
				{
					_latestMarkdown = payload;
					var html = _renderer.RenderToHtml(payload);
					PostRenderHtml(html);
				}
			}
			catch { /* ignore malformed messages */ }
		}

		private void PostRenderHtml(string html)
		{
			if (!_coreReady) return;
			var b64 = Convert.ToBase64String(Encoding.UTF8.GetBytes(html));
			_webView.CoreWebView2.ExecuteScriptAsync($"window.renderHtml(atob('{b64}'));void(0);");
		}

		public void SetMarkdown(string markdown)
		{
			_latestMarkdown = markdown ?? string.Empty;
			if (!_coreReady) return;
			var b64 = Convert.ToBase64String(Encoding.UTF8.GetBytes(_latestMarkdown));
			_webView.CoreWebView2.ExecuteScriptAsync($"window.editorSetValue(atob('{b64}'));void(0);");
		}

		public string GetCachedMarkdown() => _latestMarkdown;

		public async Task<string> GetMarkdownAsync()
		{
			// Return cached value (kept in sync by mdChanged). Fallback to JS query if needed.
			if (!string.IsNullOrEmpty(_latestMarkdown)) return _latestMarkdown;
			if (_coreReady)
			{
				var js = await _webView.CoreWebView2.ExecuteScriptAsync("window.editorGetValue()");
				return UnquoteJsonString(js);
			}
			return string.Empty;
		}

		private static string UnquoteJsonString(string jsonQuoted)
		{
			if (string.IsNullOrEmpty(jsonQuoted)) return string.Empty;
			var s = jsonQuoted;
			if (s.StartsWith("\"") && s.EndsWith("\"")) s = s.Substring(1, s.Length - 2);
			s = s.Replace("\\n", "\n").Replace("\\r", "\r").Replace("\\t", "\t").Replace("\\\"", "\"").Replace("\\\\", "\\");
			return s;
		}

		public void InsertInline(string prefix, string suffix)
		{
			if (!_coreReady) return;
			var p = Convert.ToBase64String(Encoding.UTF8.GetBytes(prefix ?? string.Empty));
			var s = Convert.ToBase64String(Encoding.UTF8.GetBytes(suffix ?? string.Empty));
			_webView.CoreWebView2.ExecuteScriptAsync($"window.insertAroundSelection(atob('{p}'), atob('{s}'));void(0);");
		}

		public void InsertSnippet(string snippet)
		{
			if (!_coreReady) return;
			var b64 = Convert.ToBase64String(Encoding.UTF8.GetBytes(snippet ?? string.Empty));
			_webView.CoreWebView2.ExecuteScriptAsync($"window.insertSnippet(atob('{b64}'));void(0);");
		}

		public void InsertHeading(int level)
		{
			if (level < 1) level = 1; if (level > 6) level = 6;
			InsertSnippet("\n" + new string('#', level) + " ");
		}

		public void InsertBulletList()
		{
			InsertSnippet("\n- ");
		}

		public void InsertNumberedList()
		{
			InsertSnippet("\n1. ");
		}

		public void InsertCheckbox(bool isChecked)
		{
			InsertSnippet(isChecked ? "\n- [x] " : "\n- [ ] ");
		}

		public void InsertTable(int rows, int cols)
		{
			if (rows < 2) rows = 2; if (cols < 2) cols = 2;
			var sb = new StringBuilder();
			// header
			for (int c = 0; c < cols; c++) sb.Append("| Header").Append(c + 1).Append(' ');
			sb.AppendLine("|");
			for (int c = 0; c < cols; c++) sb.Append("| --- ");
			sb.AppendLine("|");
			for (int r = 0; r < rows - 1; r++)
			{
				for (int c = 0; c < cols; c++) sb.Append("| cell ");
				sb.AppendLine("|");
			}
			InsertSnippet("\n" + sb.ToString() + "\n");
		}

		public void InsertLink(string text, string url)
		{
			InsertSnippet($"[{text}]({url})");
		}

		public void InsertImage(string alt, string path)
		{
			InsertSnippet($"![{alt}]({path})");
		}

		public void InsertCodeBlock(string language)
		{
			InsertSnippet($"\n```{language}\n\n```\n");
		}

		public void InsertMermaidSample()
		{
			InsertSnippet("\n```mermaid\ngraph TD; A-->B; A-->C; B-->D; C-->D;\n```\n");
		}

		public void InsertMathSample()
		{
			InsertSnippet("\n$$\\int_{0}^{1} x^2 \\; dx = \\tfrac{1}{3}$$\n");
		}

		public async void OpenMarkdownFile()
		{
			using (var dlg = new OpenFileDialog())
			{
				dlg.Filter = "Markdown (*.md)|*.md|All files (*.*)|*.*";
				if (dlg.ShowDialog() == DialogResult.OK)
				{
					var text = File.ReadAllText(dlg.FileName, new UTF8Encoding(false));
					SetMarkdown(text);
					Services.DocumentSyncService.SaveMarkdownToActiveDocument(Globals.ThisAddIn.Application, text);
				}
			}
		}

		public async void SaveMarkdownFile()
		{
			var md = await GetMarkdownAsync();
			using (var dlg = new SaveFileDialog())
			{
				dlg.Filter = "Markdown (*.md)|*.md|All files (*.*)|*.*";
				dlg.FileName = "document.md";
				if (dlg.ShowDialog() == DialogResult.OK)
				{
					File.WriteAllText(dlg.FileName, md ?? string.Empty, new UTF8Encoding(false));
					Services.DocumentSyncService.SaveMarkdownToActiveDocument(Globals.ThisAddIn.Application, md ?? string.Empty);
				}
			}
		}

		private string BuildHtmlShell()
		{
			return @"<!DOCTYPE html>
<html>
<head>
<meta charset=\"utf-8\" />
<meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
<title>Markdown</title>
<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css\" />
<style>
  html, body { height:100%; margin:0; font-family:Segoe UI, Arial, sans-serif; }
  .container { display:flex; height:100%; }
  #editor { width:50%; height:100%; border:none; padding:12px; font-family:Consolas, monospace; font-size:13px; box-sizing:border-box; outline:none; resize:none; border-right:1px solid #ddd; }
  #preview { width:50%; height:100%; overflow:auto; padding:16px; box-sizing:border-box; }
  pre { background:#f6f8fa; padding:10px; overflow:auto; }
  code { font-family:Consolas, monospace; }
  table { border-collapse: collapse; }
  table th, table td { border: 1px solid #ccc; padding: 4px 8px; }
  hr { border:none; border-top:1px solid #ccc; margin:16px 0; }
</style>
</head>
<body>
<div class=\"container\">
  <textarea id=\"editor\" placeholder=\"Введите Markdown...\"></textarea>
  <div id=\"preview\"></div>
</div>
<script src=\"https://cdn.jsdelivr.net/npm/dompurify@3.1.0/dist/purify.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js\"></script>
<script>Prism.plugins.autoloader.languages_path = 'https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/';</script>
<script src=\"https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js\"></script>
<script>mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });</script>
<script>window.MathJax = { tex: { inlineMath: [['$', '$'], ['\\\(', '\\\)']] }, svg: { fontCache: 'global' } };</script>
<script src=\"https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js\"></script>
<script>
  const editor = document.getElementById('editor');
  const preview = document.getElementById('preview');

  function debounce(fn, ms){ let t; return function(){ clearTimeout(t); t = setTimeout(()=>fn.apply(this, arguments), ms); } }

  function postToHost(type, text){
    try {
      const b64 = btoa(unescape(encodeURIComponent(text || '')));
      window.chrome && window.chrome.webview && window.chrome.webview.postMessage(type + '|' + b64);
    } catch(e) { console.error(e); }
  }

  function notifyChange(){ postToHost('mdChanged', editor.value); }

  editor.addEventListener('input', debounce(notifyChange, 120));

  window.editorSetValue = function(text){ editor.value = text || ''; notifyChange(); }
  window.editorGetValue = function(){ return editor.value || ''; }

  window.insertAroundSelection = function(prefix, suffix){
    prefix = prefix || ''; suffix = suffix || '';
    const start = editor.selectionStart || 0;
    const end = editor.selectionEnd || 0;
    const val = editor.value;
    const before = val.substring(0, start);
    const sel = val.substring(start, end);
    const after = val.substring(end);
    editor.value = before + prefix + sel + suffix + after;
    const newPos = (before + prefix + sel + suffix).length;
    editor.setSelectionRange(newPos, newPos);
    editor.focus();
    notifyChange();
  }

  window.insertSnippet = function(snippet){
    const pos = editor.selectionStart || 0;
    const val = editor.value;
    editor.value = val.substring(0, pos) + snippet + val.substring(pos);
    const newPos = (val.substring(0, pos) + snippet).length;
    editor.setSelectionRange(newPos, newPos);
    editor.focus();
    notifyChange();
  }

  window.renderHtml = function(html){
    try {
      const clean = DOMPurify.sanitize(html || '', { ADD_ATTR: ['target','rel','class','style','id'] });
      preview.innerHTML = clean;
      // Convert mermaid code blocks into divs
      const mermaidBlocks = preview.querySelectorAll('pre code.language-mermaid');
      mermaidBlocks.forEach(code => {
        const pre = code.parentElement;
        const wrapper = document.createElement('div');
        wrapper.className = 'mermaid';
        wrapper.textContent = code.textContent;
        pre.replaceWith(wrapper);
      });
      Prism.highlightAllUnder(preview);
      if (window.mermaid) {
        mermaid.init(undefined, preview.querySelectorAll('.mermaid'));
      }
      if (window.MathJax && MathJax.typesetPromise) {
        MathJax.typesetPromise([preview]).catch(err => console.error(err));
      }
    } catch(e){ console.error(e); }
  }
</script>
</body>
</html>";
		}
	}
}