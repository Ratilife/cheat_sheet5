using System;
using System.Text.RegularExpressions;
using Markdig;
using System.Net;

namespace WordMarkdownAddIn.Services
{
	public class MarkdownRenderService
	{
		private readonly MarkdownPipeline _pipeline;
		private static readonly Regex MermaidPreCodeRegex = new Regex("<pre><code class=\"language-mermaid\">([\\s\\S]*?)</code></pre>", RegexOptions.Compiled | RegexOptions.IgnoreCase);

		public MarkdownRenderService()
		{
			_pipeline = new MarkdownPipelineBuilder()
				.UseAdvancedExtensions()
				.UsePipeTables()
				.UseTaskLists()
				.UseMathematics()
				.Build();
		}

		public string RenderToHtml(string markdown)
		{
			markdown = markdown ?? string.Empty;
			var html = Markdown.ToHtml(markdown, _pipeline);
			html = TransformMermaidBlocks(html);
			return html;
		}

		private static string TransformMermaidBlocks(string html)
		{
			return MermaidPreCodeRegex.Replace(html, m =>
			{
				var inner = m.Groups[1].Value;
				var decoded = WebUtility.HtmlDecode(inner);
				return "<div class=\"mermaid\">" + decoded + "</div>";
			});
		}
	}
}